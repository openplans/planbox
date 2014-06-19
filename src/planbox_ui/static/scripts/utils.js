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

    // ====================================================
    // Event and State Logging

    log: function() {
      var args = Array.prototype.slice.call(arguments, 0);

      if (window.ga) {
        this.analytics(args);
      } else {
        NS.Utils.console.log(args);
      }
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
    }
  };

}(Planbox, jQuery));