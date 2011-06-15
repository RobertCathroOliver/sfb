SFB = typeof SFB == 'undefined' ? {} : SFB;

/* Create a new Window */
SFB.Window = function(container, content, options) {
    /* Prepare our options */
    this.options = this.defaults;
    for (var i in options) {
        this.options[i] = options[i]
    }

    /* Set up the outer container i.e. the window div */
    this.container = $(container);
    this.container.empty();
    this.container.addClass('window');

    /* Keep this accessible */
    this.content = content;

    /* Resize the container if required */
    if (this.options.width != 'container') {
        this.container.width(options.width);
    }
    if (this.options.height != 'container') {
        this.container.height(options.height);
    }

    /* Assign the display area */
    this.display_area = this.container;

    var drag_options = {'stack': '.window'};

    /* Set up scrolling */
    if (this.options.scrollable) {
        /* Wrap the display area for scrolling to exclude the scroll bars */
        this.scroll_area = $('<div></div>').addClass('scrollable');
        this.display_area = $('<div></div>');
        this.scroll_area.append(this.display_area)
        this.container.append(this.scroll_area);

        /* Prevent dragging when on the scroll bar */
        drag_options.handle = this.display_area;
    }

    /* Add our content to the display area */
    this.display_area.append(content);

    /* Setup dragging */
    this.container.draggable(drag_options);
}

SFB.Window.prototype = {
    defaults : { width: 'container',
                 height: 'container',
                 scrollable: false
               }
};
