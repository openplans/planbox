/*globals Backbone _ */

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
}(Planbox, jQuery));
