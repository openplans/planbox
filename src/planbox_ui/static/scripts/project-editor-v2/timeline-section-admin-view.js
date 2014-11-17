/*globals Backbone jQuery Handlebars Modernizr _ Pen FileAPI chrono L */

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

  NS.EventAdminView = NS.SortableListItemAdminView.extend(
    _.extend({}, NS.ContentEditableMixin, {
      template: '#event-admin-tpl',
      tagName: 'li',
      className: 'event',
      ui: {
        editables: '[data-attr]:not(.attachment-list [data-attr])',
        richEditables: '.event-description',
        deleteBtn: '.delete-event',
        datetimeEditable: '.event-datetime',
        datetimeInput: '.event-datetime-picker',
        calendarIcon: '.calendar-icon',
        tagsChooser: '.chosen-select',
        tagsInput: '.chosen-container input[type="text"]'
      },
      events: {
        'blur @ui.editables': 'handleEditableBlur',
        'input @ui.editables': 'handleEditableBlur',
        'change @ui.tagsChooser': 'handleEditableBlur',
        'chosen:showing_dropdown @ui.tagsChooser': 'handleTagsDropDown',
        'focus @ui.tagsInput': 'handleTagsInputFocus',
        'blur @ui.tagsInput': 'handleTagsInputBlur',
        'click @ui.deleteBtn': 'handleDeleteClick',
        'blur @ui.datetimeEditable': 'handleDatetimeChange',
        'input @ui.datetimeEditable': 'handleDatetimeChange',
        'click @ui.calendarIcon': 'handleCalendarIconClick'
      },
      regions: {
        attachmentList: '.attachments-region'
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
            val = $target.is('[contenteditable]') ? $target.text() : $target.val(),
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

        // Backwards compatible... deprecated.
        if (this.ui.datetimeEditable.is('[contenteditable]')) {
          this.ui.datetimeEditable.html(val);
        } else {
          this.ui.datetimeEditable.val(val);
        }
      },
      handleTagsDropDown: function() {
        // If we're already focused on the tags field, we can assume the update
        // has already been done.
        if (!this.alreadyInTagsField) {
          this.updateTagChoices();
        }
      },
      handleTagsInputFocus: function() {
        var self = this;
        _.delay(function() { self.alreadyInTagsField = true; }, 50);
      },
      handleTagsInputBlur: function() {
        this.alreadyInTagsField = false;
      },
      onRender: function() {
        // ContentEditableMixin
        this.initRichEditables();
        // Init the date picker
        this.initDatepicker();
        // Init the chosen widget for tags
        this.initTagsChooser();

        this.attachmentList.show(new NS.AttachmentListAdminView({
          parent: this.options.parent,
          model: this.model,
          collection: this.model.get('attachments')
        }));

        var chooser = this.ui.tagsChooser;
        chooser.chosen({
          width: '100%',
          create_option: true,
          create_option_text: 'Add new tag',
          no_results_text: 'No tags match',
          multiple_text: 'Select some tags'
        });
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
      },
      initTagsChooser: function() {
        this.updateTagChoices();
      },
      updateTagChoices: function() {
        // Add all the tags to the tag chooser.
        var events = this.model.collection,
            chooser = this.ui.tagsChooser,
            alltags = [], tags, newtags,
            currentVal = this.ui.tagsInput.val();

        chooser.find('option').each(function(i, option) {
          alltags.push(option.innerHTML);
        });

        events.each(function(model) {
          tags = (model.get('details') || {}).tags || [];
          newtags = _.difference(tags, alltags);
          alltags = alltags.concat(newtags);
          _.map(newtags, function(tag) {
            chooser.append('<option>' + tag + '</option>');
          });
        });

        chooser.html(NS.Utils.sortByInnerHTML(chooser.children('option')));

        chooser.trigger('chosen:updated');
        this.ui.tagsInput.val(currentVal);
      }
    })
  );

  NS.TimelineSectionAdminView = NS.SortableListAdminView.extend(
    _.extend({}, NS.ContentEditableMixin, NS.SectionAdminMixin, {
      template: '#timeline-section-admin-tpl',
      tagName: 'section',
      id: NS.SectionMixin.id,

      itemView: NS.EventAdminView,
      itemViewContainer: '.event-list',

      ui: {
        editables: '[data-attr]:not(.event [data-attr])',
        itemList: '.event-list',
        newItemFocus: '.event-title:last',
        addBtn: '.add-event-btn',
        deleteSection: '.delete-section'
      },
      events: {
        'click @ui.addBtn': 'handleAddClick',
        'blur @ui.editables': 'handleEditableBlur',
        'input @ui.editables': 'handleEditableBlur',
        'change @ui.activeToggle': 'handleActivationChange',
        'click @ui.deleteSection': 'handleDeleteSectionClick'
      },
      onRender: function() {
        // We need to do this since SortableListAdminView and ContentEditableMixin
        // both override onRender.

        // ContentEditableMixin
        this.initRichEditables();
        // SortableListAdminView
        this.initSortableItemList();
      }
    })
  );

}(Planbox, jQuery));