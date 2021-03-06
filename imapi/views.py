from django.contrib.auth.models import User
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist

from rest_framework.response import Response
from rest_framework import status, viewsets, mixins, permissions
from rest_framework.decorators import api_view, permission_classes, parser_classes


from imapi.permissions import IsOwnerOrReadOnly
from im.models import UserMessage, GroupMessage, UserRelation, Group, GroupUser, UserProfile, SaveImage
from imapi.serializer import UserMessageSerializer, GroupMessageSerializer, UserSerializer, SaveImageSerializer

# Create your views here.
""" ViewSet 简化操作
"""

class TotalMessageViewSet(mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    """
    0 只需要 list 操作， GET 请求时，返回响应数据, 所以使用 mixins.ListModelMixin  viewsets.GenericViewSet
    1 返回用户最新消息, 
    2 返回用户列表
    """
    # 添加权限
    permission_classes = [permissions.IsAuthenticated] # 权限设置，登录用户可见
    def list(self, request, format=None, **kwargs):
        """1 返回用户最新消息；
           2 此方法下修改请求本接口时，返回的 json 数据
        """
        dz3 = {} # 记录用户最新消息 pk
        # 1 用户列表
        queryset3 = request.online_now # 利用中间件缓存设置记录在线用户，并获取在线用户。注意： django 的关闭；浏览器 session 失效操作不太准确
        onlineuser = [] # 在线用户名
        for q in queryset3: onlineuser.append(q.username)
        users = UserSerializer(queryset3, many=True).data 

        # 2.1 获取用户最新消息
        ur = UserRelation.objects.filter(Q(user=request.user) | Q(user2=request.user)) # Q 可进行复杂查询
        for ur2 in ur:
            queryset = UserMessage.objects.filter(userrelation=ur2)[::-1][:5] # 最近的 5 条消息
            # 最新消息处理
            for q in queryset:
                talker = q.receiver if q.sender == request.user.username else q.sender
                if talker not in onlineuser: break
                temps = "%s->%s"% (request.user.username, talker)
                if temps not in dz3: dz3[temps] = 0
                if dz3[temps] < q.pk: dz3[temps] = q.pk

        # 保存用户最新消息 id。----暂未使用
        # for ur2 in ur:
        #     talker = ur2.user2.username if ur2.user.username == request.user.username else ur2.user.username
        #     if talker not in onlineuser: break
        #     temps = "%s->%s"% (request.user.username, talker)
        #     if temps in dz3: ur2.umid = dz3[temps];ur2.save() # 需要前端保存用户未查看信息获取前端发送用户未查看信息到后端，后端再保存。

        # 2.2 获取群组最新消息 PK；注意：此处当作只有一个群组处理
        queryset2 = GroupMessage.objects.all()[::-1][:10]
        if len(queryset2) != 0: dz3["%s->%s"%(request.user.username, queryset2[0].group.name)] = queryset2[0].pk # 群组最新消息
        # 返回数据综合
        dz = {
            'users': users,
            'message_status': dz3,
        }
        return Response(dz)


class GroupMessageViewSet(viewsets.ModelViewSet):
    '''
    用户群聊信息发送
    '''
    queryset = GroupMessage.objects.all()
    serializer_class = GroupMessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly] # 1 登录用户可见，消息发送者可修改
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
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly] # 1 登录用户可见，消息发送者可修改
    # 保存数据
    def perform_create(self, serializer):
        """
        1 前端 post 的数据要与后端字段名符合
        2 这里主要是对于外键的处理
        """
        sender = self.request.user
        receiver = User.objects.get(username=self.request.POST['receiver'])
        try:
            ur = UserRelation.objects.get(user=receiver,user2=sender)
        except ObjectDoesNotExist:
            ur, _ = UserRelation.objects.get_or_create(user=sender,user2=receiver)
        # 保存外键信息
        serializer.save(userrelation=ur)

    def list(self, request): # 重写方法
        """
        处理 get 请求返回的数据
        """
        ur = UserRelation.objects.filter(Q(user=request.user) | Q(user2=request.user)) # Q 可进行复杂查询
        dz = {}
        for ur2 in ur:
            queryset = UserMessage.objects.filter(userrelation=ur2)
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
@permission_classes((permissions.IsAuthenticated, ))
def history_message(request, format=None): # 函数式的写法
    """
    返回用户群聊接收到的id
    """
    return handle_messgae(request)

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated, ))
def newest_message(request, format=None): # 函数式的写法
    """
    返回用户群聊接收到的id
    """
    return handle_messgae(request)

@api_view(['POST'])
# @parser_classes((FormParser,)) 这个会影响 django 处理，若无返回图片数据内容需求，可不使用
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

# 历史消息和最新消息的处理函数
def handle_messgae(request, format=None):
    """
    1 根据 pk 确定 -> minpk: 历史消息; maxpk: 最近消息.
    2 返回相应的消息
    """
    paralist = ['user1','user2','minpk','type'] if 'minpk' in request.GET else ['user1','user2','maxpk','type']
    if all(k in request.GET and  request.GET[k] not in ['NaN','undefined','null'] for k in paralist): # all() 所有为真返回真
        user1name, user2name = request.GET['user1'], request.GET['user2']
        usepk = int(request.GET[paralist[2]])
        tp = request.GET['type']
        if tp == 'personal':
            # 用户之间的信息
            user = User.objects.get(username=user1name)
            user2 = User.objects.get(username=user2name)
            ur = UserRelation.objects.filter(Q(user=user,user2=user2) | Q(user=user2,user2=user)) # Q 可进行复杂查询
            dz2 = {}
            for ur2 in ur:
                if 'minpk' == paralist[2]:
                    queryset = UserMessage.objects.filter(userrelation=ur2, pk__lt=int(usepk))[::-1][:5]
                else:
                    queryset = UserMessage.objects.filter(userrelation=ur2, pk__gt=int(usepk))[::-1]
                serializer = UserMessageSerializer(queryset, many=True)
                dz2[str(ur2)] = serializer.data 
            hm_serializer = dz2

        else:# 群组信息
            if 'minpk' == paralist[2]:
                queryset2 = GroupMessage.objects.filter(pk__lt=int(usepk))[::-1][:10]
            else:
                queryset2 = GroupMessage.objects.filter(pk__gt=int(usepk)).reverse()
            hm_serializer = GroupMessageSerializer(queryset2, many=True).data
        return Response(hm_serializer)

    return Response({'error':'please use correct parameters'}, status=status.HTTP_400_BAD_REQUEST)