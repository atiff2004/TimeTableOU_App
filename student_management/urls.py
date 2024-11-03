from django.urls import path
from . import views

urlpatterns = [
    path('upload-students/', views.upload_students, name='upload_students'),
    path('create-fyp/', views.create_fyp, name='create_fyp'),
    path('load-students/', views.load_students, name='load_students'),
    path('edit-fyp-group/', views.edit_fyp_group, name='edit_fyp_group'),
    path('swap-group-members/', views.swap_group_members, name='swap_group_members'),
    path('load-class/', views.load_class, name='load_class'),
    path('fyp-list/', views.fyp_list, name='fyp_list'),
]
