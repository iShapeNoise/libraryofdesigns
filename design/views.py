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
    related_designs = Design.objects.filter(category=design.category).exclude(pk=pk)[0:3]

    # Get both images and techdraws from the organized directory structure
    design_images = get_design_images(design)
    design_techdraws = get_design_techdraws(design)

    return render(request, 'design/detail.html', {
        'design': design,
        'related_designs': related_designs,
        'design_images': design_images,
        'design_techdraws': design_techdraws,  # This must be passed to template
    })


def get_design_images(design):
    """Get list of images from the design's organized directory structure"""
    import os
    from django.conf import settings

    try:
        # Build the path using the same logic as create_design_files()
        category_path = design.category.get_full_path().replace(' > ', '/').replace(' ', '_')
        design_name_fs = design.name.replace(' ', '_')

        images_dir = os.path.join(settings.LOD_CONTENT_ROOT, 'designs', category_path, design_name_fs, 'images')
        image_files = []
        if os.path.exists(images_dir):
            for filename in os.listdir(images_dir):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                    # Use the working URL construction from before
                    image_url = f"/{settings.LOD_CONTENT_URL}designs/{category_path}/{design_name_fs}/images/{filename}"
                    image_files.append({
                        'filename': filename,
                        'url': image_url
                    })
        return image_files

    except Exception as e:
        # Return empty list if any error occurs  
        print(f"Error in get_design_images: {e}")
        return []


def get_design_techdraws(design):
    """Get list of techdraws from the design's organized directory structure"""
    import os
    from django.conf import settings

    # Build the path using the same logic as create_design_files()
    category_path = design.category.get_full_path().replace(' > ', '/').replace(' ', '_')
    design_name_fs = design.name.replace(' ', '_')
    techdraws_dir = os.path.join(settings.LOD_CONTENT_ROOT, 'designs', category_path, design_name_fs, 'techdraws')

    techdraw_files = []
    if os.path.exists(techdraws_dir):
        for filename in os.listdir(techdraws_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.pdf')):
                # Construct URL for accessing the techdraw
                techdraw_url = f"/{settings.LOD_CONTENT_URL}designs/{category_path}/{design_name_fs}/techdraws/{filename}"
                techdraw_files.append({
                    'filename': filename,
                    'url': techdraw_url
                })

    return techdraw_files


def create_design_files(design):
    """Create directory structure and OpenSCAD file for the design"""
    # Get the full category path using the existing get_full_path method  
    category_path = design.category.get_full_path().replace(' > ', '/').replace(' ', '_')
    # Use underscore version of design name for file system  
    design_name_fs = design.name.replace(' ', '_')
    # Create the base directory structure  
    design_dir = os.path.join(settings.LOD_CONTENT_ROOT, 'designs', category_path, design_name_fs)
    images_dir = os.path.join(design_dir, 'images')
    techdraws_dir = os.path.join(design_dir, 'techdraws')
    design_code_dir = os.path.join(design_dir, 'design')

    # Create directories if they don't exist  
    os.makedirs(design_dir, exist_ok=True)
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(techdraws_dir, exist_ok=True)
    os.makedirs(design_code_dir, exist_ok=True)

    # Create the OpenSCAD file  
    scad_file_path = os.path.join(design_code_dir, f"{design_name_fs}.scad")

    # Generate OpenSCAD content  
    scad_content = generate_scad_content(design)

    with open(scad_file_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(scad_content)

    return design_dir


def generate_scad_content(design):
    """Generate OpenSCAD file content with header and structured body sections"""
    # Build paths with underscores for file system
    category_path = design.category.get_full_path().replace(' > ', '/').replace(' ', '_')
    design_name_fs = design.name.replace(' ', '_')
    full_design_path = f"designs/{category_path}/{design_name_fs}/design/{design_name_fs}.scad"

    # Use fallback "Unknown" if created_by is None
    created_by_username = design.created_by.username if design.created_by else "Unknown"

    # Build header with explicit \n line endings
    header_lines = [
        f"// {design.name}",
        f"// Category: {design.category.get_full_path()}",
        f"// Full Path: {full_design_path}",
        f"// Description: {design.description or 'No description provided'}",
        f"// Created by: {created_by_username}",
        f"// Created at: {design.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
        f"// Costs: ${design.costs}"
    ]

    # Add modified_from information if available
    if hasattr(design, 'modified_from') and design.modified_from:
        header_lines.append(f"// Modified from: {design.modified_from}")

    header = '\n'.join(header_lines) + '\n\n'

    # OPENSCAD UTILITIES section with line breaks  
    utilities_section = "\n// OPENSCAD UTILITIES\n"
    if design.utilities:
        utility_files = [line.strip() for line in design.utilities.split('\n') if line.strip().endswith('.scad')]
        for utility_file in utility_files:
            utilities_section += f"include <lod_content/utilities/{utility_file}>\n"
    utilities_section += "\n"

    # BOM DESIGN IMPORTS section with line breaks  
    bom_section = "\n// BOM DESIGN IMPORTS\n"
    bom_items = design.bom_items.filter(bom_link__icontains='lod')
    if bom_items.exists():
        for bom_item in bom_items:
            if bom_item.bom_link:
                bom_section += f"include <{bom_item.bom_link}>\n"
    bom_section += "\n"

    # MODULE section with line breaks
    module_section = "\n// MODULE\n"
    if design.module:
        normalized_module = design.module.replace('\r\n', '\n').replace('\r', '\n')
        module_section += f"{normalized_module}\n"
    module_section += "\n"

    # EXAMPLES section with line breaks  
    examples_section = "\n// EXAMPLES\n"
    if design.example:
        normalized_examples = design.example.replace('\r\n', '\n').replace('\r', '\n')
        examples_section += f"{normalized_examples}\n"
    examples_section += "\n"

    return header + utilities_section + bom_section + module_section + examples_section


def handle_multiple_file_uploads(design, design_dir, images, techdraws):
    """Handle multiple file uploads to organized directory structure"""
    images_dir = os.path.join(design_dir, 'images')
    techdraws_dir = os.path.join(design_dir, 'techdraws')

    print(f"Processing {len(images)} images and {len(techdraws)} techdraws")  # Debug

    # Process multiple images
    for image_file in images:
        file_path = os.path.join(images_dir, image_file.name)
        print(f"Saving image to: {file_path}")  # Debug
        with open(file_path, 'wb+') as destination:
            for chunk in image_file.chunks():
                destination.write(chunk)

    # Process multiple techdraws
    for techdraw_file in techdraws:
        file_path = os.path.join(techdraws_dir, techdraw_file.name)
        print(f"Saving techdraw to: {file_path}")  # Debug
        with open(file_path, 'wb+') as destination:
            for chunk in techdraw_file.chunks():
                destination.write(chunk)


def parse_scad_file(design):
    """Parse OpenSCAD file content back into form fields"""
    category_path = design.category.get_full_path().replace(' > ', '/').replace(' ', '_')
    design_name_fs = design.name.replace(' ', '_')
    scad_file_path = os.path.join(settings.LOD_CONTENT_ROOT, 'designs', category_path, design_name_fs, "design", f"{design_name_fs}.scad")

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
        examples_match = re.search(r'// Assembled example\n(.*?)(?=\n//|\n\n|\Z)', content, re.DOTALL)
        if examples_match:
            parsed_data['example'] = examples_match.group(1).strip()

        return parsed_data

    except Exception as e:
        # Handle file reading errors gracefully
        return {}


def cleanup_design_files(design):
    """Remove design directory and all associated files"""
    try:
        category_path = design.category.get_full_path().replace(' > ', '/').replace(' ', '_')
        design_name_fs = design.name.replace(' ', '_')
        design_dir = os.path.join(settings.LOD_CONTENT_ROOT, 'designs', category_path, design_name_fs)

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


def delete_design_images(design):
    """Delete all images for a design"""
    import os
    import shutil
    from django.conf import settings

    category_path = design.category.get_full_path().replace(' > ', '/').replace(' ', '_')
    design_name_fs = design.name.replace(' ', '_')
    design_dir = os.path.join(settings.LOD_CONTENT_ROOT, 'designs', category_path, design_name_fs)
    images_dir = os.path.join(design_dir, 'images')

    if os.path.exists(images_dir):
        # Remove all files in the images directory
        for filename in os.listdir(images_dir):
            file_path = os.path.join(images_dir, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)


def delete_design_techdraws(design):
    """Delete all techdraws for a design"""
    import os
    import shutil
    from django.conf import settings

    category_path = design.category.get_full_path().replace(' > ', '/').replace(' ', '_')
    design_name_fs = design.name.replace(' ', '_')
    design_dir = os.path.join(settings.LOD_CONTENT_ROOT, 'designs', category_path, design_name_fs)
    techdraws_dir = os.path.join(design_dir, 'techdraws')

    if os.path.exists(techdraws_dir):
        # Remove all files in the techdraws directory
        for filename in os.listdir(techdraws_dir):
            file_path = os.path.join(techdraws_dir, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)


@login_required
def new(request):
    if request.method == 'POST':
        form = NewDesignForm(request.POST, request.FILES)
        bom_formset = BOMFormSet(request.POST)

        if form.is_valid() and bom_formset.is_valid():
            design = form.save(commit=False)
            design.added_by = request.user

            # Handle utilities file addition
            if form.cleaned_data.get('utilities_file'):
                current_utilities = design.utilities or ''
                new_file = form.cleaned_data['utilities_file']
                if current_utilities:
                    design.utilities = f"{current_utilities}\n{new_file}"
                else:
                    design.utilities = new_file

            design.save()

            # Handle multiple images from MultiFileField  
            images = request.FILES.getlist('images')
            techdraws = request.FILES.getlist('techdraws')

            # Save BOM items
            bom_formset.instance = design
            bom_formset.save()

            try:
                design_dir = create_design_files(design)
                handle_multiple_file_uploads(design, design_dir, images, techdraws)
            except Exception as e:
                print(f"Error handling files: {e}")
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


@login_required
def edit(request, pk):
    design = get_object_or_404(Design, pk=pk, added_by=request.user)  # Use added_by instead of created_by  

    # Temporarily set empty lists to test if the issue is with the functions  
    existing_images = []
    existing_techdraws = []

    if request.method == 'POST':
        form = EditDesignForm(request.POST, request.FILES, instance=design)
        bom_formset = BOMFormSet(request.POST, instance=design)

        if form.is_valid() and bom_formset.is_valid():
            design = form.save(commit=False)
            design.added_by = request.user

            # Handle utilities file addition (same as in new() view)  
            if form.cleaned_data.get('utilities_file'):
                current_utilities = design.utilities or ''
                new_file = form.cleaned_data['utilities_file']
                if current_utilities:
                    design.utilities = f"{current_utilities}\n{new_file}"
                else:
                    design.utilities = new_file

            design.save()

            # Handle image deletion  
            if form.cleaned_data.get('delete_all_images'):
                delete_design_images(design)

            # Handle techdraw deletion
            if form.cleaned_data.get('delete_all_techdraws'):
                delete_design_techdraws(design)

            # Handle new file uploads
            new_images = request.FILES.getlist('images')
            new_techdraws = request.FILES.getlist('techdraws')

            if new_images or new_techdraws:
                try:
                    design_dir = create_design_files(design)
                    handle_multiple_file_uploads(design, design_dir, new_images, new_techdraws)
                except Exception as e:
                    print(f"Error handling new files: {e}")

            # Save BOM items  
            bom_formset.save()

            # Regenerate the .scad file with updated data  
            try:
                create_design_files(design)
                # Note: For edit, we're not handling new file uploads via multiupload  
                # The edit form focuses on updating existing design data  
            except Exception as e:
                print(f"Error regenerating files: {e}")
                pass

            return redirect('design:detail', pk=design.id)

        # If form validation fails, we need to define these variables for template rendering  
        existing_images = get_design_images(design) if 'get_design_images' in globals() else []
        existing_techdraws = get_design_techdraws(design) if 'get_design_techdraws' in globals() else []

    else:
        # Parse data from .scad file and populate form  
        scad_data = parse_scad_file(design)

        # Update design instance with parsed data before creating form  
        for field, value in scad_data.items():
            if hasattr(design, field) and value:
                setattr(design, field, value)

        form = EditDesignForm(instance=design)
        bom_formset = BOMFormSet(instance=design)

        # Get existing images for display
        existing_images = get_design_images(design) if 'get_design_images' in globals() else []  
        existing_techdraws = get_design_techdraws(design) if 'get_design_techdraws' in globals() else []

    return render(request, 'design/form.html', {
        'form': form,
        'bom_formset': bom_formset,
        'existing_images': existing_images,
        'existing_techdraws': existing_techdraws,
        'title': 'Edit Design',
    })


@login_required
def delete(request, pk):
    design = get_object_or_404(Design, pk=pk, created_by=request.user)

    # Clean up associated files and directories
    cleanup_design_files(design)

    # Delete the database record
    design.delete()

    return redirect('dashboard:index')
