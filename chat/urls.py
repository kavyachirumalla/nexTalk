from django.urls import path
from . import views
urlpatterns = [
    path('', views.roomlist_view, name='room_list'),
    path('room/<str:room_name>/', views.room_view, name='room'),
    path('create/',views.create_room,name='create_room'),
    path('delete-message/<int:message_id>/',views.delete_message,name="delete_message"),
    path('upload-file/<str:room_name>/', views.upload_file, name='upload_file'),
]