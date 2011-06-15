SFB = typeof SFB == 'undefined' ? {} : SFB;
SFB.Map = function(width, height, tokens, options) {
    var self = this;
    var defaults = {size: 20, draw_labels: false, font: 'Arial'};

    var _width = width;
    var _height = height;
    var _tokens = tokens;

    var _size = options ? options.size || defaults.size : defaults.size;
    var _draw_labels = options ? options.draw_labels || defaults.draw_lables : defaults.draw_labels;
    var _font = options ? options.font || defaults.font : defaults.font;

    /* sin(60deg) */
    var sin60 = Math.sin(Math.PI / 3.0);
    /* Create a canvas for a map of the given size */
    var create_canvas = function(size) {
        var canvas = $('<canvas></canvas>').get(0);
        canvas.width = Math.ceil((1.5 * _width + 2) * size + 1);
        canvas.height = Math.ceil((2.0 * _height + 1) * sin60 * size + 1)
        return canvas;
    };
    var _hex_offsets = [[-1, 0], [-0.5, -sin60], [0.5, -sin60],
                        [1, 0], [0.5, sin60], [-0.5, sin60]];
    /* Draw a hexagon on the context centered at (x, y) */
    var draw_hexagon = function(ctx, x, y, size) {
        ctx.beginPath();
        for (var i=0; i<_hex_offsets.length; ++i) {
            ctx.lineTo(x + _hex_offsets[i][0] * size,
                       y + _hex_offsets[i][1] * size);
        }
        ctx.closePath();
        ctx.stroke();
    };
    /* Draw a label on the context centered at (x, y) */
    var draw_label = function(ctx, label, x, y, size) {
        ctx.save();
        ctx.textBaseline = 'top';
        ctx.font = (size / 2.0 - 4) + 'pt ' + _font;
        var label_width = ctx.measureText(label).width; 
        ctx.fillText(label, x - label_width / 2.0, y - sin60 * size);
        ctx.restore();
    };

    /* Calculate the hex coordinates of screen coordinates (x, y) */
    this.to_position = function(x, y) {
        var xx = x / _size, yy = y / _size;
        var X_ = Math.floor(2.0 * xx), Y_ = Math.floor(yy / sin60);
        var X_r = xx - X_ / 2.0, Y_r = yy - Y_ * sin60;
        var _X = Math.floor(X_ / 3.0), _Y = Math.floor((Y_ - _X%2) / 2.0);

        function is_forward(x, y) {
            return x%6 == 0 && y%2 == 0 || x%6 == 3 && y%2 == 1;
        }
        function is_backward(x, y) {
            return x%6 == 3 && y%2 == 0 || x%6 == 0 && y%2 == 1;
        }
        function is_above_forward(x, y) { return y < -1.9 * x + 0.85; }
        function is_above_backward(x, y) { return y < 1.9 * x; }
        if (is_forward(X_, Y_) && is_above_forward(X_r, Y_r)) {
            _X -= 1;
            if (Y_%2 == 0) { _Y -= 1; } 
        } else if (is_backward(X_, Y_) && !is_above_backward(X_r, Y_r)) {
            _X -= 1;
            if (Y_%2 == 0) { _Y += 1; }
        }
        return new SFB.Position(_X, _Y);
    };

    this.draw = function(container) {
        var canvas = create_canvas(_size);
        var ctx = canvas.getContext('2d');

        // format the labels
        function f(n) { return n < 10 ? '0' + n : '' + n; }
        // draw the hexagons
        for (var x=0; x<_width; ++x) {
            for (var y=0; y<_height; ++y) {
                var xy = (new SFB.Position(x, y)).to_screen(_size);
                draw_hexagon(ctx, xy.x, xy.y, _size);
                if (_draw_labels) {
                    draw_label(ctx, f(x+1)+f(y+1), xy.x, xy.y, _size);
                }
            }
        }
        // draw the tokens
        for (var i=0; i<_tokens.length; ++i) {
            _tokens[i].draw(ctx, _size);
        }
        var wdw = SFB.Window.create(container, canvas, 
		                    {scrollable: true,
				     width: 512,
				     height: 512});
    };
};
SFB.Position = function(x, y, facing) {
    var self = this;
    var _x = x;
    var _y = y;
    var _facing = facing || '';

    /* Angles for each rotation */
    var _rotations = {'A': 0.0, 'B': Math.PI / 3.0, 'C': 2.0 * Math.PI / 3.0,
                     'D': Math.PI, 'E': 4.0 * Math.PI / 3.0,
                     'F': 5.0 * Math.PI / 3.0, '': 0.0};
    /* Return the screen coordinates for the center of this position */
    this.to_screen = function(size) {
        var hh = size * Math.sqrt(3.0) / 2.0;
        return {x: 1.5 * _x * size + size, y: 2 * _y * hh + hh + (_x%2) * hh};
    };
    /* Return the angle for this position's facing */
    this.rotation = function() {
        return _rotations[_facing] || 0.0;
    };

};
SFB.Token = function(img, position) {
    var self = this;
    var _img = img;
    var _position = position;

    /* Update the position of this token */
    this.move = function(position) {
        _position = position;
    };
    /* Draw this position to a canvas */
    this.draw = function(ctx, size) {
        _img.onload = function() {
	    var xy = _position.to_screen(size);
            ctx.save();
            ctx.translate(xy.x, xy.y);
            ctx.scale(size / 20.0, size / 20.0);
            ctx.rotate(_position.rotation());
            ctx.drawImage(_img, -_img.width / 2.0, -img.height / 2.0);
            ctx.restore();
        };
        if (_img.complete) { _img.onload(); }
    };
};

