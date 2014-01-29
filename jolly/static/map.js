SFB = SFB || {};

/* Create a new Map */
SFB.Map = function(width, height) {
    this.width = width;
    this.height = height;
    this.tokens = {};
}

SFB.Map.prototype = {
    defaults : { size : 20 },
    add_token : function(id, position) {
        this.tokens[id] = position;
        $(this).trigger('map-change', {id: id, position: position});
    },

    remove_token : function(id) {
        delete this.tokens[id];
        $(this).trigger('map-change', {id: id});
    },

    move_token : function(id, position) {
        if (id in this.tokens) {
            delete this.tokens[id];
        }
        this.add_token(id, position);
    },

    create_window : function(container, get_token_address, options) {
        /* Prepare our options */
        var opts = this.defaults;
        for (var i in options) {
            opts[i] = options[i];
        }

        /* Retain a reference to the map */
        var map = this;

        /* Cache token images */
        var token_images = {};

        /* Calculate sin(60deg) once */
        var sin60 = Math.sin(Math.PI / 3.0);

        /* Prepare the canvas */
        var content = $('<canvas></canvas>');
        var canvas = content.get(0);
        canvas.width = Math.ceil((1.5 * map.width + 0.5) * opts.size + 2);
        canvas.height = Math.ceil((2 * map.height + 1) * sin60 * opts.size + 1);
        if (!opts.width) {
            opts.width = canvas.width;
        }
        if (!opts.height) {
            opts.height = canvas.height;
        }
       
        /* These tokens are already drawn */
        var draw_tokens = [];    

        /* Load a token image */
        function load_token_image(token_id, onload) {
            var img = new Image();
            var url = get_token_address(token_id);
            if (onload) {
                img.onload = onload;
            }
            img.src = url;
            return img;
        }
        for (var token_id in map.tokens) {
            token_images[token_id] = load_token_image(token_id);
        }

        /* Offsets of hex corners for hex of radius 1 */
        var hex_offsets = [[-1, 0], [-0.5, -sin60], [0.5, -sin60],
                           [1, 0], [0.5, sin60], [-0.5, sin60]];

        /* Draw a hexagon on the drawing context centered at (x, y) */
        function draw_hexagon(context, x, y, size) {
            context.beginPath();
            for (var i = 0; i < hex_offsets.length; ++i) {
                context.lineTo(x + hex_offsets[i][0] * size,
                               y + hex_offsets[i][1] * size);
            }
            context.closePath();
            context.stroke();
        }

        var window = new SFB.Window(container, canvas, opts);
        window.size = opts.size;

        /* Draw a token on the drawing context centered at (x, y) */
        function draw_token(context, img, x, y, rotation, size) {
            var position = window.to_screen({x: x, y: y}, size);
            context.save();
            context.translate(position.x, position.y);
            context.scale(img.width / size, img.height / size);
            context.rotate(rotation);
            context.drawImage(img, -img.width / 2, -img.height / 2);
            context.restore();
        }

        /* Convert a map position to a screen position */
        window.to_screen = function(position, size) {
            var hh = size * sin60;
            return {x: 1.5 * position.x * size + size,
                    y: 2 * position.y * hh + hh + (position.x % 2) * hh};
        };

        /* Convert a screen position to a map position */
        window.to_map = function(position, size) {

        };

        /* Convert a facing to an angle */
        window.to_angle = function(rotation) {
            return {'A': 0, 'B': Math.PI / 3, 'C': 2 * Math.PI / 3,
                    'D': Math.PI, 'E': 4 * Math.PI / 3, 'F': 5 * Math.PI / 3,
                    '0': 0}[rotation];
        };

        /* Draw the map on the canvas */
        window.draw = function() {
            var context = this.content.getContext('2d');
            var size = this.size;

            /* Draw the hexagons */
            for (var x = 0; x < map.width; ++x) {
                for (var y = 0; y < map.height; ++y) {
                    var position = this.to_screen({x: x, y: y}, size);
                    draw_hexagon(context, position.x, position.y, size);
                }
            }

            /* Draw the tokens */
            for (var token_id in map.tokens) {
                var img = token_images[token_id];
                var token = map.tokens[token_id];
                var position = this.to_screen({x: token.x, y: token.y}, size);
                var rotation = this.to_angle(token.facing);
                draw_token(context, img, x, y, rotation, size);
            }
        };
        window.redraw = function() {
            var context = this.content.getContext('2d');
            this.draw();
        };

        $(this).on('map-change', function(event, data) {
            var token_id = data.id;
            if (token_id && !(token_id in token_images)) {
                token_images[token_id] = load_token_image(token_id, function() { window.draw(); });
            } else {
                window.draw();
            }
        });
        return window;
    }
};
