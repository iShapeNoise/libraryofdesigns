import os
from django.conf import settings
from django import forms
from mptt.forms import TreeNodeChoiceField
from django.forms import inlineformset_factory
from .models import Design, Category, BillOfMaterials

INPUT_CLASSES = 'form-control border col-xs-4'

BOMFormSet = inlineformset_factory(
    Design,
    BillOfMaterials,
    fields=['bom_position',
            'bom_count',
            'bom_name',
            'bom_norm_description',
            'bom_material',
            'bom_notes',
            'bom_link'],
    extra=1,
    can_delete=True,
    widgets={
        'bom_position': forms.NumberInput(attrs={'class': INPUT_CLASSES}),
        'bom_count': forms.NumberInput(attrs={'class': INPUT_CLASSES}),
        'bom_name': forms.TextInput(attrs={'class': INPUT_CLASSES}),
        'bom_norm_description': forms.Textarea(attrs={'class': INPUT_CLASSES}),
        'bom_material': forms.TextInput(attrs={'class': INPUT_CLASSES}),
        'bom_notes': forms.Textarea(attrs={'class': INPUT_CLASSES}),
        'bom_link': forms.URLInput(attrs={'class': INPUT_CLASSES}),
    }
)


class OpenSCADFileChoiceField(forms.ChoiceField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.choices = self.get_openscad_files()

    def get_openscad_files(self):
        openscad_path = os.path.join(settings.LOD_CONTENT_ROOT,
                                     'designs/utilities')
        choices = [('', '--- Select a file ---')]

        if os.path.exists(openscad_path):
            for filename in os.listdir(openscad_path):
                if filename.endswith('.scad'):
                    choices.append((filename, filename))

        return choices


class NewDesignForm(forms.ModelForm):
    category = TreeNodeChoiceField(
        queryset=Category.objects.all(),
        empty_label="Select Category",
        widget=forms.Select(attrs={
            'class': INPUT_CLASSES
        })
    )

    # Custom field for utilities file selection
    utilities_file = OpenSCADFileChoiceField(required=False,
                                             label="Select Utility File")

    class Meta:
        model = Design
        fields = ('category', 'name', 'description', 'added_by', 'created_by',
                  'is_modified', 'modified_by', 'utilities', 'module',
                  'custom_section', 'costs', 'image')

        widgets = {
            'category': forms.Select(attrs={'class': INPUT_CLASSES}),
            'name': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'description': forms.Textarea(attrs={'class': INPUT_CLASSES}),
            'added_by': forms.Select(attrs={'class': INPUT_CLASSES}),
            'created_by': forms.Select(attrs={'class': INPUT_CLASSES}),
            'is_modified': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'onchange': 'toggleModifiedBy()'
            }),
            'modified_by': forms.Select(attrs={
                'class': INPUT_CLASSES,
                'disabled': True,
                'id': 'id_modified_by'
            }),
            'utilities': forms.Textarea(attrs={
                'class': INPUT_CLASSES,
                'id': 'id_utilities',
                'readonly': True,  # Keep readonly to prevent text editing
                'style': 'user-select: text; cursor: pointer;',  # Allow text selection
            }),
            'module': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'custom_section': forms.Textarea(attrs={'class': INPUT_CLASSES}),
            'costs': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'image': forms.FileInput(attrs={'class': INPUT_CLASSES}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate user choices for added_by, created_by, modified_by
        from django.contrib.auth.models import User
        user_choices = [(user.id, user.username) for user in User.objects.all()]
        self.fields['added_by'].choices = [('', '--- Select User ---')] + user_choices
        self.fields['created_by'].choices = [('', '--- Select User ---')] + user_choices
        self.fields['modified_by'].choices = [('', '--- Select User ---')] + user_choices


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
