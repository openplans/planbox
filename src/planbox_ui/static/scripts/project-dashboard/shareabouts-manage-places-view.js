/*globals Backbone, jQuery, Modernizr, Handlebars */

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

  var merge = function(sa1, sa2) {
    var i1 = 0, i2 = 0,
        len1 = sa1.length,
        len2 = sa2.length,
        result = [],
        val1, val2;

    while (i1 < len1 && i2 < len2) {
      val1 = sa1[i1];
      val2 = sa2[i2];
      if (val1 < val2) {
        result.push(val1);
        i1++;
      }
      else if (val1 > val2) {
        result.push(val2);
        i2++;
      }
      else {  // val1 == val2
        result.push(val1);
        i1++;
        i2++;
      }
    }

    if (i1 < len1) {
      result.splice(result.length, 0, sa1.slice(i1));
    }
    if (i2 < len2) {
      result.splice(result.length, 0, sa2.slice(i2));
    }

    return result;
  };

  NS.ManagePlacesView = Backbone.Marionette.ItemView.extend({
    template: '#shareabouts-manager-content-tpl',
    modelEvents: {
      'change': 'render'
    },
    initialize: function(options) {
      this.plugin = options.plugin;

      // For now, debounce the add-place handler, since it will rerender the
      // entire table. TODO: We can probably do the adding smarter though.
      this.plugin.places.on('add', _.debounce(_.bind(this.handleAddPlace, this), 500));

      this.columnHeaders = [];
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
    getPlaceColumnHeaders: function(place) {
      var data = place.attributes,
          headers = [], key, value;

      for (key in data) {
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
      var newColumnHeaders = this.getPlaceColumnHeaders(place);
      this.updateColumnHeaders(newColumnHeaders);
      this.render();
    },
    serializeData: function() {
      // var columnHeaders = [
      //     'dataset'
      //   , 'description'
      //   , 'geometry'
      //   , 'id'
      //   , 'lat'
      //   , 'lng'
      //   , 'dragPoint'
      //   , 'geocodeQuality'
      //   , 'geocodeQualityCode'
      //   , 'linkId'
      //   , 'mapUrl'
      //   , 'postalCode'
      //   , 'sideOfStreet'
      //   , 'street'
      //   , 'locationtype'
      //   , 'name'
      //   , 'notes_public'
      //   , 'submitter_email'
      //   , 'submitter'
      //   , 'avatar_url'
      //   , 'submitterid'
      //   , 'submittername'
      //   , 'updated_datetime'
      //   , 'url'
      //   , 'user_token'
      //   , 'visible'
      //   ];

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
      data['headers'] = this.columnHeaders;
      data['places'] = this.plugin.places.toJSON();
      data['submissions'] = this.plugin.submissions.toJSON();

      data['labels'] = attrLabelMap;

      return data;
    }
  });

}(Planbox, jQuery));