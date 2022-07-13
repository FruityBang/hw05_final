import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Follow, Group, Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='mario')
        cls.another_user = User.objects.create_user(username='supermario')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='тест',
            group=cls.group,
            image=cls.uploaded
        )

        cls.index_url = reverse('posts:index')
        cls.group_posts_url = reverse('posts:group_posts',
                                      kwargs={'slug': cls.group.slug})
        cls.profile_url = reverse('posts:profile',
                                  kwargs={'username': cls.user})
        cls.post_detail_url = reverse('posts:post_detail',
                                      kwargs={'post_id': cls.post.id})
        cls.post_edit_url = reverse('posts:post_edit',
                                    kwargs={'post_id': cls.post.id})
        cls.post_create_url = reverse('posts:post_create')
        cls.follow_index_url = reverse('posts:follow_index')
        cls.to_follow_url = reverse('posts:profile_follow',
                                    kwargs={'username': cls.user})
        cls.to_unfollow_url = reverse('posts:profile_unfollow',
                                      kwargs={'username': cls.user})

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        cache.clear()

        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.another_authorized_client = Client()
        self.another_authorized_client.force_login(self.another_user)

    def test_pages_uses_correct_template(self):
        """Views использует правильные шаблоны."""
        template_pages_list = {
            self.index_url: 'posts/index.html',
            self.group_posts_url: 'posts/group_list.html',
            self.profile_url: 'posts/profile.html',
            self.post_detail_url: 'posts/post_detail.html',
            self.post_edit_url: 'posts/create_post.html',
            self.post_create_url: 'posts/create_post.html'
        }

        for reverse_name, template in template_pages_list.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_context(self):
        """Проверка корректности переданного контекста главной страницы."""
        response = self.authorized_client.get(self.index_url)

        self.assertEqual(response.context['page_obj'].object_list[0],
                         self.post)

    def test_group_list_page_context(self):
        """Проверка корректности переданного контекста страницы группы."""
        response = (self.authorized_client.get(self.group_posts_url))

        self.assertEqual(response.context.get('group'), self.group)

    def test_profile_page_context(self):
        """
        Проверка корректности переданного контекста страницы пользователя.
        """
        response = (self.authorized_client.get(self.profile_url))

        self.assertEqual(response.context.get('author'), self.user)

    def test_post_detail_page_context(self):
        """Проверка корректности переданного контекста страницы поста."""
        response = (self.authorized_client.get(self.post_detail_url))

        self.assertEqual(response.context.get('post').id, self.post.id)

    def test_post_edit_page_context(self):
        """
        Проверка корректности переданного контекста
        страницы редактирования поста.
        """
        response = (self.authorized_client.get(self.post_edit_url))

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_create_post_page_context(self):
        """
        Проверка корректности переданного контекста страницы создания поста.
        """
        response = self.authorized_client.get(self.post_create_url)

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_is_on_page(self):
        """Проверка отображения поста на страницах."""
        pages_for_test = (
            self.index_url, self.group_posts_url, self.profile_url
        )

        for page in pages_for_test:
            response = self.authorized_client.get(page)
            self.assertEqual(response.context['page_obj'].
                             object_list[0], self.post)

    def test_post_is_not_on_wrong_group(self):
        """Проверка корректности отнесения поста к группе."""
        some_group = Group.objects.create(
            title='Другая группа',
            slug='test-other-slug',
            description='Другое описание'
        )

        response = (self.authorized_client.
                    get(reverse('posts:group_posts',
                        kwargs={'slug': some_group.slug})))

        self.assertNotIn(self.post, response.context['page_obj'])

    def test_follow_works_for_authorized(self):
        """Проверка работоспособности подписки."""
        follow_before = Follow.objects.filter(user=self.another_user,
                                              author=self.user).count()
        self.another_authorized_client.get(self.to_follow_url)
        follow_after = Follow.objects.filter(user=self.another_user,
                                             author=self.user).count()

        self.assertEqual(follow_after - follow_before, 1)

    def test_unfollow_works_for_authorized(self):
        """Проверка работоспособности отписки."""
        self.another_authorized_client.get(self.to_follow_url)
        follow_before = Follow.objects.filter(user=self.another_user,
                                              author=self.user).count()
        self.another_authorized_client.get(self.to_unfollow_url)
        follow_after = Follow.objects.filter(user=self.another_user,
                                             author=self.user).count()

        self.assertEqual(follow_before - follow_after, 1)

    def test_follower_has_post(self):
        """Пост появляется в ленте у подписчика."""
        Follow.objects.create(user=self.another_user, author=self.user)

        response = self.another_authorized_client.get(self.follow_index_url)

        self.assertEqual(response.context['page_obj'].object_list[0],
                         self.post)

    def test_antifollower_doesnt_have_post(self):
        """Пост не появляется в ленте у того, кто не подписан."""
        response = self.another_authorized_client.get(self.follow_index_url)

        self.assertNotIn(self.post, response.context['page_obj'])


class PostPaginatorTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()
        cls.user = User.objects.create_user(username='mario')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )

        posts_count = settings.POSTS_PER_PAGE + 3
        posts = (Post(author=cls.user,
                      text='Тестовый %s' % number,
                      group=cls.group) for number in range(posts_count))
        cls.posts = Post.objects.bulk_create(posts, posts_count)

        cls.index_url = reverse('posts:index')
        cls.group_posts_url = reverse('posts:group_posts',
                                      kwargs={'slug': cls.group.slug})
        cls.profile_url = reverse('posts:profile',
                                  kwargs={'username': cls.user})

    def test_first_page_ten_posts(self):
        """Проверка первой страницы Paginator."""
        pages_for_test = (
            self.index_url, self.group_posts_url, self.profile_url)

        for page in pages_for_test:
            response = self.client.get(page)
            self.assertEqual(len(response.context['page_obj']),
                             settings.POSTS_PER_PAGE)

    def test_second_page_little_posts(self):
        """Проверка второй страницы Paginator."""
        pages_for_test = (
            self.index_url + '?page=2',
            self.group_posts_url + '?page=2',
            self.profile_url + '?page=2'
        )

        for page in pages_for_test:
            response = self.client.get(page)
            self.assertEqual(len(response.context['page_obj']), 3)


class IndexPageCacheTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='mario')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.authorized_client = Client()

    def test_index_page_cache(self):
        """Тестируем кэш."""
        cache.clear()
        post = Post.objects.create(
            author=self.user,
            text='тест',
            group=self.group
        )
        response = self.authorized_client.get(reverse('posts:index'))
        content_before = (self.authorized_client.
                          get(reverse('posts:index')).content)

        post.delete()

        content_during = (self.authorized_client.
                          get(reverse('posts:index')).content)

        cache.clear()

        content_after = (self.authorized_client.
                         get(reverse('posts:index')).content)

        self.assertEqual(content_before, content_during)
        self.assertNotEqual(content_during, content_after)
        self.assertNotIn(post, response.context['page_obj'])
