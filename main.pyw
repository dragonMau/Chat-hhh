import asyncio
from sys import path

path.append("./libs")
from threading import Thread

from aiohttp import web
from lib import Storage
from server import Server
from window import Gui

storage = Storage()
gui = Gui(storage)
server = Server(gui, storage)
gui.sio = server.sio

socket_loop = Thread(target=web.run_app, args=(server.app,))
socket_loop.daemon = True
    
tkinter_loop = Thread(target=gui.root.mainloop)
tkinter_loop.daemon = True

if __name__ == '__main__':
    socket_loop.start()
    tkinter_loop.run()
