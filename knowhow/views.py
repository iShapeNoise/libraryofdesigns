from django.shortcuts import render, redirect
from django.conf import settings
import os
import markdown
from bs4 import BeautifulSoup

def lod(request):  
    courses = []  
    section_path = os.path.join(str(settings.LOD_CONTENT_ROOT), 'know-how', 'lod')  
      
    if os.path.exists(section_path):  
        for course_folder in os.listdir(section_path):  
            course_path = os.path.join(section_path, course_folder)  
            if os.path.isdir(course_path):  
                about_path = os.path.join(course_path, 'about.md')  
                if os.path.exists(about_path):  
                    try:  
                        with open(about_path, 'r', encoding="utf-8") as f:  
                            about_content = f.read()  
                            about_html = markdown.markdown(about_content)  
                          
                        course_image = None  
                        overview_img_path = os.path.join(course_path, 'overviewfiles')  
                        if os.path.exists(overview_img_path):  
                            for filename in os.listdir(overview_img_path):  
                                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):  
                                    course_image = f"/{settings.LOD_CONTENT_URL}know-how/lod/{course_folder}/overviewfiles/{filename}"  
                                    break  
                          
                        courses.append({  
                            'name': course_folder,  
                            'title': course_folder.replace('_', ' ').title(),  
                            'about_html': about_html,  
                            'course_image': course_image,  
                            'section': 'lod'  
                        })  
                    except Exception as e:  
                        print(f"Error reading course {course_folder}: {e}")  
                        continue  
      
    context = {  
        'courses': courses,  
        'section_title': 'Library of Designs Courses',  
        'has_courses': len(courses) > 0  
    }  
    return render(request, 'knowhow/lod.html', context)  
  
def cad(request):  
    courses = []  
    section_path = os.path.join(str(settings.LOD_CONTENT_ROOT), 'know-how', 'cad')  
      
    if os.path.exists(section_path):  
        for course_folder in os.listdir(section_path):  
            course_path = os.path.join(section_path, course_folder)  
            if os.path.isdir(course_path):  
                about_path = os.path.join(course_path, 'about.md')  
                if os.path.exists(about_path):  
                    try:  
                        with open(about_path, 'r', encoding="utf-8") as f:  
                            about_content = f.read()  
                            about_html = markdown.markdown(about_content)  
                          
                        course_image = None  
                        overview_img_path = os.path.join(course_path, 'overviewfiles')  
                        if os.path.exists(overview_img_path):  
                            for filename in os.listdir(overview_img_path):  
                                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):  
                                    course_image = f"/{settings.LOD_CONTENT_URL}know-how/cad/{course_folder}/overviewfiles/{filename}"  
                                    break  
                          
                        courses.append({  
                            'name': course_folder,  
                            'title': course_folder.replace('_', ' ').title(),  
                            'about_html': about_html,  
                            'course_image': course_image,  
                            'section': 'cad'  
                        })  
                    except Exception as e:  
                        print(f"Error reading course {course_folder}: {e}")  
                        continue  
      
    context = {  
        'courses': courses,  
        'section_title': 'Computer-Aided Design Courses',  
        'has_courses': len(courses) > 0  
    }  
    return render(request, 'knowhow/cad.html', context)  
  
def cam(request):  
    courses = []  
    section_path = os.path.join(str(settings.LOD_CONTENT_ROOT), 'know-how', 'cam')  
      
    if os.path.exists(section_path):  
        for course_folder in os.listdir(section_path):  
            course_path = os.path.join(section_path, course_folder)  
            if os.path.isdir(course_path):  
                about_path = os.path.join(course_path, 'about.md')  
                if os.path.exists(about_path):  
                    try:  
                        with open(about_path, 'r', encoding="utf-8") as f:  
                            about_content = f.read()  
                            about_html = markdown.markdown(about_content)  
                          
                        course_image = None  
                        overview_img_path = os.path.join(course_path, 'overviewfiles')  
                        if os.path.exists(overview_img_path):  
                            for filename in os.listdir(overview_img_path):  
                                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):  
                                    course_image = f"/{settings.LOD_CONTENT_URL}know-how/cam/{course_folder}/overviewfiles/{filename}"  
                                    break  
                          
                        courses.append({  
                            'name': course_folder,  
                            'title': course_folder.replace('_', ' ').title(),  
                            'about_html': about_html,  
                            'course_image': course_image,  
                            'section': 'cam'  
                        })  
                    except Exception as e:  
                        print(f"Error reading course {course_folder}: {e}")  
                        continue  
      
    context = {  
        'courses': courses,  
        'section_title': 'Computer-Aided Manufacturing Courses',  
        'has_courses': len(courses) > 0  
    }  
    return render(request, 'knowhow/cam.html', context)  
 

def course_detail(request, course_name, section=None, chapter_name=None):
    """Display course with accordion layout"""
    if not section:
        section = 'cad'  # default fallback

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

    # Scan for all chapter directories and load their content
    chapters = []
    if os.path.exists(course_path):
        for item in os.listdir(course_path):
            item_path = os.path.join(course_path, item)
            if os.path.isdir(item_path) and item not in ['overviewfiles', '_course']:
                chapter_index_path = os.path.join(item_path, 'index.md')
                if os.path.exists(chapter_index_path):
                    try:
                        with open(chapter_index_path, 'r', encoding='utf-8') as f:
                            chapter_content = f.read()
                            chapter_html = markdown.markdown(chapter_content)

                            # Fix image paths using BeautifulSoup
                            soup = BeautifulSoup(chapter_html, 'html.parser')
                            for img in soup.findAll('img'):
                                # Convert relative image paths to absolute web URLs
                                if not img['src'].startswith(('http', '/')):
                                    # Construct the proper web URL for the image
                                    img['src'] = f"/{settings.LOD_CONTENT_URL}know-how/{section}/{course_name}/{item}/content/{img['src']}"

                            chapter_html = str(soup)

                            chapters.append({
                                'name': item,
                                'title': item.replace('_', ' ').title(),
                                'content': chapter_html
                            })
                    except Exception as e:
                        print(f"Error reading chapter {item}: {e}")

    # Sort chapters by name for consistent ordering
    chapters.sort(key=lambda x: x['name'])

    return render(request, 'knowhow/course_detail.html', {
        'course_name': course_name,
        'section': section,
        'index_html': index_html,
        'chapters': chapters
    })
