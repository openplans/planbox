/*globals Handlebars _ jQuery FileAPI moment */

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

  Handlebars.registerHelper('debug', function(obj) {
    return JSON.stringify(obj);
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


  // A random short quote -----------------------------------------------------

  Handlebars.registerHelper('randomquote', function() {
    var quoteArray = [
        'True life is lived when tiny changes occur.', // -Leo Tolstoy
        'It\'s a bad plan that admits of no modification.', // -Publilius Syrus
        'It takes as much energy to wish as it does to plan.', // -Eleanor Roosevelt
        'A good plan today is better that a perfect plan tomorrow.', // -Geoge S. Patton
        'Planning is bringing the future into the present so that you can do something about it now.', // -Alan Lakein
        'Always have a plan, and believe in it. Nothing happens by accident.', // -Chuck Knox
        'A good plan is like a road map: it shows the final destination and usually the best way to get there.', // -H. Stanely Judd
        'A community is like a ship: everyone ought to be prepared to take the helm.', // -Henrik Ibsen
        'It\'s not the plan that\'s important, it\'s the planning.', // -Dr. Gramme Edwards
        'Plans are only good intentions unless they immediately degenerate into hard work.', // -Peter Drucker
        'If you can dream it, you can do it.', // -Walt Disney
        'A plan which succeeds is bold, one which fails is reckless.', // -General Karl von Clauswitz
        'Those who plan do better than those who do not plan even thou they rarely stick to their plan.', // -Winston Churchill
        'Good plans shape good decisions. That\'s why good planning helps to make elusive dreams come true.', // -Lester Robert Bittel
        'You got to be careful if you don\'t know where you\'re going, because you might not get there.', // -Yogi Berra
        'Prediction is difficult, especially about the future.', // -Yogi Berra
        'Plans are nothing; planning is everything.', // -Dwight D. Eisenhower
        'Alone we can do so little; together we can do so much.', // -Helen Keller
        'Why do they call it rush hour when nothing moves?' // -Robin Williams
    ];
    var randomNumber = Math.floor(Math.random()*quoteArray.length);

    return quoteArray[randomNumber];
  });


}(Planbox, jQuery));
