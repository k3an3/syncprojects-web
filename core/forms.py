from django import forms

from core.models import Album, Song


class AlbumForm(forms.ModelForm):
    songs = forms.ModelMultipleChoiceField(queryset=Song.objects.none(), required=False,
                                           help_text="Use ctrl to select multiple, or shift to select a range.")

    class Meta:
        model = Album
        fields = ['name', 'cover', 'released', 'release_date']
