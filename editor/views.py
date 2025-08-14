from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json
from .models import CADProject, RenderJob


@login_required
def editor_view(request, project_id=None):
    project = None
    if project_id:
        project = get_object_or_404(CADProject, id=project_id, user=request.user)

    context = {
        'project': project,
        'openscad_code': project.openscad_code if project else '',
    }
    return render(request, 'cad_editor/editor.html', context)


@csrf_exempt
def save_project(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        project_id = data.get('project_id')
        code = data.get('code', '')

        if project_id:
            project = get_object_or_404(CADProject, id=project_id, user=request.user)
            project.openscad_code = code
            project.save()
        else:
            project = CADProject.objects.create(
                name=data.get('name', 'Untitled'),
                user=request.user,
                openscad_code=code
            )

    return JsonResponse({'success': True, 'project_id': project.id})


@csrf_exempt
def render_project(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        project_id = data.get('project_id')
        code = data.get('code', '')

        # Create render job
        project = get_object_or_404(CADProject, id=project_id, user=request.user)
        render_job = RenderJob.objects.create(
            project=project,
            status='pending'
        )

        # Process the OpenSCAD code using BlocksCAD's rendering pipeline
        try:
            result = process_openscad_code(code)
            render_job.status = 'completed'
            render_job.save()
            return JsonResponse({'success': True, 'result': result})
        except Exception as e:
            render_job.status = 'error'
            render_job.error_message = str(e)
            render_job.save()
            return JsonResponse({'success': False, 'error': str(e)})


def process_openscad_code(code):
    """
    This function adapts BlocksCAD's rendering pipeline for Django
    Based on blockscad/viewer.js processing logic
    """
    # This would integrate with the BlocksCAD rendering engine  
    # You'll need to adapt the JavaScript code to Python or use a JavaScript engine  
    pass

