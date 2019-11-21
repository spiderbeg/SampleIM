from imapi import views
from django.urls import include, path
from rest_framework.routers import DefaultRouter

# 创建路由器并注册视图
router = DefaultRouter()
router.register('total', views.TotalMessageViewSet, base_name='total') 
router.register('groupmessage', views.GroupMessageViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('groupmgpk/', views.groupmgpk),
    path('api-auth/', include('rest_framework.urls'))
]