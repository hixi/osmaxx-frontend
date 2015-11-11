import os
import shutil
from unittest.mock import patch

from django.http import HttpRequest
from django.test import TestCase

from conversion_job.models import Extent, ConversionJob, GISFormat
from conversion_job.serializers import ConversionJobSerializer, GISFormatStatusSerializer
from converters import converter_options
from shared import ConversionProgress


class RQJobMock:
    id = ''.join(['1' for _ in range(36)])


class GISFormatListSerializerTest(TestCase):
    def setUp(self):
        self.extent = Extent.objects.create(west=0, south=0, east=0, north=0)
        self.conversion_job = ConversionJob.objects.create(extent=self.extent)
        self.gis_format_1 = GISFormat.objects.create(
            conversion_job=self.conversion_job,
            format=converter_options.get_output_formats()[0]
        )
        self.gis_format_2 = GISFormat.objects.create(
            conversion_job=self.conversion_job,
            format=converter_options.get_output_formats()[3]
        )

    @patch('conversion_job.serializers.ConversionJobSerializer._enqueue_rq_job', return_value=RQJobMock)
    def test_create(self, mock):
        self.assertEqual(GISFormat.objects.count(), 2)
        self.assertEqual(Extent.objects.count(), 1)
        self.assertEqual(ConversionJob.objects.count(), 1)
        data = {
            "gis_formats": converter_options.get_output_formats(),
            "callback_url": "http://example.com",
            "gis_options": {
                "coordinate_reference_system": "WGS_84",
                "detail_level": 1,
            },
            "extent": {
                "west": 29.525547623634335,
                "south": 40.77546776498174,
                "east": 29.528980851173397,
                "north": 40.77739734768811,
                "polyfile": None,
            }
        }
        conversion_job_serializer = ConversionJobSerializer(data=data)
        conversion_job_serializer.is_valid()
        conversion_job_serializer.save()

        self.assertEqual(Extent.objects.count(), 2)
        self.assertEqual(GISFormat.objects.count(), 2 + len(converter_options.get_output_formats()))
        self.assertEqual(ConversionJob.objects.count(), 2)

        args, kwargs = mock.call_args
        self.assertCountEqual(kwargs['format_options'].output_formats, converter_options.get_output_formats())

        self.assertNotEqual(self.conversion_job, ConversionJob.objects.last())


class GISFormatStatusSerializerTest(TestCase):
    def setUp(self):
        extent = Extent.objects.create(west=0, south=0, east=0, north=0)
        self.conversion_job = ConversionJob.objects.create(extent=extent)
        self.gis_format = GISFormat.objects.create(
            conversion_job=self.conversion_job,
            format=converter_options.get_output_formats()[0]
        )
        request = HttpRequest()
        request.META['HTTP_HOST'] = 'some-host'
        self.format_status_serializer = GISFormatStatusSerializer(self.gis_format, context={'request': request})

    def tearDown(self):
        shutil.rmtree(self.conversion_job.output_directory)
        super().tearDown()

    def _create_valid_file(self):
        matching_file_names = ['{}.zip'.format(f) for f in converter_options.get_output_formats()]
        for matching_file_name in matching_file_names:
            open(os.path.join(self.conversion_job.output_directory, matching_file_name), 'x').close()

    def test_get_download_url_is_none_when_file_is_not_available(self):
        self.gis_format.progress = ConversionProgress.SUCCESSFUL.value
        self.gis_format.save()
        self.assertIsNone(self.format_status_serializer.data.get('result_url'))

    def test_get_download_url_is_avilable_if_file_is_avaiable_even_if_progress_is_not_success(self):
        self._create_valid_file()
        os.path.join(self.conversion_job.output_directory)
        self.assertEqual(
            'http://some-host/gis_format_status/1/download_result/',
            self.format_status_serializer.data.get('result_url')
        )

    def test_get_download_url_is_defined_when_status_is_success_and_file_available(self):
        self._create_valid_file()
        self.gis_format.progress = ConversionProgress.SUCCESSFUL.value
        self.gis_format.save()
        self.assertIsNotNone(self.format_status_serializer.data.get('result_url'))

    def test_get_download_url_is_defined_when_status_raises_error_when_deleted(self):
        self.gis_format.delete()
        with self.assertRaises(GISFormat.DoesNotExist):
            # self.format_status_serializer.data already raises, but .get does raise as well.
            self.format_status_serializer.data.get('result_url')
