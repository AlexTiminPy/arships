import socket
import random
import json
import pprint


class Player:
    def __init__(self, sock, addr, matrix):
        self.sock = sock
        self.addr = addr
        self.matrix = matrix
        self.killed_cells = 0

    def __repr__(self):
        return self.matrix


"""
0 - hollow
1 - ship
2 - bombed
3 - bombed_ship
"""


class Server:
    @staticmethod
    def run():
        server = Server()
        server.first_player = server.accept_player()
        server.second_player = server.accept_player()

        coin = random.randint(0, 2)
        if coin == 0:
            server.first_player, server.second_player = server.second_player, server.first_player

        server.first_player.matrix[0][0] = 1

        while True:
            print("first player turn")
            server.tyrn(server.first_player, server.second_player)

            pprint.pprint(server.first_player.matrix)
            pprint.pprint(server.second_player.matrix)

            print("second player turn")
            server.tyrn(server.second_player, server.first_player)

            pprint.pprint(server.first_player.matrix)
            pprint.pprint(server.second_player.matrix)

    def tyrn(self, player, no_player):
        player.sock.send("your turn".encode("utf-8"))
        data = player.sock.recv(2048).decode("utf-8")
        x, y = data.split(" ")
        x = int(x)
        if x > 10:
            x = 10
        y = int(y)
        if y > 10:
            y = 10
        if no_player.matrix[x][y] == 1:
            if no_player.killed_cells == 20:
                player.sock.send("win".encode("utf-8"))
                no_player.sock.send("lose".encode("utf-8"))
            no_player.matrix[x][y] = 3
            player.sock.send("killed".encode("utf-8"))
        else:
            no_player.matrix[x][y] = 2
            player.sock.send("hollow".encode("utf-8"))

        no_player.sock.send(data.encode("utf-8"))

    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = "0.0.0.0"
        self.port = 12345
        self.server.bind((self.host, self.port))
        self.server.listen(2)

        self.first_player = None
        self.second_player = None

        print(f"online")

    def accept_player(self):
        print(f"wait client")
        sock, addr = self.server.accept()
        print(f"connected {addr}")

        sock.send("hello".encode("utf-8"))

        matrix = json.loads(sock.recv(2048))
        print(matrix)

        return Player(sock, addr, matrix)


Server.run()
