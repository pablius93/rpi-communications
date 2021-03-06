# Raspberry PI side
from . import settings
from .settings import TransferMode
import socket
import time
from os import listdir
from os.path import isfile, join
import ftplib


def start():
    """
    Starts the client side
    """
    files = [f for f in listdir(settings.DIR) if isfile(join(settings.DIR, f))]
    running = True
    while running:
        try:
            _files = set([f for f in listdir(settings.DIR) if isfile(join(settings.DIR, f))])
            new_files = set(_files) - set(files)
            if len(new_files) > 0:
                print('New files detected')
                for f in new_files:
                    print('\t-{}'.format(f))
                    if settings.TRANSFER_MODE == TransferMode.FTP:
                        send_by_ftp(file=f, ip=settings.FTP_SERVER_IP, port=settings.FTP_PORT)
                    elif settings.TRANSFER_MODE == TransferMode.SOCKET:
                        send_file(file=f, ip=settings.SERVER_IP, port=settings.PORT)
                files = _files
            else:
                print('No new files detected')
            time.sleep(settings.WAIT)
        except KeyboardInterrupt:
            running = False
    print('Goodbye !')


def send_file(file, ip, port):
    """
    Sends a file to a server listening at an specified ip and port
    :param file:    The file
    :param ip:      Server's IP
    :param port:    Server's PORT
    """
    try:
        s = socket.socket()
        s.connect((ip, port))
        print('Connected to device: {}:{}'.format(ip, port))
        f = open(join(settings.DIR, file), "rb")
        l = f.read(1024)
        while l:
            s.send(l)
            l = f.read(1024)
        f.close()
        s.shutdown(socket.SHUT_WR)
        print('File sent: {}'.format(file))
    except socket.error:
        print("Unable to connect to device {}".format(ip))


def send_by_ftp(file, ip, port):
    """
    Sends a file via FTP to a FTP Server
    :param file:    The file
    :param ip:      FTP Server's IP
    :param port:    FTP Server's port
    """
    try:
        ftp = ftplib.FTP()
        ftp.connect(ip, port)
        ftp.login(settings.FTP_USER, settings.FTP_PASSWORD)
        f = open(file, 'rb')
        ftp.storbinary("STOR {}".format(file), f)
        f.close()
        ftp.close()
    except ftplib.Error:
        print('Unable to connect to device {}'.format(ip))


if __name__ == '__main__':
    start()
