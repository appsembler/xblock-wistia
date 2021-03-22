"""
Wistia video XBlock provides a convenient way to place videos hosted on
Wistia platform.
All you need to provide is video url, this XBlock doest the rest for you.
"""

import os
import pkg_resources
import re
import tempfile

import requests

from zipfile import ZipFile, ZIP_DEFLATED
from pathlib import Path

from xblock.core import XBlock
from xblock.fields import Scope, String
from xblock.fragment import Fragment
from xblock.validation import ValidationMessage

from xblockutils.resources import ResourceLoader
from xblockutils.studio_editable import StudioEditableXBlockMixin
from webob import Response

_ = lambda text: text

loader = ResourceLoader(__name__)
# From official Wistia documentation. May change in the future
# https://wistia.com/doc/construct-an-embed-code#the_regex
VIDEO_URL_RE = re.compile(r'https?:\/\/(.+)?(wistia.com|wi.st)\/(medias|embed)\/.*')


class CaptionDownloadMixin:
    """
    Mixin providing utility functions and handler to download captions from Wistia.
    
    The utility mixin is heavily depending on the media ID property provided by the XBlock.
    """

    access_token = String(
        default='',
        display_name=_('Wistia API key'),
        help=_('The API key related to the account where the video uploaded to.'),
        scope=Scope.content,
    )

    caption_download_editable_fields = ('access_token',)

    def __send_request(self, url):
        """
        Send a request to Wistia API using the given access token if provided and return the
        response as a parsed JSON string.
        """

        return requests.get(url, params={"access_token": self.access_token}).json()

    @property
    def has_access_token(self):
        return bool(self.access_token)

    @staticmethod
    def __compress_captions(srt_files):
        """
        Compress files into a zip file.
        """

        zip_file = tempfile.NamedTemporaryFile(
            prefix="captions_",
            suffix=".zip",
            delete=False
        )

        with ZipFile(zip_file.name, mode="w", compression=ZIP_DEFLATED) as compressed:
            for srt_file in srt_files:
                compressed.write(srt_file, srt_file.split("/")[-1])

        return Path(zip_file.name)

    @staticmethod
    def __save_caption(caption):
        """
        Save the caption to a temporary file and return its absolute path.
        """

        language = caption["language"]
        content = caption['text']

        srt_file = tempfile.NamedTemporaryFile(
            prefix="{}_".format(language),
            suffix=".srt",
            delete=False
        )

        srt_file.write(bytes(content, encoding="UTF-8"))
        srt_file.close()

        return srt_file.name

    @XBlock.handler
    def download_captions(self, request, suffix=""):
        """
        Handle captions download.

        Get captions text available for the media ID and save them in separate files. The saved
        captions will be compressed and prepared for download in the response.
        """

        response = self.__send_request(
            "https://api.wistia.com/v1/medias/{}/captions.json".format(self.media_id),
        )

        srt_files = map(self.__save_caption, response)
        zip_file = self.__compress_captions(srt_files)
        map(os.unlink, srt_files)

        return Response(
            body=zip_file.read_bytes(),
            headerlist=[
                ("Content-Type", "application/zip; charset=UTF-8"),
                ("Content-Disposition", "attachment; filename=captions_{}.zip".format(
                    self.media_id,
                )),
            ],
        )


class WistiaVideoXBlock(StudioEditableXBlockMixin, CaptionDownloadMixin, XBlock):

    display_name = String(
        default='Wistia video',
        display_name=_('Component Display Name'),
        help=_('The name students see. This name appears in the course ribbon and as a header for the video.'),
        scope=Scope.settings,
    )

    href = String(
        default='',
        display_name=_('Video URL'),
        help=_('URL of the video page. E.g. https://example.wistia.com/medias/12345abcde'),
        scope=Scope.content
    )

    editable_fields = ('display_name', 'href')
    editable_fields += CaptionDownloadMixin.caption_download_editable_fields

    @property
    def media_id(self):
        """
        Extracts Wistia's media hashed id from the media url.
        E.g. https://example.wistia.com/medias/12345abcde -> 12345abcde
        """
        if self.href:
            return self.href.split('/')[-1]
        return ''

    def validate_field_data(self, validation, data):
        if data.href != '' and not VIDEO_URL_RE.match(data.href):
            validation.add(ValidationMessage(
                ValidationMessage.ERROR,
                _("Incorrect video url, please recheck")
            ))

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def student_view(self, context=None):
        """
        The primary view of the WistiaVideoXBlock, shown to students
        when viewing courses.
        """

        context = {
            "download_transcripts_text": _("Download transcripts"),
            "media_id": self.media_id,
            "has_access_token": self.has_access_token,
        }

        frag = Fragment(loader.render_template('static/html/wistiavideo.html', context))
        frag.add_css(self.resource_string('static/css/wistiavideo.css'))
        frag.add_javascript(loader.load_unicode('static/js/wistiavideo.js'))
        frag.initialize_js('WistiaVideoXBlock', {})

        return frag

    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("WistiaVideoXBlock",
             """<wistiavideo media_id="ps0suympnl"/>
             """),
            ("WistiaVideoXBlock LMS",
             """<vertical_demo>
                <wistiavideo />
                <wistiavideo/>
                <wistiavideo/>
                </vertical_demo>
             """),
        ]
