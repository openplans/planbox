/*globals Backbone, jQuery, Modernizr, Handlebars */

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

  NS.TeamListItemAdminView = Backbone.Marionette.ItemView.extend({
    template: '#team-list-item-admin-tpl',
    tagName: 'li'
  });

  NS.TeamListAdminView = Backbone.Marionette.CompositeView.extend({
    template: '#team-list-admin-tpl',
    itemView: NS.TeamListItemAdminView,
    itemViewContainer: '.team-list'
  });

}(Planbox, jQuery));