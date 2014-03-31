/*globals Handlebars _ jQuery FileAPI */

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

  Handlebars.registerHelper('debug', function(obj) {
    return JSON.stringify(obj);
  });

  Handlebars.registerHelper('window_location', function() {
    return window.location.toString();
  });

  Handlebars.registerHelper('if_fileapi_support', function(featureName, options) {
    return (FileAPI.support[featureName] ? options.fn(this) : options.inverse(this));
  });

  Handlebars.registerHelper('contact_email', function() {
    return NS.Data.contactEmail;
  });

  Handlebars.registerHelper('user', function(attr, options) {
    // If there are two args, then we asked for a specific attribute
    if (options) {
      return NS.Data.user[attr];
    }

    // Only one arg, so attr is really options
    options = attr;
    return options.fn(NS.Data.user);
  });

  Handlebars.registerHelper('status_label', function(status_value, options) {
    var status = _.findWhere(NS.Data.statuses, {'value': status_value});
    return status ? status.label : NS.Data.statuses[0].label;
  });

  Handlebars.registerHelper('each_status', function(options) {
    var result = '',
        context = this;

    _.each(NS.Data.statuses, function(status) {
      result += options.fn(_.extend(context, status));
    });

    return result;
  });

  Handlebars.registerHelper('select', function(value, options) {
    var $el = $('<div/>').html(options.fn(this)),
      selectValue = function(v) {
        $el.find('[value="'+v+'"]').attr({
          checked: 'checked',
          selected: 'selected'
        });
      };

    if (_.isArray(value)) {
      _.each(value, selectValue);
    } else {
      selectValue(value);
    }

    return $el.html();
  });

  Handlebars.registerHelper('select_highlight', function(type, url, options) {
    var $el = $('<div/>').html(options.fn(this)),
      selectValue = function(v) {
        $el.find('[value="'+v+'"]').attr({
          checked: 'checked',
          selected: 'selected'
        });
      };

    if (type === 'link') {
      $el.find('[data-type="link"]').attr({checked: 'checked', selected: 'selected'});
    } else {
      selectValue(url);
    }

    return $el.html();
  });


}(Planbox, jQuery));
