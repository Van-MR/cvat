from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

from cvat.apps.onepanelio.models import AdminUser, AuthToken

UserModel = get_user_model()


class OnepanelIOBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        # Ensure admin user exists
        AdminUser.create_admin_user(request)
        try:
            # To allow auto-login for admin, check if the form is empty
            if username is None:
                username = "admin"
            user = UserModel._default_manager.get_by_natural_key(username)
            if password is None:
                password = AuthToken.get_auth_token(request)
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            UserModel().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
