from django.test import TestCase
from django.urls import reverse
from .models import Note, Author
from .forms import NoteForm


class NoteModelTest(TestCase):
    def setUp(self):
        # Create an Author object
        author = Author.objects.create(name="Author")
        # Create a Note object for testing
        Note.objects.create(
            title="Note", content="This is sticky note content.", author=author
        )

    def test_note_has_title(self):
        # Test that a Note object has the expected title
        note = Note.objects.get(id=1)
        self.assertEqual(note.title, "Note")

    def test_note_has_content(self):
        # Test that a Note object has the expected content
        note = Note.objects.get(id=1)
        self.assertEqual(note.content, "This is sticky note content.")

    def test_note_has_author(self):
        # Test that a Note object has the expected author
        test_author = Author.objects.get(name="Author")
        note = Note.objects.get(id=1)
        self.assertEqual(note.author, test_author)


class NoteViewTest(TestCase):
    def setUp(self):
        # Create an Author object
        author = Author.objects.create(name="Author")
        # Create a Note object for testing views
        Note.objects.create(
            title="Note", content="This is sticky note content.", author=author
        )

    def test_note_list_view(self):
        # Test the note_list view
        response = self.client.get(reverse("note_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Note")

    def test_note_detail_view(self):
        # Test the note_detail view
        note = Note.objects.get(id=1)
        response = self.client.get(reverse("note_detail", args=[str(note.id)]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Note")
        self.assertContains(response, "This is sticky note content.")

    def test_note_create_view(self):
        # Test the note_create view
        response = self.client.get(reverse("note_create"))
        self.assertContains(response, "Create")

    def test_note_update_view(self):
        # Test the note_update view
        note = Note.objects.get(id=1)
        response = self.client.get(reverse("note_update", args=[str(note.id)]))
        self.assertContains(response, "Edit")

    def test_note_delete_view(self):
        # Test the note_delete view
        self.assertTrue(Note.objects.filter(pk=1).exists())
        note = Note.objects.get(pk=1)
        response = self.client.post(reverse("note_delete", args=[str(note.id)]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Note.objects.filter(pk=1).exists())


class NoteFormTest(TestCase):
    def setUp(self):
        # Create an Author object
        Author.objects.create(name="Author")

    def test_note_form(self):
        # Test the note form
        note_author = Author.objects.get(name="Author")
        form_data = {
            "title": "Test Note",
            "content": "Test content",
            "author": note_author,
        }
        form = NoteForm(data=form_data)
        self.assertTrue(form.is_valid())
