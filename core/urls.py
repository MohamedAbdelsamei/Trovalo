from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('report/new/', views.report_create, name='report_create'),
    path('report/list/', views.report_list, name='report_list'),
    path('search/', views.report_search, name='report_search'),
    

]