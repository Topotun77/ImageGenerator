from django.contrib import admin
from .models import Image, Word, UserSettings

# Register your models here.


# admin.site.register(Image)
# admin.site.register(Word)
# admin.site.register(UserSettings)


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('user', 'image', 'query_text', 'date')
    fieldsets = (
        ('Description', {
            'fields': ('image',
                       'query_text')
        }),
        ('Parameters', {
            'fields': (('user',),)
        })
    )
    search_fields = ('image', 'query_text', 'date')
    list_filter = ('image', 'query_text', 'words')


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ('name', 'count')
    fields = [
        ('name',),
        ('image',),
    ]
    search_fields = ('name',)
    list_filter = ('name', 'image', 'count')


@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'day_team', 'page_num', 'age')
    fieldsets = (
        (None, {
            'fields': (('user', 'age'),)
        }),
        (None, {
            'fields': (('day_team', 'page_num'),)
        })
    )
    search_fields = ('age',)
    list_filter = ('user', 'day_team', 'page_num', 'age')
