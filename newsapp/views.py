from django.contrib.auth import logout, login
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy

from .forms import *
from .models import *
from .utils import *

class NewsHome(DataMixin,ListView):
    model = Post
    template_name = 'newsapp/index.html'
    context_object_name = 'posts'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Главная страница')
        return dict(list(context.items()) + list(c_def.items()))

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Post.objects.filter(title__icontains=query)
        else:
            return Post.objects.filter(is_published=True).select_related('cat')

# class ShowPost(DataMixin, FormMixin, DetailView):
#     model = Post
#     template_name = 'newsapp/post.html'
#     slug_url_kwarg = 'post_slug'
#     context_object_name = 'post'
#     form_class = CommentForm

def showpost(request, post_slug):
    post = get_object_or_404(Post, slug=post_slug,
                             is_published=True)
    cats = Category.objects.annotate(Count('post'))
    # List of active comments for this post
    comments = post.comments.filter(active=True)

    if request.method == 'POST':
        # A comment was posted
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Create Comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # Assign the current post to the comment
            new_comment.post = post
            # Save the comment to the database
            new_comment.save()
    else:
        comment_form = CommentForm()
    return render(request,
                  'newsapp/post.html',
                 {'post': post,
                  'cats': cats,
                  'menu': menu,
                  'title': post.title,
                  'cat_selected': post.cat_id,
                  'comments': comments,
                  'comment_form': comment_form})


def about(request):
    cats = Category.objects.annotate(Count('post'))
    return render(request, 'newsapp/about.html', {'menu': menu,
                                                  'title': 'О сайте',
                                                  'cats': cats,
                                                  })


class AddPage(LoginRequiredMixin,DataMixin,CreateView):
    form_class = AddPostForm
    template_name = 'newsapp/addpage.html'
    success_url = reverse_lazy('home')
    login_url = reverse_lazy('home')
    raise_exception = True

    def get_context_data(self, object_list=None ,**kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Добавление статьи')
        return dict(list(context.items()) + list(c_def.items()))



class NewsCategory(DataMixin, ListView):
    model = Post
    template_name = 'newsapp/index.html'
    context_object_name = 'posts'
    allow_empty = False

    def get_queryset(self):
        return Post.objects.filter(cat__slug=self.kwargs['cat_slug'], is_published=True).select_related('cat')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c = Category.objects.get(slug=self.kwargs['cat_slug'])
        c_def = self.get_user_context(title='Категория - ' + str(c.name),
                                      cat_selected=c.pk)
        return dict(list(context.items()) + list(c_def.items()))

class RegisterUser(DataMixin, CreateView):
    form_class = RegisterUserForm
    template_name = 'newsapp/register.html'
    success_url = reverse_lazy('login')

    def get_context_data(self, object_list=None , **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title= 'Регистрация')
        return dict(list(context.items()) + list(c_def.items()))

    def form_valid(self, form):
        user = form.save()
        login(self.request,user)
        return redirect('home')

class LoginUser(DataMixin, LoginView):
    form_class = LoginUserForm
    template_name = 'newsapp/login.html'

    def get_context_data(self,object_list=None ,**kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Авторизация')
        return dict(list(context.items()) + list(c_def.items()))

    def get_success_url(self):
        return reverse_lazy('home')

def logout_user(request):
    logout(request)
    return redirect('login')

def pageNotFound(request, exception):
    return HttpResponseNotFound('<h1>Страница не найдена</h1>')