import random
import socket
import pprint
import json

i = 0


def get_rand():
    global i
    if i < 20:
        rand = random.randint(0, 1)
        if rand >= 1:
            i += 1
        return rand
    else:
        return 0


class Player:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(("localhost", 12345))

        print(f"connected")

        self.matrix = [[get_rand() for _ in range(10)] for _ in range(10)]
        self.enemy_saved_matrix = [[0 for _ in range(10)] for _ in range(10)]

    def run(self):
        print(self.parse_server_message())
        self.send_to_server(json.dumps(self.matrix))
        while True:
            print("_" * 10)
            message = self.parse_server_message()
            if message == "your turn":
                print(message)
                x = input("write raw: ")
                y = input("write column: ")

                self.send_to_server(f"{x} {y}")

                data = self.parse_server_message()

                print(data)

                x = int(x)
                if x > 10:
                    x = 10
                y = int(y)
                if y > 10:
                    y = 10

                if data == "killed":
                    self.enemy_saved_matrix[x][y] = 3
                else:
                    self.enemy_saved_matrix[x][y] = 2

                pprint.pprint(self.matrix)
                pprint.pprint(self.enemy_saved_matrix)

            else:
                x, y = message.split(" ")
                x = int(x)
                if x > 10:
                    x = 10
                y = int(y)
                if y > 10:
                    y = 10

                if self.matrix[x][y] == 1:
                    self.matrix[x][y] = 3
                else:
                    self.matrix[x][y] = 2

                pprint.pprint(self.matrix)
                pprint.pprint(self.enemy_saved_matrix)

    def send_to_server(self, data):
        self.client.send(data.encode("utf-8"))

    def parse_server_message(self):
        data = self.client.recv(2048).decode("utf-8")
        return data

    def __repr__(self):
        return self.matrix, self.enemy_saved_matrix


player = Player().run()
