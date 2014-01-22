/*globals Handlebars _ */

var Planbox = Planbox || {};

(function(NS) {

  Handlebars.registerHelper('debug', function(obj) {
    return JSON.stringify(obj);
  });

  Handlebars.registerHelper('window_location', function() {
    return window.location.toString();
  });

  Handlebars.registerHelper('status_label', function(status_value, options) {
    var status = _.findWhere(NS.Data.statuses, {'value': status_value});
    return status ? status.label : NS.Data.statuses[0].label;
  });


  Handlebars.registerHelper('each_status', function(options) {
    var result = '';

    _.each(NS.Data.statuses, function(status) {
      result += options.fn(_.extend(this, status));
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

}(Planbox));
