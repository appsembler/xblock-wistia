import json
import unittest

from mock import Mock, patch

from xblock.runtime import KvsFieldData, DictKeyValueStore
from xblock.test.tools import (
    TestRuntime
)

from wistiavideo import WistiaVideoXBlock


class WistiaXblockBaseTests(object):
    def make_xblock(self, **kwargs):
        key_store = DictKeyValueStore()
        field_data = KvsFieldData(key_store)
        runtime = TestRuntime(services={'field-data': field_data})
        xblock = WistiaVideoXBlock(runtime, scope_ids=Mock())

        for attr, val in kwargs.items():
            setattr(xblock, attr, val)

        return xblock


class WistiaXblockTests(WistiaXblockBaseTests, unittest.TestCase):
    def test_media_id_property(self):
        xblock = self.make_xblock(href='https://example.wistia.com/medias/12345abcde')
        self.assertEquals(xblock.media_id, '12345abcde')

    def test_student_view(self):
        xblock = self.make_xblock()

        student_view_html = xblock.student_view()
        self.assertIn(xblock.media_id, student_view_html.body_html())

class WistiaXblockTranscriptsDownloadTests(WistiaXblockBaseTests, unittest.TestCase):
    def __render_html(self):
        xblock = self.make_xblock()
        return xblock.student_view().body_html()

    def test_transcripts_block_exists(self):
        self.assertIn("wistia_responsive_transcripts", self.__render_html())

    def test_download_button_exists(self):
        self.assertIn("wistia_transcripts_download", self.__render_html())

    def test_access_token_not_set(self):
        media_id = "12345abcde"
        href = "https://example.wistia.com/medias/{}".format(media_id)

        xblock = self.make_xblock(href=href)
        rendered_html = xblock.student_view().body_html()

        self.assertFalse(xblock.has_access_token)
        self.assertIn("wistia_transcripts_download", rendered_html)
        self.assertIn('data-api-enabled="False"', rendered_html)

    def test_access_token_set(self):
        media_id = "12345abcde"
        href = "https://example.wistia.com/medias/{}".format(media_id)

        xblock = self.make_xblock(href=href, access_token="token")
        rendered_html = xblock.student_view().body_html()

        self.assertTrue(xblock.has_access_token)
        self.assertIn("wistia_transcripts_download", rendered_html)
        self.assertIn('data-api-enabled="True"', rendered_html)

    @patch("wistiavideo.wistiavideo.requests")
    def test_send_request(self, mock_requests):
        media_id = "12345abcde"
        href = "https://example.wistia.com/medias/{}".format(media_id)
        expected_token = "token"
        expected_url = "https://api.wistia.com/v1/medias/{}/captions.json".format(media_id)

        mock_requests.get.return_value = Mock(json=Mock(return_value=[
            {
                "language": "eng",
                "text": "caption text",
            },
        ]))

        xblock = self.make_xblock(
            href=href,
            access_token=expected_token
        )

        response = xblock.download_captions(Mock())

        self.assertEqual(response.status, "200 OK")
        self.assertNotEqual(response.body, b"")
        self.assertEqual(response.headers["Content-Type"], "application/zip; charset=UTF-8")
        self.assertEqual(
            response.headers["Content-Disposition"],
            "attachment; filename=captions_{}.zip".format(media_id)
        )

        mock_requests.get.assert_called_once_with(
            expected_url,
            params={"access_token": expected_token}
        )

class WistiaXblockValidationTests(WistiaXblockBaseTests, unittest.TestCase):
    def test_validate_correct_inputs(self):
        xblock = self.make_xblock()

        for href in ('',
                     'https://foo.wistia.com/medias/bar',
                     'https://foo.wistia.com/embed/bar',
                     'https://foo.wi.st/embed/bar',
                     'https://foo.wi.st/medias/bar'):
            data = Mock(href=href)
            validation = Mock()
            validation.add = Mock()
            xblock.validate_field_data(validation, data)

            self.assertFalse(validation.add.called)

    @patch('xblock.validation.ValidationMessage')
    def test_validate_incorrect_inputs(self, ValidationMessage):
        xblock = self.make_xblock()

        data = Mock(href='http://youtube.com/watch?v=something')
        validation = Mock()
        validation.add = Mock()

        xblock.validate_field_data(validation, data)
        self.assertTrue(validation.add.called)
