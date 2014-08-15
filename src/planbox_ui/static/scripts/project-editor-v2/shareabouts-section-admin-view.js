/*globals Backbone jQuery Handlebars Modernizr _ Pen FileAPI chrono L */

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

  NS.ShareaboutsSectionAdminView = Backbone.Marionette.ItemView.extend(
    _.extend({}, NS.ContentEditableMixin, NS.SectionAdminMixin, {
      template: '#shareabouts-section-admin-tpl',
      tagName: 'section',
      id: NS.SectionMixin.id,

      ui: {
        editables: '[data-attr]',
        richEditables: '.project-shareabouts-description',
        map: '.map',
        deleteSection: '.delete-section',
        generateSnapshot: '.generate-snapshot'
      },
      events: {
        'blur @ui.editables': 'handleEditableBlur',
        'input @ui.editables': 'handleEditableBlur',
        'click @ui.deleteSection': 'handleDeleteSectionClick',
        'click @ui.generateSnapshot': 'handleGenerateSnapshotClick'
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

      handleGenerateSnapshotClick: function(evt) {
        evt.preventDefault();

        if (!this.ui.generateSnapshot.hasClass('generating')) {
          var self = this,
              originalSnapshotButtonLabel = self.ui.generateSnapshot.html(),
              generatingSnapshotLabel = self.ui.generateSnapshot.attr('data-generating-label'),
              datasetUrl = this.model.get('details').dataset_url,
              snapshots = new Shareabouts.SnapshotCollection(),
              snapshot;

          var getFilename = function(url) {
            var filename = url.substring(url.lastIndexOf('/')+1);
            return filename;
          };

          self.ui.generateSnapshot
            .attr('disabled', 'disabled')
            .addClass('generating')
            .html(generatingSnapshotLabel);

          snapshots.url = datasetUrl + '/places/snapshots';
          snapshot = snapshots.create({}, {
            success: function() {
              snapshot.waitUntilReady({
                data: {'include_submissions': true},
                success: function(url) {
                  var filename = getFilename(url);
                  $('.existing-snapshot-wrapper').html('<a href="' + url + '" class="download-snapshot button" download="' + filename + '">Download snapshot<br><small>requested ' + moment(snapshot.get('requested_at')).fromNow() + '</small></a>');
                  self.ui.generateSnapshot
                    .removeAttr('disabled')
                    .removeClass('generating')
                    .html(originalSnapshotButtonLabel);
                },
                error: function() {
                  self.ui.generateSnapshot
                    .removeAttr('disabled')
                    .removeClass('generating')
                    .html(originalSnapshotButtonLabel);
                  alert('There was a problem generating your\nsnapshot. Please try again later.');
                },
                complete: function() {
                  self.ui.generateSnapshot
                    .removeAttr('disabled')
                    .removeClass('generating')
                    .html(originalSnapshotButtonLabel);
                }
              });
            }
          });
        }
      },

      initialize: function() {
        var self = this;

        if (!this.model.get('details').dataset_url) {
          // Create the dataset and set the dataset url on the section model
          $.ajax({
            url: '/shareabouts/create-dataset',
            type: 'POST',
            data: {
              dataset_slug: NS.Data.user.username + '-' + this.model.collection.project.get('slug')
            },
            success: function(data) {
              self.model.set('dataset_url', data.url);
            },
            error: function(xhr, status, error) {
              // Remove the unsaved collection (and the view automatically)
              self.model.collection.remove(self.model);

              NS.showErrorModal('Unable to activate Shareabouts',
                'There was a temporary problem while we were setting up your ' +
                'Shareabouts map.',
                'We\'ve been notified and will investigate it right away. ' +
                'This is likely a temporary issue so please try again shortly.');
            }
          });
        }
      }
    })
  );

}(Planbox, jQuery));