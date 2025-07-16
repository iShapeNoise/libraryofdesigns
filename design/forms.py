from django import forms
from mptt.forms import TreeNodeChoiceField
from .models import Design, Category

INPUT_CLASSES = 'form-control border col-xs-4'


class NewDesignForm(forms.ModelForm):
    category = TreeNodeChoiceField(
        queryset=Category.objects.all(),
        empty_label="Select Category",
        widget=forms.Select(attrs={
            'class': INPUT_CLASSES
        })
    )

    class Meta:
        model = Design
        fields = ('category', 'name', 'description', 'costs', 'image')
        widgets = {
            'name': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'description': forms.Textarea(attrs={'class': INPUT_CLASSES}),
            'costs': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'image': forms.FileInput(attrs={'class': INPUT_CLASSES}),
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
