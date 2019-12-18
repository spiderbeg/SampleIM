from django.urls import path

from im import views

app_name = 'im' # 你的应用名

urlpatterns = [
	path('', views.talkRoom, name='talkRoom'),
    path('signup/', views.signup, name="signup"),
    path('getLogout/', views.getLogout, name="getLogout"),
    path('getLogin/', views.getLogin, name="getLogin"),
]