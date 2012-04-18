;(function ( $, window, document, undefined ) {

    // Calculate sin(60deg) once
    var sin60 = Math.sin(Math.PI / 3);

    // Offsets of hex corners for hex of radius 1
    var hex_offsets = [[-1, 0], [-0.5, -sin60], [0.5, -sin60],
                       [1, 0], [0.5, sin60], [-0.5, sin60]];

    var drawHexagon = function(context, position, size) {
        context.beginPath();
        $.each(hex_offsets, function(index, offsets) {
            context.lineTo(position.x + offsets[0] * size, position.y + offsets[1] * size);
        });
        context.closePath();
        context.stroke();
    };

    var drawToken = function(context, img, position, rotation, size) {
        context.save();
        context.translate(position.x, position.y);
        context.scale(img.width / size, img.height / size);
        context.rotate(rotation);
        context.drawImage(img, -img.width / 2, -img.height / 2);
        context.restore();
    };

    var toScreenCoordinates = function(position, size) {
        var hh = size * sin60;
        return {x: 1.5 * position.x * size + size,
                y: 2 * position.y * hh + hh + (position.x % 2) * hh};
    };

    var toMapCoordinates = function(position, size) {
        var hh = size * sin60;
        var x = (position.x - size) / (1.5 * size);
        var y = (position.y - hh) / (2 * hh);
        var z = -0.5 * x - y;
        y = 0.5 * x + y;
        var ix = Math.floor(x + 0.5);
        var iy = Math.floor(y + 0.5);
        var iz = Math.floor(z + 0.5);
        var s = ix + iy + iz;
        if (s) {
            var abs_dx = Math.abs(ix - x);
            var abs_dy = Math.abs(iy - y);
            var abs_dz = Math.abs(iz - z);

            if (abs_dx >= abs_dy && abs_dx >= abs_dz) {
                ix -= s;
            } else if (abs_dy >= abs_dx&& abs_dy >= abs_dz) {
                iy -= s;
            } else {
                iz -= s;
            }
        }
        return {x: ix, y: Math.floor((iy - iz + (1-ix%2)) / 2)};
    };

    var rotation_map = {'A': 0, 'B': sin60, 'C': 2 * sin60,
                        'D': Math.PI, 'E': 4 * sin60, 'F': 5 * sin60,
                        '0': 0};
    var toAngle = function(facing) {
        return rotation_map[facing.toUpperCase()] || 0;
    };

    $.widget('sfb.mapview', {
        options: {
            size: 20,
        },

        _create: function() {
            var self = this;
            this.lastp = {x: this.options.map.width + 1,
                          y: this.options.map.height + 1};
            this.context = this.element.get(0).getContext('2d');
            this.element.bind('click', function(e) {
                var x = e.pageX - self.element.offset().left;
                var y = e.pageY - self.element.offset().top;
                var p = toMapCoordinates({x: x, y:y}, self.options.size);
                self._trigger('click', e, p);
            });
        },

        _init: function() {
            this._resize(this.options.size);
            this.redraw();
        },

        _resize: function(size) {
            var width = this.options.map.width;
            this.element.get(0).width = Math.ceil((1.5 * width + 0.5) * size + 2);
            var height = this.options.map.height;
            this.element.get(0).height = Math.ceil((2 * height + 1) * sin60 * size + 1);
        },

        redraw: function() {
            var self = this;
            var size = this.options.size;
            var width = this.options.map.width;
            var height = this.options.map.height;
    
            // draw the hexagons
            for (var y = 0; y < height; ++y) {
                for (var x = 0; x < width; ++x) {
                    var position = toScreenCoordinates({x: x, y: y}, size);
                    drawHexagon(this.context, position, size);
                }
            }

            $.each(this.options.map.tokens, function(token) {
                var position = toScreenCoordinates(token.position, size);
                var rotation = toAngle(token.facing);
                drawToken(self.context, token.img, position, rotation, size);
            });
        },

        destroy: function() {
            this.element.unbind('mousemove');
            $.Widget.prototype.destroy.call(this);
        },

        _setOption: function(key, value) {
            $.Widget.prototype._setOption.apply(this, arguments);
            switch(key) {
            case 'size':
                this._resize(value);
                this.redraw();
                break;
            default:
                this.options[key] = value;
                break;
            }
        }
    });
})(jQuery, window, document);
