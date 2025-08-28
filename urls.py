from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_csv, name='upload_csv'),
    path('data/<int:upload_id>/', views.view_data, name='view_data'),
    path('chat/<int:upload_id>/', views.chat_with_data, name='chat_with_data'),
    path('api/send-message/<int:upload_id>/', views.send_message, name='send_message'),
    path('delete/<int:upload_id>/', views.delete_upload, name='delete_upload'),
]
