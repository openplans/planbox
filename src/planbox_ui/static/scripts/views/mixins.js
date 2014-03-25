/*globals Pen */

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

  NS.ContentEditableMixin = {
    handleEditableBlur: function(evt) {
      var $target = $(evt.target),
          attr = $target.attr('data-attr'),
          val = $target.html();

      evt.preventDefault();

      // Set the value of what was just blurred. Setting an event to the same
      // value does not trigger a change event.
      this.model.set(attr, val);
    },
    onRender: function() {
      this.initRichEditables();
    },
    initRichEditable: function(el) {
      this.pen = new Pen({
        editor: el,
        list: ['insertorderedlist', 'insertunorderedlist', 'bold', 'italic', 'createlink'],
        stay: false
      });
    },
    initRichEditables: function() {
      var self = this;
      if (this.ui.richEditables) {
        // Init the Pen editor for each richEditable element
        this.ui.richEditables.each(function(i, el) {
          self.initRichEditable(el);
        });
      }
    }
  };
}(Planbox, jQuery));
