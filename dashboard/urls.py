from django.urls import path
from rest_framework import routers
from dashboard.views.dashboardview import login_request, homepage, logout_request, AdminListView, AdminCreateView, AdminDetailView, AdminUpdateView, AdminDeleteView

app_name = 'dashboard'
router = routers.SimpleRouter()

urlpatterns = tuple(router.urls)

urlpatterns += (
    path("", homepage, name="homepage"),
    path("login", login_request, name="login"),
    path("logout", logout_request, name="logout"),
    
    # Admin CRUD operations
    # list admin
    path('admins', AdminListView.as_view(), name='admins'),
    # create admin
    path('admins/create', AdminCreateView.as_view(), name='admins-create'),
    # detail admin
    path('admins/<int:pk>', AdminDetailView.as_view(), name='admins-detail'),
    # update admin
    path('admins/<int:pk>/update', AdminUpdateView.as_view(), name='admins-update'),
    # delete admin
    path('admins/<int:pk>/delete', AdminDeleteView.as_view(), name='admins-delete'),

)
