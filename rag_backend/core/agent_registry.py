
AGENTS = {}

def register_agent(name):
    def wrapper(cls):
        AGENTS[name] = cls()
        return cls
    return wrapper
