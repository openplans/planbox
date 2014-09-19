/*globals Backbone jQuery L */

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

  NS.ProjectLocationMapView = Backbone.Marionette.ItemView.extend({
    template: '#project-location-map-tpl',
    ui: {
      mapCheckbox: '#map-switch',
      container: '.map-container',
      map: '.map'
    },
    events: {
      'change @ui.mapCheckbox': 'handleVisibilityToggle'
    },

    onRender: function() {
      var self = this,
          geom = this.model.get('geometry'),
          options = { center: [31.5, 0], zoom: 1, scrollWheelZoom: false };

      if (geom) {
        options = {
          center: [geom.coordinates[1], geom.coordinates[0]],
          zoom: 12,
          scrollWheelZoom: false
        };
      }

      this.map = L.map(this.ui.map.get(0), options);

      this.centerMarker = L.circleMarker(this.map.getCenter(), {
        radius: 4,
        opacity: 0.9
      }).addTo(this.map);

      L.tileLayer('http://{s}.tiles.mapbox.com/v3/openplans.map-dmar86ym/{z}/{x}/{y}.png')
        .addTo(this.map);

      this.map.on('move', function(evt) {
        var center = self.map.getCenter();

        self.centerMarker.setLatLng(center);
        self.model.set({'geometry': {
          type: 'Point',
          coordinates: [center.lng, center.lat]
        }});
      });
    },

    onShow: function() {
      this.map.invalidateSize();
    },

    handleVisibilityToggle: function(evt) {
      evt.preventDefault();
      var checked = this.ui.mapCheckbox.is(':checked');

      if (checked) {
        this.ui.container.show();
        this.map.invalidateSize();
      } else {
        this.model.set('location', '');
        this.model.set('geometry', null);
        this.render();
        this.ui.container.hide();
      }
    }
  });

}(Planbox, jQuery));