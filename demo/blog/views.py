from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Post, Category, Comment


class PostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.filter(status=Post.PUBLISHED).select_related('author', 'category')


def post_detail(request, slug):
    """Detail view for a single post"""
    post = get_object_or_404(Post, slug=slug, status=Post.PUBLISHED)
    comments = post.comments.filter(is_approved=True)
    
    context = {
        'post': post,
        'comments': comments,
    }
    return render(request, 'blog/post_detail.html', context)


def category_posts(request, category_id):
    """List posts by category"""
    category = get_object_or_404(Category, id=category_id)
    posts = Post.objects.filter(category=category, status=Post.PUBLISHED)
    
    context = {
        'category': category,
        'posts': posts,
    }
    return render(request, 'blog/category_posts.html', context)


@login_required
def create_comment(request, post_id):
    """Create a new comment (API endpoint)"""
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id, status=Post.PUBLISHED)
        
        comment = Comment.objects.create(
            post=post,
            author_name=request.POST.get('author_name'),
            author_email=request.POST.get('author_email'),
            content=request.POST.get('content')
        )
        
        return JsonResponse({
            'success': True,
            'comment_id': comment.id,
            'message': 'Comment created successfully. It will be visible after approval.'
        })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


def api_post_count(request):
    """API endpoint to get post count by status"""
    counts = {
        'total': Post.objects.count(),
        'published': Post.objects.filter(status=Post.PUBLISHED).count(),
        'draft': Post.objects.filter(status=Post.DRAFT).count(),
        'archived': Post.objects.filter(status=Post.ARCHIVED).count(),
    }
    return JsonResponse(counts)
