from pathlib import Path
from time import time_ns


class HexStr:
    data: str
    def __init__(self, data: str = " ") -> None:
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

class Message:
    id: int
    owner: HexStr
    content: HexStr
    
    @staticmethod
    def load(line: str) -> None:
        try:
            id, owner, content = line.split()
        except ValueError as e:
            print(line)
            raise ValueError(e)
        m = Message(HexStr.from_hex(owner), "")
        m.id = int(id)
        m.content = HexStr.from_hex(content)
        return m
    
    def dump(self) -> str:
        return f"\n{self.id} {self.owner.to_hex()} {self.content.to_hex()}" #
    
    def pack(self) -> str:
        return {0:self.id, 1:self.owner.to_str()+": "+self.content.to_str()}
    
    def __init__(self, name: HexStr, data: str) -> None:
        self.id = time_ns()
        self.owner = name
        self.content = HexStr(data)
    
class Storage:
    users: dict[str:HexStr] #  userdata
    messages: list[Message] #  data
    def __init__(self) -> None:
        self.users = {}
        self.messages = []

def get(file_path: str, point: int, option: str = "before" or "after") -> list:
    if option == "before": baf = 40
    elif option == "after": baf = 0
    else: raise Exception(f"option must be \"before\" or \"after\", not \"{option}\"")
    p = Path(file_path)
    size = p.stat().st_size
    last_n, n, i, seek = -2, -1, 1, int(size/2)
    with open(file_path, 'r') as f:
        while last_n != n and point != n:
            i += 1
            f.seek(seek)
            last_n = n
            f.readline()
            n = int(f.readline().split()[0]) # list index out if range, need to fix
            if n > point:
                seek -= int(size/2**i)
            else:
                seek += int(size/2**i)
        f.seek(seek)
        f.readline()
        f.readline()
        for i in range(baf):
            while (f.read(1) != "\n") and (seek > 1):
                seek = f.seek(seek - 1)

        return_list = []
        for i in range(20):
            return_list.append(f.readline())
        return return_list