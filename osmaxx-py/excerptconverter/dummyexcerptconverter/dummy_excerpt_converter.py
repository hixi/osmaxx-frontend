import os
import time

from celery import shared_task

from django.core.files.base import ContentFile
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages

from excerptconverter.converter_helper import ConverterHelper, module_converter_configuration, run_model_execute

from osmaxx.excerptexport import models
from osmaxx.utils import private_storage


NAME = 'Dummy'
EXPORT_FORMATS = {
    'txt': {
        'name': 'Text (.txt)',
        'file_extension': 'txt',
        'mime_type': 'text/plain'
    },
    'markdown': {
        'name': 'Markdown (.md)',
        'file_extension': 'md',
        'mime_type': 'text/markdown'
    }
}
EXPORT_OPTIONS = {
    'detail_level': {
        'label': 'Detail level',
        'type': 'choice',
        'default': 'verbatim',
        'values': [
            {'name': 'verbatim', 'label': 'Verbatim'},
            {'name': 'simplified', 'label': 'Simplified'}
        ]
    }
}


def converter_configuration():
    return module_converter_configuration(NAME, EXPORT_FORMATS, EXPORT_OPTIONS)


def execute(extraction_order, execution_configuration, run_as_celery_tasks):
    return run_model_execute(
        execute_task,
        EXPORT_FORMATS,
        extraction_order,
        execution_configuration,
        run_as_celery_tasks
    )


def create_output_files(execution_configuration, extraction_order, supported_export_formats, converter_helper):
    for format_key in execution_configuration['formats']:
        output_file = models.OutputFile.objects.create(
            mime_type=supported_export_formats[format_key]['mime_type'],
            extraction_order=extraction_order
        )

        if not os.path.exists(private_storage.location):
            os.makedirs(private_storage.location)

        file_name = str(output_file.public_identifier) + '.' + \
            supported_export_formats[format_key]['file_extension']
        file_content = ContentFile(str('detail level: ' + execution_configuration['options']['detail_level']))
        fs_file = private_storage.save(file_name, file_content)

        # file must be committed, so reopen to attach to model
        output_file.file = fs_file
        output_file.save()

        if private_storage.exists(file_name):
            message_level = messages.SUCCESS
            message_text = _('"{file_name}" created successful').format(file_name=file_name)
        else:
            message_level = messages.ERROR
            message_text = _('Creation of "{file_name}" failed!').format(file_name=file_name)
        converter_helper.inform_user(message_level, message_text, email=False)


@shared_task
def execute_task(extraction_order_id, supported_export_formats, execution_configuration):
    wait_time = 0
    # wait for the db to be updated!
    extraction_order = None
    while extraction_order is None:
        try:
            extraction_order = models.ExtractionOrder.objects.get(pk=extraction_order_id)
        except models.ExtractionOrder.DoesNotExist:
            time.sleep(5)
            wait_time += 5
            if wait_time > 30:
                raise

    try:
        converter_helper = ConverterHelper(extraction_order)
        fake_work_waiting_time_in_seconds = 5

        # now set the new state
        extraction_order.state = models.ExtractionOrderState.WAITING
        extraction_order.save()

        time.sleep(fake_work_waiting_time_in_seconds)

        # now set the new state
        extraction_order.state = models.ExtractionOrderState.PROCESSING
        extraction_order.save()

        message_text = _('The Dummy conversion of extraction order "{order_id}" has been started.').format(
            order_id=extraction_order.id)
        converter_helper.inform_user(messages.INFO, message_text, email=False)

        create_output_files(
            execution_configuration,
            extraction_order,
            supported_export_formats,
            converter_helper
        )

        time.sleep(fake_work_waiting_time_in_seconds)

        # now set the new state (if all files have been processed) and inform the user about the state
        converter_helper.file_conversion_finished()
    except:
        # TODO: log stack trace
        message_text = _('The Dummy conversion of extraction order "{order_id}" failed.').format(
            order_id=extraction_order.id)
        converter_helper.inform_user(messages.ERROR, message_text, email=False)
        raise
