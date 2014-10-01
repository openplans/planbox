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
        highlights: '.highlight a',
        shareaboutsContainer: '#shareabouts-region'
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
        // Split the Shareabouts section from the others, so that we can treat
        // it specially.
        this.shareaboutsSection = this.collection.find(function(model) {
          return model.get('type') === 'shareabouts';
        });

        this.pageSections = new Backbone.Collection(
          this.collection.filter(function(model) {
            return model.get('type') !== 'shareabouts';
          })
        );
      },

      showShareaboutsSection: function() {
        if (this.shareaboutsView && !this.shareaboutsView.isClosed) {
          if (this.shareaboutsView.close) { this.shareaboutsView.close(); }
          else if (this.shareaboutsView.remove) { this.shareaboutsView.remove(); }
          delete this.shareaboutsView;
        }

        this.shareaboutsView = new NS.ShareaboutsSectionView({
          model: this.shareaboutsSection,
          el: this.ui.shareaboutsContainer
        });

        this.shareaboutsView.render();
        Marionette.triggerMethod.call(this.shareaboutsView, 'show');
      },

      showPageSections: function() {
        this.sectionList.show(new this.sectionListView({
          model: this.model,
          collection: this.pageSections,
          parent: this
        }));
      },

      onShow: function() {
        // Create, render, and show the Shareabouts map specially
        this.showShareaboutsSection();
        // After the project is in the DOM, show the project sections
        this.showPageSections();
      }
    })
  );


}(Planbox, jQuery));