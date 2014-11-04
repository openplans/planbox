/*globals Handlebars _ jQuery FileAPI moment */

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

  Handlebars.registerHelper('debug', function(obj) {
    return JSON.stringify(obj);
  });

  Handlebars.registerHelper('makeUniquifier', function(name, options) {
    if (!options) {
      options = name;
      name = 'uniquifier';
    }

    var newContext = {};
    newContext[name] = NS.Utils.guid();
    return options.fn(_.extend({}, this, newContext));
  });

  Handlebars.registerHelper('lookup', function(obj, attrName, options) {
    var value, isDefined = true;

    if (obj) { value = obj[attrName]; }

    // Determine whether to treat as a block helper or not.
    if (options && options.fn) {
      return (value ? options.fn(value) : options.inverse(this));
    } else {
      return value;
    }
  });

  Handlebars.registerHelper('resolve', function(obj, attrName, options) {
    var path = (attrName ? attrName.split('.') : []),
        current, index, value = obj, isDefined = true;

    for (index = 0; index < path.length; index++) {
      if (!value) { break; }
      current = path[index];
      value = value[current];
    }

    // Determine whether to treat as a block helper or not.
    if (options && options.fn) {
      return (value ? options.fn(value) : options.inverse(this));
    } else {
      return value;
    }
  });

  Handlebars.registerHelper('isAny', function(value, /* test1, test2, test3, ..., */ options) {
    var tests = _.rest(_.initial(arguments)),
        isAny = false,
        result = function(value) {
          if (_.isFunction(value)) {
            return value();
          } else {
            return value;
          }
        };
    options = _.last(arguments);
    value = result(value);

    isAny = !!(_.find(tests, function(test) {
      test = result(test);
      if (value && value === test) {
        return true;
      }
    }));

    if (isAny) {
      return options.fn(this);
    } else {
      return options.inverse(this);
    }
  });

  Handlebars.registerHelper('window_location', function() {
    return window.location.toString();
  });

  Handlebars.registerHelper('static_url', function() {
    return NS.bootstrapped.staticUrl;
  });

  Handlebars.registerHelper('if_fileapi_support', function(featureName, options) {
    return (FileAPI.support[featureName] ? options.fn(this) : options.inverse(this));
  });

  Handlebars.registerHelper('has_key', function(object, key, options) {
    return (object[key] ? options.fn(this) : options.inverse(this));
  });

  Handlebars.registerHelper('each_active_section', function(sections, options) {
    var result = '',
        context = this;

    _.each(sections, function(section) {
      if (section.active) {
        result += options.fn(_.extend({}, context, section));
      }
    });

    return result;
  });

  Handlebars.registerHelper('gte_active_section_length', function(sections, len, options) {
    var activeLength = _.filter(sections, function(s){ return s.active && s.menu_label; }).length;
    return (activeLength >= len ? options.fn(this) : options.inverse(this));
  });

  Handlebars.registerHelper('has_section_type', function(type, options) {
    var hasType = !!NS.app.sectionCollection.find(function(model) {
          return model.get('type') === type;
        });

    return (hasType ? options.fn(this) : options.inverse(this));
  });

  Handlebars.registerHelper('contact_email', function() {
    return NS.Data.contactEmail;
  });



  var global_data_attr = function(obj, attr, options) {
    // If there are two args, then we asked for a specific attribute
    if (options) {
      return obj[attr];
    }

    // Only one arg, so this is a block and attr is really options
    options = attr;
    if (obj) {
      return options.fn(obj);
    } else {
      return options.inverse(this);
    }
  };

  Handlebars.registerHelper('bootstrapped', function(data_name, attr, options) {
    return global_data_attr(NS.Data[data_name], attr, options);
  });

  Handlebars.registerHelper('user', function(attr, options) {
    return global_data_attr(NS.Data.user, attr, options);
  });

  Handlebars.registerHelper('owner', function(attr, options) {
    return global_data_attr(NS.Data.owner, attr, options);
  });

  Handlebars.registerHelper('eachUsers', function(attr, options) {
    var iter = NS.Data.user[attr],
        result = '';

    if (iter && iter.length > 0) {
      _.each(iter, function(elem) {
        result += options.fn(elem);
      });
    } else {
      result = options.inverse(this);
    }

    return result;
  })



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

    if (type === 'external') {
      $el.find('[data-link-type="external"]').attr({checked: 'checked', selected: 'selected'});
    } else {
      selectValue(url);
    }

    return $el.html();
  });


  // URLs and filepaths -------------------------------------------------------

  Handlebars.registerHelper('filename', function(fullpath) {
    var filename = fullpath.substring(fullpath.lastIndexOf('/')+1);
    return filename;
  });


  // Date and time ------------------------------------------------------------

  Handlebars.registerHelper('formatdatetime', function(datetime, format) {
    if (datetime) {
      return moment(datetime).format(format);
    }
    return datetime;
  });

  Handlebars.registerHelper('fromnow', function(datetime) {
    if (datetime) {
      return moment(datetime).fromNow();
    }
    return '';
  });

  Handlebars.registerHelper('ispast', function(datetime, options) {
    var now = new Date();
    datetime = new Date(datetime);
    return (datetime <= now ? options.fn(this) : options.inverse(this));
  });

  Handlebars.registerHelper('isfuture', function(datetime, options) {
    var now = new Date();
    datetime = new Date(datetime);
    return (datetime > now ? options.fn(this) : options.inverse(this));
  });


  // A random short quote -----------------------------------------------------

  Handlebars.registerHelper('randomquote', function() {
    var quoteArray = [
        '\u201CTrue life is lived when tiny changes occur.\u201D \u2011\u00A0Leo\u00A0Tolstoy',
        '\u201CIt\'s a bad plan that admits of no modification.\u201D \u2011\u00A0Publilius\u00A0Syrus',
        '\u201CIt takes as much energy to wish as it does to plan.\u201D \u2011\u00A0Eleanor\u00A0Roosevelt',
        '\u201CPlanning is bringing the future into the present so that you can do something about it now.\u201D \u2011\u00A0Alan\u00A0Lakein',
        '\u201CAlways have a plan, and believe in it. Nothing happens by accident.\u201D \u2011\u00A0Chuck\u00A0Knox',
        '\u201CA community is like a ship: everyone ought to be prepared to take the helm.\u201D \u2011\u00A0Henrik\u00A0Ibsen',
        '\u201CIt\'s not the plan that\'s important, it\'s the planning.\u201D \u2011\u00A0Dr.\u00A0Gramme\u00A0Edwards',
        '\u201CPlans are only good intentions unless they immediately degenerate into hard work.\u201D \u2011\u00A0Peter\u00A0Drucker',
        '\u201CIf you can dream it, you can do it.\u201D \u2011\u00A0Walt\u00A0Disney',
        '\u201CThose who plan do better than those who do not plan even thou they rarely stick to their plan.\u201D \u2011\u00A0Winston\u00A0Churchill',
        '\u201CGood plans shape good decisions. That\'s why good planning helps to make elusive dreams come true.\u201D \u2011\u00A0Lester\u00A0Robert\u00A0Bittel',
        '\u201CPrediction is difficult, especially about the future.\u201D \u2011\u00A0Yogi\u00A0Berra',
        '\u201CPlans are nothing; planning is everything.\u201D \u2011\u00A0Dwight\u00A0D.\u00A0Eisenhower',
        '\u201CAlone we can do so little; together we can do so much.\u201D \u2011\u00A0Helen\u00A0Keller',
        '\u201CWhy do they call it rush hour when nothing moves?\u201D \u2011\u00A0Robin\u00A0Williams'
    ];
    var randomNumber = Math.floor(Math.random()*quoteArray.length);

    return quoteArray[randomNumber];
  });


}(Planbox, jQuery));
