// Set the default image path for Leaflet explicitly, since we move files
// around as bart of the grunt build.
if (window.L) {
  window.L.Icon.Default.imagePath = '/static/images';
}
