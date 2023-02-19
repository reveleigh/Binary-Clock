# A basic class to use the Makerverse RV3028 Supercap Real Time Clock on the Raspberry Pi Pico
# Written by Brenton Schulz at Core Electronics
# 2021 NOV 5th Initial feature set complete
#     - Set / get date and time
#     - Set / get UNIX time (independent of main calendar clock)
#     - Enable event interrupt on EVI pin
#     - Get event timestamp
#     - Configure trickle charger for onboard supercap
#     - Configure frequency of CLK output pin

from machine import I2C, Pin

_ADDR = 0x52
_SEC = 0x00
_MIN = 0x01
_HOUR = 0x02
_DAY = 0x04
_MONTH = 0x05
_YEAR = 0x06
_STATUS = 0x0E
_CTRL1 = 0x0F
_CTRL2 = 0x10
_CIM = 0x12
_ECTRL = 0x13
_SECTS = 0x15
_DAYTS = 0x18
_UNIX = 0x1B
_ID = 0x28
_EE_CLKOUT = 0x35
_EE_BACKUP = 0x37

def _setBit(x, n):
    return x | (1 << n)

def _clearBit(x, n):
    return x & ~(1 << n)

def _writeBit(x, n, b):
    if b == 0:
        return _clearBit(x, n)
    else:
        return _setBit(x, n)
    
def _readBit(x, n):
    return x & 1 << n != 0
    
def _writeCrumb(x, n, c):
    x = _writeBit(x, n, _readBit(c, 0))
    return _writeBit(x, n+1, _readBit(c, 1))

def _writeTribit(x,n,c):
    x = _writeBit(x, n, _readBit(c, 0))
    x = _writeBit(x, n+1, _readBit(c, 1))
    return _writeBit(x, n+2, _readBit(c, 2)) 

def _bcdDecode(val):
    return (val>>4)*10 + (val&0x0F)

def _bcdEncode(val):
    return ((val//10) << 4) | (val % 10)

class Makerverse_RV3028():
    def __init__(self, i2c = None): 
        if isinstance(i2c, I2C) is False:
            print("RV3028 requires a valid i2c device")
            raise TypeError
        self.i2cDev = i2c
        
        try:
            part = int(i2c.readfrom_mem(_ADDR, _ID, 1))
        except Exception as e:
            print("Failed to find RV3028 on i2c bus") 
            raise e
               
        self.setBatterySwitchover()
        self.configTrickleCharger()
        self.setTrickleCharger()
        
    def _read(self, reg, N):
        try:
            tmp = int.from_bytes(self.i2cDev.readfrom_mem(_ADDR, reg, N), 'little')
        except:
            print("Error reading from RV3028")
            return float('NaN')
        return tmp
        
    def _write(self, reg, data):
        try:
            self.i2cDev.writeto_mem(_ADDR, reg, data)
        except:
            print("Error writing to RV3028")
            return float('NaN')
        
    def getUnixTime(self):
        return self._read(_UNIX, 4)
    
    def setUnixTime(self, time):
        self._write(_UNIX, time.to_bytes(4, 'little', False))
        
    def setBatterySwitchover(self, state = True):
        tmp = self._read(_EE_BACKUP, 1)
        if state is True:
            tmp = _writeCrumb(tmp, 2, 0b01)
        elif state is False:
            tmp = _writeCrumb(tmp, 2, 0b00)
        else:
            print("Parameter State must be True or False")
            return
        self._write(_EE_BACKUP, tmp.to_bytes(1, 'little', False))
                    
    def setTrickleCharger(self, state = True):
        tmp = self._read(_EE_BACKUP, 1)
        if state is True:
            tmp = _writeBit(tmp, 5, 1)
        elif state is False:
            tmp = _writeBit(tmp, 5, 0)
        else:
            print("Parameter State must be True or False")
            return
        self._write(_EE_BACKUP, tmp.to_bytes(1,'little', False))
        
    def configTrickleCharger(self, R = '3k'):
        tmp = self._read(_EE_BACKUP, 1)
        tmp = _setBit(tmp, 7)
        if R == '3k':
            tmp = _writeCrumb(tmp, 0, 0b00)
        elif R == '5k':
            tmp = _writeCrumb(tmp, 0, 0b01)
        elif R == '9k':
            tmp = _writeCrumb(tmp, 0, 0b10)
        elif R == '15k':
            tmp = _writeCrumb(tmp, 0, 0b11)
        else:
            print("R parameter must be '3k', '5k', '9k', or '15k'")
            return
        self._write(_EE_BACKUP, tmp.to_bytes(1, 'little', False))
        
    def configClockOutput(self, clk = 32768):
        tmp = self._read(_EE_CLKOUT, 1)
        if clk == 32768:
            tmp = _writeTribit(tmp, 0, 0)
        elif clk == 8192:
            tmp = _writeTribit(tmp, 0, 1)
        elif clk == 1024:
            tmp = _writeTribit(tmp, 0, 2)
        elif clk == 64:
            tmp = _writeTribit(tmp, 0, 3)
        elif clk == 32:
            tmp = _writeTribit(tmp, 0, 4)
        elif clk == 1:
            tmp = _writeTribit(tmp, 0, 5)
        elif clk == 0:
            tmp = _writeTribit(tmp, 0, 7)
        else:
            print("clk parameter must be 32678, 8192, 1024, 64,32, 1, or 0. Values are in units of Hz.")
            return
        self._write(_EE_CLKOUT, tmp.to_bytes(1, 'little', False))
        
    def resetEventInterrupt(self, edge = 'falling'):
        # Clear EVF, _STATUS bit 1
        tmp = self._read(_STATUS, 1)
        tmp = _clearBit(tmp, 1)
        self._write(_STATUS, bytes([tmp]))
        
        # TSS = 0, _ECTRL bit 0 (External event as time stamp source)
        # TSOW = 0, _ECTRL bit 1 (First recorded event timestamp kept)
        # EHL = 0, _ECTRL bit 6 (Falling edge default - PCB has pullup on EVI)
        # TSR = 1, _ECTRL bit 2 (reset event timestamp)
        tmp = self._read(_ECTRL, 1)
        tmp = _clearBit(tmp, 0)
        if edge == 'falling':
            tmp = _clearBit(tmp, 6)
        else:
            tmp = _setBit(tmp, 6)
        tmp = _clearBit(tmp, 1)
        tmp = _setBit(tmp, 2)
        self._write(_ECTRL, bytes([tmp]))
        
        # EIE = 1, _CTRL2 bit 2
        # TSE = 1, _CTRL2 bit 7
        tmp = self._read(_CTRL2, 1)
        tmp = _setBit(tmp, 2)
        tmp = _setBit(tmp, 7)
        self._write(_CTRL2, bytes([tmp]))

        tmp = self._write(_ECTRL, bytes([0]))
        
    def getEventInterrupt(self):
        tmp = self._read(_STATUS, 1)
        if _readBit(tmp,1) == 1:
            return True
        else:
            return False
        
    def setTime(self, time):
        if type(time) == dict:
            if 'ampm' in time:
                timeTmp = [0,0,0,0]
                timeTmp[3] = time['ampm']
            else:
                timeTmp = [0,0,0]
            timeTmp[0] = time['hour']
            timeTmp[1] = time['min']
            timeTmp[2] = time['sec']
            
            time = timeTmp
        tmp = self._read(_CTRL2, 1)
        if len(time) == 3:
            tmp = _writeBit(tmp, 1, 0)
            hrs = _bcdEncode(time[0])
        elif len(time) == 4:
            tmp = _writeBit(tmp, 1, 1)
            hrs = _bcdEncode(time[0])
            if time[3] == 'AM':
                hrs = _clearBit(hrs, 5)
            elif time[3] == 'PM':
                hrs = _setBit(hrs, 5)
        self._write(_CTRL2, tmp.to_bytes(1,'little', False))
        sec = _bcdEncode(time[2])
        mins = _bcdEncode(time[1])
        t = [sec, mins, hrs]
        self._write(_SEC, bytes(t))
        
    def getTime(self, timeFormat = 'list', eventTimestamp = False):
        if eventTimestamp is False:
            t = self._read(_SEC, 3)
        else:
            t = self._read(_SECTS, 3)
        hrFormat = _readBit(self._read(_CTRL2,1), 1)
        t = t.to_bytes(3, 'little', False)
        mins = _bcdDecode(t[1])
        secs = _bcdDecode(t[0])
        hrs = _bcdDecode(t[2])
        if hrFormat == 1:
            if _readBit(t[2], 5) == 0:
                time = [hrs, mins, secs, 'AM']
            else:
                hrByte = _clearBit(t[2], 5)
                hrs = _bcdDecode(hrByte)
                time = [hrs, mins, secs, 'PM']
        else:
            time = [hrs, mins, secs]
        if timeFormat == 'dict':
            timeTmp = {'hour': time[0], 'min': time[1], 'sec': time[2]}
            if len(time) == 4:
                timeTmp['ampm'] = time[3]
            time = timeTmp
        return time
        
    def setDate(self, date):
        if type(date) == dict:
            day = date['day']
            month = date['month']
            year = date['year']
            if year > 100:
                year -= 2000
        else:
            day = date[0]
            month = date[1]
            year = date[2]
        date = [_bcdEncode(day), _bcdEncode(month), _bcdEncode(year)]
        self._write(_DAY, bytes(date))
        
    def getDate(self, timeFormat = 'list', eventTimestamp = False):
        if eventTimestamp is False:
            tmp = self._read(_DAY, 3)
        else:
            tmp = self._read(_DAYTS, 3)
        date = tmp.to_bytes(3, 'little', False)
        day = _bcdDecode(date[0])
        month = _bcdDecode(date[1])
        year = _bcdDecode(date[2])
        if timeFormat == 'dict':
            date = {'day': day, 'month': month, 'year': year}
        else:
            date = [day, month, year]
        return date
    
    def getDateTime(self, timeFormat = 'list', eventTimestamp = False):
        time = self.getTime(timeFormat = timeFormat, eventTimestamp = eventTimestamp)
        date = self.getDate(timeFormat = timeFormat, eventTimestamp = eventTimestamp)
        # Clear event flag
        if timeFormat == 'dict':
            date.update(time)
            return date
        return date, time
     
    def timestamp(self):
        time = self.getTime()
        date = self.getDate()
        timestamp = "{:02d}".format(date[2]+2000) + "-" + "{:02d}".format(date[1]) + "-" + "{:02d}".format(date[0]) + " " + "{:02d}".format(time[0]) + ":" + "{:02d}".format(time[1]) + ":" + "{:02d}".format(time[2])
        if len(time) == 4:
            timestamp += " " + time[3]
        return timestamp
    
    def clearAllInterrupts(self):
        self._write(_STATUS, bytes([0]))
