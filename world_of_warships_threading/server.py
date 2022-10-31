import multiprocessing
import threading
import random
import json
import socket
import sys
import time


# import keyboard


class Player:
    def __init__(self, name: str, killed_cells: int = 0, field: list[list[int: 10]] = None):
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

        self.external_server = ExternalServer(self)
        self.external_server_process = multiprocessing.Process(target=self.external_server.accept_players)
        self.external_server_process.start()

        self.internal_server = InternalServer(self)
        self.internal_server.console()


class InternalServer:
    def __init__(self, parent_server):
        self.parent_server = parent_server
        self.command_dict = {
            "help": [
                self.help,
                "for help"
            ],
            "quit": [
                self.close_full_server,
                "for close server\n"
            ],

            "restart": [
                self.restart_server,
                "restart internal server"
            ],
            "start": [
                self.start_internal_server,
                "start internal server"
            ],
            "stop": [
                self.close_external_server,
                "stop internal server\n"
            ],

        }

    def console(self):
        # keyboard.add_hotkey("ctrl+c", server.command_dict["close_full_server"][0])

        self.command_dict["help"][0]()

        while True:
            time.sleep(1)
            data = input("->>")
            try:
                self.command_dict[data][0]()
            except KeyError:
                self.command_dict["help"][0]()

    def start_internal_server(self):
        if self.parent_server.external_server_process.is_alive():
            print("already started")
            return

        self.parent_server.external_server = ExternalServer(self)
        self.parent_server.external_server_process = \
            multiprocessing.Process(target=self.parent_server.external_server.accept_players)
        self.parent_server.external_server_process.start()

        print("started new process")

    def close_external_server(self):
        if self.parent_server.external_server_process.is_alive():
            print("killed old process")
            self.parent_server.external_server_process.terminate()

    def restart_server(self):
        self.close_external_server()
        self.start_internal_server()

    def close_full_server(self):
        print("closed")
        self.parent_server.external_server_process.terminate()
        sys.exit()

    def help(self):
        print("help for you:\n")

        for key, value in self.command_dict.items():
            print(f"<{key}>,{' ' * (20 - len(key))} {value[1]}")

        print(f"{'-' * 10}\n")


class ExternalServer:

    def __init__(self, parent_server):
        self.parent_server = parent_server

    def accept_players(self):
        while True:
            print(f"wait new user...")
            sock, addr = server.server.accept()
            print(f"connected {addr}")
            self.link_new_player_with_room(sock, addr)

    def link_new_player_with_room(self, sock, addr):
        player, start_data = self.wait_data_from_player(sock)
        print(f"get data from {addr}")
        self.target_game_mode(sock, addr, player, start_data)

    def wait_data_from_player(self, sock):
        sock.send(json.dumps(Server.free_players))  # sending free players to join rooms
        start_data = json.loads(sock.recv(2048))  # wait initial data for player
        player = Player(name=start_data["name"])

        return player, start_data

    def target_game_mode(self, sock, addr, player, start_data):
        if start_data["game_mode"] == "name":
            room = self.create_room_with_name_player(sock, addr, player, start_data)
            self.create_new_thread(room)

        elif start_data["game_mode"] == "random":
            room = self.create_room_with_random_player(sock, addr, player, start_data)
            self.create_new_thread(room)

        elif start_data["game_mode"] == "new":
            server.free_players.append(player)

        else:
            print(f"some problem with {start_data['name']}: {addr} |can`t find command for game mode|")
            sock.send(json.dumps("error with init data: |game mode instruction|"))

    def create_room_with_name_player(self, sock, addr, player, start_data):
        try:
            room = Room(player,
                        list(filter(lambda x: x.name == start_data["name_of_enemy"], server.free_players))[0],
                        threading.get_ident())
        except IndexError:
            print(f"some problem with {start_data['name']}: {addr} |can`t find name|")
            sock.send(json.dumps("can`t find player with this name"))
        else:
            return room

    def create_room_with_random_player(self, sock, addr, player, start_data):
        try:
            room = Room(player, random.choice(server.free_players), threading.get_ident())
        except IndexError:
            print(f"some problem with {start_data['name']}: {addr} |can`t find random player|")
            sock.send(json.dumps("no any player for now"))
        else:
            return room

    def create_new_thread(self, ready_room: Room):
        Server.rooms.append(ready_room)
        new_thread = threading.Thread(target=ready_room.run)
        print(f"created new room {ready_room.id}")
        new_thread.start()
        new_thread.join()


if __name__ == "__main__":
    server = Server()
