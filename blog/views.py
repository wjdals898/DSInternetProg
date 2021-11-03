from django.shortcuts import render
from django.views.generic import ListView, DetailView

from .models import Post, Category,Tag

# Create your views here.
class PostList(ListView):
    model = Post
    ordering = '-pk'    # 최신 순서

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PostList, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()
        return context
    # template_name = 'blog/post_list.html'
    # post_list.html이 불러와진다.

class PostDetail(DetailView):
    model = Post

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PostDetail, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()
        return context
    # post_detail.html이 불러와진다.

def category_page(request, slug):
    if slug == 'no_category':
        category = '미분류'
        post_list = Post.objects.filter(category=None)
    else:
        category = Category.objects.get(slug=slug)
        post_list = Post.objects.filter(category=category)

    return render(request, 'blog/post_list.html',
                  {
                      'post_list' : post_list,
                      'categories' : Category.objects.all(),
                      'no_category_post_count' : Post.objects.filter(category=None).count(),
                      'category' : category
                  })

def tag_page(request, slug):
    tag = Tag.objects.get(slug=slug)
    post_list = tag.post_set.all() # Post.objects.filter(tags=tag)

    return render(request, 'blog/post_list.html',
                  {
                      'post_list' : post_list,
                      'categories' : Category.objects.all(),
                      'no_category_post_count' : Post.objects.filter(category=None).count(),
                      'tag' : tag
                  })

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