from django.shortcuts import render, redirect
from django.conf import settings
import os
import markdown
from bs4 import BeautifulSoup


def lod(request):
    path = os.path.join(str(settings.MEDIA_ROOT), 'knowhow', 'lod', 'LOD.md')
    text = ''
    with open(path, 'r', encoding="utf-8") as f:
        text = f.read()
    html_text = markdown.markdown(text)
    path_img = path = os.path.join(str(settings.MEDIA_ROOT), 'knowhow', 'lod', 'img')
    soup = BeautifulSoup(html_text)
    path_here = os.path.join(str(os.getcwd()), 'templates', 'knowhow')
    img_path = os.path.relpath(path_img, path_here)
    for img in soup.findAll('img'):
        img['src'] = img['src'].replace('img', img_path)
    html_code = str(soup)
    context = {
        'html_code': html_code,
    }
    return render(request, 'knowhow/lod.html', context)


def cad(request):
    path = os.path.join(str(settings.MEDIA_ROOT), 'knowhow', 'cad', 'CAD.md')
    text = ''
    with open(path, 'r', encoding="utf-8") as f:
        text = f.read()
    html_text = markdown.markdown(text)
    path_img = path = os.path.join(str(settings.MEDIA_ROOT), 'knowhow', 'cad', 'img')
    soup = BeautifulSoup(html_text)
    path_here = os.path.join(str(os.getcwd()), 'templates', 'knowhow')
    img_path = os.path.relpath(path_img, path_here)
    for img in soup.findAll('img'):
        img['src'] = img['src'].replace('img', img_path)
    html_code = str(soup)
    context = {
        'html_code': html_code,
    }
    return render(request, 'knowhow/cad.html', context)


def cam(request):
    path = os.path.join(str(settings.MEDIA_ROOT), 'knowhow', 'cam', 'CAM.md')
    text = ''
    with open(path, 'r', encoding="utf-8") as f:
        text = f.read()
    html_text = markdown.markdown(text)
    path_img = path = os.path.join(str(settings.MEDIA_ROOT), 'knowhow', 'cam', 'img')
    soup = BeautifulSoup(html_text)
    path_here = os.path.join(str(os.getcwd()), 'templates', 'knowhow')
    img_path = os.path.relpath(path_img, path_here)
    for img in soup.findAll('img'):
        img['src'] = img['src'].replace('img', img_path)
    html_code = str(soup)
    context = {
        'html_code': html_code,
    }
    return render(request, 'knowhow/cam.html', context)
