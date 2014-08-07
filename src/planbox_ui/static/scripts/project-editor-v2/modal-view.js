/*globals Backbone jQuery Handlebars Modernizr _ Pen FileAPI chrono */

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

  NS.ModalView = Backbone.Marionette.ItemView.extend({
    template: '#modal-tpl',
    className: 'reveal-modal medium',
    attributes: {
      'data-reveal': ''
    },
    onShow: function() {
      // This is gross. We should encourage Foundation to fix this.
      this.$el.foundation().foundation('reveal', 'open');
    },
    onClose: function() {
      // This is gross. We should encourage Foundation to fix this.
      this.$el.foundation().foundation('reveal', 'close');
    }
  });

  NS.showErrorModal = function(title, subtitle, description) {
    NS.app.modalRegion.show(new NS.ModalView({
      model: new Backbone.Model({
        title: title,
        subtitle: subtitle,
        description: description
      })
    }));
  };

  NS.showProjectSaveErrorModal = function(resp) {
    var statusCode = resp.status,
        respJSON = resp.responseJSON,
        title, subtitle, description;

    ////
    // TODO: We can have a single subtitle template and a description template
    //       for ajax errors, and then pass in a status code.
    ////
    title = 'Unable to save.';
    if (statusCode === 0) {
      // No network connectivity
      subtitle = Handlebars.templates['message-ajax-no-status-error-subtitle']({});
      description = Handlebars.templates['message-ajax-no-status-error-description']({});

    } else if (statusCode === 400) {
      // Bad request (missing title, at this point)
      subtitle = Handlebars.templates['message-ajax-bad-request-error-subtitle']({errors: respJSON});
      description = Handlebars.templates['message-ajax-bad-request-error-description']({errors: respJSON});

    } else if (statusCode === 401 || statusCode === 403 || statusCode === 404) {
      // Authentication error
      // NOTE: you get a 404 when trying to access a private project, which
      // could belong to the user but they're now signed out for some reason.
      subtitle = Handlebars.templates['message-ajax-authentication-error-subtitle']({});
      description = Handlebars.templates['message-ajax-authentication-error-description']({});

    } else if (statusCode >= 500) {
      // Unknown server error
      subtitle = Handlebars.templates['message-ajax-server-error-subtitle']({});
      description = Handlebars.templates['message-ajax-server-error-description']({});

    } else {
      // No idea
      subtitle = Handlebars.templates['message-ajax-unknown-error-subtitle']({});
      description = Handlebars.templates['message-ajax-unknown-error-description']({});
    }

    NS.showErrorModal(title, subtitle, description);
  };

}(Planbox, jQuery));