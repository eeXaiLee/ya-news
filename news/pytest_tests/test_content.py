from datetime import timedelta

import pytest
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from news.forms import CommentForm
from news.models import Comment


@pytest.mark.django_db
def test_news_count(client, news_list):
    """На главной странице отображается правильное количество новостей."""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client):
    """Новости на главной странице отсортированы от новых к старым."""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    assert all_dates == sorted(all_dates, reverse=True)


@pytest.mark.django_db
def test_comments_order(client, news, author, news_id_for_args):
    """Комментарии на странице новости отсортированы от старых к новым."""
    now = timezone.now()
    for index in range(10):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Комментарий {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()

    url = reverse('news:detail', args=news_id_for_args)
    response = client.get(url)
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    assert all_timestamps == sorted(all_timestamps)


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, news_id_for_args):
    """Анонимному пользователю недоступна форма для отправки комментария."""
    url = reverse('news:detail', args=news_id_for_args)
    response = client.get(url)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_authorized_user_has_form(author_client, news_id_for_args):
    """Авторизованному пользователю доступна форма для отправки комментария."""
    url = reverse('news:detail', args=news_id_for_args)
    response = author_client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
