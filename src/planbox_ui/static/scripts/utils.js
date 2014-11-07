/*globals jQuery _ window document */

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

  NS.Utils = {
    // http://stackoverflow.com/questions/15125217/convert-html-to-plain-text-in-contenteditable
    pasteHtmlAtCaret: function(html, selectPastedContent) {
      var sel, range;
      if (window.getSelection) {
        // IE9 and non-IE
        sel = window.getSelection();
        if (sel.getRangeAt && sel.rangeCount) {
          range = sel.getRangeAt(0);
          range.deleteContents();

          // Range.createContextualFragment() would be useful here but is
          // only relatively recently standardized and is not supported in
          // some browsers (IE9, for one)
          var el = document.createElement('div');
          el.innerHTML = html;
          var frag = document.createDocumentFragment(), node, lastNode;
          while ( (node = el.firstChild) ) {
            lastNode = frag.appendChild(node);
          }
          var firstNode = frag.firstChild;
          range.insertNode(frag);

          // Preserve the selection
          if (lastNode) {
            range = range.cloneRange();
            range.setStartAfter(lastNode);
            if (selectPastedContent) {
              range.setStartBefore(firstNode);
            } else {
              range.collapse(true);
            }
            sel.removeAllRanges();
            sel.addRange(range);
          }
        }
      } else if ( (sel = document.selection) && sel.type !== 'Control') {
        // IE < 9
        var originalRange = sel.createRange();
        originalRange.collapse(true);
        sel.createRange().pasteHTML(html);
        if (selectPastedContent) {
          range = sel.createRange();
          range.setEndPoint('StartToStart', originalRange);
          range.select();
        }
      }
    },

    // http://stackoverflow.com/questions/1219860/html-encoding-in-javascript-jquery
    htmlEscape: function(str) {
      return String(str)
            .replace(/&/g, '&amp;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');
    },

    // pathJoin translated from Python's os.path.join
    pathJoin: function() {
      var i, segment, path = '';
      for (i = 0; i < arguments.length; ++i) {
        segment = arguments[i];
        if (segment[0] === '/') {
          path = segment;
        } else if (path === '' || path[path.length-1] === '/') {
          path += segment;
        } else {
          path += '/' + segment;
        }
      }
      return path;
    },

    rootPathJoin: function() {
      // Prepend the project root path to the arguments
      var allArgs = Array.prototype.slice.call(arguments, 0);
      allArgs.unshift(NS.bootstrapped.projectRootPath);

      // Then treat as a normal path join
      return NS.Utils.pathJoin.apply(this, allArgs);
    },

    guid: function() {
      var s4 = function() {
        return Math.floor((1 + Math.random()) * 0x10000)
                   .toString(16)
                   .substring(1);
      };
      return s4() + s4() + '-' + s4() + '-' + s4() + '-' +
             s4() + '-' + s4() + s4() + s4();
    },

    // Plugin hooks
    runHook: function(objects, hook, options, undefined) {
      // Go through each item and run the given hook. This can be useful, for
      // example, to run some initialization tasks that it's not appropriate
      // to do before a project is about to be saved for the first time
      // (like creating a shareabouts dataset).

      options = _.defaults(options || {}, {
        startIndex: 0,
        done: function() {},
        args: []
      });

      // Go through the items in objects and find the next one that defines
      // the hook function.
      var index = options.startIndex,
          item, hookArgs;

      if (index < _.size(objects)) {
        do {
          item = objects[index];
          index += 1;
        } while (item && !item[hook]);
      }

      // Recursively call each item's hook. When finished the hook should call
      // the `options.nextHook` callback.
      if (item) {
        hookArgs = options.args.concat([{
          nextHook: function() {
            NS.Utils.runHook(objects, hook, _.extend({}, options, {startIndex: index}));
          }
        }]);
        item[hook].apply(item, hookArgs);
      }

      else {
        options.done.apply(undefined, options.args);
      }

    },

    // ====================================================
    // Event and State Logging

    logEvents: function(root, appName) {
      $(root).on('click', '[data-log-click]', function(evt) {
        var $target = $(this),
            category = appName,
            action = 'click: ' + ($target.attr('data-ga-action') || $target.text());
        NS.Utils.log('USER', category, action);
      });
    },

    log: function() {
      var args = Array.prototype.slice.call(arguments, 0);

      if (window.Intercom && args[0].toLowerCase() === 'support') {
        this.support(args);
      } else if (window.ga && args[0].toLowerCase() !== 'support') {
        this.analytics(args);
      } else {
        NS.Utils.console.log(args);
      }
    },

    support: function(args) {
      var eventName = args[1],
          eventData;
      if (args.length > 2) { eventData = args[2]; }
      window.Intercom('trackEvent', args[1], args[2]);
    },

    // TODO: Update for Planbox rather than Shareabouts
    analytics: function(args) {
      var firstArg = args.shift(),
          secondArg,
          measure,
          measures = {
            'center-lat': 'metric1',
            'center-lng': 'metric2',
            'zoom': 'metric3',

            'panel-state': 'dimension1'
          };

      switch (firstArg.toLowerCase()) {
        case 'route':
          args = ['send', 'pageview'].concat(args);
          break;

        case 'user':
          args = ['send', 'event'].concat(args);
          break;

        case 'app':
          secondArg = args.shift();
          measure = measures[secondArg];
          if (!measure) {
            this.console.error('No metrics or dimensions matching "' + secondArg + '"');
            return;
          }
          args = ['set', measure].concat(args);
          break;

        default:
          return;
      }

      window.ga.apply(window, args);
    },

    // For browsers without a console
    console: window.console || {
      log: function(){},
      debug: function(){},
      info: function(){},
      warn: function(){},
      error: function(){}
    },

    merge: function(sa1, sa2) {
      // Merge two sorted lists, without duplication.
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
    }
  };

}(Planbox, jQuery));