import zlib
import base64


class Lineup:
    def __init__(self):
        self.scene = 0
        self.plants = bytearray(b'\x00' * 54)
        self.plants_is_imitator = bytearray(b'\x00' * 54)
        self.plants_is_asleep = bytearray(b'\x00' * 54)

        self.base = bytearray(b'\x00' * 54)
        self.base_is_imitator = bytearray(b'\x00' * 54)

        self.pumpkins = bytearray(b'\x00' * 54)
        self.pumpkins_is_imitator = bytearray(b'\x00' * 54)

        self.coffee_beans = bytearray(b'\x00' * 54)
        self.coffee_beans_is_imitator = bytearray(b'\x00' * 54)

        self.ladders = bytearray(b'\x00' * 54)
        self.rakes = bytearray(b'\x00' * 54)

        self.items = bytearray(b'\x00\x00\x00' * 54)

    def compress(self):
        for r in range(6):
            for c in range(9):
                index = r * 9 + c
                item = 0
                item += 0b11111100000000000 & (self.plants[index] << 11)
                item += 0b00000010000000000 & (self.plants_is_imitator[index] << 10)
                item += 0b00000001000000000 & (self.plants_is_asleep[index] << 9)
                item += 0b00000000110000000 & (self.base[index] << 7)
                item += 0b00000000001000000 & (self.base_is_imitator[index] << 6)
                item += 0b00000000000100000 & (self.pumpkins[index] << 5)
                item += 0b00000000000010000 & (self.pumpkins_is_imitator[index] << 4)
                item += 0b00000000000001000 & (self.coffee_beans[index] << 3)
                item += 0b00000000000000100 & (self.coffee_beans_is_imitator[index] << 2)
                item += 0b00000000000000010 & (self.ladders[index] << 1)
                item += 0b00000000000000001 & (self.rakes[index] << 0)
                self.items[index * 3: (index + 1) * 3] = item.to_bytes(3, 'little')

    def decompress(self):
        for r in range(6):
            for c in range(9):
                index = r * 9 + c
                item = int.from_bytes(self.items[index * 3: (index + 1) * 3], 'little')
                self.plants[index] = (item & 0b11111100000000000) >> 11
                self.plants_is_imitator[index] = (item & 0b00000010000000000) >> 10
                self.plants_is_asleep[index] = (item & 0b00000001000000000) >> 9
                self.base[index] = (item & 0b00000000110000000) >> 7
                self.base_is_imitator[index] = (item & 0b00000000001000000) >> 6
                self.pumpkins[index] = (item & 0b00000000000100000) >> 5
                self.pumpkins_is_imitator[index] = (item & 0b00000000000010000) >> 4
                self.coffee_beans[index] = (item & 0b00000000000001000) >> 3
                self.coffee_beans_is_imitator[index] = (item & 0b00000000000000100) >> 2
                self.ladders[index] = (item & 0b00000000000000010) >> 1
                self.rakes[index] = (item & 0b00000000000000001) >> 0

    def __str__(self):
        buffer = bytearray(b'\x00' * 163)
        buffer[:162] = self.items
        buffer[162] = self.scene
        compressed = zlib.compress(buffer)
        s = base64.b64encode(compressed)
        return s.decode()

    @classmethod
    def from_str(cls, lineup_code: str):
        compressed = base64.b64decode(lineup_code)
        buffer = zlib.decompress(compressed)
        lineup = Lineup()
        lineup.items = buffer[:162]
        lineup.scene = buffer[162]
        lineup.decompress()
        return lineup
