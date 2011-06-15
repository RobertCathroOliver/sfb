SFB = SFB || {};

SFB.Window = {
    create : function(container, content, options) {
                 var window = Object.create(this);
                 window.init(container, content, this.set_options(options));
                 return window;
             },
    set_options : SFB.make_option_parser({scrollable: false}),
    init : function(container, content, options) {
               var drag_options = {'stack': '.window'};

               this.container = $(container);
	       this.container.empty();
               this.container.addClass('window');
	       if (options.width) { this.container.width(options.width); }
               this.display_area = this.container;
               if (options.scrollable) {
                   if (!content.length) { drag_options.handle = content; }
                   this.display_area = $('<div></div>').addClass('scrollable');
		   if (options.width) {this.display_area.width(options.width);}
		   if (options.height) {this.display_area.height(options.height);}
                   this.container.append(this.display_area);
               }
	       if (content.length) {
		   for (var i=0; i<content.length; ++i) {
		       this.display_area.append(content[i]);
		   }
	       } else {
                   this.display_area.append(content);
	       }
               this.container.draggable(drag_options);
           },
    addClass : function(class) {
		   return this.display_area.addClass(class);
	       }
};
Object.defineProperty(SFB.Window, 'width',
    { get: function() { 
               return this.container.width; 
           },
      set: function(width) {
               this.container.width(width);
           },
      configurable: false,
      enumerable: true
    });
Object.defineProperty(SFB.Window, 'height',
    { get: function() { 
               return this.container.height; 
           },
      set: function(height) {
               this.container.height(height);
           },
      configurable: false,
      enumerable: true
    });

