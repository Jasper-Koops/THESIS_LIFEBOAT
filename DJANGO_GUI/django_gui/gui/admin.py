from django.contrib import admin
from .models import SavedData
# Register your models here.
#
class SavedDataAdmin(admin.ModelAdmin):
    model = SavedData
    search_fields = ['row_id']
# list_display = ('movie', 'director', 'added_by', 'rating')
# prepopulated_fields = {'slug': ('movie',)}
#
#
#
admin.site.register(SavedData, SavedDataAdmin)
