import uuid

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from .constants import RATING_MIN, RATING_MAX, SLICE_LENGTH, MAX_LENGHT


class TimeStampedMixin(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Genre(UUIDMixin, TimeStampedMixin):
    name = models.CharField(_('Name of genre'), max_length=MAX_LENGHT)
    description = models.TextField(_('Description genre'), blank=True)

    class Meta:
        db_table = "content\".\"genre"
        verbose_name = _('Genre')
        verbose_name_plural = _('Genres')
        indexes = [
            models.Index(
                fields=['name'],
                name='genre_name_idx'
            )
        ]

    def __str__(self):
        return self.name[:SLICE_LENGTH]


class Person(UUIDMixin, TimeStampedMixin):
    full_name = models.CharField(_('Full name'), max_length=MAX_LENGHT)

    class Meta:
        db_table = "content\".\"person"
        verbose_name = _('Person')
        verbose_name_plural = _('Persons')
        indexes = [
            models.Index(
                fields=['full_name'],
                name='person_full_name_idx'
            )
        ]

    def __str__(self):
        return self.full_name[:SLICE_LENGTH]


class Filmwork(UUIDMixin, TimeStampedMixin):

    class FilmWorkType(models.TextChoices):
        drama = 'drama', _('drama')
        comedy = 'comedy', _('comedy')

    title = models.CharField(_('Title of film'), max_length=MAX_LENGHT)
    description = models.TextField(_('Description of film'), blank=True)
    creation_date = models.DateField(_('Creation date'), blank=True)
    rating = models.FloatField(
        _('Rating of film'),
        blank=True,
        validators=[
            MinValueValidator(
                RATING_MIN,
                message=f'Рейтинг фильма не менее {RATING_MIN}!'
            ),
            MaxValueValidator(
                RATING_MAX,
                message=f'Рейтинг фильма не более {RATING_MAX}!'
            )
        ]
    )
    type = models.CharField(
        _('type'),
        choices=FilmWorkType.choices,
        max_length=MAX_LENGHT
    )
    genres = models.ManyToManyField(Genre, through='GenreFilmwork')
    persons = models.ManyToManyField(Person, through='PersonFilmwork')

    class Meta:
        db_table = "content\".\"film_work"
        verbose_name = _('Film')
        verbose_name_plural = _('Films')
        indexes = [
            models.Index(
                fields=['title'],
                name='film_work_title_idx'
            )
        ]

    def __str__(self):
        return self.title[:SLICE_LENGTH]


class GenreFilmwork(UUIDMixin):
    film_work = models.ForeignKey('Filmwork', on_delete=models.CASCADE)
    genre = models.ForeignKey('Genre', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content\".\"genre_film_work"
        verbose_name = _('GenreFilmwork')
        verbose_name_plural = _('GenreFilmworks')        
        indexes = [
            models.Index(
                fields=['film_work_id', 'genre_id'],
                name='genre_film_work_idx'
            )
        ]


class PersonFilmwork(UUIDMixin):
    class PersonRole(models.TextChoices):
        actor = 'actor', _('actor')
        director = 'director', _('director')
        writer = 'writer', _('writer')

    film_work = models.ForeignKey('Filmwork', on_delete=models.CASCADE)
    person = models.ForeignKey('Person', on_delete=models.CASCADE)
    role = models.TextField(
        _('Role'),
        choices=PersonRole.choices
)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content\".\"person_film_work"
        verbose_name = _('PersonFilmwork')
        verbose_name_plural = _('PersonFilmworks')
        indexes = [
            models.Index(
                fields=['film_work_id', 'person_id'],
                name='person_film_work_role_idx'
            )
        ]
