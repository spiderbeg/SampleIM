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
        # 用户列表
        # queryset3 = User.objects.filter(userprofile__online=True) # 筛选最近登录的用户 主要是 django 的关闭；浏览器 session 失效操作不太准确
        queryset3 = request.online_now # 利用中间件缓存设置记录在线用户，并获取在线用户
        onlineuser = [q.username for q in queryset3] # 在线用户名
        ur_serializer = UserSerializer(queryset3, many=True) 

        # 用户之间的信息
        ur = UserRelation.objects.filter(Q(userName=request.user.username) | Q(user2Name=request.user.username)) # Q 可进行复杂查询
        dz2 = {}
        for ur2 in ur:
            queryset = UserMessage.objects.filter(user=ur2)[::-1][:5]
            # print('用户私聊消息',queryset)
            serializer = UserMessageSerializer(queryset, many=True)
            dz2[str(ur2)] = serializer.data
            # 最新消息处理
            for i,q in enumerate(queryset):
                talker = q.user.user2Name if q.sender == request.user.username else q.sender
                if talker not in onlineuser: break
                temps = "%s->%s"% (request.user.username, talker)
                if i == 0: dz3[temps] = 0
                if dz3[temps] < q.pk: dz3[temps] = q.pk 

        um_serializer = dz2
        # 群组消息
        queryset2 = GroupMessage.objects.all()[::-1][:10]
        gm_serializer = GroupMessageSerializer(queryset2, many=True)
        # 最新消息 PK
        if len(queryset2) != 0: dz3["%s->%s"%(request.user.username, queryset2[0].group.name)] = queryset2[0].pk # 群组最新消息

        dz = {
            'users': ur_serializer.data,
            'usermessage': um_serializer,
            'groupmessage': gm_serializer.data,
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
    返回用户群聊接收到的id
    """
    if request.method == 'GET' and request.user.is_authenticated:
        user = request.user
        print(type(user), user, dir(user))
        group = Group.objects.get(name='firsttest')
        gu = GroupUser.objects.get(group=group,user=user)
        return Response({'gmid':gu.pk})

    return Response({'error':'please log in'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def history_message(request, format=None): # 函数式的写法
    """
    返回用户群聊接收到的id
    """
    if request.method == 'GET' and request.user.is_authenticated and 'user1' in request.GET:
        print(11111111,request.GET)
        user1name = request.GET['user1']
        user2name = request.GET['user2']
        minpk = request.GET['minpk']
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
        else:
            queryset2 = GroupMessage.objects.filter(pk__lt=int(minpk))[::-1][:10]
            hm_serializer = GroupMessageSerializer(queryset2, many=True).data
        return Response(hm_serializer)

    return Response({'error':'please add parameter'}, status=status.HTTP_400_BAD_REQUEST)