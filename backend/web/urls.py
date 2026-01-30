
from django.urls import path, re_path
from web.views.index import index
from web.views.user.account.get_user_info import GetUserInfoView, GetUserInfoView
from web.views.user.account.login import LoginView
from web.views.user.account.logout import LogoutView
from web.views.user.account.refresh_token import RefreshTokenView
from web.views.user.account.register import RegisterView

urlpatterns = [
    path('api/user/account/login/', LoginView.as_view()),#前后端路由不一样，1.后端url前加api用于区别前端前端前必须加 /，后端则不用
    path('api/user/account/logout/', LogoutView.as_view()),
    path('api/user/account/register/', RegisterView.as_view() ),
    path('api/user/account/refresh_token/', RefreshTokenView.as_view() ),
    path('api/user/account/get_user_info/', GetUserInfoView.as_view()),

    path('', index),


]