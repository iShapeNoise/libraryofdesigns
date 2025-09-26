import re
import os
import zipfile
import tempfile
import shutil
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .forms import NewDesignForm, EditDesignForm, BOMFormSet
from .models import Design, Category
from taggit.models import Tag


def designs(request):
    query = request.GET.get('query', '')
    category_id = request.GET.get('category', 0)
    per_page = request.GET.get('per_page', '25')  # Default to 25  

    # Start with all designs  
    designs = Design.objects.all()

    # Apply search filter if query exists  
    if query:
        designs = designs.filter(Q(name__icontains=query) |
                                 Q(description__icontains=query) |
                                 Q(tags__name__icontains=query) |
                                 Q(category__name__icontains=query) |
                                 Q(created_by__username__icontains=query) |
                                 Q(added_by__username__icontains=query))

    # Apply category filter if specified  
    if category_id:
        designs = designs.filter(category_id=category_id)

    # Get categories that contain matching designs  
    if query:
        category_ids_with_results = designs.values_list('category_id', flat=True).distinct()
        categories = Category.objects.filter(id__in=category_ids_with_results)
        for category in categories:
            category.search_result_count = designs.filter(category=category).count()
    else:
        categories = Category.objects.all()
        for category in categories:
            category.search_result_count = category.get_total_design_count()

    # Handle pagination  
    if per_page == 'all':
        # Show all results without pagination
        paginated_designs = designs
        page_obj = None
        is_paginated = False
    else:
        # Use pagination  
        try:
            per_page_int = int(per_page)
            if per_page_int not in [25, 50]:
                per_page_int = 25
        except ValueError:
            per_page_int = 25

        paginator = Paginator(designs, per_page_int)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        paginated_designs = page_obj
        is_paginated = page_obj.has_other_pages()

    # Add image processing for thumbnail display  
    for design in paginated_designs:
        design_images = get_design_images(design)
        design.first_image = design_images[0] if design_images else {'url': None}

    return render(request, 'design/designs.html', {
        'designs': paginated_designs,
        'query': query,
        'categories': categories,
        'category_id': int(category_id),
        'has_search_results': bool(query),
        'page_obj': page_obj,
        'is_paginated': is_paginated,
        'per_page': per_page,
    })


def detail(request, pk):
    design = get_object_or_404(Design, pk=pk)

    # Fix the filtering by being more explicit about the exclusion  
    related_designs = Design.objects.filter(category=design.category).exclude(pk=pk)[:12]

    # Debug output to verify filtering is working
    print(f"Current design ID: {design.id}, Name: {design.name}")
    print(f"Related design IDs: {[(d.id, d.name) for d in related_designs]}")

    # Add first image to each related design object
    for related_design in related_designs:
        design_images = get_design_images(related_design)
        related_design.first_image = design_images[0]  # No need for None check since images are mandatory

    # Get both images and techdraws from the organized directory structure
    design_images = get_design_images(design)
    design_techdraws = get_design_techdraws(design)

    # Chunk related designs for carousel (6 designs per slide)  
    def chunk_list(lst, n):
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

    related_designs_chunks = list(chunk_list(related_designs, 4))

    return render(request, 'design/detail.html', {
        'design': design,
        'related_designs': related_designs,
        'related_designs_chunks': related_designs_chunks,
        'design_images': design_images,
        'design_techdraws': design_techdraws,
    })


def designs_by_tag(request, tag_slug):
    tag = get_object_or_404(Tag, slug=tag_slug)
    designs = Design.objects.filter(tags__in=[tag])
    return render(request, 'design/designs_by_tag.html', {
        'designs': designs,
        'tag': tag
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
        f"// Production Notes: {design.production_notes or 'None specified'}",
        f"// Standardization: {design.standardization or 'None specified'}"
        f"// Costs: ${design.costs if design.costs is not None else 'Not specified'}",
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
            utilities_section += f"include <lod_content/designs/utilities/{utility_file}>\n"
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


def generate_design_markdown(design):
    """Generate markdown file with header, BOM, and utilities information"""
    # Build paths
    category_path = design.category.get_full_path().replace(' > ', '/').replace(' ', '_')
    design_name_fs = design.name.replace(' ', '_')
    design_dir = os.path.join(settings.LOD_CONTENT_ROOT, 'designs', category_path, design_name_fs)

    # Create markdown content  
    markdown_content = [] 

    # Header section - matching SCAD file header  
    markdown_content.append(f"# {design.name}")
    markdown_content.append(f"**Category:** {design.category.get_full_path()}")
    markdown_content.append(f"**Full Path:** designs/{category_path}/{design_name_fs}/design/{design_name_fs}.scad")
    markdown_content.append(f"**Description:** {design.description or 'No description provided'}")

    # Use fallback "Unknown" if created_by is None  
    created_by_username = design.created_by.username if design.created_by else "Unknown"
    markdown_content.append(f"**Created by:** {created_by_username}")
    markdown_content.append(f"**Created at:** {design.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    markdown_content.append(f"**Costs:** ${design.costs if design.costs is not None else 'Not specified'}")
    markdown_content.append(f"**Production Notes:** {design.production_notes or 'None specified'}")
    markdown_content.append(f"**Standardization:** {design.standardization or 'None specified'}")

    # Add custom creator if available  
    if design.custom_creator_name:
        markdown_content.append(f"**Custom Creator:** {design.custom_creator_name}")

    # Add modified from information if available
    if design.is_modified and design.modified_from:
        markdown_content.append(f"**Modified from:** {design.modified_from}")

    # Add tags if they exist  
    if design.tags.exists():
        tag_names = [tag.name for tag in design.tags.all()]
        markdown_content.append(f"**Tags:** {', '.join(tag_names)}")

    markdown_content.append("")

    # Images section with list format for smaller display
    images_dir = os.path.join(design_dir, 'images')
    if os.path.exists(images_dir):
        image_files = [f for f in os.listdir(images_dir)
                       if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
        if image_files:
            markdown_content.append("## Images")
            # Create a table for side-by-side display
            markdown_content.append("| | | |")
            markdown_content.append("|---|---|---|")

            # Group images in rows of 3 
            for i in range(0, len(image_files), 3):
                row_images = image_files[i:i+3]
                row_content = []
                for image_file in row_images:
                    row_content.append(f'<img src="images/{image_file}" alt="{image_file}" width="200"/>')

                # Fill empty cells if needed
                while len(row_content) < 3:
                    row_content.append("")

                markdown_content.append(f"| {' | '.join(row_content)} |")

            markdown_content.append("")

    # Techdraws section with links only
    techdraws_dir = os.path.join(design_dir, 'techdraws')
    if os.path.exists(techdraws_dir):
        techdraw_files = [f for f in os.listdir(techdraws_dir)
                          if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.pdf'))]
        if techdraw_files:
            markdown_content.append("## Technical Drawings")
            for techdraw_file in techdraw_files:
                if techdraw_file.lower().endswith('.pdf'):
                    markdown_content.append(f"- 📄 [PDF: {techdraw_file}](techdraws/{techdraw_file})")
                else:
                    markdown_content.append(f"- 🖼️ [Image: {techdraw_file}](techdraws/{techdraw_file})")
            markdown_content.append("")

    # BOM and Utilities sections (keep existing code)
    markdown_content.append("## Bill of Materials")
    bom_items = design.bom_items.filter(bom_link__icontains='lod')
    if bom_items.exists():
        for bom_item in bom_items:
            if bom_item.bom_link: 
                markdown_content.append(f"- [{bom_item.name}]({bom_item.bom_link})")
    else:
        markdown_content.append("No LoD BOM items found.")

    markdown_content.append("")

    markdown_content.append("## Utilities")
    if design.utilities:
        utility_files = [line.strip() for line in design.utilities.split('\n') if line.strip().endswith('.scad')]
        for utility_file in utility_files:
            markdown_content.append(f"- `lod_content/utilities/{utility_file}`")
    else:
        markdown_content.append("No utility files used.")

    # Write markdown file to parent folder
    md_file_path = os.path.join(design_dir, f"{design_name_fs}.md")
    with open(md_file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(markdown_content))

    return md_file_path


def copy_license_file(design):
    """Copy LICENSE.md from lod_content root to design folder"""
    import shutil

    # Build paths
    category_path = design.category.get_full_path().replace(' > ', '/').replace(' ', '_')
    design_name_fs = design.name.replace(' ', '_')
    design_dir = os.path.join(settings.LOD_CONTENT_ROOT, 'designs', category_path, design_name_fs)

    # Source and destination paths
    source_license = os.path.join(settings.LOD_CONTENT_ROOT, 'LICENSE.md')
    dest_license = os.path.join(design_dir, 'LICENSE.md')

    # Copy the license file if it exists
    if os.path.exists(source_license):
        try:
            shutil.copy2(source_license, dest_license)
            return dest_license
        except Exception as e:
            print(f"Error copying LICENSE.md: {e}")
            return None
    else:
        print("LICENSE.md not found in lod_content root")
        return None


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
                generate_design_markdown(design)
                copy_license_file(design)
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
                generate_design_markdown(design)
                copy_license_file(design)
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


def download_design(request, pk):
    """Create and serve a ZIP file with standalone design"""
    design = get_object_or_404(Design, pk=pk)

    # Build source paths
    category_path = design.category.get_full_path().replace(' > ', '/').replace(' ', '_')
    design_name_fs = design.name.replace(' ', '_')
    source_dir = os.path.join(settings.LOD_CONTENT_ROOT, 'designs', category_path, design_name_fs)

    # Create temporary directory for processing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Copy entire design folder to temp
        temp_design_dir = os.path.join(temp_dir, design_name_fs)
        shutil.copytree(source_dir, temp_design_dir)

        # Process the design for standalone use
        process_standalone_design(design, temp_design_dir)

        # Create ZIP file
        zip_filename = f"{design_name_fs}.zip"
        response = HttpResponse(content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="{zip_filename}"'

        with zipfile.ZipFile(response, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(temp_design_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    zipf.write(file_path, arcname)

        return response


def process_standalone_design(design, temp_design_dir):
    """Process design to be standalone by copying utilities and BOM files"""
    design_code_dir = os.path.join(temp_design_dir, 'design')
    design_name_fs = design.name.replace(' ', '_')

    # Collect all SCAD files to scan (main design + BOM files)  
    scad_files_to_scan = []
    files_to_copy = set()

    # Add main design SCAD file  
    main_scad_path = os.path.join(design_code_dir, f"{design_name_fs}.scad")
    if os.path.exists(main_scad_path):
        scad_files_to_scan.append(main_scad_path)

    # Add BOM SCAD files first and copy them to design folder  
    bom_items = design.bom_items.filter(bom_link__icontains='lod')
    for bom_item in bom_items:
        if bom_item.bom_link and bom_item.bom_link.endswith('.scad'):
            # Extract path from LoD link
            bom_path = bom_item.bom_link.replace('lod_content/', '')
            source_path = os.path.join(settings.LOD_CONTENT_ROOT, bom_path)
            if os.path.exists(source_path):
                filename = os.path.basename(bom_path)
                dest_path = os.path.join(design_code_dir, filename)
                shutil.copy2(source_path, dest_path)
                # Add to scan list for utility dependencies  
                scad_files_to_scan.append(dest_path)

    # Now scan all SCAD files for utility dependencies  
    for scad_file_path in scad_files_to_scan:
        extract_utility_dependencies(scad_file_path, files_to_copy)

    # Copy all collected utility files to design folder  
    for source_path, filename in files_to_copy:
        dest_path = os.path.join(design_code_dir, filename)
        if not os.path.exists(dest_path):  # Avoid overwriting  
            shutil.copy2(source_path, dest_path)

    # Update paths in all SCAD files (but not utility files)  
    for scad_file_path in scad_files_to_scan:
        update_scad_file_paths(scad_file_path, design.bom_items.filter(bom_link__icontains='lod'))


def find_utility_dependencies(utility_file_path, files_to_copy):
    """Recursively find utility dependencies in SCAD files"""
    try:
        with open(utility_file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find include statements  
        import re
        includes = re.findall(r'include <lod_content/designs/utilities/(.+?)>', content)
        for include_file in includes:
            source_path = os.path.join(settings.LOD_CONTENT_ROOT, 'designs', 'utilities', include_file)
            if os.path.exists(source_path):
                files_to_copy.add((source_path, include_file))
                # Recursively check this file too
                find_utility_dependencies(source_path, files_to_copy)
    except Exception as e:
        print(f"Error processing {utility_file_path}: {e}")


def extract_utility_dependencies(scad_file_path, files_to_copy):
    """Extract utility dependencies from a SCAD file"""
    try:
        with open(scad_file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find utility includes  
        import re
        utility_includes = re.findall(r'include <lod_content/designs/utilities/(.+?)>', content)
        for utility_file in utility_includes:
            source_path = os.path.join(settings.LOD_CONTENT_ROOT, 'designs', 'utilities', utility_file)
            if os.path.exists(source_path):
                files_to_copy.add((source_path, utility_file))
                # Recursively find dependencies in utility files  
                find_utility_dependencies(source_path, files_to_copy)
    except Exception as e:
        print(f"Error processing {scad_file_path}: {e}")


def update_scad_file_paths(scad_file_path, bom_items):
    """Update include paths in a single SCAD file"""
    try:
        with open(scad_file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Replace utility paths 
        content = re.sub(r'include <lod_content/designs/utilities/([^>]+)>', r'include <\1>', content)

        # Replace BOM paths with local filenames
        for bom_item in bom_items:
            if bom_item.bom_link and bom_item.bom_link.endswith('.scad'):
                filename = os.path.basename(bom_item.bom_link)
                content = content.replace(f'include <{bom_item.bom_link}>', f'include <{filename}>')

        # Write updated content 
        with open(scad_file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        print(f"Error updating paths in {scad_file_path}: {e}")


def bom_search(request):
    """BOM search view for selecting designs to add to BOM"""
    query = request.GET.get('query', '')
    category_id = request.GET.get('category', 0)
    per_page = request.GET.get('per_page', '25')

    # Start with all designs  
    designs = Design.objects.all()

    # Apply search filter if query exists  
    if query:
        designs = designs.filter(Q(name__icontains=query) |
                                 Q(description__icontains=query) |
                                 Q(tags__name__icontains=query) |
                                 Q(category__name__icontains=query) |
                                 Q(created_by__username__icontains=query) |
                                 Q(added_by__username__icontains=query))

    # Apply category filter if specified
    if category_id:
        designs = designs.filter(category_id=category_id)

    # Get categories with design counts (only categories with matching designs)  
    if query:
        categories_with_counts = []
        for category in Category.objects.all():
            category_designs = designs.filter(category=category)
            if category_designs.exists():
                categories_with_counts.append({
                    'id': category.id,
                    'name': category.name,
                    'design_count': category_designs.count()
                })
    else:
        categories_with_counts = [
            {
                'id': cat.id,
                'name': cat.name,
                'design_count': designs.filter(category=cat).count()
            }
            for cat in Category.objects.all()
            if designs.filter(category=cat).exists()
        ]

    # Handle pagination  
    if per_page != 'all':
        paginator = Paginator(designs, int(per_page))
        page_number = request.GET.get('page')
        designs = paginator.get_page(page_number)

    # Add image processing for each design  
    design_list = designs if per_page == 'all' else designs.object_list
    for design in design_list:
        design_images = get_design_images(design)
        design.first_image = design_images[0] if design_images else {'url': None}

    return render(request, 'design/bom_search.html', {
        'designs': designs,
        'query': query,
        'categories': categories_with_counts,
        'category_id': int(category_id) if category_id else 0,
        'per_page': per_page,
        'has_search_results': bool(query),
    })
