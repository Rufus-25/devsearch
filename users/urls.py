from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('profile/<str:pk>', views.profile, name="profile"),
    path('account', views.user_account, name="account"),
    path('edit-profile', views.edit_profile, name="edit-profile"),
    
    path('login', views.login_user, name="login"),
    path('logout', views.logout_user, name="logout"),
    path('sign-up', views.create_user, name="sign-up"),

]
