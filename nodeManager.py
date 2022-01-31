import socket
import sys
import threading
import json
from threading import Thread, Lock
from json import JSONEncoder
from contextlib import ExitStack
from functools import partial
import uuid


index = 0
port_Host = 1337
ip_Host = "127.0.0.4"
changeIpPort = True
DATABASE = {}
stop = False
opt = ""
On = True
uuidOk = False


class FakeTransaction():
    def __init__(self, Id, Sender, Reciever, Amount, uuid):
        self.Id = Id
        self.Sender = Sender
        self.Reciever = Reciever
        self.Amount = Amount
        self.uuid = uuid

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)


class ThreadServer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        # self.event= event

    def run(self):
        startServer()


class ThreadClient(threading.Thread):
    # Thread gérant la connexion avec un client
    __lock = Lock()
    __lock_tmp = Lock()

    def __init__(self,  conn):
        threading.Thread.__init__(self)
        self.connexion = conn
        #self.event = event

    def run(self):
        global uuidOk
        index = 0
        self.__lock.acquire()
        msgClient = self.connexion.recv(1024).decode()
        self.__lock.release()
        msg = json.loads(msgClient)
        self.__lock.acquire()
        global On
        if opt == "diplay Database":
            print("> ***")
            diplayDatabase(msg)
            print("> ***")
            On = True
        elif opt == "fake trans":
            uuidOk = False
            print("> Choose a transaction(uuid/value) to remplace.")
            for clef, valeur in msg.items():
                print(clef, valeur)
            select_uuid = input("> ")
            # self.__lock_tmp.acquire()
            print("> Creat fake transaction")
            new_uuid = uuid.uuid4()
            trans = FakeTransaction(str(index), input("> sender: "), input(
                "> receiver: "), input("> amount: "), str(new_uuid))
            val = None
            for x in msg.items():
                if select_uuid == x[1]:
                    print("> Transaction selected.")
                    val = x[0]
                    break
                else:
                    print("> uuid not valid, please choose again.")
            del msg[val]
            msg[trans.toJSON()] = str(new_uuid)
            # self.__lock_tmp.acquire()

            returnTransaction(msg)
        self.__lock.release()


def returnTransaction(msg):
    print("> remplace trans")
    new_connexion = connexion(ip, port)
    send_msg = []
    send_msg.append(msg)
    send_msg.append("cloud")
    send_msg.append("4")
    send_msg = json.dumps(send_msg)
    new_connexion.send(send_msg.encode())
    print("> Transfer new Database Ok.")
    new_connexion.close()
    global On
    On = True


def diplayDatabase(database2Display):
    for clef, valeur in database2Display.items():
        print(clef, valeur)


def startServer():
    mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        mySocket.bind((ip_Host, int(port_Host)))
    except socket.error:
        print("> La liaison du socket à l'adresse choisie a échoué.")
        sys.exit()
    print("> Serveur prêt, en attente de requêtes ...")
    mySocket.listen(5)
    while 1:
        connexion, adresse = mySocket.accept()
        # Créer un nouvel objet thread pour gérer la connexion de chaque client:
        th = ThreadClient(connexion)
        th.start()


def connexion(ip, port):
    connexion = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        connexion.connect((ip, int(port)))
    except socket.error:
        print("> La connexion a échoué.")
        sys.exit()
    print("> Connexion établie avec le serveur.")
    return connexion


def fake(port, ip):
    co = connexion(ip, int(port))
    msg = []
    msg.append(port_Host)
    msg.append(ip_Host)
    msg.append("3")
    msgJson = json.dumps(msg)
    co.send(msgJson.encode())


if __name__ == "__main__":
    __lock = Lock()
    while 1:
        port_Host = sys.argv[0]
        ip_Host = sys.argv[1]
        port_Host = int(port_Host)
        ip_Host = str(ip_Host)
        #event = threading.Event()
        if changeIpPort:
            print("> Please select ip and port of the node you want access.")
            port = input("> port: ")
            ip = input("> ip: ")
            changeIpPort = False
            if int(port) == 1337:
                print("> Mode Cloud ON")
            else:
                print("> Mode Cloud OFF")
            th_S = ThreadServer()
            th_S.start()
        print("> You are connect on "+str(ip_Host) + "-"+str(port_Host))
        print("> What do you want to do ?")
        print("> (1) Fake a transaction")
        print("> (2) List of transactions")
        choose = input("> ")
        if choose == "1":
            On = False
            opt = "fake trans"
            fake(port, ip)
            while not On:
                pass
        elif choose == "2":
            On = False
            opt = "diplay Database"
            fake(port, ip)
            while not On:
                pass
        else:
            print("> option not recognized, choose again.")
