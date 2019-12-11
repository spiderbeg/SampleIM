from django.contrib import admin
from .models import UserProfile, UserRelation, Group, GroupUser, UserMessage, GroupMessage, SaveImage

# Register your models here.
models2 = [UserProfile, UserRelation, Group, GroupUser, UserMessage, GroupMessage, SaveImage]
for i in models2: 
    admin.site.register(i)

# @admin.register(Rankinfo)
# class ShopRankinfoAdmin(admin.ModelAdmin):  
#     """店铺排名"""

#     list_display = ['__str__','pk']