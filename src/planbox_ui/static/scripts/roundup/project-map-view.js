/*globals Backbone, jQuery, Modernizr, Handlebars */

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

  NS.ProjectMapItemView = Backbone.Marionette.ItemView.extend({
    template: '#project-map-item-tpl',
    tagName: 'div',

    initialize: function() {
      this.layer = null;
    },

    render: function() {
      var geometry = this.model.get('geometry'),
          lat, lng;

      // Get rid of the current layer
      if (this.layer) {
        this.layer.unbindPopup();
        this.layer = null;
      }

      if (geometry) {
        lat = geometry.coordinates[1];
        lng = geometry.coordinates[0];
        this.layer = L.marker([lat, lng]);

        Backbone.Marionette.ItemView.prototype.render.call(this);

        this.layer.bindPopup(this.el);
      }

      return this;
    },
  });

  NS.ProjectMapView = Backbone.Marionette.CollectionView.extend({
    itemView: NS.ProjectMapItemView,

    initialize: function() {
      this.map = L.map(this.el);
      L.tileLayer('http://{s}.tiles.mapbox.com/v3/openplans.map-dmar86ym/{z}/{x}/{y}.png')
        .addTo(this.map);
      this.layerGroup = L.layerGroup().addTo(this.map);
    },

    renderItemView: function(view, index) {
      if (view.layer) { this.layerGroup.removeLayer(view.layer); }
      view.render();
      if (view.layer) { this.layerGroup.addLayer(view.layer); }
    },

    removeItemView: function(item){
      var view = this.children.findByModel(item);
      if (view.layer) { this.layerGroup.removeLayer(view.layer); }
      this.removeChildView(view);
      this.checkEmpty();
    },

    fitCollectionBounds: function() {
      var bounds = this.calculateCollectionBounds();
      if (bounds) {
        this.map.fitBounds(bounds);
      }
    },

    calculateCollectionBounds: function() {
      var bounds = null, geometry, lat, lng;
      this.collection.each(function(model) {
        geometry = model.get('geometry');
        if (geometry) {
          lat = geometry.coordinates[1];
          lng = geometry.coordinates[0];
          if (!bounds) {
            bounds = L.latLngBounds([[lat, lng], [lat, lng]]);
          } else {
            bounds.extend([lat, lng]);
          }
        }
      });
      return bounds;
    },

    onShow: function() {
      this.fitCollectionBounds();
      this.map.invalidateSize();
    }
  });

}(Planbox, jQuery));