from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User # 导入 Django 验证系统
from django.conf import settings

MTC = [
    ('T', 'TXT'),
    ('P', 'IMAGINE'),
    ('V', 'VIDEO'),
    ('I', 'EMOJI'),
]

# Create your models here.
class UserProfile(models.Model):
    """用户扩展信息"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    introduce = models.CharField(max_length=120)

    def __str__(self):
        return self.user.username

class UserRelation(models.Model):
    """用户-用户信息"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user') # 请求好友的一方
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user2')
    umid = models.PositiveIntegerField(default=0) # 记录用户 1 接收的用户 1、2 之间的信息 id 
    umid2 = models.PositiveIntegerField(default=0) # 同上
    create_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return '%s -> %s'%(self.user.username, self.user2.username)

class Group(models.Model):
    """群组信息"""
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=60)
    create_time = models.DateTimeField(default=timezone.now)
    introduce = models.CharField(max_length=120)
    
    def __str__(self):
        return self.name

class GroupUser(models.Model):
    """群组-用户信息"""
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    join_time = models.DateTimeField(default=timezone.now)
    gmid = models.PositiveIntegerField(default=0) # 记录用户接收的消息

    def __str__(self):
        return '%s->>%s'%(self.user.username, self.group.name)

class UserMessage(models.Model):
    """用户之间消息"""
    userrelation = models.ForeignKey(UserRelation, on_delete=models.CASCADE)
    message = models.CharField(max_length=240)
    time = models.DateTimeField(default=timezone.now)
    receiver = models.CharField(max_length=60)
    sender = models.CharField(max_length=60) # 发送人 == UserRelation 中 userName
    MESSAGE_TYPE_CHOICES = MTC
    mtype = models.CharField(
        max_length=2,
        choices=MESSAGE_TYPE_CHOICES,
        default='T',
    )

    def __str__(self):
        return 'type %s -%s: %s->%s '%(self.mtype, str(self.time), self.sender, self.receiver) + str(self.pk)

class GroupMessage(models.Model):
    """群消息"""
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    message = models.CharField(max_length=120)
    time = models.DateTimeField(default=timezone.now)
    sender = models.CharField(max_length=60)
    MESSAGE_TYPE_CHOICES = MTC
    mtype = models.CharField(
        max_length=2,
        choices=MESSAGE_TYPE_CHOICES,
        default='T',
    )

    def __str__(self):
        return 'type %s -%s:%s: %s'%(self.mtype, str(self.time), self.group, self.sender)

class SaveImage(models.Model):
    """存储接收的图片信息"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image_file = models.ImageField(upload_to='images/%Y')
    time = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return '%s-%s'%(self.user.username, self.image_file)