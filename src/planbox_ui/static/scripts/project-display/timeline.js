var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

  NS.TimelineController = function() {};
  NS.TimelineController.prototype = {
    showPastEvents: function($timeline) {
      $timeline.find('li.past-event').removeClass('hide');
      $timeline.find('.show-more-past-events').addClass('hide');
    },
    showFutureEvents: function($timeline) {
      $timeline.find('li.future-event').removeClass('hide');
      $timeline.find('.show-more-future-events').addClass('hide');
    },
    showEventsBySelectedTags: function($timeline) {
      var selectedTags = $timeline.data('selectedTags');

      $timeline.find('li.event').removeClass('hide');
      if (selectedTags.length === 0) { return; }

      $timeline.find('li.event').each(function(i, li) {
        var tags = $.data(li, 'tags') || [];
        if (_.intersection(selectedTags, tags).length === 0) {
          $(li).addClass('hide');
        }
      });
    },
    handleShowPastEventsBtn: function(evt) {
      evt.preventDefault();
      var $btn = $(evt.currentTarget),
          $timeline = $btn.parents('.project-section-timeline');
      this.showPastEvents($timeline);
    },
    handleShowFutureEventsBtn: function(evt) {
      evt.preventDefault();
      var $btn = $(evt.currentTarget),
          $timeline = $btn.parents('.project-section-timeline');
      this.showFutureEvents($timeline);
    },
    handleClickTagBtn: function(evt) {
      evt.preventDefault();
      var $tag = $(evt.currentTarget),
          tag = $tag.text(),
          $timeline = $tag.parents('.project-section-timeline'),
          selectedTags = $timeline.data('selectedTags');

      $timeline.data('selectedTags', selectedTags || []);
      selectedTags = $timeline.data('selectedTags');

      if (_.contains(selectedTags, tag)) {
        this.deselectTag($timeline, tag, $tag);
      } else {
        this.selectTag($timeline, tag, $tag);
      }
    },
    selectTag: function($timeline, text, $el) {
      var index;

      // Only one tag at a time...
      $timeline.find('.tag-btn').removeClass('selected').addClass('tertiary');
      if ($el) { $el.addClass('selected').removeClass('tertiary'); }
      $timeline.data('selectedTags', [text]);

      this.showPastEvents($timeline);
      this.showFutureEvents($timeline);
      this.showEventsBySelectedTags($timeline);
    },
    deselectTag: function($timeline, text, $el) {
      var index,
          selectedTags = $timeline.data('selectedTags');

      if ($el) { $el.removeClass('selected').addClass('tertiary'); }
      index = _.indexOf(selectedTags, text);
      selectedTags.splice(index, 1);
      $timeline.data('selectedTags', selectedTags);

      this.showPastEvents($timeline);
      this.showFutureEvents($timeline);
      this.showEventsBySelectedTags($timeline);
    },
    handleShowEventDetails: function(evt) {
      evt.preventDefault();
      var $el = $(evt.currentTarget),
          $details = $el.parents('.event').find('.event-details');
      $details.toggleClass('hide');
    }
  };

  $(function() {
    var c = new NS.TimelineController();
    $(document).on('click', '#page .show-more-past-events', _.bind(c.handleShowPastEventsBtn, c));
    $(document).on('click', '#page .show-more-future-events', _.bind(c.handleShowFutureEventsBtn, c));
    $(document).on('click', '#page .tag-btn', _.bind(c.handleClickTagBtn, c));
    $(document).on('click', '#page .show-event-details', _.bind(c.handleShowEventDetails, c));
  });
}(Planbox, jQuery));