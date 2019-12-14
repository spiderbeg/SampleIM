from django.shortcuts import render
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q
from django.conf import settings

from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.decorators import parser_classes
from rest_framework.parsers import FileUploadParser,FormParser

from PIL import Image

from imapi.permissions import IsOwnerOrReadOnly
from im.models import UserMessage, GroupMessage, UserRelation, Group, GroupUser, UserProfile, SaveImage
from imapi.serializer import UserMessageSerializer, GroupMessageSerializer, UserSerializer, SaveImageSerializer

import sys
# Create your views here.
""" ViewSet 简化操作
"""
# curl -X POST -d "message=gdivudgjfd&sender=t2&to=spiderbeg" --user t2:pythonbegin1 http://127.0.0.1:8000/imapi/usermessage/

class TotalMessageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    返回用户最新消息
    用户初次登录时
    返回与用户相关信息
    """
    # 添加权限
    permission_classes = [permissions.IsAuthenticated] # 权限设置，登录用户可见
    def list(self, request, format=None, **kwargs):
        """返回用户最新消息
        """
        dz3 = {} # 记录用户最新消息 pk
        # dz2 = {} # 用户上登录接收消息信息
        # 1 用户列表
        # 筛选最近登录的用户 主要是 django 的关闭；浏览器 session 失效操作不太准确
        # queryset3 = User.objects.filter(userprofile__online=True)
        queryset3 = request.online_now # 利用中间件缓存设置记录在线用户，并获取在线用户
        onlineuser,users = [],[] # 在线用户名
        for q in queryset3:
            dz5 = {} 
            dz5['username']=q.username
            onlineuser.append(q.username)
            users.append(dz5)
        # ur_serializer = UserSerializer(queryset3, many=True) 

        # 获取用户最新消息
        ur = UserRelation.objects.filter(Q(userName=request.user.username) | Q(user2Name=request.user.username)) # Q 可进行复杂查询
        for ur2 in ur:
            queryset = UserMessage.objects.filter(user=ur2)[::-1][:5] # 最近的 5 条消息
            # if ur2.userName != request.user.username and ur2.userName in onlineuser: dz2[ur2.userName] = ur2.umid # 获取在线用户记录的消息 id
            # 最新消息处理
            for q in queryset:
                talker = q.user.user2Name if q.sender == request.user.username else q.sender
                if talker not in onlineuser: break
                temps = "%s->%s"% (request.user.username, talker)
                if temps not in dz3: dz3[temps] = 0
                if dz3[temps] < q.pk: 
                    dz3[temps] = q.pk
        # 保存用户最新消息 id
        for ur2 in ur:
            talker = ur2.user2Name if ur2.userName == request.user.username else ur2.userName
            if talker not in onlineuser: break
            temps = "%s->%s"% (request.user.username, talker)
            if temps in dz3: ur2.umid = dz3[temps];ur2.save() # 需要前端保存用户未查看信息获取前端发送用户未查看信息到后端，后端再保存。

        # 群组消息
        # 最新消息 PK
        queryset2 = GroupMessage.objects.all()[::-1][:10]
        if len(queryset2) != 0: dz3["%s->%s"%(request.user.username, queryset2[0].group.name)] = queryset2[0].pk # 群组最新消息

        dz = {
            'users': users,
            # 'last_messsage': dz2,
            'message_status': dz3,
        }
        return Response(dz)
    def retrieve(self, *args, **kwargs):
        return Response(status=status.HTTP_404_NOT_FOUND)

class GroupMessageViewSet(viewsets.ModelViewSet):
    '''
    用户群聊信息发送
    '''
    queryset = GroupMessage.objects.all()
    serializer_class = GroupMessageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,permissions.IsAuthenticated,
                          IsOwnerOrReadOnly]
    # 保存数据
    def perform_create(self, serializer):
        # print(11111111111111111111111111,self.request.POST['sender'])
        group = Group.objects.get(name='firsttest') # 对于外键的处理
        serializer.save(group=group)
        # 此时用户最新

class UserMessageViewSet(viewsets.ModelViewSet):
    """
    用户私聊信息
    """
    queryset = UserMessage.objects.all()
    serializer_class = UserMessageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,permissions.IsAuthenticated,
                          IsOwnerOrReadOnly]
    # 保存数据
    def perform_create(self, serializer):
        sender = self.request.user
        to = User.objects.get(username=self.request.POST['to'])
        ur,created = UserRelation.objects.get_or_create(user=sender,userName=sender.username,user2Name=self.request.POST['to'])
        serializer.save(user=ur)
    def list(self, request): # 重写方法
        ur = UserRelation.objects.filter(Q(userName=request.user.username) | Q(user2Name=request.user.username)) # Q 可进行复杂查询
        dz = {}
        for ur2 in ur:
            queryset = UserMessage.objects.filter(user=ur2)
            serializer = UserMessageSerializer(queryset, many=True)
            dz[str(ur2)] = serializer.data
        return Response(dz)

@api_view(['GET'])
def groupmgpk(request, format=None): # 函数式的写法
    """
    测试接口
    """
    if request.method == 'GET':
        print('汝宁 running。。。。')
        return Response({'gmid':'ok'})

    return Response({'error':'please log in'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def history_message(request, format=None): # 函数式的写法
    """
    返回用户群聊接收到的id
    """
    paralist = ['user1','user2','minpk','type']
    # print('22222222',request)
    if request.method == 'GET' and request.user.is_authenticated and all(k in request.GET and  request.GET[k] not in ['NaN','undefined','null'] for k in paralist): # all() 所有为真返回真
        # print(11111111,request.GET)
        user1name = request.GET['user1']
        user2name = request.GET['user2']
        minpk = int(request.GET['minpk'])
        tp = request.GET['type']
        if tp == 'personal':
            # 用户之间的信息
            ur = UserRelation.objects.filter(Q(userName=user1name,user2Name=user2name) | Q(userName=user2name,user2Name=user1name)) # Q 可进行复杂查询
            dz2 = {}
            for ur2 in ur:
                queryset = UserMessage.objects.filter(user=ur2, pk__lt=int(minpk))[::-1][:5]
                # print('queryset of um',queryset)
                serializer = UserMessageSerializer(queryset, many=True)
                dz2[str(ur2)] = serializer.data
            hm_serializer = dz2
            # print('返回的是啥',hm_serializer)

        else:
            queryset2 = GroupMessage.objects.filter(pk__lt=int(minpk))[::-1][:10]
            hm_serializer = GroupMessageSerializer(queryset2, many=True).data
        return Response(hm_serializer)

    return Response({'error':'please use correct parameters'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def newest_message(request, format=None): # 函数式的写法
    """
    返回用户群聊接收到的id
    """
    paralist = ['user1','user2','maxpk','type']
    if request.method == 'GET' and request.user.is_authenticated and all(k in request.GET and  request.GET[k] not in ['NaN','undefined','null'] for k in paralist): # all() 所有为真返回真
        # print(11111111,request.GET,request.user)
        user1name = request.GET['user1']
        user2name = request.GET['user2']
        maxpk = request.GET['maxpk']
        tp = request.GET['type']
        if tp == 'personal':
            # 用户之间的信息
            ur = UserRelation.objects.filter(Q(userName=user1name,user2Name=user2name) | Q(userName=user2name,user2Name=user1name)) # Q 可进行复杂查询
            dz2 = {}
            for ur2 in ur:
                queryset = UserMessage.objects.filter(user=ur2, pk__gt=int(maxpk))[::-1]
                # print('queryset of um',queryset)
                serializer = UserMessageSerializer(queryset, many=True)
                dz2[str(ur2)] = serializer.data
            hm_serializer = dz2
        else:
            queryset2 = GroupMessage.objects.filter(pk__gt=int(maxpk)).reverse() # 与[::-1] 相同
            hm_serializer = GroupMessageSerializer(queryset2, many=True).data
        return Response(hm_serializer)

    return Response({'error':'please use correct parameters'}, status=status.HTTP_400_BAD_REQUEST)

# 保存文件到到服务器，并返回 url
@api_view(['POST'])
# @parser_classes((FormParser,))
@permission_classes((permissions.IsAuthenticated, ))
def imagefile(request, format=None):
    """
     1 保存上传的图像文件
     2 返回 url
    """
    # 获取上传的文件信息
    bf = request.FILES # <- django 等价于 request.data <-rest framework
    pic = SaveImage.objects.create(user=request.user,image_file=bf['fileInput'])
    return Response({'image_path': pic.image_file.url})