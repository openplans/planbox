/*globals Backbone jQuery Handlebars Modernizr _ Pen Shareabouts*/

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

  NS.ProjectView = Backbone.Marionette.Layout.extend(
    _.extend({}, NS.MagellanMenuMixin, {
      template: '#project-tpl',
      sectionListView: NS.ProjectSectionListView,
      ui: {
        menuItems: '.project-menu li',
        highlights: '.highlight a'
      },
      events: {
        'click @ui.menuItems': 'onClickMenuItem',
        'click @ui.highlights': 'onClickHighlight'
      },
      regions: {
        sectionList: '#section-list',
        shareaboutsRegion: '#shareabouts-region'
      },
      initialize: function() {
        this.shareaboutsSection = this.collection.find(function(model) {
          return model.get('type') === 'shareabouts';
        });

        this.pageSections = new Backbone.Collection(
          this.collection.filter(function(model) {
            return model.get('type') !== 'shareabouts';
          })
        );
      },
      onShow: function() {
        this.shareaboutsRegion.show(new NS.ShareaboutsSectionView({
          model: this.shareaboutsSection
        }));

        // After the project is in the DOM, show the project sections
        this.sectionList.show(new this.sectionListView({
          model: this.model,
          collection: this.pageSections,
          parent: this
        }));
      }
    })
  );


}(Planbox, jQuery));