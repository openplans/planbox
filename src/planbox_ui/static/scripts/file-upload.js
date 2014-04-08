/*globals jQuery FileAPI */

// https://github.com/shichuan/javascript-patterns/blob/master/jquery-plugin-patterns/lightweight.html
;(function ($, window, document, undefined) {
  'use strict';

  // Create the defaults once
  var pluginName = 'fileUpload',
  defaults = {
    url: null,
    data: {},
    dndOver: $.noop,
    dndDrop: $.noop,
    start: $.noop,
    progress: $.noop,
    complete: $.noop,
    validate: function() { return true; },
    imagePreview: null
  };

  // The actual plugin constructor
  function FileUpload(element, options) {
    this.element = element;

    // jQuery has an extend method that merges the
    // contents of two or more objects, storing the
    // result in the first object. The first object
    // is generally empty because we don't want to alter
    // the default options for future instances of the plugin
    this.options = $.extend( {}, defaults, options) ;

    this._defaults = defaults;
    this._name = pluginName;

    this.init();
  }


  // Prefetches an image file for a url to speed up load time
  // Takes an optional callback.
  FileUpload.prototype.prefetchImage = function(url, callback) {
    var img = new window.Image();
    img.addEventListener('load', callback, false);
    img.src = url;
  };

  // File Uploads
  FileUpload.prototype.previewImage = function(file, callback) {
    // Display the image preview.
    FileAPI.Image(file).get(function(err, img) {
      var url;
      if (!err) {
        url = img.toDataURL(file.type); //FileAPI.toDataURL(img);
        callback(url);
      }
    });
  };

  FileUpload.prototype.upload = function(file) {
    var data = $.extend({'Content-Type': file.type}, this.options.data);

    if (!this.options.validate(file)) {
      return;
    }

    // Start the upload.
    FileAPI.upload({
      url: this.options.url,
      data: data,
      files: {file: file},
      cache: true,
      upload: $.proxy(this.options.start, this.element),
      progress: $.proxy(this.options.progress, this.element),
      complete: $.proxy(this.options.complete, this.element)
    });
  };

  FileUpload.prototype.handleFileInputChange = function(evt) {
    evt.preventDefault();
    var files = FileAPI.getFiles(evt);
    this.upload(files[0]);
  };

  FileUpload.prototype.initDropZone = function(el) {
    if( FileAPI.support.dnd ){
      FileAPI.event.dnd(el,
        $.proxy(this.options.dndOver, this.element),
        $.proxy(this.options.dndDrop, this.element));
    }
  };

  FileUpload.prototype.init = function () {
    // Place initialization logic here
    // You already have access to the DOM element and
    // the options via the instance, e.g. this.element
    // and this.options

    $(this.element).on('change', $.proxy(this.handleFileInputChange, this));
    this.initDropZone(this.element);
  };

  // A really lightweight plugin wrapper around the constructor,
  // preventing against multiple instantiations
  $.fn[pluginName] = function ( options ) {
    return this.each(function () {
      if (!$.data(this, pluginName)) {
        $.data(this, pluginName, new FileUpload(this, options));
      }
    });
  };

}(jQuery, window, document));
