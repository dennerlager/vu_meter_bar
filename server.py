import sys
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
        self.enableBoardSupply = Output(11)
        self.enableBoardSupply.set()
        self.dac = Dac()
        self.meters = {'1': VuMeter(self.dac, 3),
                       '2': VuMeter(self.dac, 0),
                       '3': VuMeter(self.dac, 1),
                       '4': VuMeter(self.dac, 14),
                       '5': VuMeter(self.dac, 15),
                       '6': VuMeter(self.dac, 12),
                       '7': VuMeter(self.dac, 13),
                       '8': VuMeter(self.dac, 10),
                       'l': VuMeter(self.dac, 8),
                       'r': VuMeter(self.dac, 9),
                       'pfl': VuMeter(self.dac, 2),
                       'monitor': VuMeter(self.dac, 11)}
        self.led = Output(3)
        self.setupShutdownMethod()

    def setupShutdownMethod(self):
        self.shutdown = sys.exit
        return
        systemBus = dbus.SystemBus()
        consoleKit = systemBus.get_object(
            'org.freedesktop.ConsoleKit',
            '/org/freedesktop/ConsoleKit/Manager')
        interface = dbus.Interface(consoleKit,
                                   'org.freedesktop.ConsoleKit.Manager')
        self.shutdown = interface.get_dbus_method('Stop')

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
                    try:
                        self.meters[address].setLevel(data)
                    except ValueError:
                        response = '0'
                else:
                    response = '0'
        if command == 'shutdown':
            self.dac.setAllVoltagesV(0)
            self.enableBoardSupply.clear()
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
