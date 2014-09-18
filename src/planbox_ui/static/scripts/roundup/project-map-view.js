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
      this.layerGroup = L.featureGroup().addTo(this.map);
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
      if (bounds.isValid()) {
        this.map.fitBounds(bounds, {
          // Add some padding to the top of the map for tall markers
          paddingTopLeft: [0, 41]
        });
      }
    },

    calculateCollectionBounds: function() {
      return this.layerGroup.getBounds();
    },

    onShow: function() {
      this.fitCollectionBounds();
      this.map.invalidateSize();

      if (this.layerGroup.getLayers().length === 0) {
        this.$el.addClass('hide');
      } else {
        this.$el.removeClass('hide');
      }
    }
  });

}(Planbox, jQuery));