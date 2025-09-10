from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json
from .models import KidsProject, KidsRenderJob


@login_required
def keditor_view(request, project_id=None):
    project = None
    if project_id:
        project = get_object_or_404(KidsProject, id=project_id, user=request.user)

    context = {
        'project': project,
        'blocks_xml': project.blocks_xml if project else '',
        'openscad_code': project.openscad_code if project else '',
    }
    return render(request, 'keditor/keditor.html', context)


@csrf_exempt
@login_required
def save_kids_project(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        project_id = data.get('project_id')
        blocks_xml = data.get('blocks_xml', '')
        openscad_code = data.get('openscad_code', '')
        name = data.get('name', 'My Project')

        if project_id:
            project = get_object_or_404(KidsProject, id=project_id, user=request.user)
            project.blocks_xml = blocks_xml
            project.openscad_code = openscad_code
            project.name = name
            project.save()
        else:
            project = KidsProject.objects.create(
                name=name,
                user=request.user,
                blocks_xml=blocks_xml,
                openscad_code=openscad_code
            )

        return JsonResponse({'success': True, 'project_id': project.id})


@csrf_exempt
@login_required
def render_kids_project(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        project_id = data.get('project_id')
        blocks_xml = data.get('blocks_xml', '')

        project = get_object_or_404(KidsProject,
                                    id=project_id,
                                    user=request.user)
        render_job = KidsRenderJob.objects.create(
            project=project,
            status='pending'
        )

        try:
            # Process using BlocksCAD rendering pipeline
            result = process_blockscad_blocks(blocks_xml)
            render_job.status = 'completed'
            render_job.save()
            return JsonResponse({'success': True, 'result': result})
        except Exception as e:
            render_job.status = 'error'
            render_job.error_message = str(e)
            render_job.save()
            return JsonResponse({'success': False, 'error': str(e)})


def process_blockscad_blocks(blocks_xml):
    """
    Process BlocksCAD blocks XML and return rendered result
    This integrates with the BlocksCAD rendering engine
    """
    # Implementation would use the BlocksCAD JavaScript engine
    # You'll need to adapt the BlocksCAD processing logic
    pass
