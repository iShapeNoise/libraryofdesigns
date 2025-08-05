import re
import os
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .forms import NewDesignForm, EditDesignForm, BOMFormSet
from .models import Design, Category


def designs(request):
    query = request.GET.get('query', '')
    category_id = request.GET.get('category', 0)
    categories = Category.objects.all()
    designs = Design.objects.filter()

    if category_id:
        designs = designs.filter(category_id=category_id)

    if query:
        designs = designs.filter(Q(name__icontains=query) |
                                 Q(description__icontains=query))

    return render(request, 'design/designs.html', {
        'designs': designs,
        'query': query,
        'categories': categories,
        'category_id': int(category_id),
    })


def detail(request, pk):
    design = get_object_or_404(Design, pk=pk)
    related_designs = Design.objects.filter(category=design.category)
    related_designs.exclude(pk=pk)[0:3]

    return render(request, 'design/detail.html', {
        'design': design,
        'related_designs': related_designs,
    })


def create_design_files(design):
    """Create directory structure and OpenSCAD file for the design"""
    # Get the full category path using the existing get_full_path method  
    category_path = design.category.get_full_path().replace(' > ', '/')

    # Create the base directory structure  
    design_dir = os.path.join(settings.LOD_CONTENT_ROOT, 'designs', category_path, design.name)
    images_dir = os.path.join(design_dir, 'images')
    techdraws_dir = os.path.join(design_dir, 'techdraws')

    # Create directories if they don't exist  
    os.makedirs(design_dir, exist_ok=True)
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(techdraws_dir, exist_ok=True)

    # Create the OpenSCAD file  
    scad_file_path = os.path.join(design_dir, f"{design.name}.scad")

    # Generate OpenSCAD content  
    scad_content = generate_scad_content(design)

    with open(scad_file_path, 'w', encoding='utf-8') as f:
        f.write(scad_content)

    return design_dir


def generate_scad_content(design):
    """Generate OpenSCAD file content with header and structured body sections"""
    # Build the full design path
    category_path = design.category.get_full_path().replace(' > ', '/')
    full_design_path = f"""designs/{category_path}/{design.name}/{design.name}.scad"""

    header = f"""
    // {design.name}
    // Category: {design.category.get_full_path()}
    // Full Path: {full_design_path}
    // Description: {design.description or 'No description provided'}
    // Created by: {design.created_by.username}
    // Created at: {design.created_at.strftime('%Y-%m-%d %H:%M:%S')}
    // Costs: ${design.costs}"""
    # Add modified_from information if available  
    if hasattr(design, 'modified_from') and design.modified_from:
        header += f"// Modified from: {design.modified_from}\n"
    header += "\n"

    # OpenSCAD Utilities section  
    utilities_section = """// OpenSCAD Utilities"""
    if design.utilities:
        # Parse utilities field for .scad files and create include statements  
        utility_files = [line.strip() for line in design.utilities.split('\n') if line.strip().endswith('.scad')]
        for utility_file in utility_files:
            utilities_section += f"include <lod_content/utilities/{utility_file}>\n"
    utilities_section += "\n"

    # BOM Imports section - include designs referenced in BOM  
    bom_section = """// BOM Design Imports"""
    # Get BOM items that have links to other LoD designs  
    bom_items = design.bom_items.filter(bom_link__icontains='lod')  # Assuming LoD links contain 'lod'  
    for bom_item in bom_items:
        if bom_item.bom_link:
            bom_section += f"include <{bom_item.bom_link}>\n"
    bom_section += "\n"

    # Module section  
    module_section = """// Module"""
    if design.module:
        module_section += f"{design.module}\n"
    module_section += "\n"

    # Examples section  
    examples_section = """// Examples"""
    if design.custom_section:
        examples_section += f"{design.custom_section}\n"
    examples_section += "\n"

    return header + utilities_section + bom_section + module_section + examples_section


def move_uploaded_files(design, design_dir):
    """Move uploaded files to the design directory structure"""
    images_dir = os.path.join(design_dir, 'images')
    techdraws_dir = os.path.join(design_dir, 'techdraws')

    # Move main image if present
    if design.image:
        old_path = design.image.path
        new_path = os.path.join(images_dir, os.path.basename(old_path))
        if os.path.exists(old_path):
            os.rename(old_path, new_path)
            # Update the image field to point to new location
            design.image.name = os.path.relpath(new_path, settings.MEDIA_ROOT)
            design.save()

    # Move techdraw if present
    if hasattr(design, 'techdraw') and design.techdraw:
        old_path = design.techdraw.path
        new_path = os.path.join(techdraws_dir, os.path.basename(old_path))
        if os.path.exists(old_path):
            os.rename(old_path, new_path)
            design.techdraw.name = os.path.relpath(new_path, settings.MEDIA_ROOT)
            design.save()


@login_required
def new(request):
    if request.method == 'POST':
        form = NewDesignForm(request.POST, request.FILES)
        bom_formset = BOMFormSet(request.POST)

        if form.is_valid() and bom_formset.is_valid():
            design = form.save(commit=False)
            design.added_by = request.user

            # Process image list  
            if form.cleaned_data.get('image_list'):
                image_names = [name.strip() for name in form.cleaned_data['image_list'].split(',') if name.strip()]
                design.image_list = image_names

            # Process techdraw list
            if form.cleaned_data.get('techdraw_list'):
                techdraw_names = [name.strip() for name in form.cleaned_data['techdraw_list'].split(',') if name.strip()]
                design.techdraw_list = techdraw_names

            # Handle utilities file addition
            if form.cleaned_data.get('utilities_file'):
                current_utilities = design.utilities or ''
                new_file = form.cleaned_data['utilities_file']
                if current_utilities:
                    design.utilities = f"{current_utilities}\n{new_file}"
                else:
                    design.utilities = new_file

            design.save()

            # Save BOM items
            bom_formset.instance = design
            bom_formset.save()

            try:
                design_dir = create_design_files(design)
                move_uploaded_files(design, design_dir)
            except Exception as e:
                # Handle file creation errors gracefully  
                # You might want to log this error  
                pass

            return redirect('design:detail', pk=design.id)
    else:
        form = NewDesignForm()
        bom_formset = BOMFormSet()

    return render(request, 'design/form.html', {
        'form': form,
        'bom_formset': bom_formset,
        'title': 'New Design',
    })


def parse_scad_file(design):
    """Parse OpenSCAD file content back into form fields"""
    category_path = design.category.get_full_path().replace(' > ', '/')
    scad_file_path = os.path.join(settings.LOD_CONTENT_ROOT, 'designs', category_path, design.name, f"{design.name}.scad")

    if not os.path.exists(scad_file_path):
        return {}

    try:
        with open(scad_file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        parsed_data = {}

        # Parse utilities section
        utilities_match = re.search(r'// OpenSCAD Utilities\n(.*?)(?=\n//|\n\n|\Z)', content, re.DOTALL)
        if utilities_match:
            utilities_content = utilities_match.group(1).strip()
            # Extract filenames from include statements
            includes = re.findall(r'include <lod_content/utilities/(.+?)>', utilities_content)
            parsed_data['utilities'] = '\n'.join(includes)

        # Parse module section
        module_match = re.search(r'// Module\n(.*?)(?=\n//|\n\n|\Z)', content, re.DOTALL)
        if module_match:
            parsed_data['module'] = module_match.group(1).strip()

        # Parse examples section
        examples_match = re.search(r'// Examples\n(.*?)(?=\n//|\n\n|\Z)', content, re.DOTALL)
        if examples_match:
            parsed_data['custom_section'] = examples_match.group(1).strip()

        return parsed_data

    except Exception as e:
        # Handle file reading errors gracefully
        return {}


@login_required
def edit(request, pk):
    design = get_object_or_404(Design, pk=pk, created_by=request.user)

    if request.method == 'POST':
        form = EditDesignForm(request.POST, request.FILES, instance=design)

        if form.is_valid():
            design = form.save(commit=False)
            design.created_by = request.user
            design.save()

            # Regenerate the .scad file with updated data
            try:
                design_dir = create_design_files(design)
                move_uploaded_files(design, design_dir)
            except Exception as e:
                pass

            return redirect('design:detail', pk=design.id)
    else:
        # Parse data from .scad file and populate form
        scad_data = parse_scad_file(design)

        # Update design instance with parsed data before creating form
        for field, value in scad_data.items():
            if hasattr(design, field) and value:
                setattr(design, field, value)

        form = EditDesignForm(instance=design)

    return render(request, 'design/form.html', {
        'form': form,
        'title': 'Edit Design',
    })


def cleanup_design_files(design):
    """Remove design directory and all associated files"""
    try:
        category_path = design.category.get_full_path().replace(' > ', '/')
        design_dir = os.path.join(settings.LOD_CONTENT_ROOT, 'designs', category_path, design.name)

        if os.path.exists(design_dir):
            import shutil
            shutil.rmtree(design_dir)

        # Also clean up empty parent directories if they exist
        parent_dir = os.path.dirname(design_dir)
        while parent_dir != os.path.join(settings.LOD_CONTENT_ROOT, 'designs'):
            try:
                if os.path.exists(parent_dir) and not os.listdir(parent_dir):
                    os.rmdir(parent_dir)
                    parent_dir = os.path.dirname(parent_dir)
                else:
                    break
            except OSError:
                break

    except Exception as e:
        # Handle cleanup errors gracefully
        pass


@login_required
def delete(request, pk):
    design = get_object_or_404(Design, pk=pk, created_by=request.user)

    # Clean up associated files and directories
    cleanup_design_files(design)

    # Delete the database record
    design.delete()

    return redirect('dashboard:index')
