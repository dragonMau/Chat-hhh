from asyncio import sleep
from email.header import Header
from os import path
from time import time_ns

import socketio
from aiohttp import web

from lib import Storage, User, Message, HexStr
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
            self.storage.users.append(User(sid=sid))
        
        @self.sio.on('register')
        async def register(sid, data, *_):
            result = "error"
            usr: HexStr = HexStr.from_str(data["usr"])
            pwd: str = data["pwd"]
            if not path.exists(f"./local/users/{usr.to_hex()}"):
                with open(f"./local/users/{usr.to_hex()}", "w") as f:
                    f.write(f"{pwd}\n")
                    f.write(f"{usr.to_str()}\n")
                result = "ok"
            else:
                result = "overlap"
            await self.sio.emit("register answer", result, to=sid)
            
        @self.sio.on('login')
        async def login(sid, data, *_):
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
            for i, x in enumerate(self.storage.users):
                if x.name.data == usr_name.data:
                    await self.kick(x.sid)
                    del self.storage.users[i]
                if x.sid == sid:
                    del self.storage.users[i]
            self.storage.users.append(User(sid, usr_name))
            with open("./public/chat.html", "r") as f:
                await self.sio.emit("login answer", {"code":"ok", "new":f.read()}, to=sid)
            self.gui.write("\n"+ usr_name.to_str() +" joined")
            await self.sio.emit("message", {0: time_ns(), 1: usr_name.to_str() + " joined"})
            
        @self.sio.on('message')
        async def print_message(sid, message, *_):
            message = Message(next((x for x in self.storage.users if x.sid == sid), None), message)
            self.gui.write("\n" + message.pack()[1])
            with open(f"./local/messages/list", "a") as f:
                f.writelines(message.dump()+"\n")
            
            
        @self.sio.on('disconnect')
        async def disconnect(sid, *_):
            user_index = User.get(sid)
            self.gui.write("\n"+ self.storage.users[user_index].name.to_str() +" left")
            del self.storage.users[user_index]
            
    def __init__(self, gui, storage) -> None:
        self.storage = storage
        User.user_list = lambda: self.storage.users
        self.gui = gui
        self.sio = socketio.AsyncServer()
        self.app = web.Application()
        self.sio.attach(self.app)
        
        self.init_handler()
        
        self.app.router.add_static('/static', './public')
        self.app.router.add_get('/', self.index)
