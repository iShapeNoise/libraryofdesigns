from django.shortcuts import render, redirect
from django.conf import settings
import os
import markdown
from bs4 import BeautifulSoup


def section_courses(request, section):
    """Generic view for all know-how sections (cad, cam, lod)"""
    # Define section titles 
    section_titles = {
        'cad': 'Computer-Aided Design Courses',
        'cam': 'Computer-Aided Manufacturing Courses',
        'lod': 'Library of Designs Courses'
    }

    # Validate section
    if section not in section_titles:
        return redirect('knowhow:cad')  # fallback to cad

    courses = []
    section_path = os.path.join(str(settings.LOD_CONTENT_ROOT), 'know-how', section)
    if os.path.exists(section_path):
        for course_folder in os.listdir(section_path):
            course_path = os.path.join(section_path, course_folder)
            if os.path.isdir(course_path):
                about_path = os.path.join(course_path, 'about.md')
                if os.path.exists(about_path):
                    try:
                        with open(about_path, 'r', encoding="utf-8") as f:
                            about_content = f.read()

                            # Look for ExtraBtn pattern before converting to HTML  
                            extra_btn_link = None
                            extra_btn_text = None

                            # Search for ExtraBtn: pattern in raw markdown  
                            lines = about_content.split('\n')
                            for line in lines:
                                if line.strip().startswith('ExtraBtn:'):
                                    # Extract the title after "ExtraBtn:"  
                                    btn_info = line.strip()[9:].strip()  # Remove "ExtraBtn:" prefix  

                                    # Look for markdown link pattern [text](url)  
                                    import re
                                    link_match = re.search(r'\[([^\]]+)\]\(([^)]+)\)', btn_info)
                                    if link_match:
                                        extra_btn_text = link_match.group(1)
                                        extra_btn_link = link_match.group(2)
                                    else:
                                        # If no link pattern, use the text as button text  
                                        extra_btn_text = btn_info
                                    break
                            filtered_lines = []  
                            for i, line in enumerate(lines):  
                                # Skip first line if it's a header (starts with #)  
                                if i == 0 and line.strip().startswith('#'):  
                                    continue  
                                if not line.strip().startswith('ExtraBtn:'):  
                                    filtered_lines.append(line)  
                            about_content = '\n'.join(filtered_lines)  
                            about_html = markdown.markdown(about_content)
                            # Remove all hyperlinks from about.md content using BeautifulSoup  
                            soup = BeautifulSoup(about_html, 'html.parser')
                            for link in soup.findAll('a'):
                                link.replace_with(link.get_text())
                            about_html = str(soup)
                        # Look for FeatureImage.png in the same folder
                        course_image = None
                        feature_img_path = os.path.join(course_path, 'FeatureImage.png')
                        if os.path.exists(feature_img_path):
                            course_image = f"/{settings.LOD_CONTENT_URL}know-how/{section}/{course_folder}/FeatureImage.png"
                        else:
                            course_image = None
                        courses.append({
                            'name': course_folder,
                            'title': course_folder.replace('_', ' ').title(),
                            'about_html': about_html,
                            'course_image': course_image,
                            'section': section,
                            'extra_btn_link': extra_btn_link,
                            'extra_btn_text': extra_btn_text
                        })
                    except Exception as e:
                        print(f"Error reading course {course_folder}: {e}")
                        continue

    context = {
        'courses': courses,
        'section': section,
        'section_title': section_titles[section],
        'has_courses': len(courses) > 0
    }
    # Use the single generic template instead of section-specific ones
    return render(request, 'knowhow/section.html', context)


def course_detail(request, section, course_name, chapter_name=None):
    """Generic course detail view for all sections"""
    # Validate section
    valid_sections = ['cad', 'cam', 'lod']
    if section not in valid_sections:
        return redirect('knowhow:cad')

    course_path = os.path.join(str(settings.LOD_CONTENT_ROOT), 'know-how', section, course_name)

    # Get main index content for course overview
    index_html = ""
    index_path = os.path.join(course_path, 'index.md')
    if os.path.exists(index_path):
        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                index_content = f.read()
                index_html = markdown.markdown(index_content)
        except Exception as e:
            print(f"Error reading index.md for {course_name}: {e}")

    # Scan for numbered content files instead of directories
    chapters = []
    content_path = os.path.join(course_path, 'content')
    if os.path.exists(content_path):
        for filename in os.listdir(content_path):
            if filename.endswith('.md'):
                file_path = os.path.join(content_path, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Extract first line as title (usually the headline)
                        lines = content.split('\n')
                        title = lines[0].strip('#').strip() if lines else filename

                        chapter_html = markdown.markdown(content)

                        # Fix image paths using BeautifulSoup
                        soup = BeautifulSoup(chapter_html, 'html.parser')
                        for img in soup.findAll('img'):
                            # Convert relative image paths to absolute web URLs
                            if not img['src'].startswith(('http', '/')):
                                img['src'] = f"/{settings.LOD_CONTENT_URL}know-how/{section}/{course_name}/content/{img['src']}"

                            # Add responsive image styling to constrain width
                            img['class'] = img.get('class', []) + ['img-fluid']
                            img['style'] = 'max-width: 100%; height: auto;'

                        chapter_html = str(soup)

                        chapters.append({
                            'name': filename.replace('.md', ''),
                            'title': title,
                            'content': chapter_html,
                            'filename': filename
                        })
                except Exception as e:
                    print(f"Error reading content file {filename}: {e}")

    # Sort chapters by filename for proper numerical ordering
    chapters.sort(key=lambda x: x['filename'])

    return render(request, 'knowhow/course_detail.html', {
        'course_name': course_name,
        'section': section,
        'index_html': index_html,
        'chapters': chapters
    })


def course_overview(request, section, course_name):
    """Display course overview with index.md content but no links"""
    # Validate section
    valid_sections = ['cad', 'cam', 'lod']
    if section not in valid_sections:
        return redirect('knowhow:cad')

    course_path = os.path.join(str(settings.LOD_CONTENT_ROOT), 'know-how', section, course_name)

    # Get index content 
    index_html = ""
    index_path = os.path.join(course_path, 'index.md')
    if os.path.exists(index_path):
        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                index_content = f.read()
                # Convert markdown to HTML first
                index_html = markdown.markdown(index_content)

                # Remove all hyperlinks using BeautifulSoup, with special handling for about.md 
                soup = BeautifulSoup(index_html, 'html.parser')
                for link in soup.findAll('a'):
                    href = link.get('href', '')
                    # Remove all links, but especially target about.md links
                    if 'about.md' in href:
                        # Replace <a> tags with just their text content 
                        link.decompose()
                    else:
                        # For other links, also remove them to keep overview as text-only
                        link.replace_with(link.get_text())

                index_html = str(soup)
        except Exception as e:
            print(f"Error reading index.md for {course_name}: {e}")

    return render(request, 'knowhow/course_overview.html', {
        'course_name': course_name,
        'section': section,
        'index_html': index_html
    })
