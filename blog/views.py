from django.shortcuts import render
from django.views.generic import ListView, DetailView

from .models import Post

# Create your views here.
class PostList(ListView):
    model = Post
    ordering = '-pk'    # 최신 순서
    # template_name = 'blog/post_list.html'
    # post_list.html이 불러와진다.

class PostDetail(DetailView):
    model = Post
    # post_detail.html이 불러와진다.

#def index(request):
#    posts = Post.objects.all().order_by('-pk')
#
#    return render(request,'blog/post_list.html',
#                  {
#                      'posts' : posts
#                  }
#                  )

#def single_post_page(request, pk) :
#    post = Post.objects.get(pk=pk)
#
#    return render(request, 'blog/post_detail.html',
#                  {
#                      'post': post
#                  }
#                  )