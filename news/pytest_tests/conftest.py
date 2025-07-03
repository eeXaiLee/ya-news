from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.test.client import Client

from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    """Создает пользователя-автора."""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def reader(django_user_model):
    """Создает пользователя-читателя."""
    return django_user_model.objects.create(username='Читатель')


@pytest.fixture
def author_client(author):
    """Клиент с авторизованным автором."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader):
    """Клиент с авторизованным читателем."""
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def news():
    """Создает тестовую новость."""
    news = News.objects.create(title='Заголовок', text='Текст')
    return news


@pytest.fixture
def comment(news, author):
    """Создает тестовый комментарий."""
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )
    return comment


@pytest.fixture
def news_id_for_args(news):
    """Возвращает id новости в виде кортежа для URL."""
    return (news.id,)


@pytest.fixture
def comment_for_args(comment):
    """Возвращает id комментария в виде кортежа для URL."""
    return (comment.id,)


@pytest.fixture
def news_list():
    """Создает список новостей для тестирования пагинации."""
    today = datetime.today()
    news_list = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index),
        ) for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    return News.objects.bulk_create(news_list)


@pytest.fixture
def form_data():
    """Возвращает данные для формы комментария."""
    return {
        'text': 'Новый комментарий'
    }
