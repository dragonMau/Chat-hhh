class User:
    name: str
    def __init__(self, sid, name = ""):
        if name == "":
            self.name = str(sid)
        else:
            self.name = name

class Storage:
    users = {}  #  sid : userdata
    messages = {} #  id : data
    def __init__(self) -> None:
        self.users = {}
        self.messages = {}