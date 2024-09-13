from django.test import TestCase  # type: ignore
# Импортируем функцию reverse(), она понадобится для получения адреса страницы.
from django.urls import reverse  # type: ignore
from django.contrib.auth import get_user_model  # type: ignore

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestHomePage(TestCase):

    HOME_URL = reverse('notes:home')
    LIST_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.notes = Note.objects.create(
            title='Заголовок3',
            author=cls.author,
            text='Текст комментария',
        )

        cls.notes = Note.objects.create(
            title='Заголовок4',
            author=cls.reader,
            text='Текст ридера',
        )

    def test_separated_note_has_object_list(self):
        self.client.force_login(self.author)
        response = self.client.get(self.LIST_URL)
        object_list = response.context['notes_feed']
        notes_count = object_list.count()
        self.assertEqual(notes_count, 1)

    def test_author_notes_not_in_other_users_notes(self):
        self.client.force_login(self.author)
        response = self.client.get(self.LIST_URL)
        self.assertNotIn('Заголовок4', response)

    def test_authorized_client_has_form(self):
        self.client.force_login(self.author)
        urls = (
            ('notes:edit', self.notes.slug),
            ('notes:add', None),
            )
        for name, args in urls:
            with self.subTest(name=name, args=args):
                url = reverse(name, args=[args] if args else None)
        response = self.client.get(url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
