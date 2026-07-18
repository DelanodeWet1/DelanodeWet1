from django.contrib import admin
from .models import Note
from .models import Author

# Register your models here.
# Note model
admin.site.register(Note)
# Author model
admin.site.register(Author)
