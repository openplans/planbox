/*globals Backbone jQuery Handlebars Modernizr _ Pen FileAPI chrono */

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

  NS.ProjectSectionListAdminView = NS.BaseProjectSectionListView.extend({
    collectionEvents: {
      'change':  'dataChanged',
      'add':     'dataChanged',
      'remove':  'dataChanged',
      'reorder': 'dataChanged'
    },
    sectionViews: {
      'timeline': NS.TimelineSectionAdminView,
      'text': NS.TextSectionAdminView,
      'faqs': NS.FaqsSectionAdminView,
      'shareabouts': NS.ShareaboutsSectionAdminView,
      'raw': NS.RawHtmlSectionAdminView
    },
    dataChanged: function() {
      this.options.parent.dataChanged();
    }
  });

}(Planbox, jQuery));