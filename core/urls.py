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
    path('moderation/', views.moderation_queue, name='moderation_queue'),
    path('moderation/<uuid:report_id>/', views.moderate_report, name='moderate_report'),
    path('report/<uuid:report_id>/message/', views.send_report_message, name='send_report_message'),
    path('inbox/', views.inbox, name='inbox'),
    path('message/<uuid:message_id>/reply/', views.reply_message, name='reply_message'),
    path('messages/', views.message_threads, name='message_threads'),
    path('messages/report/<uuid:report_id>/', views.message_thread, name='message_thread'),



]