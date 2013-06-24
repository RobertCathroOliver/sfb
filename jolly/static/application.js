var SFB = window.SFB || {};

SFB.Error = {
    INVALID_LOGIN : {
        'message': 'Invalid login'
    },
    RESOURCE_UNAVAILABLE : {
        'message': 'Unable to locate resource'
    }
};

SFB.TemplateMapper = function(template_map) {
    return function(id) {
        return template_map.map[id];
    };
};

SFB.Loader = (function() {

    var type_map = {
        'root': SFB.Root,
        'game': SFB.Game,
        'user': SFB.User,
        'player': SFB.Player,
        'log': SFB.Log,
        'status': SFB.Status,
        'unit': SFB.ShipSystemDisplay.create,
        'queue': SFB.CommandQueue,
        'command-template': SFB.CommandTemplate,
        'system': SFB.System,
        'system-prototype': SFB.Prototype,
        'map': SFB.Map.create,
        'command': SFB.Command,
        'template-mapper': SFB.TemplateMapper,
        'layout': function(x) { return x; }
    };

    var construct = function(root_url) {
        var base_settings = {
            type: 'GET',
            dataType: 'json',
            contentType: 'application/json'
        };

        var _username;
        var _password;
        var ajax = function(type, url, data, on_success, on_error, settings) {
            var settings = $.extend(base_settings, settings);
            settings.type = type;
            settings.success = on_success;
            settings.error = on_error;
            url = 'http://' + root_url + '/' + url;
            if (_username && _password) {
                settings.beforeSend = function(xhr) {
                    xhr.setRequestHeader('Authorization', 'Basic ' + btoa(_username+':'+_password));
                }
            }
            $.ajax(url, settings);
        };

        var load = function(url, on_success, on_failure) {
            ajax('GET', url, {}, function(data) {
                if ($.isArray(data)) {
                    $.each(data, function(index, value) {
                        on_success(type_map[value.type](function(url, on_success) {
                            load(url, on_sucess, on_failure);
                        }, value));
                    });
                } else {
                    on_success(type_map[data.type](function(url, on_sucess) {
                        load(url, on_success, on_failure);
                    }, data));
                }
            }, function() {
                on_failure(SFB.Error.RESOURCE_UNAVAILABLE);
            });
        };

        var login = function(username, password, on_success, on_failure) {
            _username = undefined;
            _password = undefined;
            ajax('GET', 'user', {'email': username}, function(data) {
                if (data.length === 1) {
                    user = data[0];
                    _username = username;
                    _password = password;
                    ajax('GET', user.href, {}, function(data) {
                        on_success(data);
                    }, function() {
                        _username = undefined;
                        _password = undefined;
                        on_failure(SFB.Error.INVALID_LOGIN);
                    });
                } else {
                    on_failure(SFB.Error.INVALID_LOGIN);
                }
            }, function(data) {
                on_failure(SFB.Error.INVALID_LOGIN);
            });
        };

        var logout = function() {
            _username = undefined;
            _password = undefined;
        };

        return {
            login: login,
            logout: logout,
            load: load
        };
    };

    return construct;
})();

SFB.Application = (function(root_url, chrome_url) {

    var loader = SFB.Loader(root_url);
    var chrome_loader = SFB.Loader(chrome_url);
    var cache = {};

    var handleError = function(error) {
        console.log(error.message);
    };

    var login = function() {
        var $form = $('#login');
        var $username = $form.find('input[name="username"]');
        var $password = $form.find('input[name="password"]');
        var $submit = $form.find('input[type="submit"]');
        $username.val('');
        $password.val('');
        $password.removeClass('error');
        var submit = function(e) {
            e.preventDefault();
            $username.removeClass('error');
            $password.removeClass('error');
            var error = false;
            if (!$username.val()) {
                $username.addClass('error');
                error = true;
            }
            if (!$password.val()) {
                $password.addClass('error');
                error = true;
            }
            if (error) {
                $form.one('submit', submit);
                return;
            }
            loader.login($username.val(), $password.val(), function(user) {
                alert(user.name + ' logged in');
                $form.hide();
                $('#overlay').hide();
            }, handleError);
        };
        $form.one('submit', submit);
        $('#anonymous').one('click', function() {
            loader.logout();
            alert('Logged in Anonymously!');
            $form.hide();
            $('#overlay').hide();
        });
        $('#overlay').show();
        $form.show();
    };

    var logout = function() {
        loader.logout();
    };

    var createWindow = function(content, options) {
        var options = options || {};
        var drag_options = {
            handle: $(content),
            stack: '.window'
        };
        var w = $('<div />').addClass('window').append($(content)).draggable(drag_options);
        if (options.width) {
            w.width(options.width);
        }
        if (options.height) {
            w.height(options.height);
        }
        $('body').append(w);
        return w;
    };

    var load = function(url, callback, skip_cache) {
        if (!skip_cache && cache[url]) {
            callback(cache[url]);
        } else {
            loader.load(url, function(result) { 
                cache[url] = result; 
                callback(result); 
            }, handleError);
        }
    };

    var loadUnit = function(url, callback, skip_cache) {
        if (!skip_cache && cache[url]) {
            callback(cache[url]);
        } else {
            load(url, function(result) {
                var subsystems = [];
                var owner = result.owner.href;
                var properties = result.properties;
                var prototype = result.prototype.href;
                var count = result.subsystems.length;
                if (count === 0) {
                    callback(new SFB.ShipSystemDisplay(result.id, owner, prototype, properties, subsystems));
                }
                $.each(result.subsystems, function(index, system) {
                    load(system.href, function(system_result) {
                        subsystems.push(new SFB.ShipSystemDisplay(system_result.id, system_result.owner.href, system_result.prototype.href, system_result.properties, system_result.subsystems));
                        if (subsystems.length >= count) {
                            callback(new SFB.ShipSystemDisplay(result.id, owner, prototype, properties, subsystems));
                        }
                    }, false);
                });
            }, false);
        }
    };

    var showMap = function(map, chrome_url, options) {
        chrome_loader.load(chrome_url, function(template_mapper) {
            createWindow($('<div />').mapview({map: map, template_mapper: function(id) { return template_mapper(id).icon; }}), options);
        }, handleError);
    };

    var showSSD = function(ssd, chrome_url, options) {
        chrome_loader.load(chrome_url, function(template_mapper) {
            chrome_loader.load(template_mapper(ssd.getId()).ssd, function(layout) {
                createWindow($('<div />').ssdview({ssd: ssd, layout: layout}), options);
            }, handleError);
        }, handleError);
    };

    return {
        login: login,
        logout: logout,
        load: load,
        showMap: showMap,
        showSSD: showSSD
    };
})('api.sfb.local', 'static.sfb.local');

