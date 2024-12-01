from django.contrib import admin
from .models import Genre, GenreFilmwork, Filmwork, Person, PersonFilmwork


class PersonFilmWorkInline(admin.TabularInline):
    model = PersonFilmwork
    extra = 3


class GenreFilmworkInline(admin.TabularInline):
    model = GenreFilmwork
    min_num = 1
    extra = 0

@admin.register(Filmwork)
class FilmworkAdmin(admin.ModelAdmin):
    inlines = (
        GenreFilmworkInline,
        PersonFilmWorkInline
    )
    list_display = (
        'title',
        'description',
        'type',
        'created',
        'rating',
        'created',
        'modified',
    )
    list_display_links = (
        'title',
    )
    list_editable = (
        'type',
    )
    list_filter = ('type',)
    search_fields = (
        'title',
        'description',
    )

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'description',
    )
    list_display_links = (
        'name',
    )

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    inlines = (
        PersonFilmWorkInline,
    )
    list_display = (
        'full_name',
        'created',
        'modified',
    )
    list_display_links = (
        'full_name',
    )
    search_fields = (
        'full_name',
    )
    


