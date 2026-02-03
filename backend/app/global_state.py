from datetime import datetime

class GlobalState:
    last_interaction_timestamp = datetime.now()

    @classmethod
    def update_interaction(cls):
        cls.last_interaction_timestamp = datetime.now()
        
    @classmethod
    def get_last_interaction(cls):
        return cls.last_interaction_timestamp

global_state = GlobalState()
