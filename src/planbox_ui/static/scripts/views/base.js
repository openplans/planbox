/*globals Backbone _ window */

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

  NS.BaseProjectView = Backbone.Marionette.CompositeView.extend({
    itemViewContainer: '#section-list',

    getItemViewOptions: function(section, index) {
      var type = section.get('type'),
          options = {parent: this};

      if (type === 'timeline') {
        options.collection = this.model.get('events');
      }

      if (type === 'faqs') {
        var faqCollection = new NS.FaqCollection(section.get('details'));
        faqCollection.on('change add remove reorder', function() {
          section.set('details', faqCollection.toJSON());
        });
        options.collection = faqCollection;
      }

      return options;
    },

    getItemView: function(section) {
      var type = section.get('type'),
          SectionView = this.sectionViews[type];

      if (!SectionView) {
        throw NS.projectException('Section type "' + type + '" unrecognized.', this.model.toJSON());
      }

      return SectionView;
    }
  });

  NS.ListItemAdminView = Backbone.Marionette.ItemView.extend({
    initialize: function() {
      // cid is not accessible in the toJSON output
      this.$el.attr('data-id', this.model.cid);
    },

    handleDeleteClick: function(evt) {
      evt.preventDefault();

      if (window.confirm('Really delete?')) {
        // I know this is weird, but calling destroy on the model will sync,
        // and there's no url to support that since it's related to the project
        // model. So we're just going to do the remove directly.
        this.model.collection.remove(this.model);
      }
    }

  });

}(Planbox, jQuery));
