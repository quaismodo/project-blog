from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
# импортируем класс Paginator, PageNotAnInteger
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# импортируем класс ListView 
from django.views.generic import ListView
# импортируем класс формы
from .forms import EmailPostForm, CommentForm
# импортируем функцию send_mail для отправки писем
from django.core.mail import send_mail

# испортируем декоратор для работы с POST запросами
from django.views.decorators.http import require_POST

# def post_list(request):
#     # получаем объект со всеми опубликованными постами, используя кастомный менеджер
#     post_list = Post.published.all()
#     # используем класс Paginator для создания страниц
#     paginator = Paginator(post_list, 3)
#     page_number = request.GET.get('page', 1)
#     try:
#         # проверяем есть ли на странице результат отображения
#         posts = paginator.page(page_number)
#     except PageNotAnInteger:
#         # обрабатываем исключение, если в качестве номера страницы указано не число
#         posts = paginator.page(1)
#     except EmptyPage:
#         # обработка исключения пустой страницы,
#         # paginator.num_pages возвращает последний номер страницы
#         posts = paginator.page(paginator.num_pages)

#     return render(request, 'blog/post/list.html', {'posts': posts})

class PostListView(ListView):
    """
    Alternative post list view
    """
    # queryset - указывается модель из которой выбираем множество
    queryset = Post.published.all()
    # объявляем контекстную переменную posts для результатов запроса (objetc_list - по умолчанию)
    context_object_name = 'posts'
    # paginate_by - указываем количество записей на странице
    paginate_by = 3
    # имя шаблона
    template_name = 'blog/post/list.html'


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, status=Post.Status.PUBLISHED,
                             slug=post, publish__year=year,
                             publish__month=month, publish__day=day)

    comments = post.comments.filter(active=True)
    # находим все связанные с данным постом, комментарии
    # (обращаемся по полю comments, так как задали его в моделях related_name)
    form = CommentForm()

    return render(request, 'blog/post/detail.html', {'post': post, 'comments': comments, 'form': form})


def post_share(request, post_id):
    # определили представление post_share,
    # которое в качестве параметров принимает объект запроса (request) и post_id 
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    send = False

    if request.method == 'POST':
        # мы используем request.method == 'POST', чтобы различать два сценария
        # запрос POST, указывает, что форма отправляется
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read {post.title}"
            message = f"Read {post.title} at {post_url}\n\n{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, 'your_account@gmail.com', [cd['to']])
            send = True
    else:
        # когда страница загружается первый раз, представление получает запрос GET
        # если GET-запрос, тогда пользователю будет показана пустая форма
        form = EmailPostForm()

    return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'send': send})

@require_POST
# данное представление работает только с POST запросом
def post_comment(request, post_id):
    # получаем объект поста по id поста
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None
    # comment none, для проверки, был ли отправлен уже пост
    form = CommentForm(data=request.POST)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()

    return render(request, 'blog/post/comment.html', {'post': post, 'form': form, 'comment': comment})