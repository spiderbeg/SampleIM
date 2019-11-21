from rest_framework import serializers
from django.contrib.auth.models import User
from im.models import UserMessage, GroupMessage, Group

"""1 选择考量
 1 实体之间关系
 2 多模型数据表示
"""

class UserMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserMessage
        fields = '__all__'
        
class GroupMessageSerializer(serializers.ModelSerializer):
    # groupname = serializers.ReadOnlyField(source='group.name') # 多对一 关联； 一对多：snippets = serializers.PrimaryKeyRelatedField(many=True, queryset=Snippet.objects.all())
    # snippets = serializers.HyperlinkedRelatedField(view_name='group-detail', read_only=True)
    class Meta:
        model = GroupMessage
        fields = ['message', 'timeg', 'sender', 'pk',]
        # fields = ['__all__', 'snippets']