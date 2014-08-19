/*globals Backbone, jQuery, Modernizr, Handlebars */

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

  NS.ProjectListItemAdminView = Backbone.Marionette.ItemView.extend({
    template: '#project-list-item-admin-tpl',
    tagName: 'li'
  });

  NS.ProjectListAdminView = Backbone.Marionette.CompositeView.extend({
    template: '#project-list-admin-tpl',
    itemView: NS.ProjectListItemAdminView,
    itemViewContainer: '.project-list'
  });

}(Planbox, jQuery));