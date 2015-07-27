import os

from django.shortcuts import get_object_or_404, render_to_response
from django.http import StreamingHttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.core.servers.basehttp import FileWrapper
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.views.generic import View
from django.core.files.storage import FileSystemStorage
from django.conf import settings

from .models import ExtractionOrder, Excerpt, OutputFile, BBoxBoundingGeometry
from .models.extraction_order import ExtractionOrderState
from osmaxx.contrib.auth.frontend_permissions import (
    frontend_access_required,
    LoginRequiredMixin,
    FrontendAccessRequiredMixin
)
from .forms import ExportOptionsForm, NewExcerptForm
from .tasks import create_export
from . import settings as excerptexport_settings

private_storage = FileSystemStorage(location=settings.PRIVATE_MEDIA_ROOT)


class NewExtractionOrderView(LoginRequiredMixin, FrontendAccessRequiredMixin, View):
    def get(self, request, excerpt_form_initial_data=None):
        active_excerpts = Excerpt.objects.filter(is_active=True)
        active_bbox_excerpts = active_excerpts.filter(bounding_geometry__bboxboundinggeometry__isnull=False)
        active_file_excerpts = active_excerpts.filter(
            bounding_geometry__osmosispolygonfilterboundinggeometry__isnull=False)
        view_model = {
            'user': request.user,
            'export_options_form': ExportOptionsForm(auto_id='%s'),
            'new_excerpt_form': NewExcerptForm(auto_id='%s', initial=excerpt_form_initial_data),
            'excerpts': {
                'own_private': active_bbox_excerpts.filter(is_public=False, owner=request.user),
                'own_public': active_bbox_excerpts.filter(is_public=True, owner=request.user),
                'other_public': active_bbox_excerpts.filter(is_public=True).exclude(owner=request.user),
                'countries': active_file_excerpts
            }
        }
        return render_to_response('excerptexport/templates/new_excerpt_export.html', context=view_model,
                                  context_instance=RequestContext(request))

    def post(self, request):
        export_options_form = ExportOptionsForm(request.POST)
        if export_options_form.is_valid():
            export_options = export_options_form.get_export_options(excerptexport_settings.EXPORT_OPTIONS)

            extraction_order = None
            if request.POST['form-mode'] == 'existing-excerpt':
                existing_excerpt_id = request.POST['existing_excerpt.id']
                extraction_order = ExtractionOrder.objects.create(
                    excerpt_id=existing_excerpt_id,
                    orderer=request.user
                )

            if request.POST['form-mode'] == 'new-excerpt':
                new_excerpt_form = NewExcerptForm(request.POST)
                if new_excerpt_form.is_valid():
                    form_data = new_excerpt_form.cleaned_data
                    bounding_geometry = BBoxBoundingGeometry.create_from_bounding_box_coordinates(
                        form_data['new_excerpt_bounding_box_north'],
                        form_data['new_excerpt_bounding_box_east'],
                        form_data['new_excerpt_bounding_box_south'],
                        form_data['new_excerpt_bounding_box_west']
                    )

                    excerpt = Excerpt.objects.create(
                        name=form_data['new_excerpt_name'],
                        is_active=True,
                        is_public=form_data['new_excerpt_is_public']
                        if ('new_excerpt_is_public' in form_data) else False,
                        bounding_geometry=bounding_geometry,
                        owner=request.user
                    )

                    extraction_order = ExtractionOrder.objects.create(
                        excerpt=excerpt,
                        orderer=request.user
                    )

                else:
                    messages.error(request, _('Invalid excerpt.'))
                    return self.get(request, new_excerpt_form.data)

            if extraction_order.id:
                create_export.delay(extraction_order.id, export_options)
                messages.success(request, _(
                    'Successful creation of extraction order extraction order %(id)s. '
                    'The conversion process will start soon.'
                ) % {'id': extraction_order.id})
                return HttpResponseRedirect(
                    reverse('excerptexport:status', kwargs={'extraction_order_id': extraction_order.id})
                )

            else:
                messages.error(request, _('Creation of extraction order failed.') % {'id': extraction_order.id})
                return self.get(request, export_options_form.data)

        else:
            messages.error(request, _('Invalid export options.'))
            return self.get(request, export_options_form.data)


@login_required()
@frontend_access_required()
def list_downloads(request):
    view_context = {
        'host_domain': request.get_host(),
        'extraction_orders': ExtractionOrder.objects.filter(
            orderer=request.user,
            state=ExtractionOrderState.FINISHED
        )
    }
    return render_to_response('excerptexport/templates/list_downloads.html', context=view_context,
                              context_instance=RequestContext(request))


def download_file(request, uuid):
    output_file = get_object_or_404(OutputFile, public_identifier=uuid, deleted_on_filesystem=False)
    if not output_file.file:
        return HttpResponseNotFound('<p>No output file attached to output file record.</p>')

    download_file_name = excerptexport_settings.APPLICATION_SETTINGS['download_file_name'] % {
        'id': str(output_file.public_identifier),
        'name': os.path.basename(output_file.file.name)
    }

    # stream file in chunks
    response = StreamingHttpResponse(
        FileWrapper(
            private_storage.open(output_file.file),
            excerptexport_settings.APPLICATION_SETTINGS['download_chunk_size']
        ),
        content_type=output_file.mime_type
    )
    response['Content-Length'] = private_storage.size(output_file.file)
    response['Content-Disposition'] = 'attachment; filename=%s' % download_file_name
    return response


@login_required()
@frontend_access_required()
def extraction_order_status(request, extraction_order_id):
    view_context = {
        'host_domain': request.get_host(),
        'extraction_order': get_object_or_404(ExtractionOrder, id=extraction_order_id, orderer=request.user)
    }
    return render_to_response('excerptexport/templates/extraction_order_status.html', context=view_context,
                              context_instance=RequestContext(request))


@login_required()
@frontend_access_required()
def list_orders(request):
    view_context = {
        'host_domain': request.get_host(),
        'extraction_orders': ExtractionOrder.objects.filter(orderer=request.user)
        .order_by('-id')[:excerptexport_settings.APPLICATION_SETTINGS['orders_history_number_of_items']]
    }
    return render_to_response('excerptexport/templates/list_orders.html', context=view_context,
                              context_instance=RequestContext(request))