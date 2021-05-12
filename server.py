import socket
from _thread import *
import sys

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server = 'localhost'
port = 5555

serverIp = socket.gethostbyname(server)

try:
        socket.bind((server, port))

except socket.error as error:
        print(str(error))

socket.listen(2)
print('En attente de connexion...')

currentId = "0"
position = ["0:50,50", "1:100,100"]

def threaded_client(connection):
        global currentId, position
        connection.send(str.encode(currentId))
        currentId = "1"
        reply = ''
        while True:
                try:
                        data = connection.recv(2048)
                        reply = data.decode('utf-8')
                        if not data:
                                connection.send(str.encode("Au Revoir"))
                                break
                        else:
                                print("Reçu : " + reply)
                                array = reply.split(":")
                                id = int(array[0])
                                position[id] = reply

                                if id == 0:
                                        nid = 1
                                if id == 1:
                                        nid = 0
                                reply = position[nid][:]
                                print("Envoi : " + reply)

                        connection.sendall(str.encode(reply))
                except:
                        break
        print("Connexion terminé")
        connection.close()

while True:
        connection, address = socket.accept()
        print("Connecté à : ", address)

        start_new_thread(threaded_client, (connection,))
