/*globals Backbone jQuery Handlebars Modernizr _ Pen */

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

    // Handlebars support for Marionette
  Backbone.Marionette.TemplateCache.prototype.compileTemplate = function(rawTemplate) {
    return Handlebars.compile(rawTemplate);
  };

  // View =====================================================================
  NS.ModalView = Backbone.Marionette.ItemView.extend({
    template: '#modal-tpl',
    className: 'overlay',
    ui: {
      closeBtn: '.btn-close',
    },
    events: {
      'click @ui.closeBtn': 'handleClose'
    },
    handleClose: function(evt) {
      evt.preventDefault();
      this.close();
    }
  });

  NS.WelcomeModalView = NS.ModalView.extend({
    template: '#welcome-modal-tpl'
  });

  NS.ProjectView = Backbone.Marionette.CompositeView.extend({
    template: '#project-tpl',
    itemViewContainer: '#section-list',

    getItemViewOptions: function(item, index) {
      var type = item.get('type'),
          options = {parent: this};

      if (type === 'timeline') {
        options.collection = this.model.get('events');
      } else {
        throw NS.projectException('Section type "' + type + '" unrecognized.', this.model.toJSON());
      }

      return options;
    },
    getItemView: function(item) {
      var type = item.get('type'),
          project = this.model,
          SectionView;

      if (type === 'timeline') {
        SectionView = NS.TimelineView;
      } else {
        throw NS.projectException('Section type "' + type + '" unrecognized.', this.model.toJSON());
      }

      return SectionView;
    }
  });

  // Sections =================================================================
  NS.SectionMixin = {
    id: function() {
      return this.model.get('slug');
    }
  };

  NS.EventView = Backbone.Marionette.ItemView.extend({
    template: '#event-tpl',
    tagName: 'li',
    className: 'event'
  });

  NS.TimelineView = Backbone.Marionette.CompositeView.extend({
    template: '#timeline-section-tpl',
    tagName: 'section',
    className: 'project-timeline',
    id: NS.SectionMixin.id,

    itemView: NS.EventView,
    itemViewContainer: '.event-list'
  });

}(Planbox, jQuery));