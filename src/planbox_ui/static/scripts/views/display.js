/*globals Backbone jQuery Handlebars Modernizr _ Pen Shareabouts*/

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

    ui: {
      link: '.attachment-link',
      title: '.attachment-title'
    },
    events: {
      'click @ui.link': 'onLinkClick'
    },

    onLinkClick: function(evt) {
      var label = this.ui.title.text();
      NS.Utils.log('USER', 'project-display', 'attachment-click', label);
    }
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
    id: NS.SectionMixin.id,
    className: 'project-section-timeline',

    itemView: NS.EventView,
    itemViewContainer: '.event-list'
  });

  NS.TextSectionView = Backbone.Marionette.ItemView.extend({
    template: '#text-section-tpl',
    tagName: 'section',
    id: NS.SectionMixin.id,
    className: 'project-section-text'
  });

  NS.RawHtmlSectionView = Backbone.Marionette.ItemView.extend({
    template: '#raw-section-tpl',
    tagName: 'section',
    id: NS.SectionMixin.id,
    className: 'project-section-raw'
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

      var label = this.ui.question.text(),
          state = this.ui.question.hasClass('is-selected') ? 'open' : 'close';
      NS.Utils.log('USER', 'project-display', 'faq-click-' + state, label);
    }
  });

  NS.FaqsSectionView = Backbone.Marionette.CompositeView.extend({
    template: '#faqs-section-tpl',
    tagName: 'section',
    id: NS.SectionMixin.id,
    className: 'project-section-faqs',

    itemView: NS.FaqView,
    itemViewContainer: '.faq-list'
  });

  NS.ShareaboutsSectionView = Backbone.Marionette.ItemView.extend({
    template: '#shareabouts-section-tpl',
    tagName: 'section',
    id: NS.SectionMixin.id,
    className: 'project-section-shareabouts',
    ui: {
      shareabouts: '.project-shareabouts'
    },
    onShow: function() {
      var details = this.model.get('details');

      new Shareabouts.Map({
        el: this.ui.shareabouts,
        map: details.map,
        layers: details.layers,
        placeStyles: [
          {
            condition: 'true',
            icon: {
              iconUrl: NS.bootstrapped.staticUrl + 'images/markers/dot-blue.png',
              iconSize: [18, 18],
              iconAnchor: [9, 9]
            },
            focusIcon: {
              iconUrl: NS.bootstrapped.staticUrl + 'images/markers/marker-blue.png',
              shadowUrl: NS.bootstrapped.staticUrl + 'images/markers/marker-shadow.png',
              iconSize: [25, 41],
              shadowSize: [41, 41],
              iconAnchor: [12, 41]
            }
          },
        ],
        datasetUrl: details.dataset_url + '/places',
        templates: Handlebars.templates
      });

    }
  });

  // View =====================================================================
  NS.ModalView = Backbone.Marionette.ItemView.extend({
    template: '#modal-tpl',
    className: 'reveal-modal medium',
    attributes: {
      'data-reveal': ''
    },
    onShow: function() {
      // This is gross. We should encourage Foundation to fix this.
      this.$el.foundation().foundation('reveal', 'open');
    },
    onClose: function() {
      // This is gross. We should encourage Foundation to fix this.
      this.$el.foundation().foundation('reveal', 'close');
    }
  });

  NS.ProjectSectionListView = NS.BaseProjectSectionListView.extend({
    sectionViews: {
      'timeline': NS.TimelineSectionView,
      'text': NS.TextSectionView,
      'faqs': NS.FaqsSectionView,
      'shareabouts': NS.ShareaboutsSectionView,
      'raw': NS.RawHtmlSectionView
    }
  });

  NS.ProjectView = NS.BaseProjectView.extend({
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
    onDomRefresh: function() {
      // The dom changed. Make sure that any Foundation plugins are init'd.
      $(document).foundation();

      var self = this,
          debouncedScrollHandler = _.debounce(function(evt) {
            var offsets = self.offsets(),
                item, i;

            for(i=0; i<offsets.length; i++){
              item = offsets[i];
              if (item.viewport_offset >= item.top_offset) {
                NS.Utils.log('ROUTE', item.arrival.attr('data-magellan-destination'));
                return true;
              }
            }
          }, 250);

      // Only bind the scroll event if a magellan widget exists. They don't if
      // there are not enough items to warrant it.
      if ($('[data-magellan-expedition]').length) {
        $(window).off('scroll').on('scroll', debouncedScrollHandler);
      }
    },
    onClickMenuItem: function(evt) {
      var $target = $(evt.currentTarget),
          label = $target.attr('data-magellan-arrival');
      NS.Utils.log('USER', 'project-display', 'menu-click', label);
    },
    onClickHighlight: function(evt) {
      var $target = $(evt.currentTarget),
          label = $target.attr('data-highlight-type');
      NS.Utils.log('USER', 'project-display', 'highlight-click', label);
    },
    offsets: function() {
      var self = this,
          expedition = $('[data-magellan-expedition]'),
          destination_threshold = expedition.data('magellanExpeditionInit').destination_threshold,
          viewport_offset = $(window).scrollTop();

      return $('[data-magellan-destination]').map(function(idx, el) {
        var dest = $(el),
            top_offset = dest.offset().top - destination_threshold - expedition.outerHeight();
        return {
          destination : dest,
          arrival : $(this),
          top_offset : top_offset,
          viewport_offset : viewport_offset
        };
      }).sort(function(a, b) {
        if (a.top_offset < b.top_offset) {return 1;}
        if (a.top_offset > b.top_offset) {return -1;}
        return 0;
      });
    }
  });


}(Planbox, jQuery));