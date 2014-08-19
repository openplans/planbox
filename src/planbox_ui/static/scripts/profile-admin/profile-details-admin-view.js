/*globals Backbone, jQuery, Modernizr, Handlebars */

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

  NS.ProfileDetailsAdminView = Backbone.Marionette.ItemView.extend({
    template: '#profile-details-admin-tpl'
  });

}(Planbox, jQuery));