/*globals Backbone, jQuery, Modernizr, Handlebars */

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

  NS.ProjectListItemAdminView = Backbone.Marionette.ItemView.extend({
    template: '#project-list-item-admin-tpl',
    tagName: 'li',
    className: 'project',
    ui: {
      changeSlugBtn: '.change-slug',
      cancelSlugBtn: '.cancel-slug-change'
    },
    events: {
      'click @ui.changeSlugBtn': 'handleOpenSlugForm',
      'click @ui.cancelSlugBtn': 'handleCloseSlugForm'
    },
    handleOpenSlugForm: function(evt) {
      evt.preventDefault();
      var context = $(evt.currentTarget).parents('li.project');
      context.find('.slug').addClass('hide');
      context.find('form').removeClass('hide');
    },
    handleCloseSlugForm: function(evt) {
      evt.preventDefault();
      var context = $(evt.currentTarget).parents('li.project');
      context.find('.slug').removeClass('hide');
      context.find('form').addClass('hide');
    }
  });

  NS.ProjectListAdminView = Backbone.Marionette.CompositeView.extend({
    template: '#project-list-admin-tpl',
    itemView: NS.ProjectListItemAdminView,
    itemViewContainer: '.project-list'
  });

}(Planbox, jQuery));