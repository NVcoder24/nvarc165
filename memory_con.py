import mybin, charmap

class AddressSpace:
    def __init__(self) -> None:
        pass

    def read(self, addr:int) -> int:
        return 0

    def write(self, addr:int, value:int) -> None:
        pass

class MemoryController:
    def __init__(self) -> None:
        self.memory_map = {}

    def map(self, name:str, start:int, stop:int, space:AddressSpace) -> None:
        self.memory_map[name] = [
            start, stop,
            space
        ]

    def read(self, addr:int) -> int:
        for i in self.memory_map:
            if self.memory_map[i][0] <= addr and self.memory_map[i][1] >= addr:
                return self.memory_map[i][2].read(addr - self.memory_map[i][0])
        return 0

    def write(self, addr:int, value:int):
        for i in self.memory_map:
            if self.memory_map[i][0] <= addr and self.memory_map[i][1] >= addr:
                return self.memory_map[i][2].write(addr - self.memory_map[i][0], value)
        return 0

class Ram(AddressSpace):
    def __init__(self, length:int) -> None:
        self.ram = []
        for i in range(length):
            self.ram.append(0)

    def read(self, addr:int) -> int:
        if addr < 0 or addr > len(self.ram) - 1:
            return 0
        return self.ram[addr]

    def write(self, addr:int, value:int) -> None:
        if addr < 0 or addr > len(self.ram) - 1:
            return 0
        self.ram[addr] = value

class Keyboard(AddressSpace):
    def __init__(self) -> None:
        self.value = 0

    def read(self, addr:int) -> int:
        return self.value

    def write(self, addr:int, value:int) -> None:
        pass

    def set_char(self, value:int) -> None:
        self.value = value

class TextScreen(AddressSpace):
    def __init__(self, x:int, y:int) -> None:
        self.x = x
        self.y = y
        self.space = []
        for _x in range(x + 1):
            for _y in range(y + 1):
                self.space.append(0)

    def read(self, addr:int) -> int:
        if addr < 0 or addr > len(self.space) - 1:
            return 0
        return self.space[addr]

    def write(self, addr:int, value:int) -> None:
        if addr < 0 or addr > len(self.space) - 1:
            return 0
        self.space[addr] = value
    
    def get_char(self, addr:int) -> str:
        if addr < 0 or addr > len(self.space) - 1:
            return " "
        if self.space[addr] not in charmap.charmap_rev:
            return "?"
        return charmap.charmap_rev[self.space[addr]]

    def get_char_xy(self, x:int, y:int) -> str:
        return self.get_char(x + self.x * y)

class GraphicScreen(AddressSpace):
    def __init__(self, x:int, y:int) -> None:
        self.space = []
        for _x in range(x):
            for _y in range(y):
                self.space.append(0)

    def read(self, addr:int) -> int:
        if addr < 0 or addr > len(self.space) - 1:
            return 0
        return self.space[addr]

    def write(self, addr:int, value:int) -> None:
        if addr < 0 or addr > len(self.space) - 1:
            return 0
        self.space[addr] = value
    
    def get_rgb(self, addr:int) -> tuple:
        if addr < 0 or addr > len(self.space) - 1:
            return 0
        _bin = mybin.dec_to_bin(self.space[addr])
        return (
            int(mybin.dec_to_bin(_bin[0:3]) / 2 ** 3 - 1 * 255),
            int(mybin.dec_to_bin(_bin[3:6]) / 2 ** 3 - 1 * 255),
            int(mybin.dec_to_bin(_bin[6:8]) / 2 ** 2 - 1 * 255),
        )