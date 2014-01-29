var SFB = {};
SFB.Root = function() {
    console.log('Root');
};
SFB.Game = function(id, title) {
    this.getId = function() {
        return id;
    };

    this.getTitle = function() {
        return title;
    };
};

SFB.Game.create = function(load, data) {
    return new SFB.Game(data.href, data.title);
};
SFB.User = function() {
    console.log('User');
};
SFB.Player = function() {
    console.log('Player');
};
SFB.Log = function() {
    console.log('Log');
};
SFB.Status = function() {
    console.log('Status');
};
SFB.CommandQueue = function() {
    console.log('CommandQueue');
};
SFB.CommandTemplate = function() {
    console.log('CommandTemplate');
};
SFB.Prototype = function() {
    console.log('Prototype');
};
SFB.Command = function() {
    console.log('Command');
};
SFB.System = function(id, owner, prototype, properties, subsystems) {
    this.getId = function() {
        return id;
    };

    this.getOwner = function() {
        return owner;
    };

    this.getPrototype = function() {
        return prototype;
    };

    this.properties = properties;
    this.subsystems = subsystems;
};
SFB.System.getParams = function() {
    return ['id', 'owner', 'prototype', 'properties', 'subsystems'];
};

SFB.Map = function(width, height, tokens) {
    var self = this;

    this.getWidth = function() {
        return width;
    };
    this.getHeight = function() {
        return height;
    };

    var tokens = tokens || [];
    this.getTokens = function() {
        return tokens;
    };
    this.addToken = function(token) {
        tokens.push(token);
        $(self).trigger('map-change');
    };

    this.removeToken = function(token) {
        var index = tokens.indexOf(token);
        if (index != -1) {
            tokens.splice(index, 1);
            $(self).trigger('map-change');
        }
    };
};
SFB.Map.create = function(load, data) {
    var tokens = [];
    $.each(data.units, function(index, unit) {
        var position = SFB.Position(unit.position);
        tokens.push({
            id: unit.id,
            position: {x: position.x, y: position.y},
            facing: position.facing,
        });
    });
    return new SFB.Map(data.width, data.height, tokens);
};

SFB.Position = function(position) {
    return {
        x: parseInt(position.substring(0, 2), 10),
        y: parseInt(position.substring(2, 4), 10),
        facing: position.substring(4)
    }
};

SFB.ShipSystemDisplay = function(id, owner, prototype, properties, subsystems) {
    this.getId = function() {
        return id;
    };

    this.getOwner = function() {
        return owner;
    };

    this.getPrototype = function() {
        return prototype;
    };

    this.properties = properties;
    this.subsystems = subsystems;
    var self = this;

    var systems = $.extend({}, subsystems);

    this.isDamaged = function(system_id) {
        var system = systems[system_id];
        if (system === undefined) {
            return false;
        }
        return system.damaged;
    };

    this.updateSystem = function(system_id, property, value) {
        var system = systems[system_id];
        if (system === undefined) {
            return;
        }
        system[property] = value;
        $(self).trigger('ssd-change');
    };
};
SFB.ShipSystemDisplay.create = function(load, data) {
    return new SFB.ShipSystemDisplay(data.id, data.owner, data.prototype, data.properties, data.subsystems);
};
;(function ($, window, document, undefined) {

    var makeSVG = function(tag, attributes) {
        var el = document.createElementNS('http://www.w3.org/2000/svg', tag);
        $.each(attributes, function(name, value) {
            el.setAttribute(name, value);
        });
        return el;
    };

    var createBox = function(id, params) {
        return makeSVG('rect', {'data-id': id, 'class': 'box', 'x': params.x, 'y': params.y, 'width': '1', 'height': '1', 'vector-effect': 'non-scaling-stroke'});
    };

    var createDamage = function(position) {
        var g = makeSVG('g', {'stroke': 'black', 'fill': 'black', 'stroke-width': '2'});
        g.appendChild(makeSVG('line', {'x1': position.x, 'y1': position.y, 'x2': position.x + 1, 'y2': position.y + 1, 'vector-effect': 'non-scaling-stroke'}));
        g.appendChild(makeSVG('line', {'x1': position.x, 'y1': position.y + 1, 'x2': position.x + 1, 'y2': position.y, 'vector-effect': 'non-scaling-stroke'}));
        return g;
    };

    var createLabel = function(params, size) {
        var label = makeSVG('text', {'x': params.x * size, 'y': params.y * size - 2, 'text-anchor': 'middle', 'font-size': '8pt', 'font-family': 'sans-serif'});
        var text = document.createTextNode(params.label);
        label.appendChild(text);
        return label;
    };

    var createInnerLabel = function(params, size) {
        var label = makeSVG('text', {'x': (params.x + 1) * size, 'y': (params.y + 1.5) * size , 'text-anchor': 'middle', 'font-size': '8pt', 'style': 'dominant-baseline: middle;', 'font-family': 'sans-serif'});
        var text = document.createTextNode(params.label);
        label.appendChild(text);
        return label;
    };

    var getBounds = {
        circle: function(params) {
            return [params.x - params.radius, params.y - params.radius, params.x + params.radius, params.y + params.radius];
        },
        line: function(params) {
            return [Math.min(params.x1, params.x2), Math.min(params.y1, params.y2), Math.max(params.x1, params.x2), Math.max(params.y1, params.y2)];
        },
        rectangle: function(params) {
            return [params.x, params.y, params.x + params.width, params.y + params.height];
        }
    };

    var createShape = {
        circle: function(params) {
            return makeSVG('circle', {'cx': params.x, 'cy': params.y, 'r': params.radius, 'vector-effect': 'non-scaling-stroke'});
        },
        rectangle: function(params) {
            return makeSVG('rect', {'x': params.x, 'y': params.y, 'width': params.width, 'height': params.height, 'vector-effect': 'non-scaling-stroke'});
        },
        line: function(params) {
            return makeSVG('line', {'x1': params.x1, 'y1': params.y1, 'x2': params.x2, 'y2': params.y2, 'vector-effect': 'non-scaling-stroke'});
        }
    };

    $.widget('sfb.ssdview', {
        options: {
            size: 20,
        },

        _create: function() {
            var svg = makeSVG('svg', {'version': '1.1'});
            var ssd = makeSVG('g', {'stroke-width': '1', 'fill': 'none', 'stroke': 'black'});
            var text = makeSVG('g', {'stroke-width': '1', 'fill': 'black', 'stroke': 'none' });
            svg.appendChild(ssd);
            svg.appendChild(text);
            this.element.append(svg);
            this.svg = svg;
            this.ssd_element = ssd;
            this.text_element = text;
        },

        _init: function() {
            var self = this;
            this.layout = this.options.layout;
            this.ssd = this.options.ssd;
            $(this.ssd).bind('ssd-change', function() {
                self.redraw();
            });
            var min_x = 0, max_x = 0, min_y = 0, max_y = 0;
            $.each(this.layout.boxes, function(key, value) {
                if (value.x < min_x) { min_x = value.x; }
                if (value.x > max_x) { max_x = value.x; }
                if (value.y < min_y) { min_y = value.y; }
                if (value.y > max_y) { max_y = value.y; }
            });

            $.each(this.layout.shapes, function(key, value) {
                var bounds = getBounds[value.shape](value);
                if (bounds[0] < min_x) { min_x = bounds[0]; }
                if (bounds[2] > max_x) { max_x = bounds[2]; }
                if (bounds[1] < min_y) { min_y = bounds[1]; }
                if (bounds[3] > max_y) { max_y = bounds[3]; }
            });
            this.width = max_x - min_x;
            this.height = max_y - min_y;
            this.min_x = min_x;
            this.min_y = min_y;
            this.resize(this.options.size);
            this.redraw();
        },

        resize: function(size) {
            this.options.size = size;
            this.svg.setAttribute('width', ((this.width + 1) * size + 2) + 'px');
            this.svg.setAttribute('height', ((this.height + 1) * size + 2) + 'px');
            var translate_x = 0;
            if (this.min_x < 0) {
                translate_x = -this.min_x;
            }
            var translate_y = 0;
            if (this.min_y < 0) {
                translate_y = -this.min_y;
            }
            this.ssd_element.setAttribute('transform', 'scale('+size+') translate('+translate_x+','+translate_y+')');
            this.text_element.setAttribute('transform', 'scale('+(size/20)+')');
        },

        redraw: function() {
            var self = this;
            while (this.ssd_element.firstChild) {
                this.ssd_element.removeChild(this.ssd_element.firstChild);
            }

            $.each(this.layout.shapes, function(key, value) {
                var shape = createShape[value.shape](value);
                self.ssd_element.appendChild(shape);
            });

            $.each(this.layout.labels, function(key, value) {
                var label = createLabel(value, self.options.size);
                self.text_element.appendChild(label);
            });

            $.each(this.layout.boxes, function(key, value) {
                if (value.label) {
                    var label = createInnerLabel(value, self.options.size);
                    self.text_element.appendChild(label);
                }
                if (self.ssd.isDamaged(key)) {
                    var damage = createDamage(value);
                    self.ssd_element.appendChild(damage);
                }
                var box = createBox(key, value);
                self.ssd_element.appendChild(box);
            });
        },

        destroy: function() {
            this.element.empty();
            $.Widget.prototype.destroy.call(this);
        },

        _setOption: function(key, value) {
            $.Widget.prototype._setOption.apply(this, arguments);
            switch(key) {
            case 'size':
                this.resize(value);
                break;
            default:
                break;
            }
        }
    });
    
})(jQuery, window, document);

;(function ($, window, document, undefined) {

    // Calculate sin(60deg) once
    var sin60 = Math.sin(Math.PI / 3);

    // Offsets of hex corners for hex of radius 1
    var hex_offsets = [[-1, 0], [-0.5, -sin60], [0.5, -sin60],
                       [1, 0], [0.5, sin60], [-0.5, sin60]];
    var hex_coordinates = $.map(hex_offsets, function(x) { return x.join(','); }).join(' ');

    var createHexagon = function(position) {
        var screen_position = toScreenCoordinates(position, 1);
        var translation = screen_position.x + ',' + screen_position.y;
        return makeSVG('polygon', {'data-x': position.x, 'data-y': position.y, 'points': hex_coordinates, 'transform': 'translate('+translation+')', 'vector-effect': 'non-scaling-stroke'});
    };

    var createToken = function(image, position, rotation) {
        var screen_position = toScreenCoordinates(position, 1);
        var translation = screen_position.x + ',' + screen_position.y;
        var angle = toAngle(rotation);
        var token = makeSVG('image', {'x': '-0.5', 'y': '-0.5', 'width': '1', 'height': '1', 'transform': 'translate('+translation+'), rotate('+angle+')'});
        token.setAttributeNS('http://www.w3.org/1999/xlink', 'xlink:href', image);
        return token;
    };

    var toScreenCoordinates = function(position, size) {
        var hh = size * sin60;
        return {x: 1.5 * position.x * size + size,
                y: 2 * position.y * hh + hh + (position.x % 2) * hh};
    };

    var rotation_map = {'A': 0, 'B': 60, 'C': 120,
                        'D': 180, 'E': 240, 'F': 300,
                        '0': 0};
    var toAngle = function(facing) {
        return rotation_map[facing.toUpperCase()] || 0;
    };

    var makeSVG = function(tag, attributes) {
        var el = document.createElementNS('http://www.w3.org/2000/svg', tag);
        $.each(attributes, function(name, value) {
            el.setAttribute(name, value);
        });
        return el;
    };

    $.widget('sfb.mapview', {
        options: {
            size: 20,
        },

        _create: function() {
            var svg = makeSVG('svg', {'version': '1.1'});
            var hexmap = makeSVG('g', {'id': 'hexmap', 'stroke-width': '1', 'fill': 'none', 'stroke': 'black'});
            svg.appendChild(hexmap);
            this.element.append(svg);
            this.svg = svg;
            this.hexmap = hexmap;
        },

        _init: function() {
            var self = this;
            this.map = this.options.map;
            this.template_mapper = this.options.template_mapper;
            $(this.map).bind('map-change', function() {
                self.redraw();
            });
            this.resize(this.options.size);
            this.redraw();
        },

        resize: function(size) {
            this.options.size = size;
            var width = this.map.getWidth();
            this.svg.setAttribute('width', Math.ceil((1.5 * width + 0.5) * size + 2) + 'px');
            var height = this.map.getHeight();
            this.svg.setAttribute('height', Math.ceil((2 * height + 1) * sin60 * size + 1) + 'px');
            this.hexmap.setAttribute('transform', 'scale('+size+')');
        },

        redraw: function() {
            var self = this;
            while (this.hexmap.firstChild) {
                this.hexmap.removeChild(this.hexmap.firstChild);
            }
            var size = this.options.size;
            var width = this.map.getWidth();
            var height = this.map.getHeight();
            var tokens = this.map.getTokens();
    
            // draw the hexagons
            for (var y = 0; y < height; ++y) {
                for (var x = 0; x < width; ++x) {
                    var hexagon = createHexagon({x: x, y: y});
                    this.hexmap.appendChild(hexagon);
                }
            }

            $.each(tokens, function(index, token) {
                var img_src = self.template_mapper(token.id);
                var el = createToken(img_src, token.position, token.facing);
                self.hexmap.appendChild(el);
            });
        },

        destroy: function() {
            this.element.empty();
            $.Widget.prototype.destroy.call(this);
        },

        _setOption: function(key, value) {
            $.Widget.prototype._setOption.apply(this, arguments);
            switch(key) {
            case 'size':
                this.resize(value);
                break;
            default:
                break;
            }
        }
    });
})(jQuery, window, document);

;(function($, window, document, undefined) {
    
    var table_html = '<table><thead><tr><th>Game</th><th>&nbsp;</th></thead><tbody></tbody></table>';
    var row_tmpl = '<tr><td>${title}</td><td><button class="sfb-view-game" data-href="${href}">View</button></td></tr>';

    $.widget('sfb.gamelistview', {
        options: {
        },
    
        _create: function() {
            var self = this;
            this.table = $(table_html);
            this.element.append(this.table);
            this.table.on('click', '.sfb-view-game', function(e) {
        	$(self.element).trigger('view-game', $(this).attr('data-href'));
            });
        },

        _init: function() {
            this.games = this.options.games;
            this.redraw();
        },

        redraw: function() {
            this.table.find('tbody').empty();
            $.tmpl(row_tmpl, this.games).appendTo(this.table.find('tbody'));
        },

        destroy: function() {
            this.table.remove();
            $.Widget.prototype.destroy.call(this);
        },

        _setOption: function(key, value) {
            $.Widget.prototype._setOption.apply(this, arguments);
        
            switch(key) {
            case 'games':
                this.games = this.option.games;
                this.redraw();
                break;
            };
        }
    });
})(jQuery, window, document);

;(function($, window, document, undefined) {

    var players_table_html = '<table><thead><tr><th>Player</th><th>Units</th></tr></thead><tbody></tbody></table>';
    var player_row_tmpl = '<tr><td>${name}</td><td><ul class="unit-list">{{tmpl(units) "#sfb-unit-list-template"}}</ul></td></tr>';
    var player_row_tmpl = '<tr><td>${name}</td><td><ul class="unit-list"></ul></td></tr>';
    var unit_list_tmpl = '<li>${id}</li>';

    $(function() {
        $('<script id="sfb-unit-list-template" type="text/x-jquery-tmpl">'+unit_list_tmpl+'</script>').appendTo('body');
    });

    $.widget('sfb.gamesummary', {
        options: {
        },

        _create: function() {
            this.game = this.options.game;
            this.players_table = $(players_table_html);
            this.element.append(this.players_table);
        },

        _init: function() {
            this.game = this.options.game;
            this.redraw();
        },

        redraw: function() {
            this.players_table.find('tbody').empty();
            $.tmpl(player_row_tmpl, this.game.players).appendTo(this.players_table.find('tbody'));
        },

        destroy: function() {
            this.players_table.remove();
            $.Widget.prototype.destroy.call(this);
        },

        _setOption: function(key, value) {
            $.Widget.prototype._setOption.apply(this, arguments);

            switch(key) {
            case 'game':
                this.game = this.option.game;
                this.redraw();
                break;
            };
        }
    });
})(jQuery, window, document);

