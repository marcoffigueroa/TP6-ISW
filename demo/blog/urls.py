from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(), name='post_list'),
    path('post/<slug:slug>/', views.post_detail, name='post_detail'),
    path('category/<int:category_id>/', views.category_posts, name='category_posts'),
    path('api/comment/<int:post_id>/', views.create_comment, name='create_comment'),
    path('api/post-count/', views.api_post_count, name='api_post_count'),
]