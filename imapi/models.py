# from django.db import models

# # Create your models here.
# from django.db import models
# from django.utils import timezone
# from django.contrib.auth.models import User # 导入 Django 验证系统

# # Create your models here.
# class UserProfile(models.Model):
#     """用户扩展信息"""
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     loginTime = models.DateTimeField(default=timezone.now)
#     logoutTime = models.DateTimeField(default=timezone.now)

#     def __str__(self):
#         return '%s: %s'%(self.user.username, self.loginTime)

# class UserRelation(models.Model):
#     """用户-用户信息"""
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     userName = models.CharField(max_length=60)
#     user2Name = models.CharField(max_length=60)
#     umid = models.PositiveIntegerField(default=0) # 记录用户 1 接收的用户 1、2 之间的信息 id 
#     umid2 = models.PositiveIntegerField(default=0) # 同上

#     def __str__(self):
#         return '%s-%s'%(self.userName, self.user2Name)

# class Group(models.Model):
#     """群组信息"""
#     name = models.CharField(max_length=60)
    
#     def __str__(self):
#         return self.name

# class GroupUser(models.Model):
#     """群组-用户信息"""
#     group = models.ForeignKey(Group, on_delete=models.CASCADE)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     userName = models.CharField(max_length=60)
#     groupName = models.CharField(max_length=60)
#     gmid = models.PositiveIntegerField(default=0) # 记录用户接收的消息

#     def __str__(self):
#         return '%s-%s'%(self.userName, self.groupName)

# class UserMessage(models.Model):
#     """用户之间消息"""
#     user = models.ForeignKey(UserRelation, on_delete=models.CASCADE)
#     message = models.CharField(max_length=120)
#     timeu = models.DateTimeField(default=timezone.now)
#     sender = models.CharField(max_length=60)

#     def __str__(self):
#         return '%s: %s'%(str(self.timeu), self.sender)

# class GroupMessage(models.Model):
#     """群消息"""
#     group = models.ForeignKey(Group, on_delete=models.CASCADE)
#     message = models.CharField(max_length=120)
#     timeg = models.DateTimeField(default=timezone.now)
#     sender = models.CharField(max_length=60)

#     def __str__(self):
#         return '%s:%s: %s'%(str(self.timeg), self.group, self.sender)