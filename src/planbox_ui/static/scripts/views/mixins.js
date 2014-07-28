/*globals Pen jQuery */

var Planbox = Planbox || {};

(function(NS, $) {
  'use strict';

  NS.ContentEditableMixin = {
    handleEditableBlur: function(evt) {
      var $target = $(evt.currentTarget),
          attr = $target.attr('data-attr'),
          val = $target.is('[contenteditable]') ? $target.html() : $target.val();

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
    canUsePen: function() {
      // Pen requires access to the classList attribute on DOM elements (see
      // https://developer.mozilla.org/en-US/docs/Web/API/Element.classList).
      // Check whether this feature is available.
      return ('classList' in document.createElement('a'));
    },
    initRichEditables: function() {
      var self = this;
      if (this.canUsePen() && this.ui.richEditables) {
        // Init the Pen editor for each richEditable element
        this.ui.richEditables.each(function(i, el) {
          self.initRichEditable(el);
        });
      }
    }
  };

  NS.SectionMixin = {
    id: function() {
      return 'section-' + this.model.get('slug') + '-wrapper';
    }
  };

  NS.SectionAdminMixin = {
    className: function() {
      return [
        'project-section',
        'project-section-' + this.model.get('type'),
        this.model.get('active') ? 'active' : ''
      ].join(' ');
    },
    handleActivationChange: function(evt) {
      evt.preventDefault();
      // Expecting values of "on" (truthy) or "" (falsey)
      var isActive = !!$(evt.currentTarget).val();
      this.$el.toggleClass('active', isActive);
      this.model.set('active', isActive);
    }
  };
}(Planbox, jQuery));
