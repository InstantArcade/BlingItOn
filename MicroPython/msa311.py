# MSA311 3-axis accelerometer (MEMSensing Microsystems), MicroPython driver for I2C.
# From the MSA311 datasheet V1.1 (Mar. 2021):
#   7-bit I2C address 0x62 (0b1100010), fixed. PARTID register 0x01 = 0x13.
#   ACC_X/Y/Z: 0x02..0x07, low byte first. LSB register holds ACC[3:0] in bits 7:4,
#   MSB register holds ACC[11:4]: 12-bit two's complement, left-justified in 16 bits.
#   Range 0x0F FS[1:0]: 00 +-2 g, 01 +-4 g, 10 +-8 g, 11 +-16 g
#   -> 1024 / 512 / 256 / 128 LSB per g.
#   ODR 0x10: bits 7:5 X/Y/Z disable (0 = enabled), ODR[3:0] (0111 = 125 Hz).
#   Power mode 0x11: PWR_MODE bits 7:6, 00 normal, 01 low power, 11 suspend.
#   The default 0x11 = 0xDE is SUSPEND mode, so the chip must be woken before it measures.
#   Wake-up from power-down: 1 ms; start-up from power off: 3 ms.
import time

_ADDR = 0x62
_PARTID = 0x01
_ACC_X_LSB = 0x02
_RANGE = 0x0F
_ODR = 0x10
_PWR = 0x11

_FS = {2: (0b00, 1024), 4: (0b01, 512), 8: (0b10, 256), 16: (0b11, 128)}  # FS bits, LSB/g


class MSA311:
    def __init__(self, i2c, addr=_ADDR, g_range=2):
        """g_range: 2, 4, 8 or 16 g full scale."""
        if g_range not in _FS:
            raise ValueError('g_range must be 2, 4, 8 or 16')
        self.i2c = i2c
        self.addr = addr
        time.sleep_ms(3)  # start-up time from power off
        pid = self.i2c.readfrom_mem(addr, _PARTID, 1)[0]
        if pid != 0x13:
            raise OSError('MSA311 not found (PARTID 0x%02X, expected 0x13): check wiring' % pid)
        fs, self._lsb_per_g = _FS[g_range]
        # Normal mode: clear PWR_MODE bits 7:6, keep LOW_POWER_BW bits.
        p = self.i2c.readfrom_mem(addr, _PWR, 1)[0]
        self._w(_PWR, p & 0x3F)
        time.sleep_ms(2)  # wake-up time 1 ms
        self._w(_ODR, 0x07)  # X/Y/Z enabled, 125 Hz
        self._w(_RANGE, fs)
        time.sleep_ms(20)  # let a couple of fresh samples arrive (8 ms each at 125 Hz)

    def _w(self, reg, val):
        self.i2c.writeto_mem(self.addr, reg, bytes([val]))

    def raw(self):
        """(x, y, z) 12-bit counts, read in one 6-byte burst from 0x02."""
        d = self.i2c.readfrom_mem(self.addr, _ACC_X_LSB, 6)
        out = []
        for i in (0, 2, 4):
            v = d[i] | (d[i + 1] << 8)  # LSB register first, then MSB register
            if v & 0x8000:
                v -= 65536
            out.append(v >> 4)  # 12-bit value sits in bits 15:4
        return tuple(out)

    def read(self):
        """(x, y, z) acceleration in g."""
        x, y, z = self.raw()
        k = self._lsb_per_g
        return x / k, y / k, z / k

    def read_ms2(self):
        """(x, y, z) acceleration in m/s^2."""
        return tuple(v * 9.80665 for v in self.read())