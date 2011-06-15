var SpeedPlot = new Class({
    IMPULSES_PER_TURN: 32,

    Implements: [Options],
    options: {
        speed_limits: {
            constant_acceleration: 10,
            multiple_acceleration: 2,
            impulses_between_changes: 8,
            first_change_impulse: 3,
            last_change_impulse: 28,
            maximum_speed: 31
        },
        previous_plot: [{speed: 31, duration: IMPULSES_PER_TURN}]
    },
    plot: [{speed: 0, duration: IMPULSES_PER_TURN}],

    initialize: function(plot, options) {
        this.setOptions(options);
        this.plot = plot;
        this.previous_plot = this.options.previous_plot;
        this.normalize();
        if (!this.validate()) {
            throw new Exception('Invalid Plot');
        }

        this.impulse_speeds = function(plot) {
            var result = [];
            for (var i=0; i<plot.length; ++i) {
                plot[i].duration.times(function() { result.push(plot[i].speed); });
            }
            return result;
        }.bind(this)(plot);

        this.impulse_moves = function(speeds) {
            var moves = [];
            for (var i=0; i<this.IMPULSES_PER_TURN; ++i) {
                var has_move = false;
                for (var k=0; i<speeds; ++k) {
                    if (i == Math.ceil(this.IMPULSES_PER_TURN / speeds[i] * (k + 1)) - 1) {
                        has_move = true;
                        break;
                    }
                }
                result.push(has_move);
            }
        }.bind(this)(this.impulse_speeds);
    },
    normalize: function() {
        var result = [{speed: this.plot[0].speed,
                       duration: this.plot[0].duration}];
        var index = 0;
        for (var i=1; i<plot.length; ++i) {
            if (plot[i].duration == 0) { continue; }
            if (plot[i].speed == result[index].speed) {
                result[index].duration += plot[i].duration;
                continue;
            }
            result.push({speed: this.plot[i].speed,
                         duration: this.plot[i].duration});
            ++index;
        }
        this.plot = result;
    },
    validate: function() {
        var speed_limits = this.options.speed_limits;
        if (!this.plot || this.plot.length == 'undefined' || 
             this.plot.length == 0) {
            return false;
        }
        if (this.plot[0].duration < speed_limits.first_change_impulse) {
            return false;
        }
        if (this.plot.length > 1 && 
            this.IMPULSES_PER_TURN - this.plot[this.plot.length-1].duration >
            speed_limits.last_change_impulse) {
            return false;
        }
        var speeds = $A(this.previous_plot.impulse_speeds).extend(this.plot.impulse_speeds);
        var current_impulse = 0;
        for (var i=0; i<this.plot.length; ++i) {
            if (this.plot[i].duration < speed_limits.impulses_between_changes) {
                return false;
            }
            if (this.plot[i].speed > this.maximum_speed(Math.min.run(speeds.slice(current_impulse, current_impulse + this.IMPULSES_PER_TURN)))) {
                return false;
            }
            current_impulse += this.plot[i].duration;
        }
        return true;
    },
    maximum_speed: function(speed) {
        return Math.min(this.speed_limits.maximum_speed,
                    Math.max(speed + this.speed_limits.constant_acceleration,
                             speed * this.speed_limits.multiple_acceleration));
    },
    toString: function() {
        var result = 'SpeedPlot([';
        for (var i=0; i<this.plot.length; ++i) {
            result += '{speed: ' + this.plot[i].speed + ', ' +
                       'duration: ' + this.plot[i].duration + '}';
            if (i != this.plot.length-1) {
                result += ', ';
            }
        }
        result += '])';
        return result;
    }
});
