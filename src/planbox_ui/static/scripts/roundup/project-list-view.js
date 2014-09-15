/*globals Backbone, jQuery, Modernizr, Handlebars */

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

  NS.ProjectListItemView = Backbone.Marionette.ItemView.extend({
    template: '#project-list-item-tpl',
    tagName: 'div'
  });

  NS.ProjectListView = Backbone.Marionette.CompositeView.extend({
    template: '#project-list-tpl',
    itemView: NS.ProjectListItemView,
    itemViewContainer: '.project-list'
  });

}(Planbox, jQuery));