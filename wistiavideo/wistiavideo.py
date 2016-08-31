"""
Wistia video XBlock provides a convenient way to place videos hosted on
Wistia platform.
All you need to provide is video url, this XBlock doest the rest for you.
"""

import pkg_resources

from xblock.core import XBlock
from xblock.fields import Scope, Integer, String
from xblock.fragment import Fragment

_ = lambda text: text


class WistiaVideoXBlock(XBlock):

    display_name = String(
        default='Wistia video',
        display_name=_('Display Name'),
        help=_('Display name for this module'),
        scope=Scope.settings,
    )

    href = String(
        default='',
        display_name=_('Video URL'),
        help=_('URL of the video page.\nE.g. https://example.wistia.com/medias/12345abcde'),
        scope=Scope.content
    )

    @property
    def media_id(self):
        """
        Extracts Wistia's media hashed id from the media url.
        E.g. https://edx.wistia.com/medias/12345abcde -> 12345abcde
        """
        if self.href:
            return self.href.split('/')[-1]
        return ''

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def studio_view(self, context):
        """
        Create a fragment used to display the edit view in the Studio.
        """
        html_str = self.resource_string('static/html/studio.html')
        frag = Fragment(unicode(html_str).format(
            href=self.href, href_display_name=self.fields['href'].display_name,
                        href_help=self.fields['href'].help,
                        media_id=self.media_id)
                        )
        frag.add_javascript(self.resource_string('static/js/src/studio.js'))
        frag.initialize_js('WistiaVideoXBlock')

        return frag

    @XBlock.json_handler
    def studio_submit(self, data, suffix=''):
        """
        Called when submitting the form in Studio.
        """
        self.href = data.get('href')

        return {'result': 'success'}

    def student_view(self, context=None):
        """
        The primary view of the WistiaVideoXBlock, shown to students
        when viewing courses.
        """
        html = self.resource_string('static/html/wistiavideo.html')
        frag = Fragment(html.format(self=self))
        frag.add_css(self.resource_string('static/css/wistiavideo.css'))
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
