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
            'bom_standard',
            'bom_material',
            'bom_notes',
            'bom_link'],
    extra=1,
    can_delete=True,
    widgets={
        'bom_position': forms.NumberInput(attrs={'class': INPUT_CLASSES}),
        'bom_count': forms.NumberInput(attrs={'class': INPUT_CLASSES}),
        'bom_name': forms.TextInput(attrs={'class': INPUT_CLASSES}),
        'bom_standard': forms.TextInput(attrs={'class': INPUT_CLASSES}),
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
        fields = ('category', 'name', 'description', 'created_by', 'custom_creator_name',
                  'is_modified', 'modified_from', 'utilities', 'module',
                  'example', 'costs', 'image', 'image_list', 'techdraw',
                  'techdraw_list', 'production_notes')

        widgets = {
            'category': forms.Select(attrs={
                'class': INPUT_CLASSES,
                'required': True
            }),
            'name': forms.TextInput(attrs={
                'class': INPUT_CLASSES,
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': INPUT_CLASSES,
                'required': True
            }),
            'created_by': forms.Select(attrs={
                'class': INPUT_CLASSES,
                'required': True
            }),
            'custom_creator_name': forms.TextInput(attrs={
                'class': INPUT_CLASSES,
                'placeholder': 'Enter creator name',
                'id': 'id_custom_creator_name',
                'style': 'display: none;'  # Initially hidden
            }),
            'is_modified': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'onchange': 'toggleModifiedBy()'
            }),
            'modified_from': forms.URLInput(attrs={
                'class': INPUT_CLASSES,
                'placeholder': 'Please paste url of LoD Design to determine predecessor',
                'id': 'id_modified_from'
            }),
            'utilities': forms.Textarea(attrs={
                'class': INPUT_CLASSES,
                'id': 'id_utilities',
                'readonly': True,  # Keep readonly to prevent text editing
                'style': 'user-select: text; cursor: pointer;',  # Allow text selection
            }),
            'module': forms.Textarea(attrs={
                'class': INPUT_CLASSES,
                'required': True
            }),
            'example': forms.Textarea(attrs={
                'class': INPUT_CLASSES,
                'required': True
            }),
            'costs': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'production_notes': forms.Textarea(attrs={'class': INPUT_CLASSES}),
            'image': forms.FileInput(attrs={
                'class': INPUT_CLASSES,
                'accept': 'images/*'
            }),
            'image_list': forms.TextInput(attrs={
                'class': INPUT_CLASSES,
                'placeholder': 'image1.jpg, image2.png, image3.gif',
                'readonly': True
            }),
            'techdraw': forms.FileInput(attrs={
                'class': INPUT_CLASSES,
                'accept': 'techdraws/*'
            }),
            'techdraw_list': forms.TextInput(attrs={
                'class': INPUT_CLASSES,
                'placeholder': 'drawing1.jpg, drawing2.png, drawing3.gif',
                'readonly': True
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate user choices for added_by, created_by, modified_by
        from django.contrib.auth.models import User
        user_choices = [(user.id, user.username) for user in User.objects.all()]
        self.fields['created_by'].choices = [('', '--- Select User ---')] + user_choices + [('add_creator', 'Add creator')]


class EditDesignForm(forms.ModelForm):
    class Meta:
        model = Design
        fields = ('name',
                  'description',
                  'costs',
                  'image',
                  'is_modified',
                  'techdraw',
                  'module',
                  'example')
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
            'techdraw': forms.FileInput(attrs={
                'class': INPUT_CLASSES
            }),
            'module': forms.TextInput(attrs={
                'class': INPUT_CLASSES
            }),
            'example': forms.TextInput(attrs={
                'class': INPUT_CLASSES
            }),
        }
