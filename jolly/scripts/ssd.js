SFB = typeof SFB == 'undefined' ? {} : SFB;

SFB.ShipSystemDisplay = function(layout, options) {
    var self = this;
    var _defaults = {size: 15};

    var _size = options.size;

    var _min_x = 0;
    var _max_x = 0;
    var _min_y = 0;
    var _max_y = 0;

    this.set_options = function(options) {
	options = options || _defaults;


    };
    this.to_screen = function(x, y) {
        return {x: (x - _min_x + 0.5) * _size + 1,
                y: (y - _min_y + 0.5) * _size + 1};
    };
    var create_shapes = function(shapes) {
        var result = [];
        for (var i=0; i<shapes.length; ++i) {
	    var c = self.to_screen(shapes[i].x, shapes[i].y);
	    shapes[i].x = c.x;
	    shapes[i].y = c.y;
            result.push(SFB.Shapes.make(shapes[i]));
        }
        return result;
    };
    var create_boxes = function(boxes) {
	var result = [];
	for (var i=0; i<boxes.length; ++i) {
	}
	return result;
    };
    var create_canvas = function(size) {
        var canvas = $('<canvas></canvas>').get(0);
        canvas.width = (max_x - min_x + 1) * size + 2;
        canvas.height = (max_y - min_y + 1) * size + 2;
        return canvas;
    };
};

function ShipSystemDisplay(layout) {
    var self = this;
    this.size = 15;

    var min_x = 0;
    var max_x = 0;
    var min_y = 0;
    var max_y = 0;
    $.each(layout['boxes'], function(key, value) {
        if (value.x < min_x) { min_x = value.x; }
        if (value.x > max_x) { max_x = value.x; }
        if (value.y < min_y) { min_y = value.y; }
        if (value.y > max_y) { max_y = value.y; }
    });
    $.each(layout['labels'], function(key, value) {
        if (value.x < min_x) { min_x = value.x; }
        if (value.x > max_x) { max_x = value.x; }
        if (value.y < min_y) { min_y = value.y; }
        if (value.y > max_y) { max_y = value.y; }
    });
    $.each(layout['shapes'], function(key, value) {
        var min_xs = [value.x, value.x - value.radius, value.x1, value.x2];
        var max_xs = [value.x + value.width, value.x + value.radius, value.x1, value.x2];
        var min_ys = [value.y, value.y - value.radius, value.y1, value.y2];
        var max_ys = [value.y + value.height, value.y + value.radius, value.y1, value.y2];
        for (var x in min_xs) {
            if (min_xs[x] != undefined && min_xs[x] < min_x) { min_x = min_xs[x]; }
        }
        for (var x in max_xs) {
            if (max_xs[x] != undefined && max_xs[x] > max_x) { max_x = max_xs[x]; }
        }
        for (var y in min_ys) {
            if (min_ys[y] != undefined && min_ys[y] < min_y) { min_y = min_ys[y]; }
        }
        for (var y in max_ys) {
            if (max_ys[y] != undefined && max_ys[y] > max_y) { max_y = max_ys[y]; }
        }
    });

    this.canvas_size = function() {
        return [(max_x - min_x + 1) * this.size + 2, (max_y - min_y + 1) * this.size + 2];
    };

    this.to_screen = function(x, y) {
        return {'x': (x - min_x + 0.5) * self.size + 1,
                'y': (y - min_y + 0.5) * self.size + 1};
    };

    this.draw = function(container) {
        $(container).empty();
        var canvas = $('<canvas></canvas>');
        var canvas_size = this.canvas_size();
        canvas.get(0).width = canvas_size[0];
        canvas.get(0).height = canvas_size[1];
        var ctx = canvas.get(0).getContext('2d');
        
        $(container).append(canvas)
                    .addClass('ssd')
                    .draggable({'handle': 'canvas', 'stack': '.ui-draggable'});

        if (self.size >= 3) {
            $.each(layout['boxes'], function(key, value) {
                var v = self.to_screen(value.x, value.y);
                ctx.strokeRect(v.x - self.size / 2.0, v.y - self.size / 2.0, self.size, self.size);
                if (value.label != undefined && self.size >= 15) {
                    ctx.save();
                    ctx.textBaseline = 'top';
                    var label_width = ctx.measureText(value.label).width;
                    ctx.fillText(value.label, v.x - label_width / 2.0, v.y - self.size / 2.0 + 1);
                    ctx.restore();
                }
            });
        }
        if (self.size >= 15) {
            $.each(layout['labels'], function(index, value) {
                draw_label(ctx, value.label, value.x, value.y);
            });
        }
        $.each(layout['shapes'], function(index, value) {
            switch (value.shape) {
                case 'circle':
                    draw_circle(ctx, value.x, value.y, value.radius);
                    break;
                case 'line':
                    draw_line(ctx, value.x1, value.y1, value.x2, value.y2);
                    break;
                case 'rectangle':
                    draw_rect(ctx, value.x, value.y, value.width, value.height);
                    break;
                default:
                    break;
            }
        });
    };

    function draw_label(ctx, label, x, y) {
        ctx.save();
        ctx.textBaseline = 'bottom';
        ctx.font = '6pt Arial';
        var label_width = ctx.measureText(label).width;
        var v = self.to_screen(x, y);
        ctx.fillText(label, v.x - label_width / 2.0, v.y + self.size / 2.0 - 1);
        ctx.restore();
    };

    function draw_circle(ctx, x, y, radius) {
        var v = self.to_screen(x, y);
        ctx.beginPath();
        ctx.arc(v.x, v.y, radius * self.size, 0, Math.PI * 2.0, false);
        ctx.stroke();
    };

    function draw_line(ctx, x1, y1, x2, y2) {
        var v1 = self.to_screen(x1, y1);
        var v2 = self.to_screen(x2, y2);
        ctx.beginPath();
        ctx.moveTo(v1.x, v1.y);
        ctx.lineTo(v2.x, v2.y);
        ctx.stroke();
    };

    function draw_rect(ctx, x, y, width, height) {
        var v = self.to_screen(x, y);
        ctx.beginPath();
        ctx.rect(v.x, v.y, width * self.size, height * self.size);
        ctx.stroke();
    };

}

SFB.Shapes = {};
SFB.Shapes.make = function(arg) {
    var shape = SFB.Shapes[arg.type.charAt(0) + arg.type.slice(1)];
    var keys = shape.keys;
    var args = [];
    for (var i=0; i<keys.length; ++i) {
        args.push(arg[keys[i]]);
    }
    function F() {
        return shape.apply(this, args);
    }
    F.prototype = shape.prototype;
    return new F();
};
SFB.Shapes.Circle = function(x, y, radius) {
    this.draw = function(ctx) {
        ctx.beginPath();
        ctx.arc(x, y, 0, Math.PI * 2.0, false);
        ctx.stroke();
    };
    this.box = function() {
        return {min_x: x - radius, max_x: x + radius,
                min_y: y - radius, max_y: y + radius};
    }
};
SFB.Shapes.Circle.keys = ['x', 'y', 'radius'];
SFB.Shapes.Line = function(x1, y1, x2, y2) {
    this.draw = function(ctx) {
        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2);
        ctx.stroke();
    };
    this.box = function() {
        return {min_x: Math.min(x1, x2), max_x: Math.max(x1, x2),
                min_y: Math.min(y1, y2), max_y: Math.max(y1, y2)}; 
    };
};
SFB.Shapes.Line.keys = ['x1', 'y1', 'x2', 'y2'];
SFB.Shapes.Rectangle = function(x, y, w, h) {
    this.draw = function(ctx) {
        ctx.beginPath();
        ctx.rect(x, y, w, h);
        ctx.stroke();
    };
    this.box = function() {
        return {min_x: x, max_x: x + w,
                min_y: y, max_y: y + h};
    };
};
SFB.Shapes.Rectangle.keys = ['x','y','width','height'];
