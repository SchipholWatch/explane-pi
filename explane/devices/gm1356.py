import time

from enum import Enum

import usb.core
import usb.util

from ..exceptions import FatalDeviceError


class MeasureRange(Enum):
    R_30_130 = 0
    R_30_80 = 1
    R_50_100 = 2
    R_60_110 = 3
    R_80_130 = 4


class Gm1356:
    FILTER_DBA = 0
    FILTER_DBC = 1

    CURRENT_MEASUREMENT = 0
    MAX_MEASUREMENT = 1

    SPEED_SLOW = 0
    SPEED_FAST = 1

    CMD_CONFIGURE = 0x56  # Write this with data to set device configuration
    CMD_STATE_REQUEST = 0xB3

    PACKET_SIZE = 8  # bytes

    ENDPOINT_IN = 0x81
    ENDPOINT_OUT = 0x02

    ID_VENDOR = 0x64bd
    ID_PRODUCT = 0x74e3

    TIMEOUT_MS = 100

    def connect(self):
        self.dev = usb.core.find(idVendor=self.ID_VENDOR, idProduct=self.ID_PRODUCT)
        if self.dev is None:
            raise FatalDeviceError("Could not find GM1356 sound measurement device")

        if self.dev.is_kernel_driver_active(0):
            self.dev.detach_kernel_driver(0)
        usb.util.claim_interface(self.dev, 0)

    def configure(self, measure_range, filter_db, measurement_type, speed):
        settings = measure_range.value | (filter_db << 4) | (measurement_type << 5) | (speed << 6)
        command = bytearray([self.CMD_CONFIGURE, settings])
        # TODO Catch USB overflow error
        self.dev.write(self.ENDPOINT_OUT, command, self.TIMEOUT_MS)
        time.sleep(0.1)
        self.dev.read(self.ENDPOINT_IN, self.TIMEOUT_MS)  # Discard data

    def read_sound_pressure_level(self):
        self.dev.write(self.ENDPOINT_OUT, bytearray([self.CMD_STATE_REQUEST]), self.TIMEOUT_MS)
        time.sleep(0.1)
        # TODO Catch USB overflow error
        data = self.dev.read(self.ENDPOINT_IN, self.PACKET_SIZE, self.TIMEOUT_MS)

        return ((data[0] * 256) + data[1]) / 10
