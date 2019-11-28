from rest_framework import serializers
from django.contrib.auth.models import User
from im.models import UserMessage, GroupMessage, Group

"""1 选择考量
 1 实体之间关系
 2 多模型数据表示
"""

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username']

class UserMessageSerializer(serializers.ModelSerializer):
    receiver = serializers.ReadOnlyField(source='user.user2Name')
    class Meta:
        model = UserMessage
        fields = ['timeu', 'message', 'sender', 'receiver', 'pk']
        
class GroupMessageSerializer(serializers.ModelSerializer):
    groupname = serializers.ReadOnlyField(source='group.name') # 多对一 关联； 一对多：snippets = serializers.PrimaryKeyRelatedField(many=True, queryset=Snippet.objects.all())
    # snippets = serializers.HyperlinkedRelatedField(view_name='group-detail', read_only=True)
    class Meta:
        model = GroupMessage
        fields = ['message', 'timeg', 'sender', 'pk','groupname']
        # fields = ['__all__', 'snippets']
