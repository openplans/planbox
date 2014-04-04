/*globals Backbone jQuery Handlebars Modernizr _ Pen FileAPI chrono */

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

  // Sections =================================================================
  NS.EventAdminView = NS.SectionListItemAdminView.extend(
    _.extend({}, NS.ContentEditableMixin, {
      template: '#event-admin-tpl',
      tagName: 'li',
      className: 'event',
      ui: {
        editables: '[contenteditable]',
        richEditables: '.event-description',
        deleteBtn: '.delete-event-btn',
        datetimeEditable: '.event-datetime',
        datetimeInput: '.event-datetime-picker',
        calendarIcon: '.calendar-icon'
      },
      events: {
        'blur @ui.editables': 'handleEditableBlur',
        'click @ui.deleteBtn': 'handleDeleteClick',
        'blur @ui.datetimeEditable': 'handleDatetimeChange',
        'input @ui.datetimeEditable': 'handleDatetimeChange',
        'click @ui.calendarIcon': 'handleCalendarIconClick'
      },
      setEventDate: function(val) {
        var results = chrono.parse(val, new Date()),
            result, start, end;

        this.model.set('datetime_label', val || '');
        if (results.length > 0) {
          result = results[0];

          this.model.set({
            start_datetime: result.startDate || '',
            end_datetime: result.endDate || ''
          });

          return result.startDate;
        } else  {
          this.model.set({
            start_datetime: '',
            end_datetime: ''
          });
        }
      },
      handleCalendarIconClick: function(evt) {
        evt.preventDefault();
        this.ui.datetimeInput.pickadate('open');

        // Stop further propagation, because the picker widget is rigged to
        // close if you click anywhere besides its attached input.
        evt.stopPropagation();
      },
      handleDatetimeChange: function(evt) {
        evt.preventDefault();

        var $target = $(evt.currentTarget),
            val = $target.text(),
            picker = this.ui.datetimeInput.pickadate('picker'),
            newDate;

        this.setEventDate(val);

        newDate = this.model.get('start_datetime');
        if (newDate) {
          picker.set('select', newDate, {muted: true});
        }
      },
      handleDatetimePickerChange: function(evt) {
        var $target = this.ui.datetimeInput,
            val = $target.val();

        this.setEventDate(val);
        this.ui.datetimeEditable.html(val);
      },
      onRender: function() {
        // ContentEditableMixin
        this.initRichEditables();
        // Init the date picker
        this.initDatepicker();
      },
      initDatepicker: function() {
        var picker;

        this.ui.datetimeInput.pickadate({
          format: 'mmmm d, yyyy',
          formatSubmit: 'yyyy-mm-dd',
          editable: true,
          selectYears: true,
          selectMonths: true
        });

        picker = this.ui.datetimeInput.pickadate('picker');
        picker.on('set', _.bind(this.handleDatetimePickerChange, this));
      }
    })
  );

  NS.TimelineSectionAdminView = NS.SectionListAdminView.extend(
    _.extend({}, NS.ContentEditableMixin, {
      template: '#timeline-section-admin-tpl',
      tagName: 'section',
      className: 'project-timeline',

      itemView: NS.EventAdminView,
      itemViewContainer: '.event-list',

      ui: {
        editables: '[contenteditable]:not(.event [contenteditable])',
        itemList: '.event-list',
        newItemFocus: '.event-title:last',
        addBtn: '.add-event-btn'
      },
      events: {
        'click @ui.addBtn': 'handleAddClick',
        'blur @ui.editables': 'handleEditableBlur'
      },
      onRender: function() {
        // We need to do this since SectionListAdminView and ContentEditableMixin
        // both override onRender.

        // ContentEditableMixin
        this.initRichEditables();
        // SectionListAdminView
        this.initSortableItemList();
      }
    })
  );

  NS.TextSectionAdminView = Backbone.Marionette.ItemView.extend(
    _.extend({}, NS.ContentEditableMixin, {
      template: '#text-section-admin-tpl',
      tagName: 'section',
      className: 'project-text',

      ui: {
        editables: '[contenteditable]',
        richEditables: '.project-text-content'
      },
      events: {
        'blur @ui.editables': 'handleEditableBlur'
      }
    })
  );

  NS.FaqAdminView = NS.SectionListItemAdminView.extend(
    _.extend({}, NS.ContentEditableMixin, {
      template: '#faq-admin-tpl',
      tagName: 'div',
      className: 'faq',

      ui: {
        editables: '[contenteditable]',
        richEditables: '.faq-answer',
        deleteBtn: '.delete-faq-btn'
      },
      events: {
        'blur @ui.editables': 'handleEditableBlur',
        'click @ui.deleteBtn': 'handleDeleteClick'
      }
    })
  );

  NS.FaqsSectionAdminView = NS.SectionListAdminView.extend(
    _.extend({}, NS.ContentEditableMixin, {
      template: '#faqs-section-admin-tpl',
      tagName: 'section',
      className: 'project-faqs',

      itemView: NS.FaqAdminView,
      itemViewContainer: '.faq-list',

      ui: {
        editables: '[contenteditable]:not(.faq [contenteditable])',
        itemList: '.faq-list',
        newItemFocus: '.faq-question:last',
        addBtn: '.add-faq-btn'
      },
      events: {
        'click @ui.addBtn': 'handleAddClick',
        'blur @ui.editables': 'handleEditableBlur'
      },
      onRender: function() {
        // We need to do this since SectionListAdminView and ContentEditableMixin
        // both override onRender.

        // ContentEditableMixin
        this.initRichEditables();
        // SectionListAdminView
        this.initSortableItemList();
      }
    })
  );
}(Planbox, jQuery));