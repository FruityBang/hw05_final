from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='mario')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='тест' * 10,
        )

    def test_models_str(self):
        """Метод __str__ возвращает название объектов"""
        post = PostModelTest.post
        group = PostModelTest.group
        model_str = {
            str(post): post.text[:15],
            str(group): group.title
        }

        for model_name, expected_value in model_str.items():
            with self.subTest(model_name=model_name):
                self.assertEqual(
                    model_name, expected_value,
                    '__str__ возвращает названия объектов некорректно'
                )
