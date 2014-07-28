/*globals Backbone jQuery Handlebars Modernizr _ Pen FileAPI chrono */

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

  NS.ProjectAdminView = Backbone.Marionette.Layout.extend(
    _.extend({}, NS.ContentEditableMixin, {
      template: '#project-admin-tpl',
      ui: {
        editables: '[data-attr]:not(#section-list [data-attr])',
        richEditables: '.project-description',
        saveBtn: '.save-btn',
        statusSelector: '.status-selector',
        statusLabel: '.project-status',
        visibilityToggle: '[name=project-public]',
        customDomainMessage: '.custom-domain-message',
        customDomainMessageBtn: '.custom-domain-message-btn',
        userMenuLink: '.user-menu-link',
        userMenu: '.user-menu',
        editableNavMenuLinks: '.sub-nav a[contenteditable]',
        publishBtn: '.btn-public',
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
        'click @ui.customDomainMessageBtn': 'handleCustomDomainMessageBtn',
        'click @ui.userMenuLink': 'handleUserMenuClick',
        'click @ui.publishBtn': 'handlePublish',
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
      },

      onRender: function() {
        this.initRichEditables();
        this.initDropZones();
        // this.showRegions();
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

      initDropZones: function() {
        var view = this;

        this.ui.imageDropZones.fileUpload({
          url: 'https://' + NS.Data.s3UploadBucket + '.s3.amazonaws.com/',
          data: _.clone(NS.Data.s3UploadData),
          dndOver: function(isOver) {
            $(this).toggleClass('file-dragging', isOver);
          },
          dndDrop: function(files) {
            var $this = $(this);
            $this.removeClass('file-dragging');
            $this.data('fileUpload').upload(files);
          },
          validate: function(files) {
            var i;
            // Make sure this is an image before continuing
            for (i=0; i<files.length; i++) {
              if (files[i].type.indexOf('image/') !== 0) {
                NS.showErrorModal(
                  'Unable to save that file.',
                  'This file doesn\'t seem to be an image file.',
                  'Make sure the file you\'re trying to upload is a valid image file ' +
                  'and try again.'
                );

                // Return false to prevent the upload from starting
                return false;
              }
            }
            return true;
          },
          start: function(xhr, options) {
            // When the upload starts
            var $this = $(this),
                $imageContainer = $this.closest('.image-holder');

            // Apply the uploading class.
            $this.addClass('file-uploading');

            // Show a preview
            // TODO: file[0] is not great
            $this.data('fileUpload').previewImage(options.files.file[0], function(dataUrl) {
              view.setImageOnContainer($imageContainer, dataUrl);
            });
          },
          complete: function(err, xhr, options) {
            // When the upload is complete
            var $this = $(this),
                $imageContainer = $this.closest('.image-holder'),
                attrName = $imageContainer.attr('data-attr'),
                imageUrl = window.encodeURI(
                  options.url + options.data.key.replace('${filename}',
                  // TODO: file[0] is not great
                  options.files.file[0].name)
                );

            // Remove the uploading class.
            $this.removeClass('file-uploading');

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
            $this.data('fileUpload').prefetchImage(imageUrl);

            // On success, apply the attribute to the project.
            view.model.set(attrName, imageUrl);
          }
        });
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
          $externalLinkInput.removeClass('hide');
          this.model.set($target.attr('name'), $externalLinkInput.val());
        } else {
          $externalLinkInput.addClass('hide');
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
            self.onSaveSuccess(model, makePublic);
          },
          error: function(model, resp) {
            self.onSaveError(model, resp);
          }
        });
      },
      handleSave: function(evt) {
        evt.preventDefault();
        var self = this,
            $target = $(evt.currentTarget);

        if (!$target.hasClass('disabled')) {
          this.save();
        }
      },
      handlePublish: function(evt) {
        evt.preventDefault();
        this.save(true);
      },
      handleCustomDomainMessageBtn: function(evt) {
        evt.preventDefault();
        this.ui.customDomainMessage.toggleClass('is-open');
      },
      handleUserMenuClick: function(evt) {
        evt.preventDefault();
        this.ui.userMenu.toggleClass('is-open');
      },
      onSaveSuccess: function(model, makePublic) {
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
          // Note: we defer so that the modal is visible after re-rendering.
          _.defer(function() {
            NS.app.modalRegion.show(new NS.ProjectAdminModalView({
              model: model
            }));
          });
        }
      },
      onSaveError: function(model, resp) {
        NS.showProjectSaveErrorModal(resp);
      },
      dataChanged: function() {
        // Show the save button
        this.ui.saveBtn.removeClass('disabled');
      }
    })
  );

}(Planbox, jQuery));