import jolly.json_encode

from jolly.json_encode import encode, make_object_decoder

def get_api_property_encoders(settings):
    api_property_encoders = jolly.json_encode.get_api_property_encoders(settings)
    api_property_encoders.update({
        'DamageAllocationChart' : (lambda dac: dac.name),
        'SpeedPlot' : (lambda speedplot: 'speedplot'),
        'AccelerationLimit' : (lambda limit: {'maximum-speed': limit.max_speed,
                                              'maximum-addition': limit.max_addition,
                                              'maximum-multiplication': limit.max_multiple}),
        'TurnMode' : (lambda turnmode: turnmode.name),
        'Duration' : (lambda duration: {'turns': 'turns', 'impulses': duration.impulses})
    })
    return api_property_encoders

def get_api_encoders(settings):
    api_encoders = jolly.json_encode.get_api_encoders(settings, get_api_property_encoders(settings))
    return api_encoders

def get_db_encoders(settings):
    db_encoders = jolly.json_encode.get_db_encoders(settings)
    db_encoders.update({
        'DamageAllocationChart' : (lambda dac: dac.name),
        'SpeedPlot' : (lambda speedplot: {'$class': 'sfb.movement.SpeedPlot',
                                          'speeds': 'speeds'}),
        'AccelerationLimit' : (lambda limit: {'$class': 'sfb.movement.AccelerationLimit',
                                              'maximum-speed': limit.max_speed,
                                              'maximum-addition': limit.max_addition,
                                              'maximum-multiplication': limit.max_multiple}),
        'TurnMode' : (lambda turnmode: turnmode.name),
        'Duration' : (lambda duration: {'$class': 'sfb.chrono.Duration',
                                        'turns': duration.turns if duration.turns_only else 0,
                                        'impulses': None if duration.turns_only else duration.impulses})
    })
    return db_encoders

def get_db_decoders(settings, decoder):
    db_decoders = jolly.json_encode.get_db_decoders(settings, decoder)
    db_decoders.update({
        'sfb.movement.SpeedPlot' : make_object_decoder({'speeds': 'speeds'}, decoder),
        'sfb.movement.AccelerationLimit' : make_object_decoder({'maximum-speed': 'max_speed', 
                                                                'maximum-addition': 'max_addition',
                                                                'maximum-multiplication': 'max_multiple'}, decoder),
        'sfb.chrono.Duration' : make_object_decoder({'turns': 'turns',
                                                     'impulses': 'impulses'}, decoder),
    })
    return db_decoders
