class IONIQ_BEV:

    def __init__(self, dongle):
        self.dongle = dongle
        self.dongle.setProtocol('CAN_11_500')
        self.dongle.setCANRxMask('7FF')

    def getData(self):
        raw = {}
		
        self.dongle.setCANTx('7E4')		
        self.dongle.setCANRxFilter('7EC')
        for cmd in [2101,2105]:
            raw[cmd] = self.dongle.sendCommand(str(cmd))
 
        self.dongle.setCANTx('7e6')	
        self.dongle.setCANRxFilter('7EE')
        raw[2180] = self.dongle.sendCommand(str(2180))
        raw[2202] = {0x7CE22: 'noData'} #initdata  - will fail at filter if charging
        chargingBits = raw[2101][0x7EC21][5] \
                if 0x7EC21 in raw[2101] else None
        if chargingBits != None and chargingBits & 0x80 != 0x80:
            self.dongle.setCANTx('7c6')		
            self.dongle.setCANRxFilter('7CE')
            raw[2202] = self.dongle.sendCommand('22b002')
		   
        dcBatteryCurrent = int.from_bytes(raw[2101][0x7EC21][6:7] + raw[2101][0x7EC22][0:1],
                byteorder='big', signed=True) / 10.0 \
                if 0x7EC21 in raw[2101] and 0x7EC22 in raw[2101] else None
        dcBatteryVoltage = int.from_bytes(raw[2101][0x7EC22][1:3],
                byteorder='big', signed=False) / 10.0 \
                if 0x7EC22 in raw[2101] else None

        data = {'SOC_BMS':      raw[2101][0x7EC21][0] / 2.0 \
                    if 0x7EC21 in raw[2101] else None,
                'SOC_DISPLAY':  raw[2105][0x7EC24][6] / 2.0 \
                    if 0x7EC24 in raw[2105] else None,
                'EXTENDED': {
				    'externalTemperature':    (raw[2180][0x7EE22][1] - 80) / 2.0 \
					    if 0x7EE22 in raw[2180] else None,
						
                    'auxBatteryVoltage':        raw[2101][0x7EC24][4] / 10.0 \
                        if 0x7EC24 in raw[2105] else None,

                    'batteryInletTemperature':  int.from_bytes(raw[2101][0x7EC23][2:3],
                        byteorder='big', signed=True) \
                        if 0x7EC23 in raw[2105] else None,

                    'batteryMaxTemperature':    int.from_bytes(raw[2101][0x7EC22][3:4],
                        byteorder='big', signed=True) \
                        if 0x7EC22 in raw[2105] else None,

                    'batteryMinTemperature':    int.from_bytes(raw[2101][0x7EC22][4:5],
                        byteorder='big', signed=True) \
                        if 0x7EC22 in raw[2105] else None,

                    'cumulativeEnergyCharged':  int.from_bytes(raw[2101][0x7EC25][6:7] + raw[2101][0x7EC26][0:3],
                        byteorder='big', signed=False) / 10 \
                        if 0x7EC25 in raw[2101] else None,

                    'cumulativeEnergyDischarged':  int.from_bytes(raw[2101][0x7EC26][3:7],
                        byteorder='big', signed=False) / 10 \
                        if 0x7EC26 in raw[2101] else None,

                    'odo':  int.from_bytes(raw[2202][0x7CE21][3:6],
                        byteorder='big', signed=False) \
                        if 0x7CE21 in raw[2202] else None,

                    'charging':                 1 if chargingBits != None and \
                            chargingBits & 0x80 == 0x80 else 0,

                    'normalChargePort':         1 if chargingBits != None and \
                            chargingBits & 0x20 == 0x20 else 0,

                    'rapidChargePort':          1 if chargingBits != None and \
                            chargingBits & 0x40 == 0x40 else 0,

                    'dcBatteryCurrent':         dcBatteryCurrent,

                    'dcBatteryPower':           dcBatteryCurrent * dcBatteryVoltage / 1000.0 \
                        if dcBatteryCurrent!= None and dcBatteryVoltage != None else None,

                    'dcBatteryVoltage':         dcBatteryVoltage,

                    'soh':                      int.from_bytes(raw[2105][0x7EC24][0:2],
                        byteorder='big', signed=False) / 10.0 \
                        if 0x7EC24 in raw[2105] else None,
                    }
                }

        data.update(self.getBaseData())

        return data

    def getBaseData(self):
        return {
            "CAPACITY": 28,
            "SLOW_SPEED": 2.3,
            "NORMAL_SPEED": 4.6,
            "FAST_SPEED": 50
        }
