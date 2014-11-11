/*globals Backbone, jQuery, Modernizr, Handlebars */

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

  NS.ShareaboutsDashboardPlacesListView = Backbone.Marionette.ItemView.extend({
    template: '#shareabouts-dashboard-places-list-tpl',
    modelEvents: {
      'change': 'render'
    },
    ui: {
      scrolltable: '.table-container',
      scrollLeft: '.scroll-button.left',
      scrollRight: '.scroll-button.right',
      visibleCheckboxes: '.visible-checkbox'
    },
    events: {
      'click @ui.scrollLeft': 'handleScrollLeft',
      'click @ui.scrollRight': 'handleScrollRight',
      'change @ui.visibleCheckboxes': 'handleVisibilityChange'
    },
    initialize: function(options) {
      this.plugin = options.plugin;

      // For now, debounce the add-place handler, since it will rerender the
      // entire table. TODO: We can probably do the adding smarter though.
      this.plugin.places.on('add', _.debounce(_.bind(this.handleAddPlace, this), 500));

      this.columnHeaders = [];
      $(window).on('resize', _.bind(this.onWindowResize, this));
      this.plugin.app.on('toggle:projectDashboard:tabs', _.bind(this.onToggleTabs, this));
    },
    getHeadersForValue: function(key, value) {
      var self = this,
          headers = [];

      if (_.isArray(value) || _.isObject(value)) {
        _.each(value, function(item, subKey) {
          var itemHeaders = self.getHeadersForValue(subKey.toString(), item);
          _.each(itemHeaders, function(itemHeader, index) {
            itemHeaders[index] = key + '.' + itemHeader;
          });
          headers = headers.concat(itemHeaders);
        });
      }

      else {
        headers = [key];
      }

      return headers;
    },
    getColumnHeaders: function(place) {
      var data = place.attributes,
          headers = [], key, value,
          exclude = ['visible'];

      for (key in data) {
        if (_.contains(exclude, key)) { continue; }
        headers = headers.concat(this.getHeadersForValue(key, data[key]));
      }

      return headers;
    },
    updateColumnHeaders: function(headers) {
      var self = this;
      _.each(headers, function(header) {
        var newIndex = _.sortedIndex(self.columnHeaders, header);
        self.columnHeaders.splice(newIndex, 0, header);
      });
      self.columnHeaders = _.uniq(self.columnHeaders, true);
    },
    handleAddPlace: function(place) {
      var newColumnHeaders = this.getColumnHeaders(place);
      this.updateColumnHeaders(newColumnHeaders);
      this.render();
    },
    serializeData: function() {
      var attrLabelMap = {
        'url': 'api url',
        'created_datetime': 'created',
        'updated_datetime': 'last updated',
        'geometry.coordinates.0': 'geometry lng',
        'geometry.coordinates.1': 'geometry lat',
        'geometry.type': 'geometry type',
        'private-email': 'email'
      };

      var attrTypeMap = {
        'created_datetime': 'time',
        'updated_datetime': 'time',
        'submitter.avatar_url': 'image',
        'url': 'url'
      };

      Handlebars.registerHelper('isTimeAttr', function(key, options) {
        return (attrTypeMap[key] === 'time' ? options.fn(this) : options.inverse(this));
      });

      Handlebars.registerHelper('isImageAttr', function(key, options) {
        return (attrTypeMap[key] === 'image' ? options.fn(this) : options.inverse(this));
      });

      Handlebars.registerHelper('isUrlAttr', function(key, options) {
        return (attrTypeMap[key] === 'url' ? options.fn(this) : options.inverse(this));
      });

      Handlebars.registerHelper('isDefaultAttr', function(key, options) {
        return (_.isUndefined(attrTypeMap[key]) ? options.fn(this) : options.inverse(this));
      });

      var data = Backbone.Marionette.ItemView.prototype.serializeData.call(this);
      data.headers = this.columnHeaders;
      data.places = this.plugin.places.toJSON();
      data.submissions = this.plugin.submissions.toJSON();

      data.labels = attrLabelMap;

      return data;
    },

    handleVisibilityChange: function(evt) {
      var $checkbox = $(evt.currentTarget),
          checked = $checkbox.prop('checked'),
          id = $checkbox.attr('data-shareabouts-id'),
          place = this.plugin.places.get(id),
          $row = $checkbox.closest('tr');

      $checkbox.prop('disabled', true);
      place.save({type: 'Feature', properties: {visible: checked}}, {
        url: place.url() + '?include_invisible',
        patch: true,
        success: function() {
          $row.toggleClass('row-visible', checked);
          $row.toggleClass('row-invisible', !checked);
          $row.find('.visible-value').html(checked.toString());
        },
        error: function() {
          $checkbox.prop('checked', !checked);
          // TODO: Handle error
        },
        complete: function() {
          $checkbox.prop('disabled', false);
        }
      });
    },

    fixTableHeader: function() {
      if (window.matchMedia(Foundation.media_queries.large).matches) {
        var tbodyHeight = $(window).height() - this.$('#places-datatable table').offset().top - 60;
        var tHeadHeight = this.$('#places-datatable thead').height();
        this.$('#places-datatable tbody').css({ maxHeight: tbodyHeight });
        this.$('#places-datatable .table-map').css({ height: tbodyHeight + tHeadHeight });
      } else {
        this.$('#places-datatable tbody').css({ maxHeight: 'none' });
        this.$('#places-datatable .table-map').css({ height: 200 });
      }
    },

    toggleScrollNavButtons: function() {
      if ( this.ui.scrolltable.scrollLeft() > 15 ) {
        this.$('.scroll-button.left').removeClass('hide');
      } else {
        this.$('.scroll-button.left').addClass('hide');
      }

      var tableContainerWidth = this.ui.scrolltable.width();
      var tableWidth = this.$('#places-datatable table').width();
      if ( this.ui.scrolltable.scrollLeft() <= tableWidth - tableContainerWidth - 15 ) {
        this.$('.scroll-button.right').removeClass('hide');
      } else {
        this.$('.scroll-button.right').addClass('hide');
      }
    },

    handleScrollLeft: function(evt) {
      evt.preventDefault();
      this.ui.scrolltable.animate({ scrollLeft: 0 });
    },

    handleScrollRight: function(evt) {
      evt.preventDefault();
      var tableWidth = this.$('#places-datatable table').width();
      this.ui.scrolltable.animate({ scrollLeft: tableWidth });
    },

    handleTableUpdated: function(table) {
      this.updateMapMarkers();
      this.fitToMapMarkers();
    },

    initSortableTable: function() {
      var options = {
        valueNames: this.columnHeaders,
        page: 50,
        plugins: [ ListPagination({outerWindow: 2}) ]
      };
      this.table = new List('places-datatable', options);
      this.table.on('updated', _.bind(this.handleTableUpdated, this));
      this.ui.scrolltable.scroll(_.bind(this.toggleScrollNavButtons, this));
      this.toggleScrollNavButtons();
    },

    initMap: function() {
      var $map = this.$('.places-map');
      this.map = L.map($map[0]).setView([0, 0], 1);
      L.tileLayer('https://{s}.tiles.mapbox.com/v3/openplans.map-dmar86ym/{z}/{x}/{y}.png', {
        attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://mapbox.com">Mapbox</a>',
        maxZoom: 18
      }).addTo(this.map);

      this.markerLayer = L.featureGroup([])
        .addTo(this.map);
    },

    redrawMap: function() {
      this.map.invalidateSize();
    },

    getLayerForRow: function(row) {
      var id = $(row).attr('data-shareabouts-id'),
          layer = this.rowToLayerMap[id];
      return layer;
    },

    updateMapMarkers: function() {
      if (this.markerLayer) {
        var self = this;

        var normalStyle = {
          fillColor: 'blue',
          color: 'blue',
          fillOpacity: 0.2,
          opacity: 0.5,
          radius: 5
        };

        var highlightStyle = {
          fillColor: 'black',
          color: 'blue',
          fillOpacity: 1,
          opacity: 1
        };

        // Clear any existing events and markers
        this.$('.table-container tbody tr').off('onmouseenter').off('onmouseleave').off('click');
        this.markerLayer.clearLayers();

        // Add the markers to the map for each visible row
        this.rowToLayerMap = {};
        self.$('.table-container tbody tr').each(function(i, row) {
          var id = $(row).attr('data-shareabouts-id'),
              place = self.plugin.places.get(id),
              lat = place.get('geometry').coordinates[1],
              lng = place.get('geometry').coordinates[0],
              marker;

          marker = L.circleMarker([lat, lng], normalStyle)
            .addTo(self.markerLayer);

          self.rowToLayerMap[id] = marker;
          self.bindRowEvents(row, marker, normalStyle, highlightStyle);
        });
      }
    },

    bindRowEvents: function(row, marker, normalStyle, highlightStyle) {
      var self = this;

      $(row)
        .on('mouseenter', function(evt) {
          marker.setStyle(highlightStyle);
        })
        .on('mouseleave', function(evt) {
          marker.setStyle(normalStyle);
        })
        .on('click', function(evt) {
          self.map.panTo(marker.getLatLng(), {animate: false});
          self.map.setZoom(15, {animate: false});
        });

      marker
        .on('mouseover', function() {
          $(row).addClass('is-hovering');
          marker.setStyle(highlightStyle);
        })
        .on('mouseout', function() {
          $(row).removeClass('is-hovering');
          marker.setStyle(normalStyle);
        })
        .on('click', function() {
          row.scrollIntoView();
        });
    },

    fitToMapMarkers: function() {
      if (this.markerLayer.getLayers().length) {
        this.map.fitBounds(this.markerLayer);
      }
    },

    render: function() {
      Backbone.Marionette.ItemView.prototype.render.apply(this, arguments);
      this.initSortableTable();
      this.initMap();
      this.fixTableHeader();
      this.redrawMap();
      this.updateMapMarkers();
      this.fitToMapMarkers();
      return this;
    },

    onShow: function() {
      this.fixTableHeader();
      this.redrawMap();
      this.fitToMapMarkers();
    },

    onWindowResize: function() {
      this.fixTableHeader();
      this.toggleScrollNavButtons();
      this.redrawMap();
    },

    onToggleTabs: function() {
      this.fixTableHeader();
      this.redrawMap();
      this.fitToMapMarkers();
    }
  });

}(Planbox, jQuery));