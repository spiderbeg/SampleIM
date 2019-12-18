from imapi import views
from django.urls import include, path
from rest_framework.routers import DefaultRouter

# 创建路由器并注册视图
router = DefaultRouter()
router.register('total', views.TotalMessageViewSet, base_name='total') 
router.register('groupmessage', views.GroupMessageViewSet)
router.register('usermessage', views.UserMessageViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('groupmgpk/', views.groupmgpk), # 测试接口
    path('historymessage/', views.history_message),
    path('newestmessage/', views.newest_message),
    path('imagefile/', views.imagefile),
    path('api-auth/', include('rest_framework.urls'))
]