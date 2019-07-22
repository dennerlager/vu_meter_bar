import dbus
import select
import socket
from ad5360 import Dac
from gpio import Output
from vumeter import VuMeter

class Server:
    def __init__(self):
        self.clientsocket = None
        self.socket = self.openSocket()
        self.bar = Bar()

    def openSocket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        host_name = ''
        port_number = 50661
        sock.bind((host_name, port_number))
        sock.listen(1)
        return sock

    def run(self):
        while True:
            self.clientsocket, address = self.socket.accept()
            while True:
                if not select.select([self.clientsocket.fileno()], [], [], 0.1)[0]:
                    continue
                messageFromClient = self.clientsocket.recv(4096).decode()
                if self.hasClientClosed(messageFromClient):
                    self.clientsocket.close()
                    break
                response = self.bar.process(messageFromClient)
                self.respond(response)

    def hasClientClosed(self, messageFromClient):
        '''An empty message from a readable socket means
        the other side has closed. '''
        return messageFromClient == ''

    def respond(self, response):
        self.clientsocket.sendall(response.encode())

class Bar:
    def __init__(self):
        dac = Dac()
        self.meters = {'1': VuMeter(dac, 0),
                       '2': VuMeter(dac, 1),
                       '3': VuMeter(dac, 2),
                       '4': VuMeter(dac, 3),
                       '5': VuMeter(dac, 4),
                       '6': VuMeter(dac, 5),
                       '7': VuMeter(dac, 6),
                       '8': VuMeter(dac, 7),
                       'l': VuMeter(dac, 8),
                       'r': VuMeter(dac, 9),
                       'pfl': VuMeter(dac, 10), }
        self.led = Output(8)
        self.setupShutdownMethod()

    def setupShutdownMethod(self):
        import sys;
        self.shutdown = sys.exit
        # systemBus = dbus.SystemBus()
        # consoleKit = systemBus.get_object(
        #     'org.freedesktop.ConsoleKit',
        #     '/org/freedesktop/ConsoleKit/Manager')
        # interface = dbus.Interface(consoleKit,
        #                            'org.freedesktop.ConsoleKit.Manager')
        # self.shutdown = interface.get_dbus_method("Stop")

    def process(self, message):
        response = '1'
        command, addresses, datas = self.parse(message)
        if command == 'turnLedOn':
            self.led.set()
        if command == 'turnLedOff':
            self.led.clear()
        if command == 'setMeter':
            for address, data in zip(addresses, datas):
                if address in self.meters.keys():
                    self.meters[address].setLevel(data)
                else:
                    response = '0'
        if command == 'shutdown':
            self.shutdown()
        return response

    def parse(self, message):
        command, *rest = message.split(':')
        addresses = []
        datas = []
        for i in range(len(rest)//2):
            addresses.append(rest[i*2])
            try:
                datas.append(int(rest[i*2+1]))
            except ValueError:
                datas.append(rest[i*2+1])
        return command, addresses, datas

if __name__ == '__main__':
    server = Server()
    server.run()
