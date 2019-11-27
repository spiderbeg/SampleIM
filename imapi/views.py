from django.shortcuts import render
from django.contrib.auth.models import User
from django.utils import timezone

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

class TotalMessageViewSet(viewsets.ReadOnlyModelViewSet):
    """
       用户初次登录时
       返回与用户相关信息
    """
    # 添加权限
    permission_classes = [permissions.IsAuthenticated] # 权限设置，登录用户可见
    def list(self, request, format=None, **kwargs):
        user = request.user
        print(type(user), user)
        # 用户列表
        # up = UserProfile.objects.filter(online=True)
        queryset3 = User.objects.filter(userprofile__online=True) # 筛选 
        ur_serializer = UserSerializer(queryset3, many=True) 
        # 用户之间的信息
        queryset = UserMessage.objects.all()
        um_serializer = UserMessageSerializer(queryset, many=True)
        # 群组消息
        queryset2 = GroupMessage.objects.all()[::-1][:20]
        gm_serializer = GroupMessageSerializer(queryset2, many=True)
        dz = {
            'users': ur_serializer.data,
            'usermessage': um_serializer.data,
            'groupmessage': gm_serializer.data,
            'thanks': 'right!',
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
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly]
    # 保存数据
    def perform_create(self, serializer):
        group = Group.objects.get(name='firsttest') # 对于外键的处理
        serializer.save(group=group)

class UserMessageViewSet(viewsets.ModelViewSet):
    """
    用户私聊信息
    """
    queryset = UserMessage.objects.all()
    serializer_class = UserMessageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly]

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

    