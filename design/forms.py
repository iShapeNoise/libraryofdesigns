import os
from PIL import Image
from django.conf import settings
from django import forms
from mptt.forms import TreeNodeChoiceField
from django.forms import inlineformset_factory
from django.core.exceptions import ValidationError
from .models import Design, Category, BillOfMaterials
from multiupload.fields import MultiFileField
from taggit.forms import TagWidget


INPUT_CLASSES = 'form-control border col-xs-4'

BOMFormSet = inlineformset_factory(
    Design,
    BillOfMaterials,
    fields=['bom_position',
            'bom_count',
            'bom_material'],
    extra=1,
    can_delete=True,
    widgets={
        'bom_position': forms.NumberInput(attrs={
            'class': INPUT_CLASSES,
            'placeholder': 'Position number'
        }),
        'bom_count': forms.NumberInput(attrs={
            'class': INPUT_CLASSES,
            'placeholder': 'Quantity',
            'value': '1'
        }),
        'bom_material': forms.TextInput(attrs={
            'class': INPUT_CLASSES,
            'placeholder': 'Material specification'
        }),
    }
)


class OpenSCADFileChoiceField(forms.ChoiceField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.choices = self.get_openscad_files()

    def get_openscad_files(self):
        openscad_path = os.path.join(settings.LOD_CONTENT_ROOT, 'designs/utilities')
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

    # Multiple file upload fields
    images = MultiFileField(
        min_num=0,
        max_num=10,
        max_file_size=1024*1024*2,  # 2MB per file
        required=False,
        help_text="Upload up to 10 images (max 2MB each)"
    )

    techdraws = MultiFileField(
        min_num=0,
        max_num=5,
        max_file_size=1024*1024*2,  # 2MB per file
        required=False,
        help_text="Upload up to 5 technical drawings (images or PDFs, max 2MB each)"
    )

    class Meta:
        model = Design
        fields = ('category', 'tags', 'name', 'description', 'created_by', 'custom_creator_name',
                  'is_modified', 'modified_from', 'utilities', 'module',
                  'example', 'costs', 'production_notes', 'standardization')

        widgets = {
            'category': forms.Select(attrs={
                'class': INPUT_CLASSES,
                'required': True
            }),
            'tags': TagWidget(),
            'name': forms.TextInput(attrs={
                'class': INPUT_CLASSES,
                'required': True,
                'placeholder': 'Enter unique design name'
            }),
            'description': forms.Textarea(attrs={
                'class': INPUT_CLASSES,
                'required': True,
                'placeholder': 'Please enter design description'
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
                'placeholder': 'https://libraryofdesigns.cc/original-design-url',
                'id': 'id_modified_from'
            }),
            'utilities': forms.Textarea(attrs={
                'class': INPUT_CLASSES,
                'id': 'id_utilities',
                'readonly': True,
                'placeholder': 'Selected utility files will appear here',
                'style': 'user-select: text; cursor: pointer;',
            }),
            'module': forms.Textarea(attrs={
                'class': INPUT_CLASSES,
                'required': True,
                'placeholder': 'module design_name(parameters) {\n    // Your OpenSCAD code here\n}',
                'rows': 20
            }),
            'example': forms.Textarea(attrs={
                'class': INPUT_CLASSES,
                'required': True,
                'placeholder': ' // Add transformations translate([x,y,z]) rotate([x,y,z]) above module example/s for assembly\ndesign_name(param1=value1, param2=value2);',
                'rows': 7
            }),
            'costs': forms.TextInput(attrs={
                'class': INPUT_CLASSES,
                'placeholder': '25.50 (enter amount without currency symbol)',
                'required': False
            }),
            'production_notes': forms.Textarea(attrs={
                'class': INPUT_CLASSES,
                'placeholder': 'Manufacturing instructions, material requirements, assembly notes',
                'rows': 3
            }),
            'standardization': forms.Textarea(attrs={
                'class': INPUT_CLASSES,
                'placeholder': 'ISO/GPS norms and standards (e.g., ISO 286-1, GPS tolerancing)',
                'rows': 3
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Clear the default value for new forms  
        if not self.instance.pk:  # Only for new designs  
            self.fields['description'].initial = ''

        # Populate user choices for added_by, created_by, modified_by
        from django.contrib.auth.models import User
        user_choices = [(user.id, user.username) for user in User.objects.all()]
        self.fields['created_by'].choices = [('', '--- Select User ---')] + user_choices + [('add_creator', 'Add creator')]

    def clean_name(self):  # ADD THIS METHOD
        name = self.cleaned_data.get('name')
        if name:
            existing_design = Design.objects.filter(name__iexact=name).first()
            if existing_design:
                raise forms.ValidationError(
                    f"A design with the name '{name}' already exists. "
                    f"Please choose a different name to avoid conflicts."
                )
            # Check for problematic characters  
            problematic_chars = ['#', '?', '&', '%', '<', '>', '"', '|', '*', ':', '\\', '/']
            found_chars = [char for char in problematic_chars if char in name]

            if found_chars:
                char_list = ', '.join(f"'{char}'" for char in found_chars)
                raise forms.ValidationError(
                    f"Design name contains invalid characters: {char_list}. "
                    f"Please use only letters, numbers, spaces, hyphens, and underscores."
                )

            # Check for names that start/end with problematic characters
            if name.startswith('.') or name.endswith('.'):
                raise forms.ValidationError(
                    "Design name cannot start or end with a period."
                )

        return name


class EditDesignForm(forms.ModelForm):
    # Add the utilities file selection field  
    utilities_file = OpenSCADFileChoiceField(required=False,
                                             label="Select Utility File")

    # Add multiupload fields for editing  
    images = MultiFileField(
        min_num=0,
        max_num=10,
        max_file_size=1024*1024*2,  # 2MB per file
        required=False,
        help_text="Upload additional images (max 2MB each)"
    )

    techdraws = MultiFileField(
        min_num=0,
        max_num=5,
        max_file_size=1024*1024*2,  # 2MB per file
        required=False,
        help_text="Upload additional technical drawings (max 2MB each)"
    )

    # Add image management fields  
    delete_all_images = forms.BooleanField(
        required=False,
        label="Delete all existing images",
        help_text="Check this box to remove all current images"
    )

    delete_all_techdraws = forms.BooleanField(
        required=False,
        label="Delete all existing techdraws",
        help_text="Check this box to remove all current techdraws"
    )

    class Meta:
        model = Design
        fields = ('category', 'tags', 'name', 'description', 'created_by',
                  'custom_creator_name', 'is_modified', 'modified_from',
                  'utilities', 'module', 'example', 'costs',
                  'production_notes', 'standardization')

        widgets = {
            'category': forms.Select(attrs={
                'class': INPUT_CLASSES,
                'required': True
            }),
            'tags': TagWidget(),
            'created_by': forms.Select(attrs={
                'class': INPUT_CLASSES,
                'required': True
            }),
            'custom_creator_name': forms.TextInput(attrs={
                'class': INPUT_CLASSES,
                'placeholder': 'Enter creator name',
                'style': 'display: none;'
            }),
            'is_modified': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'onchange': 'toggleModifiedBy()'
            }),
            'modified_from': forms.URLInput(attrs={
                'class': INPUT_CLASSES,
                'placeholder': 'Please paste url of LoD Design to determine predecessor'
            }),
            'utilities': forms.Textarea(attrs={
                'class': INPUT_CLASSES,
                'readonly': True,
                'style': 'user-select: text; cursor: pointer;'
            }),
            'name': forms.TextInput(attrs={
                'class': INPUT_CLASSES,
                'placeholder': 'Enter design name'
            }),
            'description': forms.Textarea(attrs={
                'class': INPUT_CLASSES,
                'placeholder': 'Please enter design description here'
            }),
            'costs': forms.TextInput(attrs={
                'class': INPUT_CLASSES,
                'placeholder': 'Enter production costs (e.g., 25.50)',
                'required': False
            }),
            'module': forms.Textarea(attrs={
                'class': INPUT_CLASSES,
                'placeholder': 'Enter OpenSCAD module code here',
                'rows': 20
            }),
            'example': forms.Textarea(attrs={
                'class': INPUT_CLASSES,
                'placeholder': 'Enter module example with assembly parameters',
                'rows': 7
            }),
            'production_notes': forms.Textarea(attrs={
                'class': INPUT_CLASSES,
                'placeholder': 'Enter information about production and use of machines',
                'rows': 7
            }),
            'standardization': forms.Textarea(attrs={
                'class': INPUT_CLASSES,
                'placeholder': 'ISO/GPS norms and standards (e.g., ISO 286-1, GPS tolerancing)',
                'rows': 3
            })
        }

    def __init__(self, *args, **kwargs):  # ADD THIS METHOD HERE  
        super().__init__(*args, **kwargs)
        # Populate user choices for created_by  
        from django.contrib.auth.models import User
        user_choices = [(user.id, user.username) for user in User.objects.all()]
        self.fields['created_by'].choices = [('', '--- Select User ---')] + user_choices + [('add_creator', 'Add creator')]

    def clean(self):
        cleaned_data = super().clean()
        delete_all_images = cleaned_data.get('delete_all_images')
        new_images = self.files.getlist('images')

        # Check if user is deleting all images without adding new ones
        if delete_all_images and not new_images:
            raise forms.ValidationError("Add at least one design image!")

        return cleaned_data
