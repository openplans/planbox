// Generated on 2014-01-09 using generator-webapp 0.4.6
'use strict';

// # Globbing
// for performance reasons we're only matching one level down:
// 'test/spec/{,*/}*.js'
// use this if you want to recursively match all subfolders:
// 'test/spec/**/*.js'

module.exports = function (grunt) {

  // Load grunt tasks automatically
  require('load-grunt-tasks')(grunt);

  // Time how long tasks take. Can help when optimizing build times
  require('time-grunt')(grunt);

  // Define the configuration for all the tasks
  grunt.initConfig({

    // Project settings
    pkg: grunt.file.readJSON('package.json'),
    yeoman: {
      // Configurable paths
      app: 'src/planbox_ui/static',
      tpl: 'src/planbox_ui/jstemplates',
      test: 'src/planbox_ui/jstests',
      dist: 'dist'
    },

    // Watches files for changes and runs tasks based on the changed files
    watch: {
      js: {
        files: ['<%= yeoman.app %>/scripts/{,*/}*.js'],
        tasks: ['jshint'],
        options: {
          livereload: true
        }
      },
      jstest: {
        files: ['<%= yeoman.test %>/spec/{,*/}*.js'],
        tasks: ['test:watch']
      },
      gruntfile: {
        files: ['Gruntfile.js']
      },
      compass: {
        files: ['<%= yeoman.app %>/styles/{,*/}*.{scss,sass}'],
        tasks: ['compass:server', 'autoprefixer']
      },
      styles: {
        files: ['<%= yeoman.app %>/styles/{,*/}*.css'],
        tasks: ['newer:copy:styles', 'autoprefixer']
      },
      livereload: {
        options: {
          livereload: '<%= connect.options.livereload %>'
        },
        files: [
          '<%= yeoman.tpl %>/{,*/}*.`',
          '.tmp/styles/{,*/}*.css',
          '<%= yeoman.app %>/images/{,*/}*.{gif,jpeg,jpg,png,svg,webp}'
        ]
      }
    },

    // The actual grunt server settings
    connect: {
      options: {
        port: 9000,
        livereload: 35729,
        // Change this to '0.0.0.0' to access the server from outside
        hostname: 'localhost'
      },
      livereload: {
        options: {
          open: true,
          base: [
            '.tmp',
            '<%= yeoman.app %>'
          ]
        }
      },
      test: {
        options: {
          port: 9001,
          base: [
            '.tmp',
            '<%= yeoman.test %>',
            '<%= yeoman.app %>'
          ]
        }
      },
      dist: {
        options: {
          open: true,
          base: '<%= yeoman.dist %>',
          livereload: false
        }
      }
    },

    // Empties folders to start fresh
    clean: {
      dist: {
        files: [{
          dot: true,
          src: [
            '.tmp',
            '<%= yeoman.dist %>/*',
            '!<%= yeoman.dist %>/.git*'
          ]
        }]
      },
      server: '.tmp'
    },

    // Make sure code styles are up to par and there are no obvious mistakes
    jshint: {
      options: {
        jshintrc: '.jshintrc',
        reporter: require('jshint-stylish')
      },
      all: [
        'Gruntfile.js',
        '<%= yeoman.app %>/scripts/{,*/}*.js',
        '!<%= yeoman.app %>/scripts/{,*/}*.min.js',
        '!<%= yeoman.app %>/scripts/vendor/*',
        '<%= yeoman.test %>/spec/{,*/}*.js'
      ]
    },


    // Mocha testing framework configuration options
    mocha: {
      all: {
        options: {
          run: true,
          urls: ['http://<%= connect.test.options.hostname %>:<%= connect.test.options.port %>/index.html']
        }
      }
    },



    // Compiles Sass to CSS and generates necessary files if requested
    compass: {
      options: {
        sassDir: '<%= yeoman.app %>/styles',
        cssDir: '.tmp/styles',
        generatedImagesDir: '.tmp/images/generated',
        imagesDir: '<%= yeoman.app %>/images',
        javascriptsDir: '<%= yeoman.app %>/scripts',
        fontsDir: '<%= yeoman.app %>/styles/fonts',
        importPath: '<%= yeoman.app %>/bower_components',
        httpImagesPath: '/images',
        httpGeneratedImagesPath: '/images/generated',
        httpFontsPath: '/styles/fonts',
        relativeAssets: false,
        assetCacheBuster: false
      },
      dist: {
        options: {
          generatedImagesDir: '<%= yeoman.dist %>/images/generated'
        }
      },
      server: {
        options: {
          debugInfo: true
        }
      }
    },

    // Add vendor prefixed styles
    autoprefixer: {
      options: {
        browsers: ['last 1 version']
      },
      dist: {
        files: [{
          expand: true,
          cwd: '.tmp/styles/',
          src: '{,*/}*.css',
          dest: '.tmp/styles/'
        }]
      }
    },

    // Automatically inject Bower components into the HTML file
    'bower-install': {
      app: {
        html: '<%= yeoman.tpl %>/index.html',
        ignorePath: '<%= yeoman.app %>/'
      }
    },

    // Renames files for browser caching purposes
    rev: {
      dist: {
        files: {
          src: [
            '<%= yeoman.dist %>/scripts/{,*/}*.js',
            '<%= yeoman.dist %>/styles/{,*/}*.css',
            '<%= yeoman.dist %>/images/{,*/}*.{gif,jpeg,jpg,png,webp}',
            '<%= yeoman.dist %>/styles/fonts/{,*/}*.*'
          ]
        }
      }
    },

    // This is not very useful for Django templates
    // --------------------------------------------
    // Reads HTML for usemin blocks to enable smart builds that automatically
    // concat, minify and revision files. Creates configurations in memory so
    // additional tasks can operate on them
    // useminPrepare: {
    //   options: {
    //     dest: '<%= yeoman.dist %>'
    //   },
    //   html: '<%= yeoman.tpl %>/index.html'
    // },

    // // Performs rewrites based on rev and the useminPrepare configuration
    // usemin: {
    //   options: {
    //     assetsDirs: ['<%= yeoman.dist %>']
    //   },
    //   html: ['<%= yeoman.dist %>/{,*/}*.html'],
    //   css: ['<%= yeoman.dist %>/styles/{,*/}*.css']
    // },

    // The following *-min tasks produce minified files in the dist folder
    imagemin: {
      dist: {
        files: [{
          expand: true,
          cwd: '<%= yeoman.app %>/images',
          src: '{,*/}*.{gif,jpeg,jpg,png}',
          dest: '<%= yeoman.dist %>/images'
        }]
      }
    },
    svgmin: {
      dist: {
        files: [{
          expand: true,
          cwd: '<%= yeoman.app %>/images',
          src: '{,*/}*.svg',
          dest: '<%= yeoman.dist %>/images'
        }]
      }
    },

    // This is not very useful for Django templates
    // --------------------------------------------
    // htmlmin: {
    //   dist: {
    //     options: {
    //       collapseBooleanAttributes: true,
    //       collapseWhitespace: true,
    //       removeAttributeQuotes: true,
    //       removeCommentsFromCDATA: true,
    //       removeEmptyAttributes: true,
    //       removeOptionalTags: true,
    //       removeRedundantAttributes: true,
    //       useShortDoctype: true
    //     },
    //     files: [{
    //       expand: true,
    //       cwd: '<%= yeoman.dist %>',
    //       src: '{,*/}*.html',
    //       dest: '<%= yeoman.dist %>'
    //     }]
    //   }
    // },

    cssmin: {
      dist: {
        files: {
          '<%= yeoman.app %>/styles/style.min.css': [
            '<%= yeoman.app %>/bower_components/normalize-css/normalize.css',
            '<%= yeoman.app %>/styles/style.css'
          ],
          '<%= yeoman.app %>/styles/print.min.css': [
            '<%= yeoman.app %>/styles/print.css'
          ],
          '<%= yeoman.app %>/styles/admin.min.css': [
            '<%= yeoman.app %>/styles/admin.css',
            '<%= yeoman.app %>/bower_components/pickadate/lib/themes/classic.css',
            '<%= yeoman.app %>/bower_components/pickadate/lib/themes/classic.date.css'
          ]
        }
      }
    },
    uglify: {
      options: {
        banner: '/*! <%= pkg.name %> <%= grunt.template.today("yyyy-mm-dd") %> */\n'
      },
      dist: {
        files: {
          '<%= yeoman.app %>/scripts/components.min.js': [
            '<%= yeoman.app %>/bower_components/jquery/jquery.js',
            '<%= yeoman.app %>/bower_components/handlebars/handlebars.js',
            '<%= yeoman.app %>/bower_components/underscore/underscore.js',
            '<%= yeoman.app %>/bower_components/backbone/backbone.js',
            '<%= yeoman.app %>/bower_components/backbone.marionette/lib/backbone.marionette.js',
            '<%= yeoman.app %>/bower_components/backbone-relational/backbone-relational.js',
            '<%= yeoman.app %>/bower_components/swag/lib/swag.js'
          ],
          '<%= yeoman.app %>/scripts/components-admin.min.js': [
            '<%= yeoman.app %>/bower_components/jqueryui/ui/jquery.ui.core.js',
            '<%= yeoman.app %>/bower_components/jqueryui/ui/jquery.ui.widget.js',
            '<%= yeoman.app %>/bower_components/jqueryui/ui/jquery.ui.mouse.js',
            '<%= yeoman.app %>/bower_components/jqueryui/ui/jquery.ui.sortable.js',
            '<%= yeoman.app %>/bower_components/jqueryui-touch-punch/jquery.ui.touch-punch.js',
            '<%= yeoman.app %>/bower_components/django-csrf.js/django-csrf.js',
            '<%= yeoman.app %>/bower_components/pen/src/pen.js',
            '<%= yeoman.app %>/bower_components/FileAPI/dist/FileAPI.js',
            '<%= yeoman.app %>/bower_components/moment/moment.js',
            '<%= yeoman.app %>/bower_components/chrono/chrono.min.js',
            '<%= yeoman.app %>/bower_components/pickadate/lib/picker.js',
            '<%= yeoman.app %>/bower_components/pickadate/lib/picker.date.js'
          ],
          '<%= yeoman.app %>/scripts/app.min.js': [
            '<%= yeoman.app %>/scripts/utils.js',
            '<%= yeoman.app %>/scripts/handlebars-helpers.js',
            '<%= yeoman.app %>/scripts/models.js',
            '<%= yeoman.app %>/scripts/views/mixins.js',
            '<%= yeoman.app %>/scripts/views/base.js',
            '<%= yeoman.app %>/scripts/views/display.js',
            '<%= yeoman.app %>/scripts/views/admin/section.js',
            '<%= yeoman.app %>/scripts/views/admin/project.js',
            '<%= yeoman.app %>/scripts/app.js'
          ],
          '<%= yeoman.app %>/scripts/modernizr.min.js': [
            '<%= yeoman.app %>/bower_components/modernizr/modernizr.js'
          ]
        }
      }
    },
    concat: {
      dist: {}
    },

    // Copies remaining files to places other tasks can use
    copy: {
      dist: {
        files: [{
          expand: true,
          dot: true,
          cwd: '<%= yeoman.app %>',
          dest: '<%= yeoman.dist %>',
          src: [
            '*.{ico,png,txt}',
            '.htaccess',
            'images/{,*/}*.webp',
            '{,*/}*.html',
            'styles/fonts/{,*/}*.*'
          ]
        }]
      },
      styles: {
        expand: true,
        dot: true,
        cwd: '<%= yeoman.app %>/styles',
        dest: '.tmp/styles/',
        src: '{,*/}*.css'
      }
    },



    // Run some tasks in parallel to speed up build process
    concurrent: {
      server: [
        'compass:server',
        'copy:styles'
      ],
      test: [
        'copy:styles'
      ],
      dist: [
        'compass',
        'copy:styles',
        'imagemin',
        'svgmin'
      ]
    }
  });


  grunt.registerTask('serve', function (target) {
    if (target === 'dist') {
      return grunt.task.run(['build', 'connect:dist:keepalive']);
    }

    grunt.task.run([
      'clean:server',
      'concurrent:server',
      'autoprefixer',
      'connect:livereload',
      'watch'
    ]);
  });

  grunt.registerTask('server', function () {
    grunt.log.warn('The `server` task has been deprecated. Use `grunt serve` to start a server.');
    grunt.task.run(['serve']);
  });

  grunt.registerTask('test', function(target) {
    if (target !== 'watch') {
      grunt.task.run([
        'clean:server',
        'concurrent:test',
        // 'autoprefixer',
      ]);
    }

    grunt.task.run([
      'connect:test',
      'mocha'
    ]);
  });

  grunt.registerTask('build', [
    // 'clean:dist',
    // 'useminPrepare',
    // 'concurrent:dist',
    // 'autoprefixer',
    'concat',
    'cssmin',
    'uglify',
    // 'copy:dist',
    // 'rev',
    // 'usemin',
    // 'htmlmin'
  ]);

  grunt.registerTask('default', [
    'newer:jshint',
    'test',
    'build'
  ]);
};
