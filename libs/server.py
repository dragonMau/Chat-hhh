from asyncio import sleep
from os import path
from time import time_ns

import socketio
from aiohttp import web

from lib import HexStr, Message, Storage, get
from window import Gui


class Server:
    sio: socketio.AsyncServer
    app: web.Application
    gui: Gui
    storage: Storage
    
    async def kick(self, sid: str) -> None:
        await self.sio.emit("stop", to=sid)
        await self.sio.disconnect(sid)
    
    async def index(self, request) -> web.Response:
        with open('./public/index.html') as f:
            return web.Response(text=f.read(), content_type='text/html')
    
    def init_handler(self) -> None:
        
        @self.sio.on('connect')
        async def connect(sid, *_):
            self.storage.users[sid] = HexStr(sid)
                    
        @self.sio.on('register')
        async def register(sid, data, *_):
            result = "error"
            usr_name: HexStr = HexStr.from_str(data["usr"])
            pwd: str = data["pwd"]
            if not path.exists(f"./local/users/{usr_name.to_hex()}"):
                with open(f"./local/users/{usr_name.to_hex()}", "w") as f:
                    f.write(f"{pwd}\n")
                    f.write(f"{usr_name.to_str()}\n")
                result = "ok"
            else:
                result = "overlap"
            await self.sio.emit("register answer", result, to=sid)
            
        @self.sio.on('login')
        async def login(sid, data, *_):
            t = time_ns()
            usr_name: HexStr = HexStr.from_str(data["usr"])
            pwd = data["pwd"]
            usr_path = f"./local/users/{usr_name.to_hex()}"
            if not path.exists(usr_path):
                await self.sio.emit("login answer", {"code":"wrong usr", "new":""}, to=sid)
                return
            with open(usr_path, "r") as f:
                user_data = f.read().split("\n")
                if pwd != user_data[0]:
                    await self.sio.emit("login answer", {"code":"wrong pwd", "new":""}, to=sid)
                    return
            buf = []
            for x_sid, x_name in self.storage.users.items():
                if x_name == usr_name:
                    await self.kick(x_sid)
                    buf.append(x_sid)
                if x_sid == sid:
                    buf.append(x_sid)
            for i in buf:
                self.storage.users[i]=""
                del self.storage.users[i]
            self.storage.users[sid] = usr_name
            with open("./public/chat.html", "r") as f:
                await self.sio.emit("login answer", {"code":"ok", "new":f.read(), "req_id":str(t)}, to=sid)
            
            await sleep(1)
            await self.sio.emit("message", time_ns())
            self.gui.write("\n"+ usr_name.to_str() +" joined")
            with open(f"./local/messages/list", "a") as f:
                f.writelines(Message(HexStr(), usr_name.to_str() + " joined").dump())
            
        @self.sio.on('message')
        async def print_message(sid, raw_message, *_):
            if raw_message:
                await self.sio.emit("message", time_ns())
                message = Message(self.storage.users[sid], raw_message)
                self.gui.write("\n" + message.pack()[1])
                with open(f"./local/messages/list", "a") as f:
                    f.writelines(message.dump())
            
            
        @self.sio.on('disconnect')
        async def disconnect(sid, *_):
            user_name = self.storage.users[sid]
            await self.sio.emit("message", time_ns())
            self.gui.write("\n"+ user_name.to_str() +" left")
            with open(f"./local/messages/list", "a") as f:
                f.writelines(Message(HexStr(), user_name.to_str() +" left").dump())
            del self.storage.users[sid]
        
        @self.sio.on('request')
        async def request(sid, data, *_):
            d = [Message.load(i).pack() for i in get(f"./local/messages/list", int(data["point"]), data["option"]) if len(i.split()) == 3]
            await self.sio.emit("request answer", d, to=sid)
    
    def __init__(self, gui, storage) -> None:
        self.storage = storage
        self.gui = gui
        self.sio = socketio.AsyncServer()
        self.app = web.Application()
        self.sio.attach(self.app)
        
        self.init_handler()
        
        self.app.router.add_static('/static', './public')
        self.app.router.add_get('/', self.index)
