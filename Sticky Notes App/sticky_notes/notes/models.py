from django.db import models


class Note(models.Model):
    """Model representing a sticky note.

    Fields:
    - title: CharField for the note title.
    - body: TextField for the note body.
    - created_at: DateTimeField that captures the date and time the note was created.

    Relationships:
    - author: ForeignKey representing the author of the note.

    Methods:
    - __str__: Returns a string representation of the note, showing the title.

    :param models.Model: Django's base model class.
    """

    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    # Define a ForeignKey for the author's relationship
    author = models.ForeignKey(
        "Author", on_delete=models.CASCADE, null=True, blank=True
    )

    def __str__(self):
        return self.title


class Author(models.Model):
    """Model representing the author of a note.

    Fields:
    - name: CharField for the author's name.

    Methods:
    - __str__: Returns the name of the author.

    :param models.Model: Django's base model class.
    """

    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
