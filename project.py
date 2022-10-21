import socket
import json
import random

def printer(m):
    for row in m:
        for col in row:
            print(col, end=" ")
        print()


def send_something(soc, data):
    soc.sendall(data.encode())


ships = [[1,1,1,1,0,0,1,0,0,1],
         [0,0,0,0,0,0,0,0,0,0],
         [0,0,0,0,1,0,1,0,0,0],
         [0,0,0,0,1,0,1,0,0,0],
         [0,0,0,0,1,0,1,0,0,0],
         [0,0,0,0,0,0,0,0,0,0],
         [0,0,1,1,0,0,1,1,0,0],
         [0,0,0,0,0,0,0,0,0,0],
         [0,0,0,0,0,1,0,1,0,0],
         [1,1,0,0,0,0,0,0,0,0]]
shots = [[0 for r in range(10)] for d in range(10)]



HOST = '172.16.11.26'  # ip-адрес сервера, мы знаем, что он будет запущен на той же машине, что и клиент
PORT = 12345        # мы знаем, что сервер слушает порт 65432

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:  # конструктор tcp-сокета
    addr = (HOST, PORT)          # кортеж из ip-адреса и порта
    s.connect(addr)              # подключаемся к серверу
    print(s.recv(2048).decode())
    s.sendall(json.dumps(ships).encode())
    while True:
        data = s.recv(2048).decode()  # считываем ответ сервера
        printer(shots)
        print("Куда стреляем:")
        xy = input()
        send_something(s, xy)
        x, y = xy.split(' ')
        x = int(x)
        y = int(y)
        data = s.recv(2048).decode()
        if data == "win":
            break
        print(data)
        if data == "killed":
            shots[x][y] = 2
        else:
            shots[x][y] = 3




