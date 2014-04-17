/*globals Backbone _ window jQuery */

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

  NS.BaseProjectView = Backbone.Marionette.Layout.extend({
    regions: {
      highlightHappeningNow: '#highlight-happening-now',
      highlightGetInvolved: '#highlight-get-involved',
      sectionList: '#section-list'
    },

    showRegions: function() {
      // You must set sectionListView in the derived view class to the view
      // for displaying the list of sections.
      this.sectionList.show(new this.sectionListView({
        model: this.model,
        collection: this.collection,
        parent: this
      }));
    },

    onRender: function() {
      this.showRegions();
    },
    onDomRefresh: function() {
      // The dom changed. Make sure that any Foundation plugins are init'd.
      $(document).foundation();
    }
  });

  NS.BaseProjectSectionListView = Backbone.Marionette.CollectionView.extend({
    initialize: function() {
      this.options.itemViewOptions = this.getItemViewOptions;
    },

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

  NS.SortableListItemAdminView = Backbone.Marionette.Layout.extend({
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

  NS.SortableListAdminView = Backbone.Marionette.CompositeView.extend({
    collectionEvents: {
      'change':  'dataChanged',
      'add':     'dataChanged',
      'remove':  'dataChanged',
      'reorder': 'dataChanged'
    },
    itemViewOptions: function() {
      // Pass the parent to the itemViews in case they need to call dataChanged
      return { parent: this.options.parent };
    },
    onRender: function() {
      this.initSortableItemList();
    },
    initSortableItemList: function() {
      var self = this;

      this.ui.itemList.sortable({
        handle: '.handle',
        update: function(evt, ui) {
          var id = $(ui.item).attr('data-id'),
              model = self.collection.get(id),
              index = $(ui.item).index();

          // Silent because we don't want the list to rerender
          self.collection.moveTo(model, index);
        }
      });
    },
    handleAddClick: function(evt) {
      evt.preventDefault();

      this.collection.add({});

      this.$(this.ui.newItemFocus.selector).focus();
    },
    dataChanged: function() {
      this.options.parent.dataChanged();
    }
  });

}(Planbox, jQuery));
