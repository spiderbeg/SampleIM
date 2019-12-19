"""1 对象级别的权限
 1 所有的代码片段都可以被任何人看到
 2 确保只有创建代码片段的用户才能更新或删除他 
"""
from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    1 使用于用户信息模型 UserMessage
    2 功能自定义权限只允许信息的发送者，接收者编辑它
    """
    def has_object_permission(self, request, view, obj):
        # 读取权限允许任何请求
        # 所以我们总是允许 GET, HEAD 或 OPTIONS 请求
        if request.method in permissions.SAFE_METHODS:
            return True
        
        #非安全请求时，只有该 usermessage 实例即信息发送者和接收者才允许写权限
        return obj.sender == request.user.username