from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt  
from django.contrib.auth.decorators import login_required  
import json  
from .models import CADProject  


@login_required  
def editor_view(request, design_id=None):  
    design = None  
    openscad_code = None  
      
    if design_id:  
        design = get_object_or_404(CADProject, id=design_id, user=request.user)  
        if design.openscad_code and design.openscad_code.strip():  
            openscad_code = design.openscad_code  
  
    context = {  
        'design': design,  
        'openscad_code': openscad_code,  
    }  
    return render(request, 'editor/editor.html', context)  


@csrf_exempt  
@login_required  
def save_design(request):  
    if request.method == 'POST':  
        data = json.loads(request.body)  
        design_id = data.get('design_id')  
        code = data.get('code', '')  
  
        if design_id:  
            design = get_object_or_404(CADProject, id=design_id, user=request.user)  
            design.openscad_code = code  
            design.save()  
        else:  
            design = CADProject.objects.create(  
                name=data.get('name', 'Untitled Design'),  
                user=request.user,  
                openscad_code=code  
            )  
  
        return JsonResponse({'success': True, 'design_id': design.id})


@csrf_exempt
def render_design(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        design_id = data.get('design_id')  # Changed from project_id  
        code = data.get('code', '')

        # Create render job
        design = get_object_or_404(CADProject, id=design_id, user=request.user)  # Changed variable name
        render_job = RenderJob.objects.create(
            project=design,  # Note: model field name stays the same  
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

