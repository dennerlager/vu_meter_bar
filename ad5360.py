import spi
import bitstruct
import unittest

class Memory:
    def getChannelAddress(self, channel):
        return 0b01000 + channel

    def getPublicAddress(self):
        return 0

class Dac:
    vref = 2.5
    def __init__(self):
        self.memory = Memory()
        self.spi = spi.Spi(0)

    def setVoltageV(self, channel, voltage):
        self.checkChannel(channel)
        self.checkVoltage(voltage)
        self.spi.transceive(self.assembleMessage(
            modeBits=3,
            address=self.memory.getChannelAddress(channel),
            voltage=voltage))

    def setAllVoltagesV(self, voltage):
        self.checkVoltage(voltage)
        self.spi.transceive(self.assembleMessage(
            modeBits=3,
            address=self.memory.getPublicAddress(),
            voltage=voltage))

    def checkVoltage(self, voltage):
        if not -2*self.vref <= voltage <= 2*self.vref:
            raise ValueError(f'{voltage}V out of range')

    def checkChannel(self, channel):
        if not 0 <= channel <= 15:
            raise ValueError(f'channel {channel} out of range')

    def assembleMessage(self, modeBits, address, voltage):
        return bitstruct.pack('>u2u6s16', modeBits, address,
                              self.convertVoltage2Value(voltage))

    def convertVoltage2Value(self, voltage):
        return 2**16 / (4*self.vref) * voltage

class DacTest(unittest.TestCase):
    def setUp(self):
        self.dac = Dac()

    def test_setVoltageVRaises(self):
        self.assertRaises(ValueError, self.dac.setVoltageV, 0, 20)
        self.assertRaises(ValueError, self.dac.setVoltageV, 0, -20)
        self.assertRaises(ValueError, self.dac.setVoltageV, -1, 0)
        self.assertRaises(ValueError, self.dac.setVoltageV, 16, 0)

if __name__ == '__main__':
    unittest.main()
