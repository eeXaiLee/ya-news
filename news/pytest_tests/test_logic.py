from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
        client, news_id_for_args, form_data
):
    """Анонимный пользователь не может отправить комментарий."""
    url = reverse('news:detail', args=news_id_for_args)
    client.post(url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_user_can_create_comment(
    author_client, author, news, news_id_for_args, form_data
):
    """Авторизованный пользователь может отправить комментарий."""
    url = reverse('news:detail', args=news_id_for_args)
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


@pytest.mark.django_db
def test_user_cant_use_bad_words(
    author_client, news_id_for_args
):
    """Нельзя использовать запрещённые слова в комментарии."""
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    url = reverse('news:detail', args=news_id_for_args)
    response = author_client.post(url, data=bad_words_data)
    assertFormError(response.context['form'], 'text', WARNING)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_author_can_edit_comment(
    author_client, comment, comment_for_args, news_id_for_args, form_data
):
    """Автор может редактировать свой комментарий."""
    url = reverse('news:edit', args=comment_for_args)
    response = author_client.post(url, data=form_data)
    expected_url = reverse('news:detail', args=news_id_for_args) + '#comments'
    assertRedirects(response, expected_url)
    comment.refresh_from_db()
    assert comment.text == form_data['text']


@pytest.mark.django_db
def test_author_can_delete_comment(
    author_client, comment_for_args, news_id_for_args
):
    """Автор может удалить свой комментарий."""
    url = reverse('news:delete', args=comment_for_args)
    response = author_client.delete(url)
    expected_url = reverse('news:detail', args=news_id_for_args) + '#comments'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(
    reader_client, comment, comment_for_args, form_data,
):
    """Нельзя редактировать чужой комментарий."""
    url = reverse('news:edit', args=comment_for_args)
    response = reader_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment_for_args[0])
    assert comment.text == comment_from_db.text


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(
    reader_client, comment_for_args
):
    """Нельзя удалить чужой комментарий."""
    url = reverse('news:delete', args=comment_for_args)
    response = reader_client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
