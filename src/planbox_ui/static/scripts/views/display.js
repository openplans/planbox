/*globals Backbone jQuery Handlebars Modernizr _ Pen */

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

    // Handlebars support for Marionette
  Backbone.Marionette.TemplateCache.prototype.compileTemplate = function(rawTemplate) {
    return Handlebars.compile(rawTemplate);
  };

  // Sections =================================================================
  NS.AttachmentView = Backbone.Marionette.Layout.extend({
    template: '#attachment-tpl',
    tagName: 'li',
    className: 'attachment',
  });

  NS.AttachmentListView = Backbone.Marionette.CompositeView.extend({
    template: '#attachments-section-tpl',
    itemView: NS.AttachmentView,
    itemViewContainer: '.attachment-list'
  });

  NS.EventView = Backbone.Marionette.Layout.extend({
    template: '#event-tpl',
    tagName: 'li',
    className: 'event',
    regions: {
      attachmentList: '.attachments-region'
    },
    onRender: function() {
      this.attachmentList.show(new NS.AttachmentListView({
        model: this.model,
        collection: this.model.get('attachments')
      }));
    }
  });

  NS.TimelineSectionView = Backbone.Marionette.CompositeView.extend({
    template: '#timeline-section-tpl',
    tagName: 'section',
    className: 'project-timeline',

    itemView: NS.EventView,
    itemViewContainer: '.event-list'
  });

  NS.TextSectionView = Backbone.Marionette.ItemView.extend({
    template: '#text-section-tpl',
    tagName: 'section',
    className: 'project-text'
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

    itemView: NS.FaqView,
    itemViewContainer: '.faq-list'
  });


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

  NS.ProjectSectionListView = NS.BaseProjectSectionListView.extend({
    sectionViews: {
      'timeline': NS.TimelineSectionView,
      'text': NS.TextSectionView,
      'faqs': NS.FaqsSectionView
    }
  });

  NS.ProjectView = NS.BaseProjectView.extend({
    template: '#project-tpl',
    sectionListView: NS.ProjectSectionListView
  });


}(Planbox, jQuery));