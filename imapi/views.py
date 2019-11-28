from django.shortcuts import render
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q

from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import api_view


from imapi.permissions import IsOwnerOrReadOnly
from im.models import UserMessage, GroupMessage, UserRelation, Group, GroupUser, UserProfile
from imapi.serializer import UserMessageSerializer, GroupMessageSerializer, UserSerializer

# Create your views here.
""" ViewSet 简化操作
"""
# curl -X POST -d "message=gdivudgjfd&sender=t2&to=spiderbeg" --user t2:pythonbegin1 http://127.0.0.1:8000/imapi/usermessage/

class TotalMessageViewSet(viewsets.ReadOnlyModelViewSet):
    """
       用户初次登录时
       返回与用户相关信息
    """
    # 添加权限
    permission_classes = [permissions.IsAuthenticated] # 权限设置，登录用户可见
    def list(self, request, format=None, **kwargs):
        user = request.user
        # print(type(user), user)
        # 用户列表
        # queryset3 = User.objects.filter(userprofile__online=True) # 筛选最近登录的用户 主要是 django 的关闭；浏览器 session 失效操作不太准确
        queryset3 = request.online_now # 利用中间件缓存设置记录在线用户
        ur_serializer = UserSerializer(queryset3, many=True) 

        # 用户之间的信息
        ur = UserRelation.objects.filter(Q(userName=request.user.username) | Q(user2Name=request.user.username)) # Q 可进行复杂查询
        dz2 = {}
        for ur2 in ur:
            queryset = UserMessage.objects.filter(user=ur2)[::-1][:20]
            serializer = UserMessageSerializer(queryset, many=True)
            dz2[str(ur2)] = serializer.data
        um_serializer = dz2

        # 群组消息
        queryset2 = GroupMessage.objects.all()[::-1][:20]
        gms = queryset2[-1].pk
        gme = queryset2[0].pk
        gm_serializer = GroupMessageSerializer(queryset2, many=True)
        dz = {
            'users': ur_serializer.data,
            'usermessage': um_serializer,
            'groupmessage': gm_serializer.data,
            'um_status': {'start':gms,'end':gme},
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
        print(11111111111111111111111111,self.request.POST['sender'])
        group = Group.objects.get(name='firsttest') # 对于外键的处理
        serializer.save(group=group)

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
        print(2222222, sender,to,ur)
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
    返回用户群聊接收到的id
    """
    if request.method == 'GET' and request.user.is_authenticated:
        user = request.user
        print(type(user), user, dir(user))
        group = Group.objects.get(name='firsttest')
        gu = GroupUser.objects.get(group=group,user=user)
        return Response({'gmid':gu.pk})

    return Response({'error':'please log in'}, status=status.HTTP_400_BAD_REQUEST)

    