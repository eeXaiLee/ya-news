from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects
from pytest_lazy_fixtures import lf


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args, method',
    (
        ('news:home', None, lf('client.get')),
        ('news:detail', lf('id_for_args'), lf('client.get')),
        ('users:login', None, lf('client.get')),
        ('users:logout', None, lf('client.post')),
        ('users:signup', None, lf('client.get')),
    ),
)
def test_public_pages_available_for_anonymous_user(name, args, method):
    url = reverse(name, args=args)
    response = method(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (lf('author_client'), HTTPStatus.OK),
        (lf('reader_client'), HTTPStatus.NOT_FOUND),
    )
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_availability_for_comment_edit_and_delete(
    parametrized_client, expected_status, name, comment_for_args
):
    url = reverse(name, args=comment_for_args)
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_redirect_for_anonymous_client(client, name, comment_for_args):
    login_url = reverse('users:login')
    url = reverse(name, args=comment_for_args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
