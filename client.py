import socket

class Client():
    def __init__(self, ipAddress='127.0.0.1', port=50661):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip = ipAddress
        self.port = port
        self.socket.connect((self.ip, self.port))

    def transceive(self, command, addresses=[''], datas=['']):
        message = (f'{command}')
        for address, data in zip(addresses, datas):
            message += f':{address}:{data}'
        self.socket.sendall(message.encode())
        response = self.socket.recv(4096).decode()
        if not response == '1':
            raise RuntimeError(f'command {command}, {address}, {data} failed')

    def turnLedOn(self):
        self.transceive('turnLedOn')

    def turnLedOff(self):
        self.transceive('turnLedOff')

    def setMeters(self, addresses, levels):
        self.transceive('setMeter', addresses, levels)

    def setMeter(self, address, level):
        self.setMeters([address], [level])

    def shutdownServer(self):
        try:
            self.transceive('shutdown')
        except RuntimeError:
            pass

if __name__ == '__main__':
    client = Client()
    client.setMeter(1, 100)
    client.setMeters([1, 2, 3, 4, 5, 6, 7, 8, 'l', 'r', 'pfl'],
                     [i*10 for i in range(11)])
    client.shutdownServer()
