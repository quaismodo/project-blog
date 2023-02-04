from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
# импортируем класс Paginator, PageNotAnInteger
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# импортируем класс ListView
from django.views.generic import ListView
# импортируем класс формы
from .forms import EmailPostForm, CommentForm, SearchForm
# импортируем функцию send_mail для отправки писем
from django.core.mail import send_mail

# испортируем декоратор для работы с POST запросами
from django.views.decorators.http import require_POST

from taggit.models import Tag

# имортируем Count для агрегации количества
from django.db.models import Count


from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity


def post_list(request, tag_slug=None):
    # получаем объект со всеми опубликованными постами, используя кастомный менеджер
    post_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])

    # используем класс Paginator для создания страниц
    paginator = Paginator(post_list, 4)
    page_number = request.GET.get('page', 1)
    try:
        # проверяем есть ли на странице результат отображения
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        # обрабатываем исключение, если в качестве номера страницы указано не число
        posts = paginator.page(1)
    except EmptyPage:
        # обработка исключения пустой страницы,
        # paginator.num_pages возвращает последний номер страницы
        posts = paginator.page(paginator.num_pages)

    return render(request, 'blog/post/list.html', {'posts': posts, 'tag': tag})

# class PostListView(ListView):
#     """
#     Alternative post list view
#     """
#     # queryset - указывается модель из которой выбираем множество
#     queryset = Post.published.all()
#     # объявляем контекстную переменную posts для результатов запроса (objetc_list - по умолчанию)
#     context_object_name = 'posts'
#     # paginate_by - указываем количество записей на странице
#     paginate_by = 3
#     # имя шаблона
#     template_name = 'blog/post/list.html'


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, status=Post.Status.PUBLISHED,
                             slug=post, publish__year=year,
                             publish__month=month, publish__day=day)

    comments = post.comments.filter(active=True)
    # находим все связанные с данным постом, комментарии
    # (обращаемся по полю comments, так как задали его в моделях related_name)
    form = CommentForm()

    # получаем id тегов текущего поста,
    # flat=True для того чтобы получить отдельные значения такие как [1, 2, 3, ...]
    # вместо [(1,),(2,),(3,),...]
    post_tags_ids = post.tags.values_list('id', flat=True)
    # дальше получаем все посты, которые содержат любой из полученных id тегов, кроме текущего поста
    similar_posts = Post.published.filter(
        tags__in=post_tags_ids).exclude(id=post.id)
    # с помощью функции агрегации Count создаем вычисляемое поле same_tags,
    # которое содержит количество общих тегов со всеми запрошенными тегами
    # упорядочиваем результат по количеству общих тегов (в порядке убывания) и по публикации,
    # чтобы сначала отображались последние посты с таким же количеством общим тегов.
    # Нарезаем результат, чтобы получить только первые 4 поста
    similar_posts = similar_posts.annotate(same_tags=Count(
        'tags')).order_by('-same_tags', '-publish')[:4]

    return render(request, 'blog/post/detail.html', {'post': post, 'comments': comments, 'form': form, 'similar_posts': similar_posts})


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


def post_search(request):
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            search_vector = SearchVector('title', weight='A') + SearchVector('body', weight='B')
            search_query = SearchQuery(query)
            results = Post.published.annotate(
                similarity=TrigramSimilarity('title', query),).filter(similarity__gt=0.1).order_by('-similarity')
    return render(request,
                  'blog/post/search.html',
                  {'form': form,
                   'query': query,
                   'results': results})
