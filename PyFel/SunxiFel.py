import struct

import usb1


class SunxiException(Exception):
    pass


class SunxiFel:

    def __init__(self):
        self.VENDOR_ID = 0x1f3a
        self.PRODUCT_ID = 0xefe8
        self.INTERFACE = 0x00
        self.OUT_ENDPOINT = 0x01
        self.IN_ENDPOINT = 0x82
        pass

    def check(self):
        self.usbContext = usb1.USBContext()

        self.handle = self.usbContext.openByVendorIDAndProductID(
            self.VENDOR_ID,
            self.PRODUCT_ID,
            skip_on_error=True,
        )
        if self.handle is None:
            raise FileNotFoundError("Device not found")

        self.handle.claimInterface(self.INTERFACE)
        return True

    FMT = '{}  {}  |{}|'

    def _hexdump_gen(self, byte_string, _len=16, n=0, sep=' '):
        while byte_string[n:]:
            col0, col1, col2 = format(n, '08x'), [], ''
            for i in bytearray(byte_string[n:n + _len]):
                col1 += [format(i, '02x')]
                col2 += chr(i) if 31 < i < 127 else '.'
            col1 += ['  '] * (_len - len(col1))
            col1.insert(_len // 2, sep)
            print(self.FMT.format(col0, ' '.join(col1), col2))
            n += _len

    def _dump(self, prefix, packet):
        print(prefix)
        self._hexdump_gen(packet)

    def _send_request(self, request):
        self._dump("> {}".format(self.OUT_ENDPOINT), request)
        self.handle.bulkWrite(self.OUT_ENDPOINT, request)

    def _recv_response(self):
        response = self.handle.bulkRead(self.IN_ENDPOINT, 1024)
        self._dump("< {}".format(self.IN_ENDPOINT), response)
        return response

    def verify(self):
        self._send_request(
            b'AWUC\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x0c\x12\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        self._send_request(b'\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        response = self._recv_response()
        if len(response) < 13 or response[12] != 0:
            raise SunxiException("USB Request failed")

        self._send_request(
            b'AWUC\x00\x00\x00\x00\x20\x00\x00\x00\x00\x00\x00\x0c\x11\x00\x20\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        # self._send_request(b'\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        response = self._recv_response()

        if len(response) < 32 or response[0:8] != b'AWUSBFEX':
            raise SunxiException("Bad Response from Verify Request")

        # AWUSBFEX soc=00001667(A33) 00000001 ver=0001 44 08 scratchpad=00007e00 00000000 00000000
        v = struct.unpack("<llhBB", response[8:20])
        print("{} soc={:08x} {:08x} ver={:04x} {:02x} {:02x}".format(response[0:8].decode(), *v))
