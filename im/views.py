from django.shortcuts import render, redirect
from .models import UserProfile, UserRelation, Group, GroupUser, UserMessage, GroupMessage
from django.utils import timezone
from django.contrib.auth.models import User # 导入 Django 验证系统

from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm

from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login

# Create your views here.

def sendmessage(request):
    """发送消息"""
    user = request.user
    sender = request.user.username
    message = request.POST['groupmessage']
    print(sender,request.POST,message=='')
    group,created = Group.objects.get_or_create(name = 'firsttest') # 测试用群
    gp = GroupMessage.objects.create(group=group, message=message, sender=sender) # 保存群消息
    group,created = GroupUser.objects.get_or_create(group=group,user=user,groupName='firsttest',userName=sender) # 建立群用户关系
    return redirect('im:talkRoom')


@login_required
def talkRoom(request):
    """返回群消息，用户消息"""
    # uid = request.user.pk
    group,created = Group.objects.get_or_create(name='firsttest') # 测试用群
    # print(type(group),dir(group))
    # gp = group.groupmessage_set.all()
    # print(gp)
    return render(request, 'im/chatroom.html', {'gourpmessages': ''}) #


def getLogin(request):
    """保存用户登录时间"""
    user = request.user
    UserProfile.objects.update_or_create(
    user = user,
    defaults={'loginTime': timezone.now()},
    )
    return redirect('im:talkRoom')

def getLogout(request):
    """保存用户登出时间"""
    user = request.user # 获取用户名
    logout(request) # 登出
    UserProfile.objects.update_or_create(
    user = user,
    defaults={'logoutTime': timezone.now()},
    )
    return redirect('im:talkRoom')

#----------signup------------------------------------------------------------
def signup(request):#用户注册
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password) # 用户注册，返回用户对象
            login(request, user) # 执行登录过程
            return redirect('im:talkRoom')
    else:
        form = UserCreationForm()
    return render(request, 'im/signup.html', {'form':form})
