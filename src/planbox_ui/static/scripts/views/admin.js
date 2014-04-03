/*globals Backbone jQuery Handlebars Modernizr _ Pen FileAPI chrono */

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

  // Handlebars support for Marionette
  Backbone.Marionette.TemplateCache.prototype.compileTemplate = function(rawTemplate) {
    return Handlebars.compile(rawTemplate);
  };

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
        console.debug('clicked datepicker icon');

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
          console.debug('setting date in picker to', newDate);
          picker.set('select', newDate, {muted: true});
        }
      },
      handleDatetimePickerChange: function(evt) {
        var $target = this.ui.datetimeInput,
            val = $target.val();

        this.setEventDate(val);
        console.debug('date picker set to', val);
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


  // Admin ====================================================================

  NS.showErrorModal = function(title, subtitle, description) {
    NS.app.overlayRegion.show(new NS.ModalView({
      model: new Backbone.Model({
        title: title,
        subtitle: subtitle,
        description: description
      })
    }));
  };

  NS.showProjectSaveErrorModal = function(resp) {
    var statusCode = resp.status,
        respJSON = resp.responseJSON,
        title, subtitle, description;

    ////
    // TODO: We can have a single subtitle template and a description template
    //       for ajax errors, and then pass in a status code.
    ////
    title = 'Unable to save.';
    if (statusCode === 0) {
      // No network connectivity
      subtitle = Handlebars.templates['message-ajax-no-status-error-subtitle']({});
      description = Handlebars.templates['message-ajax-no-status-error-description']({});

    } else if (statusCode === 400) {
      // Bad request (missing title, at this point)
      subtitle = Handlebars.templates['message-ajax-bad-request-error-subtitle']({errors: respJSON});
      description = Handlebars.templates['message-ajax-bad-request-error-description']({errors: respJSON});

    } else if (statusCode === 401 || statusCode === 403 || statusCode === 404) {
      // Authentication error
      // NOTE: you get a 404 when trying to access a private project, which
      // could belong to the user but they're now signed out for some reason.
      subtitle = Handlebars.templates['message-ajax-authentication-error-subtitle']({});
      description = Handlebars.templates['message-ajax-authentication-error-description']({});

    } else if (statusCode >= 500) {
      // Unknown server error
      subtitle = Handlebars.templates['message-ajax-server-error-subtitle']({});
      description = Handlebars.templates['message-ajax-server-error-description']({});

    } else {
      // No idea
      subtitle = Handlebars.templates['message-ajax-unknown-error-subtitle']({});
      description = Handlebars.templates['message-ajax-unknown-error-description']({});
    }

    NS.showErrorModal(title, subtitle, description);
  };

  NS.ProjectAdminModalView = Backbone.Marionette.ItemView.extend({
    template: '#project-admin-modal-tpl',
    className: 'overlay',
    ui: {
      closeBtn: '.btn-close',
      publishBtn: '.btn-public',
      makePublicContent: '.make-public-content',
      shareContent: '.share-content'
    },
    events: {
      'click @ui.closeBtn': 'handleClose',
      'click @ui.publishBtn': 'handlePublish'
    },
    handleClose: function(evt) {
      evt.preventDefault();
      this.close();
    },
    handlePublish: function(evt) {
      var self = this;

      evt.preventDefault();

      this.model.save({public: true}, {
        // We are not interested in change events that come from the server,
        // and it causes the save button to enable after saving a new project
        silent: true,

        success: function() {
          self.ui.makePublicContent.addClass('is-hidden');
          self.ui.shareContent.removeClass('is-hidden');
        },
        error: function(model, resp) {
          NS.showProjectSaveErrorModal(resp);
        }
      });
    }
  });

  NS.ProjectSectionListAdminView = NS.BaseProjectSectionListView.extend({
    collectionEvents: {
      'change':  'dataChanged',
      'add':     'dataChanged',
      'remove':  'dataChanged',
      'reorder': 'dataChanged'
    },
    sectionViews: {
      'timeline': NS.TimelineSectionAdminView,
      'text': NS.TextSectionAdminView,
      'faqs': NS.FaqsSectionAdminView
    },
    dataChanged: function() {
      this.options.parent.dataChanged();
    }
  });

  NS.ProjectAdminView = NS.BaseProjectView.extend(
    _.extend({}, NS.ContentEditableMixin, {
      template: '#project-admin-tpl',
      ui: {
        editables: '[contenteditable]:not(#section-list [contenteditable])',
        richEditables: '.project-description',
        saveBtn: '.save-btn',
        statusSelector: '.status-selector',
        statusLabel: '.project-status',
        visibilityToggle: '[name=project-public]',
        userMenuLink: '.user-menu-link',
        userMenu: '.user-menu',
        editableNavMenuLinks: '.project-nav a[contenteditable]',
        publishBtn: '.btn-public',
        fileInputs: 'input[type="file"]',
        imageHolders: '.image-holder',
        imageDropZones: '.image-dnd',
        removeImageLinks: '.remove-img-btn',
        hightlightLinkSelector: '.highlight-link-selector',
        hightlightExternalLink: '.highlight-external-link'
      },
      events: {
        'blur @ui.editables': 'handleEditableBlur',
        'blur @ui.editableNavMenuLinks': 'handleEditableNavMenuLinkBlur',
        'change @ui.statusSelector': 'handleStatusChange',
        'change @ui.visibilityToggle': 'handleVisibilityChange',
        'click @ui.saveBtn': 'handleSave',
        'click @ui.userMenuLink': 'handleUserMenuClick',
        'click @ui.publishBtn': 'handlePublish',
        'change @ui.fileInputs': 'handleFileInputChange',
        'click @ui.removeImageLinks': 'handleRemoveImage',
        'change @ui.hightlightLinkSelector': 'handleHighlightLinkChange',
        'blur @ui.hightlightExternalLink': 'handleHighlightExternalLinkBlur'
      },
      modelEvents: {
        'change': 'dataChanged',
        'sync': 'onSync'
      },
      sectionListView: NS.ProjectSectionListAdminView,

      initialize: function() {
        // Hijack paste and strip out the formatting
        this.$el.on('paste', '[contenteditable]', function(evt) {
          evt.preventDefault();

          var pasted;
          // WebKit and FF
          if (evt && evt.originalEvent && evt.originalEvent.clipboardData &&
              evt.originalEvent.clipboardData.getData) {
            // This preserves line breaks, so don't worry about getting the HTML
            pasted = evt.originalEvent.clipboardData.getData('text/plain');
          } else if (window.clipboardData && window.clipboardData.getData)  {
            // IE
            pasted = window.clipboardData.getData('Text');
          }

          // Convert line breaks into <br> and paste
          NS.Utils.pasteHtmlAtCaret(pasted.replace(/\n/g, '<br>'));
        });

        // Do simple protection against accidental drops of images outside of
        // drop areas (http://stackoverflow.com/a/6756680).
        window.addEventListener('dragover', function(e) {
          e = e || event;
          e.preventDefault();
        }, false);
        window.addEventListener('drop', function(e) {
          e = e || event;
          e.preventDefault();
        }, false);

        this.initRegions();
      },

      onRender: function() {
        this.initRichEditables();
        this.initDropZones();
        this.showRegions();
      },

      // Prefetches an image file for a url to speed up load time
      // Takes an optional callback.
      prefetchImage: function(url, callback) {
        var img = new Image();   // Create new img element
        img.addEventListener('load', callback, false);
        img.src = url;
      },

      setImageOnContainer: function($el, url) {
        $el.addClass('has-image');
        if ($el.hasClass('image-as-background')) {
          $el.css('background-image', 'url("' + url + '")');
        } else {
          $el.find('img.image-target').attr('src', url);
        }
      },

      removeImageFromContainer: function($el) {
        if ($el.hasClass('image-as-background')) {
          $el.css('background-image', 'none');
        } else {
          $el.find('img.image-target').attr('src', '');
        }
        $el.removeClass('has-image');
      },

      // File Uploads
      previewImage: function(file, $el) {
        var self = this;

        // Display the image preview.
        FileAPI.Image(file).get(function(err, img) {
          var url;
          if (!err) {
            url = img.toDataURL(file.type); //FileAPI.toDataURL(img);
            self.setImageOnContainer($el, url);
          }
        });
      },

      handleRemoveImage: function(evt) {
        evt.preventDefault();
        var $target = $(evt.currentTarget),
            $imgContainer = $target.closest('.image-holder'),
            confirmMsg = $target.attr('data-confirm-msg'),
            attrName = $imgContainer.attr('data-attr');

        if (window.confirm(confirmMsg)) {
          this.removeImageFromContainer($imgContainer);
          this.model.set(attrName, '');
        }
      },

      uploadImage: function(files, $el) {
        var self = this,
            bucketUrl = 'https://' + NS.Data.s3UploadBucket + '.s3.amazonaws.com/',
            data = _.clone(NS.Data.s3UploadData),
            file = files[0],
            attrName = $el.attr('data-attr'),
            imageUrl = window.encodeURI(bucketUrl + data.key.replace('${filename}', file.name));

        // Make sure this is an image before continuing
        if (file.type.indexOf('image/') !== 0) {
          NS.showErrorModal(
            'Unable to save that file.',
            'This file doesn\'t seem to be an image file.',
            'Make sure the file you\'re trying to upload is a valid image file ' +
            'and try again.'
          );

          return;
        }

        // Apply the uploading class.
        $el.addClass('file-uploading');

        // Start the upload.
        data['Content-Type'] = file.type;
        FileAPI.upload({
          url: bucketUrl,
          data: data,
          files: {file: file},
          cache: true,
          complete: function (err, xhr){
            // Remove the uploading class.
            $el.removeClass('file-uploading');

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

            // Fetch the image to make loading faster
            self.prefetchImage(imageUrl);

            // On success, apply the attribute to the project.
            self.model.set(attrName, imageUrl);
          }
        });

        this.previewImage(file, $el);
      },
      handleFileInputChange: function(evt) {
        evt.preventDefault();
        var $imgContainer = $(evt.currentTarget).closest('.image-holder'),
            files;

        // Get the files
        files = FileAPI.getFiles(evt);
        FileAPI.reset(evt.currentTarget);

        this.uploadImage(files, $imgContainer);
      },
      initDropZones: function() {
        var self = this;
        self.ui.imageDropZones.each(function(i, imageDropZone) {
          self.initDropZone(imageDropZone);
        });
      },
      initDropZone: function(el) {
        var self = this,
            $imgContainer = $(el).closest('.image-holder');

        if( FileAPI.support.dnd ){
          FileAPI.event.dnd(el,
            // onFileHover
            function (over){
              $imgContainer.toggleClass('over', over);
            },
            // onFileDrop
            function(files) {
              $imgContainer.removeClass('over');
              self.uploadImage(files, $imgContainer);
            }
          );
        }
      },

      handleHighlightLinkChange: function(evt) {
        evt.preventDefault();

        var $target = $(evt.currentTarget),
            $selected = $target.find('option:selected'),
            $externalLinkInput = $target.siblings('.highlight-external-link'),
            linkType = $selected.attr('data-link-type'),
            linkTypeModelProp = $target.attr('data-link-type-name');

        // Handle external link  visibility
        this.model.set(linkTypeModelProp, linkType);

        if (linkType === 'external') {
          $externalLinkInput.removeClass('is-hidden');
          this.model.set($target.attr('name'), $externalLinkInput.val());
        } else {
          $externalLinkInput.addClass('is-hidden');
          this.model.set($target.attr('name'), $selected.val());
        }
      },

      handleHighlightExternalLinkBlur: function(evt) {
        var $target = $(evt.currentTarget),
            attr = $target.attr('data-attr'),
            val = $target.val();

        evt.preventDefault();

        // Set the value of what was just blurred. Setting an event to the same
        // value does not trigger a change event.
        this.model.set(attr, val);
      },

      onSync: function() {
        // When the model is synced with the server, we're going to rerender
        // the view to match the data.
        this.render();
      },
      handleEditableNavMenuLinkBlur: function(evt) {
        var $target = $(evt.target),
            attr = $target.attr('data-attr') || 'menu_label',
            sectionId = $target.attr('data-id'),
            val = $target.text(),
            sectionCollection = this.model.get('sections'),
            sectionModel = sectionCollection.get(sectionId);

        evt.preventDefault();

        // Set the value of what was just blurred. Setting an event to the same
        // value does not trigger a change event.
        sectionModel.set(attr, val);
      },
      handleStatusChange: function(evt) {
        var $target = $(evt.target),
            attr = $target.attr('data-attr'),
            val = $target.val();

        evt.preventDefault();

        this.ui.statusLabel
          // .removeClass('project-status-not-started project-status-active project-status-complete')
          // .addClass('project-status-'+val)
          .find('strong').text(_.findWhere(NS.Data.statuses, {'value': val}).label);

        this.model.set(attr, val);
      },
      handleVisibilityChange: function(evt) {
        var $target = $(evt.target),
            attr = $target.attr('data-attr'),
            val = ($target.val() === 'true');

        evt.preventDefault();

        // For IE8 only
        this.ui.visibilityToggle.removeClass('checked');
        $target.addClass('checked');

        this.model.set(attr, val);
      },
      save: function(makePublic) {
        var self = this,
            data = null;

        if (makePublic) {
          data = {public: true};
        }

        this.model.clean();
        this.model.save(data, {
          // We are not interested in change events that come from the server,
          // and it causes the save button to enable after saving a new project
          silent: true,
          success: function(model) {
            var path = '/' + NS.Data.user.username + '/' + model.get('slug') + '/';

            if (window.location.pathname !== path) {
              if (Modernizr.history) {
                window.history.pushState('', '', path);
              } else {
                window.location = path;
              }
            }

            if (makePublic || !model.get('public')) {
              // Show the modal if we're publishing this right now
              NS.app.overlayRegion.show(new NS.ProjectAdminModalView({
                model: model
              }));
            }
          },
          error: function(model, resp) {
            NS.showProjectSaveErrorModal(resp);
          }
        });
      },
      handleSave: function(evt) {
        evt.preventDefault();
        var self = this,
            $target = $(evt.target);

        if (!$target.hasClass('btn-disabled')) {
          this.save();
        }
      },
      handlePublish: function(evt) {
        evt.preventDefault();
        this.save(true);
      },
      handleUserMenuClick: function(evt) {
        evt.preventDefault();
        this.ui.userMenu.toggleClass('is-open');
      },
      dataChanged: function() {
        // Show the save button
        this.ui.saveBtn.removeClass('btn-disabled');
      }
    })
  );
}(Planbox, jQuery));