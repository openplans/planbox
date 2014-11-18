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
    ui: {
      showEventDetailsBtn: '.show-event-details',
      eventDetails: '.event-details'
    },
    events: {
      'click @ui.showEventDetailsBtn': 'handleShowEventDetails',
    },
    onRender: function() {
      this.attachmentList.show(new NS.AttachmentListView({
        model: this.model,
        collection: this.model.get('attachments')
      }));

      var nowTime = $.now();
      var eventTime = this.$('.event-datetime').attr('data-datetime');

      // Associate with a past or future event
      eventTime = new Date(eventTime);
      if ( eventTime < nowTime ) {
        this.$el.addClass('past-event');
      } else {
        this.$el.addClass('future-event');
      }

      // Store the tags on the element
      var tags = this.model.get('details').tags;
      $.data(this.el, 'tags', tags);
    },
    handleShowEventDetails: function(evt) {
      evt.preventDefault();
      this.ui.eventDetails.toggleClass('hide');
    }
  });

  NS.TimelineSectionView = Backbone.Marionette.CompositeView.extend({
    template: '#timeline-section-tpl',
    tagName: 'section',
    id: NS.SectionMixin.id,
    className: 'project-section-timeline',

    itemView: NS.EventView,
    itemViewContainer: '.event-list',

    ui: {
      showPastEventsBtn: '.show-more-past-events',
      showFutureEventsBtn: '.show-more-future-events',
      tagBtn: '.tag-btn'
    },
    events: {
      'click @ui.showPastEventsBtn': 'handleShowPastEventsBtn',
      'click @ui.showFutureEventsBtn': 'handleShowFutureEventsBtn',
      'click @ui.tagBtn': 'handleClickTagBtn'
    },
    onRender: function() {
      var pastCount = this.$('.past-event').length;
      var futureCount = this.$('.future-event').length;

      if ( pastCount ) {
        this.$('.past-event').addClass('hide');
        this.$('.show-more-past-events').removeClass('hide');
      }

      if ( futureCount > 4 ) {
        this.$('.future-event').slice(4).addClass('hide');
        this.$('.show-more-future-events').removeClass('hide');
      }
    },
    showPastEvents: function() {
      $('li.past-event').removeClass('hide');
      $('.show-more-past-events').addClass('hide');
    },
    showFutureEvents: function() {
      $('li.future-event').removeClass('hide');
      $('.show-more-future-events').addClass('hide');
    },
    showEventsBySelectedTags: function() {
      var selectedTags = this.selectedTags;

      this.$('li.event').removeClass('hide');
      if (selectedTags.length === 0) { return; }

      this.$('li.event').each(function(i, li) {
        var tags = $.data(li, 'tags') || [];
        if (_.intersection(selectedTags, tags).length === 0) {
          $(li).addClass('hide');
        }
      });
    },
    handleShowPastEventsBtn: function(evt) {
      evt.preventDefault();
      this.showPastEvents();
    },
    handleShowFutureEventsBtn: function(evt) {
      evt.preventDefault();
      this.showFutureEvents();
    },
    handleClickTagBtn: function(evt) {
      evt.preventDefault();
      var $tag = $(evt.currentTarget),
          tag = $tag.text();
      this.selectedTags = this.selectedTags || [];
      if (_.contains(this.selectedTags, tag)) {
        this.deselectTag(tag, $tag);
      } else {
        this.selectTag(tag, $tag);
      }
    },
    selectTag: function(text, $el) {
      var index;

      if ($el) { $el.addClass('selected'); }
      index = _.sortedIndex(this.selectedTags, text);
      this.selectedTags.splice(index, 0, text);

      this.showPastEvents();
      this.showFutureEvents();
      this.showEventsBySelectedTags();
    },
    deselectTag: function(text, $el) {
      var index;

      if ($el) { $el.removeClass('selected'); }
      index = _.indexOf(this.selectedTags, text);
      this.selectedTags.splice(index, 1);

      this.showPastEvents();
      this.showFutureEvents();
      this.showEventsBySelectedTags();
    },
    serializeData: function() {
      var data = NS.TimelineSectionView.__super__.serializeData.call(this),
          alltags = [], tags;

      this.model.get('project').get('events').each(function(eventModel) {
        tags = (eventModel.get('details') || {}).tags || [];
        alltags = alltags.concat(tags);
      });
      data.tags = _.uniq(alltags.sort(), true);

      return data;
    }
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
    getShareaboutsEl: function() {
      return this.ui.shareabouts;
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
        el: this.getShareaboutsEl(),
        map: details.map,
        layers: details.layers,
        placeStyles: (details.place_styles || []).concat([
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
        ]),
        datasetUrl: details.dataset_url + '/places',
        templates: _.extend({}, Handlebars.templates, compiledTemplates)
      });

      Shareabouts.auth = new Shareabouts.Auth({
        apiRoot: 'https://data.shareabouts.org/api/v2/',
        successPage: '/shareabouts/success',
        errorPage: '/shareabouts/error'
      });

      $(Shareabouts.auth).on('authsuccess', function(evt, data) {
        sa.setUser(data);

        // So the auth dropdown aligns properly
        $(document).foundation({'dropdown': {}});
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
        sectionList: '#section-list'
      },
      onShow: function() {
        // After the project is in the DOM, show the project sections
        this.sectionList.show(new this.sectionListView({
          model: this.model,
          collection: this.collection,
          parent: this
        }));
      }
    })
  );


}(Planbox, jQuery));