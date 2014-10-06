/*globals Backbone jQuery Handlebars Modernizr _ Pen Shareabouts*/

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

  NS.BaseShareaboutsSectionView = NS.ShareaboutsSectionView;
  NS.ShareaboutsSectionView = NS.BaseShareaboutsSectionView.extend({
    className: 'project-section-shareabouts project-shareabouts',

    getShareaboutsEl: function() {
      return this.$el;
    }
  });

}(Planbox, jQuery));