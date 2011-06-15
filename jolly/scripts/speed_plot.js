SFB = typeof SFB == 'undefined' ? {} : SFB;
SFB.SpeedPlot = function(plot, previous_plot, options) {
    var self = this;

    this.set_options = function(options) {
        var defaults = {IMPULSES_PER_TURN: 32,
                        speed_limits: {constant_acceleration: 10,
                                       multiple_acceleration: 2,
                                       impulses_between_changes: 8,
                                       first_change_impulse: 3,
                                       last_change_impulse: 28,
                                       maximum: 31}
        };
        options = SFB.make_option_parser(defaults)(options);
        self.IMPULSES_PER_TURN = options.IMPULSES_PER_TURN;
        self.speed_limits = SFB.make_option_parser(defaults.speed_limits)(options.speed_limits);
    };
    this.set_options(options);
    previous_plot = previous_plot || [{speed: this.speed_limits.maximum,
                                       duration: this.IMPULSES_PER_TURN}];
    /* Is the given plot valid */
    var validate = function(plot, previous_plot) {
        if (!plot || plot.length == 'undefined' || plot.length == 0) { 
            return false;
        }
        if (plot.length > 1 &&
                plot[0].duration < self.speed_limits.first_change_impulse) {
            return false;
        }
        var total_duration = 0;
        for (var i=0; i<plot.length; ++i) {
            total_duration += plot[i].duration;
        }
        if (total_duration != self.IMPULSES_PER_TURN) {
            return false;
        }
        if (plot.length > 1 && 
            self.IMPULSES_PER_TURN - plot[plot.length - 1].duration > self.speed_limits.last_change_impulse) {
            return false;
        }
        var previous_speeds = calculate_speeds(previous_plot);
        if (plot[0].speed > max_possible_speed(Math.min.apply(null, previous_speeds), self.speed_limits)) {
            return false;
        }
        var min_speed = plot[0].speed;
        var current_impulse = 0;
        for (var i=1; i<plot.length-1; ++i) {
            if (plot[i].duration < self.speed_limits.impulses_between_changes) {
                return false;
            }
            var previous_min = Math.min.apply(null, previous_speeds.slice(current_impulse))
            var maximum = max_possible_speed(Math.min(min_speed, previous_min), self.speed_limits);
            if (plot[i].speed > maximum) {
                return false;
            }
            if (plot[i].speed < min_speed) { min_speed = plot[i].speed; }
            current_impulse += plot[i].duration;
        }
        return true;
    };
    /* Determine the maximum speed given acceleration limits */
    var max_possible_speed = function(speed, limits) {
        return Math.min(limits.maximum, 
                Math.max(speed + limits.constant_acceleration, 
                         speed * limits.multiple_acceleration));
    };
    /* Determine the speed each impulse given a plot */
    var calculate_speeds = function (plot) {
        var speeds = [];
        var j = 0;
        var seg_end = plot[0].duration;
        for (var i=0; i<self.IMPULSES_PER_TURN; ++i) {
            if (i >= seg_end) { ++j; seg_end += plot[j].duration; }
            speeds.push(plot[j].speed);
        }
        return speeds;
    }
    /* Determine the which impulses have moves given the speed each impulse */
    function calculate_moves(speeds) {
        var moves = [];
        for (var i=0; i<self.IMPULSES_PER_TURN; ++i) {
            var has_move = false;
            for (var k=0; k<speeds[i]; ++k) {
               if (i == Math.ceil(self.IMPULSES_PER_TURN / speeds[i] * (k + 1)) - 1) {
                   has_move = true;
                   break;
               }
            }
            moves.push(has_move);
        }
        return moves;
    }
    var _impulse_speeds = calculate_speeds(plot);
    var _impulse_moves = calculate_moves(_impulse_speeds);

    /* Create the DOM for the speeds */
    var create_speed_dom = function(plot) {
        var root = $('<div>').addClass('speeds');
        function create_speed_node(speed, duration) {
            var seg_width = Math.max(0, 16 * duration - 2);
	    var event = create_hover_handlers(speed);
            var node = $('<div />').addClass('speed')
                                   .width(seg_width)
                                   .data('initial_width', seg_width)
                                   .text(speed)
				   .hover(event.start, event.end);
            return node;
        }
        function create_slider_node() {
            var event = create_drag_handlers(plot, root);
            var node = $('<div />').addClass('slider')
                                   .draggable({axis: 'x',
                                               containment: 'parent',
                                               grid: [16, 0],
                                               drag: event.drag,
                                               stop: event.stop});
            return node;
        }
        root.append(create_speed_node(plot[0].speed -1, 0).hide());
        root.append(create_slider_node());
        for (var i=0; i<plot.length; ++i) {
            root.append(create_speed_node(plot[i].speed, plot[i].duration));
            root.append(create_slider_node());
        }
        root.append(create_speed_node(plot[plot.length-1].speed - 1, 0).hide());
        return root;
    };
    /* Create the DOM for the moves */
    var create_moves_dom = function() {
        var root = $('<div />').addClass('moves');
        for (var i=0; i<self.IMPULSES_PER_TURN; ++i) {
            root.append($('<div />').text(i+1));
        }
        return root;
    };
    /* Highlight the impulses with moves */
    var highlight_moves = function(impulse_moves, context) {
        $('.moves div', context).each(function(i, v) {
            $(v).toggleClass('move', impulse_moves[i]);
        });
    }
    /* Draw the speedplot */
    this.draw = function(container) {
        var speeds = create_speed_dom(plot);
        var moves = create_moves_dom();

        var window = SFB.Window.create(container, [speeds, moves], {width: 514, height: 29});
        highlight_moves(_impulse_moves, $(container));
    };
    /*  handlers for dragging */
    var create_drag_handlers = function(plot, context) {
        var handle_drag = function(event, ui) {
            if (ui.position.left == 0) {
                $(this).prev().width($(this).prev().data('initial_width'));
                $(this).next().width($(this).next().data('initial_width'));
            } else {
                var access = ui.position.left > 0 ? 
                               {p: 'prev', n: 'next', delta: -1} :
                               {p: 'next', n: 'prev', delta: 1};
                var p = $(this)[access.p]();
                p.width(Math.max(0, p.data('initial_width') - ui.position.left * access.delta)).show();
                var n = $(this)[access.n]();
                while (access.delta * ui.position.left < 0) {
                    n.width(Math.max(0, n.data('initial_width') + ui.position.left * access.delta));
                    if (!n.width()) { n.hide(); } else { n.show(); }
                    ui.position.left += access.delta * Math.min(-1 * access.delta * ui.position.left, n.data('initial_width'));
                    n = n[access.n]()[access.n]();
                    n[access.p]().width(ui.position.left == 0 ? 2 : 0);
                }
            }
        };
        var handle_stop = function(event, ui) {
            var new_plot = plot_from_dom($(this).parent, plot);
            if (validate(new_plot, previous_plot)) { plot = new_plot; }

            $(context).replaceWith(create_speed_dom(plot));
            _impulse_speeds = calculate_speeds(plot);
            _impulse_moves = calculate_moves(_impulse_speeds);
            highlight_moves(_impulse_moves, context.parent());
        };
        return {drag: handle_drag, stop: handle_stop};
    };
    /* Create a new plot from the DOM speed widths and the given plot */
    var plot_from_dom = function(root, plot) {
        var new_plot = [];
        $('.speed', root).each(function(k, v) {
            var duration = Math.ceil($(v).width() / 16);
            if (duration==0) { return; }
            var speed = k == 0 ? plot[0].speed - 1 :
                        k > plot.length ? plot[plot.length-1].speed - 1 :
                        plot[k-1].speed;
            new_plot.push({speed: speed, duration: duration});
        });
        return normalize_plot(new_plot);
    };
    var normalize_plot = function(plot) {
	var result = [{speed: plot[0].speed, duration: plot[0].duration}];
	var index = 0;
	for (var i=1; i<plot.length; ++i) {
	    if (plot[i].duration == 0) { continue; }
	    if (plot[i].speed == result[index].speed) {
		result[index].duration += plot[i].duration;
		continue;
	    }
	    result.push({speed: plot[i].speed, duration: plot[i].duration});
	    ++index;
	}
	return result;
    };
    /* Create event handlers for acceleration/deceleration changes */
    var create_hover_handlers = function(speed) {
        function create_speed_changer(increment) {
            return function(event) {
                var root = $(event.target).parents('.speeds');
                var new_plot = plot_from_dom(root, plot);
                root.children('.speed').each(function(k, v) {
                    if (v == event.target.parentElement) {
                        new_plot[k-1].speed += increment;
                    }
                });
	        new_plot = normalize_plot(new_plot);	
                if (validate(new_plot, previous_plot)) { 
                    plot = new_plot; 
		}
                $(root).replaceWith(create_speed_dom(plot));
                _impulse_speeds = calculate_speeds(plot);
                _impulse_moves = calculate_moves(_impulse_speeds);
                highlight_moves(_impulse_moves);
            };
        }
        var handle_hover = function(event) {
            $(this).empty();
            var minus = $('<span />').addClass('minus')
                                     .text('-')
                                     .click(create_speed_changer(-1));
            var plus = $('<span />').addClass('plus')
                                    .text('+')
                                    .click(create_speed_changer(1));
	    $(event.target).append(minus)
		           .append($('<span />').text(speed))
			   .append(plus);
        };
        var handle_unhover = function(event) {
	    $(this).empty().text(speed);
        };
        return {start: handle_hover, end: handle_unhover};
    };
    function show_plot(plot) {
        var out = '';
        for (var i=0; i<plot.length; ++i) {
            out += '(' + plot[i].speed + ' : ' + plot[i].duration + ')';
        }
        return out;
    }
};
