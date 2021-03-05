class EventDistributorException(Exception):
    pass

class EventDistributor:
    def __init__(self):
        self.event_listeners = {}
        pass
    
    def on(self, event_name:str):
        """
        This is a decorator that attaches to a function accepting a `dict` payload.
        When `event_name` is called, with its payload; the function will be triggered with the payload passed as an argument.
        """
        def wrapper(func):
            self.event_listeners.update({
                event_name: func
            })
        return wrapper
    
    def display_listeners(self):
        import pprint
        pprint.pprint(self.event_listeners)

    def distrbute(self, event_name: str, payload: dict):
        listener = self.event_listeners.get(event_name, None)
        if listener is not None:
            listener(payload)
        else:
            raise EventDistributorException('No such event; make sure this event is correctly added.')

# Testing code:       
# ed = EventDistributor()

# @ed.on_event('process')
# def process(payload):
#     print(payload)
#     return None

# @ed.on_event('make response')
# def process(payload):
#     import pprint
#     print('make response: ', end='\t')
#     pprint.pprint(payload)


# ed.distrbute_event('make response', {'name': 'mkr'})
# ed.distrbute_event('process', {'name': 'process'})