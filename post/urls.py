from django.urls import path
from .views import get_post_analysis, create_post

app_name = 'post' 

urlpatterns = [
    path('', create_post, name='post-create'),
    path('<str:post_id>/analyze', get_post_analysis, name='post-analyziz'),
    ]

