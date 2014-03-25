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

    getItemViewOptions: function(section, index) {
      var type = section.get('type'),
          options = {parent: this};

      if (type === 'timeline') {
        options.collection = this.model.get('events');
      }

      if (type === 'faqs') {
        var faqCollection = new NS.FaqCollection(section.get('details'));
        options.collection = faqCollection;
      }

      return options;
    },
    getItemView: function(section) {
      var type = section.get('type'),
          project = this.model,
          SectionView;

      switch (type) {
      case 'timeline':
        SectionView = NS.TimelineSectionView;
        break;

      case 'text':
        SectionView = NS.TextSectionView;
        break;

      case 'faqs':
        SectionView = NS.FaqsSectionView;
        break;

      default:
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

  NS.TimelineSectionView = Backbone.Marionette.CompositeView.extend({
    template: '#timeline-section-tpl',
    tagName: 'section',
    className: 'project-timeline',
    id: NS.SectionMixin.id,

    itemView: NS.EventView,
    itemViewContainer: '.event-list'
  });

  NS.TextSectionView = Backbone.Marionette.ItemView.extend({
    template: '#text-section-tpl',
    tagName: 'section',
    className: 'project-text',
    id: NS.SectionMixin.id
  });

  NS.FaqView = Backbone.Marionette.ItemView.extend({
    template: '#faq-tpl',
    tagName: 'div',
    className: 'faq',
    ui: {
      'question': 'dt'
    },
    events: {
      'click @ui.question': 'handleQuestionClick'
    },

    handleQuestionClick: function(evt) {
      evt.preventDefault();
      this.ui.question.toggleClass('is-selected');
    }
  });
  
  NS.FaqsSectionView = Backbone.Marionette.CompositeView.extend({
    template: '#faqs-section-tpl',
    tagName: 'section',
    className: 'project-faqs',
    id: NS.SectionMixin.id,

    itemView: NS.FaqView,
    itemViewContainer: '.faq-list'
  });

}(Planbox, jQuery));