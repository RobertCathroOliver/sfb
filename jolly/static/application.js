SFB = typeof SFB == 'undefined' ? {} else SFB;

/* Create a new Application */
SFB.Application = function(url) {
    /* This URL is the starting point for the application */
    this.base_url = url;

    /* Some default settings for ajax requests */
    var base_ajax_settings = {
	'cache': false,
	'contentType': 'application/json',
	'dataType': 'json',
	'type': 'GET'
    };

    this.submit_ajax_request = function(url, options) {
	var settings = base_ajax_settings;
	for (var i in options) {
	    settings[i] = options[i];
	}
	settings.url = url;
        $.ajax(settings);
    }

    var command_list = {};
    function load_command_template(url) {
	if (url in command_list) {
	    return command_list[url];
	}
	var on_load = function(data, textStatus, jqXHR) {
	    command_list[url] = new SFB.Command(data);
	};
	this.submit_ajax_request(url, {success: on_load});
    }

};

SFB.Command = function(template) {

    var CommandArgument = function(template) {
	this.name = template.name;
	this.required = template.required;
	this.type = SFB.InputType(template.type);
    };

    this.name = template.name;
    this.step = template.step;
    this.can_cancel = template.can_cancel;
    this.required = template.required;
    this.arguments = {};
    for (var i in template.arguments) {
	this.arguments[i] = new CommandArgument(template.arguments[i]);
    }
};
SFB.Command.prototype = {
    this.required_fields = function() {
        var result = {'time': SFB.InputType('time')(this.step)};
	for (var i in this.arguments) {
	    if (this.arguments[i].required) {
		result[this.arguments[i].name] = this.arguments[i].type;
	    }
	}
	return result;
    },

    this.queue = function(url, data) {
	var on_queue = function(data, textStatus, jqXHR) {
	    $(data).trigger('command-queued');
	};
	var on_error = function(jqXHR, textStatus, errorThrown) {
	    $(data).trigger('error-command-queue', jqXHR.responseText)
	}
	var options = {type: 'POST', data: data, success: on_queue, error: on_error};
	SFB.Application.submit_ajax_request(url, options);
    },

    this.update = function(url, data) {
	var on_update = function(data, textStatus, jqXHR) {
	    $(data).trigger('command-updated');
	};
	var on_error = function(jqXHR, textStatus, errorThrown) {
	    $(data).trigger('error-command-update', jqXHR.responseText)
	}
	var options = {type: 'PUT', data: data, success: on_update, error: on_error};
	SFB.Application.submit_ajax_request(url, options);
    },

    this.cancel = function(url) {
	var on_cancel = function(data, textStatus, jqXHR) {
	    $(data).trigger('command-cancelled');
	};
	var on_error = function(jqXHR, textStatus, errorThrown) {
	    $(data).trigger('error-command-cancel', jqXHR.responseText)
	}
	var options = {type: 'DELETE', success: on_cancel, error: on_error};
	SFB.Application.submit_ajax_request(url, options);
    },
};
