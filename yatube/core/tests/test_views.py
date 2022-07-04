from django.test import Client, TestCase


class ErrorPagesTest(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_404page_uses_custom_template(self):
        """Несуществующая страница отдает кастомный шаблон."""
        response = self.guest_client.get('/notfoundpage/')
        self.assertTemplateUsed(response, 'core/404.html')
