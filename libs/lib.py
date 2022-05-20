from time import time_ns


class HexStr:
    data: str
    def __init__(self, data: str = "") -> None:
        self.data = data
    def to_str(self) -> str:
        return self.data
    def to_hex(self) -> str:
        return self.data.encode("utf-8").hex()
    @staticmethod
    def from_hex(hdata):
        return HexStr(bytes.fromhex(hdata).decode("utf-8"))
    @staticmethod
    def from_str(data):
        return HexStr(data)
    
class User:
    user_list = lambda: []
    name: HexStr
    sid: str
    @staticmethod
    def load(name: HexStr):
        return next((x for x in User.user_list() if x.name.data == name.data), None)
    @staticmethod
    def get(sid: str) -> int:
        i = 0
        while User.user_list()[i].sid != sid:
            i += 1
        return i
    def __init__(self, sid: str, name: HexStr = HexStr()) -> None:
        self.sid = sid
        if name.data == "":
            self.name: HexStr = HexStr.from_str(sid)
        else: 
            self.name: HexStr = name


class Message:
    id: int
    owner: User
    content: HexStr
    
    def load(self, line: str) -> None:
        self = Message()
        self.id, owner, content = line.split()
        self.owner = User.load(HexStr.from_hex(owner))
        self.content = HexStr.from_hex(content)
    
    def dump(self) -> str:
        return f"{self.id} {self.owner.name.to_hex()} {self.content.to_hex()}"
    
    def pack(self) -> str:
        return [self.id, f"{self.owner.name.to_str()}: {self.content.to_str()}"]
    
    def __init__(self, name: User, data: str) -> None:
        self.id = time_ns()
        self.owner = name
        self.content = HexStr(data)
    
class Storage:
    users: list[User]  #   userdata
    messages: list[Message] #  data
    def __init__(self) -> None:
        self.users = []
        self.messages = []