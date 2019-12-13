from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User # 导入 Django 验证系统
from django.conf import settings

import os
import base64

from PIL import Image

# Create your models here.
class UserProfile(models.Model):
    """用户扩展信息"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    loginTime = models.DateTimeField(default=timezone.now)
    logoutTime = models.DateTimeField(default=timezone.now)
    online = models.BooleanField(default=False)

    def __str__(self):
        return '%s: %s'%(self.user.username, self.loginTime)

class UserRelation(models.Model):
    """用户-用户信息"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    userName = models.CharField(max_length=60)
    user2Name = models.CharField(max_length=60)
    umid = models.PositiveIntegerField(default=0) # 记录用户 1 接收的用户 1、2 之间的信息 id 
    umid2 = models.PositiveIntegerField(default=0) # 同上

    def __str__(self):
        return '%s -> %s'%(self.userName, self.user2Name)

class Group(models.Model):
    """群组信息"""
    name = models.CharField(max_length=60)
    
    def __str__(self):
        return self.name

class GroupUser(models.Model):
    """群组-用户信息"""
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    userName = models.CharField(max_length=60)
    groupName = models.CharField(max_length=60)
    gmid = models.PositiveIntegerField(default=0) # 记录用户接收的消息

    def __str__(self):
        return '%s->>%s'%(self.userName, self.groupName)

class UserMessage(models.Model):
    """用户之间消息"""
    user = models.ForeignKey(UserRelation, on_delete=models.CASCADE)
    message = models.CharField(max_length=120)
    timeu = models.DateTimeField(default=timezone.now)
    sender = models.CharField(max_length=60) # 发送人 == UserRelation 中 userName
    MESSAGE_TYPE_CHOICES = [
        ('T', 'TXT'),
        ('P', 'IMAGINE'),
        ('V', 'VIDEO'),
    ]
    mtype = models.CharField(
        max_length=2,
        choices=MESSAGE_TYPE_CHOICES,
        default='T',
    )

    def __str__(self):
        return 'type %s -%s: %s->%s'%(self.mtype, str(self.timeu), self.sender, self.user.user2Name) + str(self.pk)

class GroupMessage(models.Model):
    """群消息"""
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    message = models.CharField(max_length=120)
    timeg = models.DateTimeField(default=timezone.now)
    sender = models.CharField(max_length=60)
    MESSAGE_TYPE_CHOICES = [
        ('T', 'TXT'),
        ('P', 'IMAGINE'),
        ('V', 'VIDEO'),
    ]
    mtype = models.CharField(
        max_length=2,
        choices=MESSAGE_TYPE_CHOICES,
        default='T',
    )

    def __str__(self):
        return 'type %s -%s:%s: %s'%(self.mtype, str(self.timeg), self.group, self.sender)

class SaveImage(models.Model):
    """存储接收的图片信息"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image_file = models.ImageField(upload_to='images/%Y')
    
    def __str__(self):
        return '%s-%s'%(self.user.username, self.image_file)

    def get_cover_base64(self):
        return image_as_base64(self.image_file.path)

def image_as_base64(image_file):
    """
    将文件内容 base64 转为 二进制
    """
    print('跑了没',image_file)
    if not os.path.isfile(image_file):
        return None
    with open(image_file, 'rb') as img_f:
        rea = img_f.read()
        print('保存的',rea[:1000])
        encoded_string = base64.b64decode(rea)
        print('转之后',encoded_string[:1000])
    with open(image_file, 'wb') as img_f2:
        img_f2.write(encoded_string)