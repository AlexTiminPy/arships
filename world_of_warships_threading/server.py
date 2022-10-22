import multiprocessing
import threading
import random
import json
import pprint
import socket
import sys
import time
import keyboard


class Player:
    def __init__(self, name: str, field: list[list[int: 10]], killed_cells: int):
        self.name = name
        self.field = field
        self.killed_cells = killed_cells


class Room:
    def __init__(self, player_1: Player, player_2: Player, id: int):
        self.player_1 = player_1
        self.player_2 = player_2
        self.id = id

    def run(self):
        pass


class Server:
    free_players = []
    threads = []
    rooms = []

    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = "0.0.0.0"
        self.port = 12345
        self.server.bind((self.host, self.port))
        self.server.listen()

        external_server = multiprocessing.Process(target=ExternalServer.accept_players, args=(self,))
        external_server.start()

        InternalServer.console(external_server)

        external_server.join()


class InternalServer:
    @staticmethod
    def console(external_server):

        help_data = (f"<quit>              for close program\n"
                     f"<childs>            to get processes\n"
                     f"<close rooms>       to terminate external part of server\n"
                     f"<current>           to get info about main process\n")

        time.sleep(1)

        keyboard.add_hotkey("ctrl+c", lambda: external_server.terminate() and sys.exit())

        while True:
            data = input("->>")
            if data == "quit":
                print("closed")
                external_server.terminate()
                sys.exit()
            elif data == "childs":
                print(multiprocessing.active_children())
            elif data == "close rooms":
                external_server.terminate()
            elif data == "current":
                print(multiprocessing.current_process())
            elif data == "help":
                print(help_data)
            else:
                print(help_data)


class ExternalServer:

    @staticmethod
    def accept_players(server):
        while True:
            print(f"wait new user...")
            sock, addr = server.server.accept()
            print(f"connected {addr}")
            ExternalServer.link_new_player_with_room(sock, addr)

    @staticmethod
    async def link_new_player_with_room(sock, addr):
        player, start_data = await ExternalServer.wait_data_from_player(sock)
        print(f"get data from {addr}")
        ExternalServer.target_game_mode(sock, addr, player, start_data)

    @staticmethod
    async def wait_data_from_player(sock):
        sock.send(json.dumps(Server.free_players))  # sending free players to join rooms
        start_data = json.loads(sock.recv(2048))  # wait initial data for player
        player = Player(name=start_data["name"], field=start_data["field"], killed_cells=0)

        return player, start_data

    @staticmethod
    def target_game_mode(sock, addr, player, start_data):
        if start_data["game_mode"] == "name":
            room = ExternalServer.create_room_with_name_player(sock, addr, player, start_data)
            ExternalServer.create_new_thread(room)

        elif start_data["game_mode"] == "random":
            room = ExternalServer.create_room_with_random_player(sock, addr, player, start_data)
            ExternalServer.create_new_thread(room)

        elif start_data["game_mode"] == "new":
            server.free_players.append(player)

        else:
            print(f"some problem with {start_data['name']}: {addr} |can`t find command for game mode|")
            sock.send(json.dumps("error with init data: |game mode instruction|"))

    @staticmethod
    def create_room_with_name_player(sock, addr, player, start_data):
        try:
            room = Room(player,
                        list(filter(lambda x: x.name == start_data["name_of_enemy"], server.free_players))[0],
                        threading.get_ident())
        except IndexError:
            print(f"some problem with {start_data['name']}: {addr} |can`t find name|")
            sock.send(json.dumps("can`t find player with this name"))
        else:
            return room

    @staticmethod
    def create_room_with_random_player(sock, addr, player, start_data):
        try:
            room = Room(player, random.choice(server.free_players), threading.get_ident())
        except IndexError:
            print(f"some problem with {start_data['name']}: {addr} |can`t find random player|")
            sock.send(json.dumps("no any player for now"))
        else:
            return room

    @staticmethod
    def create_new_thread(ready_room: Room):
        Server.rooms.append(ready_room)
        new_thread = threading.Thread(target=ready_room.run)
        print(f"created new room {ready_room.id}")
        new_thread.start()
        new_thread.join()


if __name__ == "__main__":
    server = Server()
