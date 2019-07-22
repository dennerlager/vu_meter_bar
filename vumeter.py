class VuMeter:
    fullScaleVoltage = 1.2
    def __init__(self, dac, dacchannel):
        self.dac = dac
        self.channel = dacchannel

    def setLevel(self, percent):
        if not 0 <= percent <= 200:
            raise ValueError(f'{percent}% out of range')
        self.dac.setVoltageV(self.channel,
                             self.fullScaleVoltage / 200 * percent)
