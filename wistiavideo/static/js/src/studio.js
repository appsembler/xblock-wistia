function WistiaVideoXBlock(runtime, element) {

  var handlerUrl = runtime.handlerUrl(element, 'studio_submit');

  $(function ($) {
    $(element).find('.save-button').bind('click', function() {
      var data = {
        href: $(element).find('input[name=href]').val(),
      };
      runtime.notify('save', {state: 'start'});

      $.post(handlerUrl, JSON.stringify(data)).done(function(response) {
        runtime.notify('save', {state: 'end'});
      });
    });

    $(element).find('.cancel-button').bind('click', function() {
      runtime.notify('cancel', {});
    });

  });
}
