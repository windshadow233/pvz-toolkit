class Lineup:
    def __init__(self):
        self.scene = None
        self.mode = None
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


