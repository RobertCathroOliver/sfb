def create_command(request, value_resolver):

    # Determine whether the user is authenticated
    if not request.user:
        return Unauthorized()

    # Convert the data from XML/JSON to a Python dict
    try:
        data = parse_request(request)
    except MalformedData:
        return MalformedDataResponse(Command)

    # Ensure that a 'command' is present in the dict
    try:
        command_data = data['command']
    except KeyError:
        return MalformedDataResponse(Command)

    # Ensure that a valid template is present
    try:
        template_uri = command_data['template_href']
        template = get_object_by_uri(template_uri)
        if not isinstance(template, CommandTemplate):
            raise KeyError("No template by that name exists.")
        template_arguments = template.arguments
    except KeyError:
        return MalformedDataResponse(Command)

    # Determine the parameters that have been set
    try:
        request_parameters = command_data['parameters']
    except KeyError:
        request_parameters = {}
    response_parameters = {}

    # Determine the time
    try:
        time = value_resolver.resolve(request_parameters['time'])
        response_parameters['time'] = time
        del request_parameters['time']
    except KeyError:
        response_parameters['time'] = None
    except ValueError:
        response_parameters['time'] = None
        del request_parameters['time']

    # Determine the issuer
    try:
        source = value_resolver.resolve(request_parameters['source'])
        issuer = source.parent
        if not issuer in request.user.players:
            return Unauthorized()
    except KeyError, ValueError, AttributeError:
        response_parameters['source'] = None

    # Determine the arguments
    arguments = {}
    for pname, pvalue in request_parameters.items():
        try:
            arguments[pname] = value_resolver.resolve(pvalue)
	    response_parameters[pname] = arguments[pname]
        except ValueError: 
            pass

    command = Command(issuer, template, time, arguments)

    return command


