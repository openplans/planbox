/*globals Backbone, jQuery, Modernizr, Handlebars */

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

  NS.ProjectListEmptyView = Backbone.Marionette.ItemView.extend({
    template: '#project-list-empty-tpl',
    tagName: 'div'
  });

  NS.ProjectListItemView = Backbone.Marionette.ItemView.extend({
    template: '#project-list-item-tpl',
    tagName: 'div'
  });

  NS.ProjectListView = Backbone.Marionette.CompositeView.extend({
    template: '#project-list-tpl',
    itemView: NS.ProjectListItemView,
    itemViewContainer: '.project-list',
    emptyView: NS.ProjectListEmptyView,

    showEmptyView: function(){
      var EmptyView = this.getEmptyView();

      if (EmptyView && !this._showingEmptyView){
        this._showingEmptyView = true;
        var model = this.model;
        this.addItemView(model, EmptyView, 0);
      }
    }
  });

}(Planbox, jQuery));