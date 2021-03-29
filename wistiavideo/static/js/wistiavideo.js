function WistiaVideoXBlock(runtime, element) {
    "use strict";

    const downloadBtnSelector = '.wistiavideo_block .wistia_responsive_transcripts .wistia_transcripts_download';
    const wistiaEmbeddedSelector = ".wistiavideo_block .wistia_responsive_padding .wistia_responsive_wrapper .wistia_embed";

    const mediaId = $(wistiaEmbeddedSelector).data("mediaId");
    const apiEnabled = $(downloadBtnSelector).data("apiEnabled") === 'True';

    const downloadHandlerUrl = runtime.handlerUrl(element, 'download_captions');
    const captionUrlBase = `http://fast.wistia.net/embed/captions/${mediaId}.vtt`;

    let embeddedVideo = undefined;
    let currentCaptionLanguage = '';

    $(downloadBtnSelector, element).click(function (e) {
        e.preventDefault();

        const targetUrl = apiEnabled ? downloadHandlerUrl : `${captionUrlBase}?lang=${currentCaptionLanguage}`;

        window.open(targetUrl, '_blank', 'noopener');
    });

    window._wq = window._wq || [];

    window._wq.push({ id: mediaId, onReady: function(video) {
        embeddedVideo = video;

        // Change caption language if user changes caption language
        embeddedVideo.bind('captionschange', function (details) {
            if (details.visible && currentCaptionLanguage != details.language) {
                currentCaptionLanguage = details.language
            }
        });

        embeddedVideo.plugin('captions').then(function (captions) { 
            if (captions.captions.length > 0) {
                // Set the default caption language as the current
                currentCaptionLanguage = captions.options.language;

                // Show the download button
                $(downloadBtnSelector).show();
            }
        });
    }});
}
