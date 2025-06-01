from django import forms

from .models import Design

INPUT_CLASSES = 'w-full py-4 px-6 rounded-xl border'


class NewDesignForm(forms.ModelForm):
    class Meta:
        model = Design
        fields = ('category', 'name', 'description', 'costs', 'image',)
        widgets = {
            'category': forms.Select(attrs={
                'class': INPUT_CLASSES
            }),
            'name': forms.TextInput(attrs={
                'class': INPUT_CLASSES
            }),
            'description': forms.Textarea(attrs={
                'class': INPUT_CLASSES
            }),
            'costs': forms.TextInput(attrs={
                'class': INPUT_CLASSES
            }),
            'image': forms.FileInput(attrs={
                'class': INPUT_CLASSES
            }),
        }


class EditDesignForm(forms.ModelForm):
    class Meta:
        model = Design
        fields = ('name', 'description', 'costs', 'image', 'is_modified')
        widgets = {
            'name': forms.TextInput(attrs={
                'class': INPUT_CLASSES
            }),
            'description': forms.Textarea(attrs={
                'class': INPUT_CLASSES
            }),
            'costs': forms.TextInput(attrs={
                'class': INPUT_CLASSES
            }),
            'image': forms.FileInput(attrs={
                'class': INPUT_CLASSES
            }),
        }
