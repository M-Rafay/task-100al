from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy, reverse
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.views.generic.edit import DeleteView
from django.http import HttpResponseRedirect
from django.contrib.auth.models import Group
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db import transaction
from requests import request
import os
import pandas as pd


from user.models.usermodel import User
from ..forms.userforms import UserCreateForm, UserUpdateForm
from task import settings as SETTINGS
# from task.utils import helper as HELPER

import logging
logger = logging.getLogger(__name__)


def login_request(request):
    '''login view for the dashboard'''
    try:
        # if request.method == "POST" then the user will be authenticated
        if request.method == "POST":
            # request form data validations
            form = AuthenticationForm(request, data=request.POST)
            if form.is_valid():
                username = form.cleaned_data.get('username')
                if username.contains("abc"):
                    logger.error(f"User with name abc in it is not accepted")
                    messages.error(request, "User with name abc in it is not accepted")
                    
                    
                password = form.cleaned_data.get('password')
                # authenticate the user
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    messages.info(request, f"You are now logged in as {username}.")
                    logger.info(f"User {username} logged in.")
                    return redirect("/dashboard/")
                else:
                    logger.error(f"User {username} failed to login.")
                    messages.error(request, "Invalid username or password.")
            else:
                logger.error("User failed to login.")
                messages.error(request, "Invalid username or password.")
        # if request.method == "GET" then the user will be redirected to the login page
        form = AuthenticationForm()
        logger.info("login page accessed.")
        return render(request=request, template_name="company/login.html",
                      context={"login_form": form})
    except Exception as e:
        logger.error(f"Error in login_request: {e}")
        messages.error(request, "Invalid username or password.")


def homepage(request):
    '''Homepage view for the dashboard'''
    try:
        return render(request=request, template_name="company/home.html")
    except Exception as e:
        logger.error(f"Error in homepage: {e}")
        messages.error(request, "Error getting the Homepage")
        return redirect("/dashboard")


def logout_request(request):
    '''logout view for the dashboard'''
    try:
        logout(request)
        messages.info(request, "You have successfully logged out.")
        return redirect("/dashboard/login")
    except Exception as e:
        logger.error(f"Error in logout_request: {e}")
        messages.error(request, "Error logging out.")
        return redirect("/dashboard/login")

class AdminListView(PermissionRequiredMixin, LoginRequiredMixin, ListView):
    '''List view for admins'''
    permission_required = 'user.view_user'
    model = User
    template_name = 'admins/list.html'
    context_object_name = 'admins'
    paginate_by = 5
    login_url = '/dashboard/login'
    success_message = 'Admin successfully fetched!'
    error_message = "Error getting the Admins"

    def get_paginate_by(self, queryset):
        """
        Paginate by specified value in querystring, or use default class property value.
        """
        return self.request.GET.get('paginate_by', self.paginate_by)

    def get_queryset(self, *args, **kwargs):
        try:
            # get filters in the query string
            q = self.request.GET.get('q')
            # get order_by in the query string
            order_by = self.request.GET.get('order_by', 'id')
            # Get company profile
            
            if q:
                # searches through everything using Q import
                self.admins = User.objects.filter(
                    Q(id__icontains=q) |
                    Q(name__icontains=q) |
                    Q(role__icontains=q) |
                    Q(phone_no__icontains=q),
                    # only show users in User_Role group
                    groups__name='User_Role'
                    ).order_by(order_by)
            else:
                # if no query string is provided, show all users in User_Role group
                self.admins = User.objects.filter(
                    groups__name='User_Role').order_by(order_by)
            
            return self.admins
        except Exception as e:
            logger.error(f"Error in get_queryset: {e}")
            messages.error(self.request, self.error_message)
            return None

    def get_context_data(self, **kwargs):
        '''overrides the default context data for pagination'''
        try:
            context = super(AdminListView, self).get_context_data(**kwargs)
            admins = self.get_queryset()
            df = pd.DataFrame(User.objects.filter(groups__name='User_Role').values())
            df.to_csv(SETTINGS.BASE_DIR + '/data/admins.csv', index=False)
            page = self.request.GET.get('page')
            order_by = self.request.GET.get('order_by', 'id')
            # dynamic pagination
            self.paginate_by = self.request.GET.get('paginate_by', 5)
            try:
                int(self.paginate_by)
            except ValueError:
                self.paginate_by = 5
            paginator = Paginator(admins, self.paginate_by)
            try:
                # get the page number from the query string
                admins = paginator.page(page)
            except PageNotAnInteger:
                admins = paginator.page(1)
            except EmptyPage:
                admins = paginator.page(paginator.num_pages)
            context['admins'] = admins
            context['order_by'] = order_by
            context['user_csv'] = SETTINGS.SITE_URL + SETTINGS.MEDIA_URL + 'admins.csv'
            return context
        except Exception as e:
            logger.error(f"Error in get_context_data: {e}")
            messages.error(self.request, self.error_message)
            return None


class AdminCreateView(CreateView):
    '''Create view for admins'''

    model = User
    form_class = UserCreateForm
    template_name = 'admins/create.html'
    success_url = reverse_lazy('dashboard:admins')
    # failure_url = reverse_lazy('dashboard:admins')
    success_message = 'Admin successfully created!'
    error_message = "Error creating the Admin"

    def get_context_data(self, **kwargs):
        
        context = super(AdminCreateView, self).get_context_data(**kwargs)
        # passing role and groups to the form
        context['title'] = 'Create ' + self.request.GET.get('role').replace('_', ' ')
        context['role'] = self.request.GET.get('role').replace('_', ' ')
        context['group'] = self.request.GET.get('role')
        return context

    def post(self, request, *args, **kwargs):
        '''overrides the default post method to generate a password and
            add the user to the User_Role group'''
        try:
            if self.request.method == 'POST':
                data = self.request.POST.copy()
                # extracting group from role
                data['created_by'] = 1
                group = data['role']
                data['role'] = group.replace('_', ' ').title()

                form = UserCreateForm(data, request.FILES)
                with transaction.atomic():
                    if form.is_valid():
                        self.object = form.save(commit=False)
                        self.object.set_password(data['password'])
                        self.object.save()
                        # add the user to the User_Role group
                        my_group = Group.objects.get(name=group)
                        my_group.user_set.add(self.object)
                        login(request, self.object)
                        return HttpResponseRedirect(self.get_success_url())
                    messages.error(self.request, self.error_message)
                    return super(AdminCreateView, self).post(request, *args, **kwargs)
        except Exception as e:
            
            logger.error(f"Error in post: {e}")
            messages.error(self.request, self.error_message)
            return super(AdminCreateView, self).post(request, *args, **kwargs)


class AdminDetailView(PermissionRequiredMixin, LoginRequiredMixin, DetailView):
    '''Detail view for admins'''
    
    permission_required = 'user.view_user'
    model = User
    template_name = 'admins/detail.html'
    context_object_name = 'admin'
    login_url = '/dashboard/login'

    def get_context_data(self, **kwargs):
        
        context = super(AdminDetailView, self).get_context_data(**kwargs)
        # creating a presigned url for the profile image
        return context


class AdminUpdateView(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    '''Update view for admins'''
    
    permission_required = 'user.change_user'
    model = User
    template_name = 'admins/update.html'
    context_object_name = 'admin'
    form_class = UserUpdateForm
    login_url = '/dashboard/login'
    success_message = 'Admin successfully updated!'
    error_message = "Error updating the Admin"

    # redirects to the admin list view if unauthorized permission
    def handle_no_permission(self):
        messages.error(self.request, "You do not have permission to perform this action.")
        return redirect('dashboard:admins')

    def get_success_url(self):
        '''overrides the default success url to redirect to the admins list page'''
        try:
            return reverse_lazy('dashboard:admins')
        except Exception as e:
            logger.error(f"Error in get_success_url: {e}")
            messages.error(self.request, self.error_message)
            return reverse_lazy('')

    def get_context_data(self, **kwargs):
        
        context = super(AdminUpdateView, self).get_context_data(**kwargs)
        # if str(self.request.id) != str(self.kwargs['pk']):
        #     messages.error(self.request, "user cannot update other users")
        #     raise Exception("user cannot update other users")
        # passing role and groups to the form
        context['title'] = 'Create ' + self.request.GET.get('role').replace('_', ' ')
        context['role'] = self.request.GET.get('role').replace('_', ' ')
        context['group'] = self.request.GET.get('role')
        # creating a presigned url for the profile image
        return context

    def post(self, request, pk, *args, **kwargs):
        '''overrides the default post method to generate a password and
            add the user to the User_Role group'''
        try:
            if request.POST.get('cancel'):
                return HttpResponseRedirect(self.get_success_url())
            else:
                
                is_password_updated = False
                user_obj = User.objects.get(id=pk)

                data = self.request.POST.copy()
                data._mutable = True

                # extracting group from role
                group = data['role']
                data['role'] = group.replace('_', ' ').title()
                # if password not found in request then set the password to the existing password
                if 'password' not in data or data['password'] == "":
                    data["password"] = user_obj.password
                    is_password_updated = True
                
                form = UserUpdateForm(data, instance=user_obj)
                with transaction.atomic():
                    if form.is_valid():
                        self.object = form.save(commit=False)
                        # if password found in request then reset the password
                        if ('password' in data and data['password'] != "" and
                        not is_password_updated):
                            self.object.set_password(data['password'])
                        self.object.save()

                        return HttpResponseRedirect(self.get_success_url())                    
                    messages.error(self.request, self.error_message)
                    return super(AdminUpdateView, self).post(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in post: {e}")
            messages.error(self.request, self.error_message)
            return super(AdminUpdateView, self).get(request, *args, **kwargs)


    def get(self, request, pk, *args, **kwargs):
        super(AdminUpdateView, self).get(request, *args, **kwargs)
        if str(self.request.user.id) != str(self.kwargs['pk']):
            messages.error(self.request, "user cannot update other users")
            # raise Exception("user cannot update other users")
            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(**kwargs))   
class AdminDeleteView(PermissionRequiredMixin, LoginRequiredMixin, DeleteView):
    '''Delete view for admins'''

    permission_required = 'user.delete_user'
    model = User
    # template_name = 'admins/delete.html'
    success_url = reverse_lazy('dashboard:admins')
    login_url = '/dashboard/login'
    success_message = 'Admin successfully deleted!'
    error_message = "Error deleting the Admin"

    def delete(self, request, *args, **kwargs):
        '''overrides the default delete method to soft delete the user'''
        try:
            self.object = self.get_object()
            self.object.soft_delete()
            return HttpResponseRedirect(self.get_success_url())
        except Exception as e:
            logger.error(f"Error in delete: {e}")
            messages.error(self.request, self.error_message)
            return HttpResponseRedirect(self.get_success_url())
