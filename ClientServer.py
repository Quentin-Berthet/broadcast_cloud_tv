import socket, sys, threading, json
from threading import Thread, Lock
from json import JSONEncoder
from contextlib import ExitStack
from functools import partial
import uuid




DATABASE = {}
numero = 0
CONN_CLIENT = {} 
TRANSACTION_DONE = False
restart = False
LST_IP = []
LST_NEIGHBOURS = []
ResOn = 0
nb_neighbour = 0
nb_loop = 0
#---------------------CLIENT---------------------------
TRANS_DONE = False
opt_cloud = False
PORT_H = 1337
HOST = "127.0.0.1"


class Transaction():
    def __init__(self, Id, Sender, Reciever, Amount, uuid):
        self.Id = Id
        self.Sender = Sender
        self.Reciever = Reciever
        self.Amount = Amount
        self.uuid = uuid
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)
    

class Msg(object):
    def __init__(self, Transaction, typeMsg, rate, sender):
        self.transaction = Transaction
        self.type = typeMsg
        self.rate = rate
        self.sender = sender
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)

def loadIps(num):
    doc = open("routing-0"+ str(num)+".txt", "r")
    lst_port = []
    for line in (doc):
        port = line.split(":")
        lst_port.append(port[1])
    return lst_port

def loadNeightbours(num):
    doc = open("neighbour-"+ str(num)+".txt", "r")
    lst_neighbours = []
    for line in (doc):
        if line != "\n":
            Host = line.split(":")
            realPort =  Host[1].rstrip('\n')
            realIp = Host[0].rstrip('\n')
            if opt_cloud == True:
                lst_neighbours.append(realIp)
            else:
                lst_neighbours.append(realPort)
    return lst_neighbours



#---------------SERVER-------------------------------

def findNeighbours(ip):
    neighbours = []
    for neighbour in LST_NEIGHBOURS:
        if neighbour[0] == ip:
            print(neighbour)
    #return neighbours

def checkId(id_trans, database):
    for ele in database.values():
        if ele == id_trans:
            return True
    return False


def ratio2Porcent(val):
    res = 100 * val
    return res

class ThreadServer(threading.Thread):
    def __init__(self, ip, port, num):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.num = num
        self.on = True
    
    def run(self):
        startServer(self.ip, self.port, self.num)


class ThreadClient(threading.Thread):
    # Thread gérant la connexion avec un client
    __lock = Lock()
    def __init__(self, conn, neighbours):
        threading.Thread.__init__(self)
        self.connexion = conn
        self.neighbours = neighbours


    def run(self):
        global nb_loop
        global ResOn
        global restart
        templateTypeList = []
        closeSend = False
        nom = self.getName() # Chaque thread possède un nom
        self.__lock.acquire()
        msgClient = self.connexion.recv(1024).decode()
        self.__lock.release()
        msg = json.loads(msgClient)
        nombre = len(loadNeightbours(numero))
        global DATABASE
        if type(msg) == type(templateTypeList):
            if msg[2] == "3":
                portParent = msg[0]
                ipParent = msg[1]
                self.__lock.acquire()
                so = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                if opt_cloud:
                    so.connect((str(ipParent) , int(portParent)))
                else:
                    so.connect((ipParent, int(portParent)))
                msgJson = json.dumps(DATABASE)
                so.send(msgJson.encode())
                so.close()
                self.__lock.release()
            elif msg[2] == "4":
                DATABASE = msg[0]
                print("> Your Database has been modified.")
            closeSend = True
            restart = True
        #si msg == 1 sa veux dire que voisin a recu et stoquer la bonne transaction si msg == 2 na pas recu la bonne transaction
        if msg == 1:
            ResOn += 1
            closeSend = True
        if msg == 1 or msg == 2:
            closeSend = True
            nb_loop += 1
        res = ResOn/nb_neighbour
        if type(msg) == type(1):
            if nb_loop == nombre:
                #tout le monde a repondu au rate on affiche resultat final 
                print("> resultat : "+ str(ratio2Porcent(res)) +"%")
                ResOn = 0
                res = 0
                nb_loop = 0
                restart = True
        if not closeSend:           #section destiné au rate
            if "type" in msg:
                id_trans  = msg.get("transaction")[-1]
                if checkId(id_trans, DATABASE):
                    self.__lock.acquire()
                    sender = msg.get("sender")
                    so = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    if opt_cloud:
                        so.connect((sender, PORT_H))
                    else:
                        so.connect((HOST, int(sender)))
                    so.send(b"1")
                    self.__lock.release()
                    so.close()
                else:
                    self.__lock.acquire()
                    sender = msg.get("sender")
                    so = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    if opt_cloud:
                        so.connect((sender, PORT_H))
                    else:
                        so.connect((HOST, int(sender)))
                    so.send(b"2")
                    self.__lock.release()
                    so.close()
            else:           #section destiné à la transaction
                print("> ***")
                diplayDatabase(msg)
                print("> ***")
                for neighbour in self.neighbours:
                    if msgClient not in DATABASE:
                        self.__lock.acquire()
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        if opt_cloud:
                            s.connect((neighbour, PORT_H))
                        else:
                            s.connect((HOST, int(neighbour)))
                        s.sendall(msgClient.encode())
                        self.__lock.release()
            if "type" not in msg:
                DATABASE[msgClient] = msg.get("uuid")
            self.connexion.close()
        if restart:
            closeSend = False
            restart = False
        if msgClient.upper() == "FIN" or msgClient =="":
            th_E._Thread__stop()
            print("> Client arrêté. Connexion interrompue.")
            self.connexion.close()
        


def startServer(host, port, num):
    mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        mySocket.bind((host, int(port)))
    except socket.error:
        print( "> La liaison du socket à l'adresse choisie a échoué.")
        sys.exit()
    print( "> Serveur prêt, en attente de requêtes ...")
    mySocket.listen(5)
    while 1:
        connexion, adresse = mySocket.accept()
        # Créer un nouvel objet thread pour gérer la connexion de chaque client:
        clients = loadNeightbours(num)
        th = ThreadClient(connexion, clients)
        th.start()


class ThreadEmission(threading.Thread):
    __lock = Lock()
    def __init__(self, co, trans, port):
        threading.Thread.__init__(self)
        self.connexion = co # réf. du socket de coexion
        self.trans = trans
        self.port = port

    def run(self):
        self.__lock.acquire()
        msgTmp = Msg(Transaction(0,0,0,0,0), "template_msg",0, 1330)
        if type(self.trans) != type(msgTmp):
            tr = self.trans.toJSON()
        else:
            tr = self.trans.toJSON()
        tr = bytes(tr, 'utf-8'), 
        self.connexion.send(tr[0])
        self.__lock.release()


def connexionServer(port,trans, num):
    # Thread principal - Établissement de la coexion :
    connexion = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        if opt_cloud:
            connexion.connect((port, PORT_H))
        else:
            connexion.connect((HOST, int(port)))
    except socket.error:
        print("> La connexion a échoué.")
        sys.exit()
    print("> Connexion établie avec le serveur.")
    # Dialogue avec le serveur : on lance deux threads pour gérer indépendamment l'émission et la réception des messages :
    th_E = ThreadEmission(connexion, trans, port)
    th_E.start()


#------------------TP---------------------

def createTransaction(trans, neighbours, num):
    transaction = trans.toJSON()
    for neighbour in neighbours:
        DATABASE[transaction] = trans.uuid
        connexionServer(neighbour, trans, num)

def creatTransForRate(msg, nb_neigh, lst_neighbours):
    for neighbour in lst_neighbours:
        connexionServer(neighbour, msg ,numero)

def diplayDatabase(database2Display):
    for clef, valeur in database2Display.items():
        print("> ["+str(clef)+"] - ["+str(valeur)+"]")



if __name__ == "__main__":
    On = True
    num = sys.argv[1]
    numero = int(num)
    port = int(sys.argv[2])
    ip = sys.argv[3]
    if ip == "127.0.0.1":
        opt_cloud = False
        print("> mode Cloud OFF.")
    else:
        opt_cloud = True
        print("> mode Cloud ON.")
    index_trans = 0
    #lst_ip = loadIps(num)
    th_S = ThreadServer(ip, port, num)
    th_S.start()
    lst_neighbours = loadNeightbours(num)
    index = 0

    nb_neighbour = len(lst_neighbours)
    while On:
        print("> What do you want to do?")
        print("> Create a transaction (1)")
        print("> Rate a transaction (2)")
        choose = str(input("> "))
        if choose == "1":
            trans = Transaction(str(index)+"-"+str(port)+"-"+ip, input("> sender: "), input("> receiver: "), input("> amount: "), str(uuid.uuid4()))
            createTransaction(trans ,lst_neighbours, num)
            index += 1
        elif choose == "2":
            print("> choose your transaction: ")
            diplayDatabase(DATABASE)
            trans_id = input()
            trans = None
            for el in DATABASE.items():
                if el[1] == trans_id:
                    trans = el
            if opt_cloud:
                message = Msg(trans,"rate", 0, ip)
            else:
                message = Msg(trans,"rate", 0, port)
            creatTransForRate(message, nb_neighbour, lst_neighbours)


