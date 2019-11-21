"""1 对象级别的权限
 1 所有的代码片段都可以被任何人看到
 2 确保只有创建代码片段的用户才能更新或删除他 
"""
from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    自定义权限只允许对象的所有者编辑它
    """
    def has_object_permission(self, request, view, obj):
        # 读取权限允许任何请求
        # 所以我们总是允许 GET, HEAD 或 OPTIONS 请求
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # 只有该snippet的所有者才允许写权限
        return obj.sender == request.user.username