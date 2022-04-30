from django import forms

from user.models.usermodel import User


class UserCreateForm(forms.ModelForm):
    '''User Create and Update Form'''
    class Meta:
        model = User
        fields = ['name', 'password', 'phone_no', 'email', 'role']

    # creating fields non mandatory
    def __init__(self, *args, **kwargs):
        super(UserCreateForm, self).__init__(*args, **kwargs)


class UserUpdateForm(forms.ModelForm):
    '''User Create and Update Form'''
    class Meta:
        model = User
        fields = ['name', 'password', 'phone_no', 'email', 'role']

    # creating fields non mandatory
    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        self.fields['password'].required = False

