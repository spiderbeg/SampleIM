# 记录用户在线与否
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.contrib.auth.models import User
from im.models import UserProfile

def record_user_logged_in(sender, user, request, **kwargs):
    # Record the user logged in
    if request.user.is_authenticated:
        up = UserProfile.objects.filter(user=request.user).update(online=True)
        


def record_user_logged_out(sender, user, request, **kwargs):
    # Record the user logged out
    if request.user.is_authenticated:
        up = UserProfile.objects.filter(user=request.user).update(online=False)

user_logged_in.connect(record_user_logged_in)
user_logged_out.connect(record_user_logged_out)