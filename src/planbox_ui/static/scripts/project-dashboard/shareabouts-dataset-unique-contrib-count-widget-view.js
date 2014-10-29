/*globals Backbone, jQuery, Modernizr, Handlebars */

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

  NS.DatasetUniqueContribCountWidgetView = Backbone.Marionette.ItemView.extend({
    template: '#dataset-unique-contrib-count-widget-tpl',
    modelEvents: {
      'change': 'render'
    },
    initialize: function(options) {
      this.plugin = options.plugin;

      this.plugin.places.on('add', _.bind(this.render, this));
      this.plugin.submissions.on('add', _.bind(this.render, this));
    },
    serializeData: function() {
      var userTokens = this.plugin.places.pluck('user_token').concat(
        this.plugin.submissions.pluck('user_token'));
      userTokens = _.uniq(userTokens);

      var data = {
        'unique_contributor_count': userTokens.length
      };

      return data;
    }
  });

}(Planbox, jQuery));