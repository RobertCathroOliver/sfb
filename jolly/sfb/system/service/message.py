class Message(Service):
    """Provide the ability for a Unit to post messages."""

    def __init__(self):
        props = [FormalParameter('message', str, True, '')]
        super(Message, self).__init__('message', props)
    
