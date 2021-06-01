function WistiaVideoXBlock(runtime, element) {
    "use strict";

    const captionsDownloadBtnSelector = $(element).find(".wistia_captions_download");
    const transcriptsDownloadBtnSelector = $(element).find(".wistia_transcripts_download");
    const wistiaEmbeddedSelector = $(element).find(".wistia_embed");

    const mediaId = $(wistiaEmbeddedSelector).data("mediaId");
    const apiEnabled = $(captionsDownloadBtnSelector).data("apiEnabled") === 'True';

    const downloadCaptionsHandlerUrl = runtime.handlerUrl(element, 'download_captions');

    const noTranscriptsMessage = "This media does not have a transcript."
    const transcriptsUrl = `http://fast.wistia.net/embed/transcripts/${mediaId}`;
    const captionsUrlBase = `http://fast.wistia.net/embed/captions/${mediaId}.vtt`;

    let embeddedVideo = undefined;
    let currentCaptionLanguage = '';

    $(captionsDownloadBtnSelector, element).click(function (e) {
        e.preventDefault();

        const targetUrl = apiEnabled ? downloadCaptionsHandlerUrl : `${captionsUrlBase}?lang=${currentCaptionLanguage}`;
        window.open(targetUrl, '_blank', 'noopener');
    });

    $(transcriptsDownloadBtnSelector, element).click(function (e) {
        e.preventDefault();
        window.open(transcriptsUrl, '_blank', 'noopener');
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
                $(captionsDownloadBtnSelector).show();
            }
        });

        fetch(transcriptsUrl).then(function(response) {
            if (response.ok) {
                response.text().then(function(body) {
                    if (!body.includes(noTranscriptsMessage)) {
                        $(transcriptsDownloadBtnSelector).show();
                    }
                }).catch(function(error) {
                    console.log(error)
                });
            }
        });
    }});
}
