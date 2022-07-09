from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='mario')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='тест',
            group=cls.group
        )

        cls.index_url = '/'
        cls.group_posts_url = '/group/test-slug/'
        cls.profile_url = '/profile/mario/'
        cls.post_detail_url = '/posts/1/'
        cls.post_edit_url = '/posts/1/edit/'
        cls.post_create_url = '/create/'
        cls.post_comment_url = '/posts/1/comment/'

    def setUp(self):
        cache.clear()

        self.guest_client = Client()

        self.not_author = User.objects.create_user(username='Hardbass')
        self.authorized_not_author = Client()
        self.authorized_not_author.force_login(self.not_author)

        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_posts_edit_redirect(self):
        """Запрос post_edit перенаправляет не автора поста на post_detail."""
        client_list = (self.guest_client, self.authorized_not_author)

        for client in client_list:
            with self.subTest(client=client):
                response = (self.client.
                            get(self.post_edit_url))
                self.assertRedirects(response, '/auth/login/?next=/posts/1/edit/')

    def test_posts_create_not_exists_anonymous(self):
        """Создание поста недоступно для незарегистрированного пользователя."""
        response = self.guest_client.get(self.post_create_url)

        self.assertNotEqual(response.status_code, HTTPStatus.OK)

    def test_post_comment_not_exists_anonymous(self):
        """
        Комментирование поста не доступно незарегистрированному пользователю.
        """
        response = self.guest_client.get(self.post_comment_url)

        self.assertNotEqual(response.status_code, HTTPStatus.OK)

    def test_posts_url_exists_anonymous(self):
        """Страницы существуют для незарегистрированного пользователя."""
        urls_list = (
            self.index_url, self.group_posts_url, self.profile_url,
            self.post_detail_url)

        for url in urls_list:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_url_not_exists(self):
        """Несуществующая страница не найдена."""
        response = self.guest_client.get('/404/')

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_posts_url_exists_authorized_author(self):
        """Страницы существуют для зарегистрированного пользователя."""
        urls_list = (
            self.post_create_url, self.post_edit_url)

        for url in urls_list:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_url_uses_correct_template(self):
        """URL использует правильные шаблоны."""
        template_url_list = {
            self.index_url: 'posts/index.html',
            self.group_posts_url: 'posts/group_list.html',
            self.profile_url: 'posts/profile.html',
            self.post_detail_url: 'posts/post_detail.html',
            self.post_edit_url: 'posts/create_post.html',
            self.post_create_url: 'posts/create_post.html'
        }

        for url, template in template_url_list.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
