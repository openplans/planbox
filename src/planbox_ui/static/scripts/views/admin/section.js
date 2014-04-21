/*globals Backbone jQuery Handlebars Modernizr _ Pen FileAPI chrono L */

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

  // Sections =================================================================
  NS.AttachmentAdminView = NS.SortableListItemAdminView.extend(
    _.extend({}, NS.ContentEditableMixin, {
      template: '#attachment-admin-tpl',
      tagName: 'li',
      className: 'attachment',
      ui: {
        editables: '[contenteditable]',
        richEditables: '.attachment-description',
        deleteBtn: '.delete-attachment-btn'
      },
      events: {
        'blur @ui.editables': 'handleEditableBlur',
        'click @ui.deleteBtn': 'handleDeleteClick'
      }
    })
  );

  NS.AttachmentListAdminView = NS.SortableListAdminView.extend(
    _.extend({}, NS.ContentEditableMixin, {
      template: '#attachments-section-admin-tpl',
      className: '',
      itemView: NS.AttachmentAdminView,
      itemViewContainer: '.attachment-list',

      ui: {
        editables: '[contenteditable]:not(.event [contenteditable])',
        dropZones: '.event-attachment-dnd',
        itemList: '.attachment-list'
      },

      events: {
        'blur @ui.editables': 'handleEditableBlur'
      },
      initDropZones: function() {
        var view = this;

        this.ui.dropZones.fileUpload({
          url: 'https://' + NS.Data.s3UploadBucket + '.s3.amazonaws.com/',
          data: _.clone(NS.Data.s3UploadData),
          thumbnail: {
            width: 100,
            height: 100
          },
          dndOver: function(isOver) {
            $(this).toggleClass('file-dragging', isOver);
          },
          dndDrop: function(files) {
            var $this = $(this);
            $this.removeClass('file-dragging');
            $this.data('fileUpload').upload(files);
          },
          validate: function(files) {
            // Files less than 5mb (in bytes)
            if (files[0].size > 5242880) {
              NS.showErrorModal(
                'Unable to save that file.',
                'This file is too large.',
                'This file is bigger than the file size limit of 5mb. Upload ' +
                'a smaller file and try again.'
              );

              // Return false to prevent the upload from starting
              return false;
            }
            return true;
          },
          start: function(xhr, options) {
            // When the upload starts
            var $container = $(this);

            // Apply the uploading class.
            $container.addClass('file-uploading');
          },
          complete: function(err, xhr, options) {
            // When the upload is complete
            var $container = $(this),
                hasThumbnail = !!options.files.file[1],
                fileUrl = window.encodeURI(
                  options.url + options.data.key.replace('${filename}',
                  options.files.file[0].name)
                ),
                thumbnailUrl = hasThumbnail ? window.encodeURI(
                  options.url + options.data.key.replace('${filename}',
                  options.files.file[1].name)
                ) : null,
                newModel;

            // Remove the uploading class.
            $container.removeClass('file-uploading');

            if (err) {
              NS.showErrorModal(
                'Unable to save that file.',
                'We were unable to save your image.',
                'Sorry about that. Please save your changes, reload the page, ' +
                'and try again. Please email us at ' + NS.Data.contactEmail + ' ' +
                'if you have any more trouble.'
              );

              return;
            }

            // On success, create a new attachment model on the event.
            newModel = view.collection.add({
              type: options.files.file[0].type,
              thumbnail_url: thumbnailUrl,
              url: fileUrl
            });
          }
        });
      },
      onRender: function() {
        // We need to do this since SortableListAdminView and ContentEditableMixin
        // both override onRender.

        // ContentEditableMixin
        this.initRichEditables();
        // SortableListAdminView
        this.initSortableItemList();

        this.initDropZones();
      }
    })
  );

  NS.EventAdminView = NS.SortableListItemAdminView.extend(
    _.extend({}, NS.ContentEditableMixin, {
      template: '#event-admin-tpl',
      tagName: 'li',
      className: 'event',
      ui: {
        editables: '[contenteditable]:not(.attachment-list [contenteditable])',
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

        this.attachmentList.show(new NS.AttachmentListAdminView({
          parent: this.options.parent,
          model: this.model,
          collection: this.model.get('attachments')
        }));
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

  NS.TimelineSectionAdminView = NS.SortableListAdminView.extend(
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
        // We need to do this since SortableListAdminView and ContentEditableMixin
        // both override onRender.

        // ContentEditableMixin
        this.initRichEditables();
        // SortableListAdminView
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

  NS.ShareaboutsSectionAdminView = Backbone.Marionette.ItemView.extend(
    _.extend({}, NS.ContentEditableMixin, NS.SectionAdminMixin, {
      template: '#shareabouts-section-admin-tpl',
      tagName: 'section',

      ui: {
        editables: '[contenteditable]',
        richEditables: '.project-shareabouts-description',
        activeToggle: '[name="active"]',
        map: '.map'
      },
      events: {
        'blur @ui.editables': 'handleEditableBlur',
        'change @ui.activeToggle': 'handleActivationChange'
      },

      onShow: function() {
        var options = this.model.get('details'),
            i, layerOptions;

        this.map = L.map(this.ui.map.get(0), options.map);
        for (i = 0; i < options.layers.length; ++i) {
          layerOptions = options.layers[i];
          L.tileLayer(layerOptions.url, layerOptions).addTo(this.map);
        }

        this.map.on('moveend', _.bind(this.handleMapMoveEnd, this));
      },

      handleMapMoveEnd: function() {
        var center = this.map.getCenter(),
            zoom = this.map.getZoom(),
            mapOptions = _.defaults({
                center: [center.lat, center.lng],
                zoom: zoom
              },
              this.model.get('details').map
            );

        this.model.set('map', mapOptions);
      },
    })
  );

  NS.FaqAdminView = NS.SortableListItemAdminView.extend(
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

  NS.FaqsSectionAdminView = NS.SortableListAdminView.extend(
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