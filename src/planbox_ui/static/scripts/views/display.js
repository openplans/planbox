/*globals Backbone jQuery Handlebars Modernizr _ Pen Shareabouts*/

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

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

  NS.ImageSectionView = Backbone.Marionette.ItemView.extend({
    template: '#image-section-tpl',
    tagName: 'section',
    id: NS.SectionMixin.id,
    className: 'project-section-image'
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
      var details = this.model.get('details'),
          compiledTemplates = details.templates,
          sa;

      // Compile string templates if necessary
      _.each(details.templates, function(tpl, key) {
        if(_.isString(tpl)) {
          compiledTemplates[key] = Handlebars.compile(tpl);
        }
      });

      sa = new Shareabouts.Map({
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
        templates: _.extend({}, Handlebars.templates, compiledTemplates)
      });

      Shareabouts.auth = new Shareabouts.Auth({
        apiRoot: 'http://data.shareabouts.org/api/v2/',
        successPage: '/shareabouts/success',
        errorPage: '/shareabouts/error'
      });

      $(Shareabouts.auth).on('authsuccess', function(evt, data) {
        sa.setUser(data);
      });

      Shareabouts.auth.initUser();
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
      'image': NS.ImageSectionView,
      'faqs': NS.FaqsSectionView,
      'shareabouts': NS.ShareaboutsSectionView,
      'raw': NS.RawHtmlSectionView
    }
  });

  NS.ProjectView = Backbone.Marionette.Layout.extend({
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
      sectionList: '#section-list'
    },
    onShow: function() {
      // After the project is in the DOM, show the project sections
      this.sectionList.show(new this.sectionListView({
        model: this.model,
        collection: this.collection,
        parent: this
      }));
    },
    onDomRefresh: function() {
      var self = this,
          debouncedScrollHandler = _.debounce(function(evt) {
            var offsets = self.offsets(),
                item, i, dest, path;

            for(i=0; i<offsets.length; i++){
              item = offsets[i];
              if (item.viewport_offset >= item.top_offset) {
                dest = item.arrival.attr('data-magellan-destination');
                path = NS.Utils.rootPathJoin(dest);

                if (path !== self.currentPath) {
                  self.currentPath = path;
                  NS.Utils.log('ROUTE', path);
                }
                return true;
              }
            }
          }, 500);

      // Only bind the scroll event if a magellan widget exists. They don't if
      // there are not enough items to warrant it.
      if ($('[data-magellan-expedition]').length) {
        $(window).off('scroll', debouncedScrollHandler).on('scroll', debouncedScrollHandler);

        $(document).on('click', '[data-magellan-link]', function(evt) {
          // See line 3147 in foundation.js. This should be an accessible function.
          // TODO: Pull request to make this public.
          evt.preventDefault();
          var expedition = $('[data-magellan-expedition]'),
              settings = expedition.data('magellan-expedition-init'),
              hash = $(this).attr('href').split('#').join(''),
              target = $("a[name='"+hash+"']");

          if (target.length === 0) {
            target = $('#'+hash);
          }

          // Account for expedition height if fixed position
          var scroll_top = target.offset().top;
          scroll_top = scroll_top - expedition.outerHeight();

          $('html, body').stop().animate({
            'scrollTop': scroll_top
          }, 700, 'swing', function () {
            if(history.pushState) {
              history.pushState(null, null, '#'+hash);
            }
            else {
              location.hash = '#'+hash;
            }
          });
        });
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
          settings = expedition.data('magellan-expedition-init') || {
            destination_threshold: 20
          },
          destination_threshold = settings.destination_threshold,
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