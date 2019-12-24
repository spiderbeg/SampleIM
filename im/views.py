from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib.auth.models import User # 导入 Django 验证系统
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login, authenticate
from django.core.exceptions import ObjectDoesNotExist


from .models import UserProfile, UserRelation, Group, GroupUser, UserMessage, GroupMessage


# Create your views here.

# def sendmessage(request):
#     """发送消息"""
#     user = request.user
#     sender = request.user.username
#     message = request.POST['groupmessage']
#     # print(sender,request.POST,message=='')
#     group,created = Group.objects.get_or_create(name = 'firsttest') # 测试用群
#     gp = GroupMessage.objects.create(group=group, message=message, sender=sender) # 保存群消息
#     group,created = GroupUser.objects.get_or_create(group=group,user=user,groupName='firsttest',userName=sender) # 建立群用户关系
#     return redirect('im:talkRoom')


@login_required
def talkRoom(request):
    """返回群消息，用户消息"""
    try:
        Group.objects.get(name='firsttest') # 测试用群
    except ObjectDoesNotExist:
        Group.objects.get_or_create(name='firsttest',creator=request.user) # 测试用群
    return render(request, 'im/chatroom2.html', {'gourpmessages': ''}) #


def getLogin(request):
    """保存用户登录时间"""
    return redirect('im:talkRoom')

def getLogout(request):
    """重定向至登录页面"""
    logout(request) # 登出
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

# from im.models import SaveImage
# def testform(request):
#     """测试表单"""
#     print('length', request.META['CONTENT_LENGTH'])
#     bf = request.FILES
#     print(bf)
#     print(111111111,vars(bf))
#     print('django 自带form 使用\n ',bf['fileInput'].file.getvalue())
#     pic = SaveImage.objects.create(user=request.user,image_file=bf['fileInput'])
#     # return Response({'image_path': pic.image_file.url})
#     return redirect('im:talkRoom')

