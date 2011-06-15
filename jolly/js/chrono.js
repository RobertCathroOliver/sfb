var sfb = (function(sfb) {
    sfb.Moment = function(turn, impulse, step) {
        this.turn = turn;
        this.impulse = impulse;
        this.step = step;
    };
    sfb.Moment.prototype.toString = function() {
        return this.turn + '.' + (this.impulse ? this.impulse + '.': '') + this.step;
    };
    sfb.Moment.fromString = function(value) {
        var moment_regexp = /(\d+)\.(?:(\d+)\.)?([a-z-]+)/;
        var args = moment_regexp.exec(value);
        return new Moment(args[1], args[2], args[3]);
    };
        })(sfb || {});
    
