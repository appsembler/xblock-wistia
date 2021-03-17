function WistiaVideoXBlock(runtime, element) {
    "use strict";

    const downloadHandlerUrl = runtime.handlerUrl(element, 'download_captions');
    const downloadBtnSelector = '.wistiavideo_block .wistia_responsive_transcripts .wistia_transcripts_download';
    const wistiaEmbeddedSelector = ".wistiavideo_block .wistia_responsive_padding .wistia_responsive_wrapper .wistia_embed";
    const mediaId = $(wistiaEmbeddedSelector).data("mediaId");

    $(downloadBtnSelector, element).click(function (e) {
        e.preventDefault();
        window.open(downloadHandlerUrl, '_blank');
    });

    window._wq = window._wq || [];

    _wq.push({ id: mediaId, onReady: function(video) {
        video.plugin('captions').then(function (captions) { 
            if (captions.captions.length > 0) {
                $(downloadBtnSelector).show();
            }
        });
    }});
}