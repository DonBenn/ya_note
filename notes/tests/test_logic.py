from http import HTTPStatus  # type: ignore

from django.contrib.auth import get_user_model  # type: ignore
from django.test import Client, TestCase  # type: ignore
from django.urls import reverse  # type: ignore

from notes.models import Note
from notes.forms import WARNING

User = get_user_model()


class TestNoteCreation(TestCase):
    COMMENT_TEXT = 'Текст комментария'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Мимо Крокодил')
        cls.notes = Note.objects.create(title='Заголовок',
                                        text='Текст',
                                        author=cls.author)
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.url = reverse('notes:add')
        cls.slug = 'slug'
        cls.form_data = {
            'title': 'Заголовок5',
            'text': 'Текст5',
            'slug': cls.slug,
        }

    def test_anonymous_user_cant_create_note(self):

        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

        self.auth_client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 2)

    def test_user_cant_create_notes_with_the_same_slug(self):

        self.auth_client.post(self.url, data=self.form_data)
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=self.slug + (WARNING)
        )

    def test_slug_can_create_automaticly(self):

        self.auth_client.post(self.url, data={'title': 'Заголовок7',
                                              'text': 'Текст7'})
        note = Note.objects.get(title='Заголовок7')
        self.assertIsNotNone(note.slug)


class TestNoteEditDelete(TestCase):

    COMMENT_TEXT = 'Текст комментария'
    NEW_COMMENT_TEXT = 'Обновлённый комментарий'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор комментария')
        cls.notes = Note.objects.create(
            title='Заголовок8',
            text=cls.COMMENT_TEXT,
            author=cls.author,)
        success_url = reverse('notes:success')
        cls.url_to_notes = success_url
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.edit_url = reverse('notes:edit', args=(cls.notes.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.notes.slug,))
        cls.form_data = {
            'title': 'Заголовок99',
            'text': cls.NEW_COMMENT_TEXT,
        }

    def test_author_can_delete_note(self):

        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.url_to_notes)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_cant_delete_note_of_another_user(self):

        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_edit_note(self):

        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.url_to_notes)
        self.notes.refresh_from_db()
        self.assertEqual(self.notes.text, self.NEW_COMMENT_TEXT)

    def test_user_cant_edit_note_of_another_user(self):

        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.notes.refresh_from_db()
        self.assertEqual(self.notes.text, self.COMMENT_TEXT)
