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

  NS.OrderedCollectionMixin = {
    // https://github.com/marionettejs/backbone.marionette/wiki/Adding-support-for-sorted-collections
    // Inspired by the above link, but it doesn't work when you start with an
    // empty (or unsorted) list.
    appendHtml: function(collectionView, itemView, index){
      var collection = collectionView.collection,
          childrenContainer = collectionView.itemViewContainer ? collectionView.$(collectionView.itemViewContainer) : collectionView.$el,
          children = childrenContainer.children(),
          indices = [],
          sortNumber = function(a,b) { return a - b; },
          goHereIndex, i;

      // Get the indices off of the child containers.
      children.each(function() {
        var $sibling = $(this),
            siblingCid = $sibling.data('item-cid'),
            siblingItem = collection.get({cid: siblingCid}),
            siblingIndex = collection.indexOf(siblingItem);
        indices.push(siblingIndex);
      });

      // There are two possibilites here. Either:
      //
      // 1) We are adding an item at an index that doesn't yet exist in the
      //    collection view. For example, this happens when the collection
      //    first gets loaded into view. Each model's item gets added to the
      //    view, but not necessarily in order.
      // 2) We are adding an item at an index currenly occupied by another
      //    item. This happens when we add a new item to the collection after
      //    the view has already been rendered.
      //
      // In the latter case, where the index is already used, we need to
      // update the indices list to reflect the added item.

      // console.log('before', indices);
      goHereIndex = indices.indexOf(index);
      if (goHereIndex === -1) {  // Case #1 above

        indices.push(index);
        indices.sort(sortNumber);
        goHereIndex = indices.indexOf(index);

      } else {  // Case #2 above

        indices.splice(goHereIndex, 0, index);
        for (i = goHereIndex + 1; i < indices.length; ++i) {
          indices[i]++;
        }

      }
      // console.log('after', indices);
      // console.log('at', goHereIndex);

      if(goHereIndex === 0) {
        childrenContainer.prepend(itemView.el);
      } else {
        childrenContainer.children().eq(goHereIndex-1).after(itemView.el);
      }

      itemView.$el.data('item-cid', itemView.model.cid);
    }
  };

}(Planbox, jQuery));
