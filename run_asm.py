import ctypes
from ctypes import wintypes as wt
from enum import Enum
import binascii


class Reg(Enum):
    EAX = 0
    EBX = 3
    ECX = 1
    EDX = 2
    ESI = 6
    EDI = 7
    EBP = 5
    ESP = 4


class RunAsm:
    def __init__(self, lock):
        self.code = bytearray()
        self.calls_pos = []
        self.length = 0
        self.lock = lock

        self.VirtualAllocEx = ctypes.windll.kernel32.VirtualAllocEx
        self.VirtualAllocEx.argtypes = [
            wt.HANDLE, wt.LPVOID, ctypes.c_size_t,
            wt.DWORD, wt.DWORD
        ]
        self.VirtualAllocEx.restype = wt.LPVOID

        self.VirtualFreeEx = ctypes.windll.kernel32.VirtualFreeEx

        self.WriteProcessMemory = ctypes.windll.kernel32.WriteProcessMemory

        self.CreateRemoteThread = ctypes.windll.kernel32.CreateRemoteThread
        self.CreateRemoteThread.argtypes = [
            wt.HANDLE, wt.LPVOID, ctypes.c_size_t,
            wt.LPVOID, wt.LPVOID, wt.DWORD, wt.LPVOID
        ]
        self.CreateRemoteThread.restype = wt.HANDLE

        self.WaitForSingleObject = ctypes.windll.kernel32.WaitForSingleObject
        self.WaitForSingleObject.argtypes = [wt.HANDLE, wt.DWORD]
        self.WaitForSingleObject.restype = wt.DWORD

        self.CloseHandle = ctypes.windll.kernel32.CloseHandle
        self.CloseHandle.argtypes = [wt.HANDLE]
        self.CloseHandle.restype = wt.BOOL

    def hex(self):
        return binascii.hexlify(self.code).decode()

    def __len__(self):
        return self.length

    def asm_init(self):
        self.code.clear()
        self.calls_pos.clear()
        self.length = 0

    def asm_add_byte(self, hex_byte: int):
        assert 0 <= hex_byte < 0xff
        self.code.append(hex_byte)
        self.length += 1

    def asm_add_word(self, hex_word: int):
        assert 0 <= hex_word < 0xffff
        self.code.extend(hex_word.to_bytes(2, 'little'))
        self.length += 2

    def asm_add_dword(self, hex_dword: int):
        assert 0 <= hex_dword <= 0xffffffff
        self.code.extend(hex_dword.to_bytes(4, 'little'))
        self.length += 4

    def asm_add_list(self, hex_list):
        self.code.extend(hex_list)
        self.length += len(hex_list)

    def asm_push_byte(self, hex_byte):
        """push xx"""
        self.asm_add_byte(0x6a)
        self.asm_add_byte(hex_byte)

    def asm_push_dword(self, hex_dword):
        """push xxxxxxxx"""
        self.asm_add_byte(0x68)
        self.asm_add_dword(hex_dword)

    def asm_mov_exx(self, reg: Reg, value: int):
        """mov exx, xxxxxxxx"""
        self.asm_add_byte(0xb8 + reg.value)
        self.asm_add_dword(value)

    def asm_mov_exx_dword_ptr(self, reg: Reg, value: int):
        """mov exx, dword ptr [xxxxxxxx]"""
        self.asm_add_byte(0x8b)
        self.asm_add_byte(0x05 + reg.value * 8)
        self.asm_add_dword(value)

    def asm_mov_exx_dword_ptr_exx_add(self, reg: Reg, value: int):
        """mov exx, dword ptr [exx + xxxxxxxx]"""
        self.asm_add_byte(0x8b)
        self.asm_add_byte(0x80 + reg.value * 9)
        if reg == Reg.ESP:
            self.asm_add_byte(0x24)
        self.asm_add_dword(value)

    def asm_push_exx(self, reg: Reg):
        """push exx"""
        self.asm_add_byte(0x50 + reg.value)

    def asm_pop_exx(self, reg: Reg):
        """pop exx"""
        self.asm_add_byte(0x58 + reg.value)

    def asm_mov_exx_exx(self, reg_to: Reg, reg_from: Reg):
        """mov exx_to, exx_from"""
        self.asm_add_byte(0x8b)
        self.asm_add_byte(0xc0 + reg_to.value * 8 + reg_from.value)

    def asm_call(self, addr: int):
        self.asm_add_byte(0xe8)
        self.calls_pos.append(self.length)
        self.asm_add_dword(addr)

    def asm_ret(self):
        self.asm_add_byte(0xc3)

    def write_memory(self, phand, address, data, length=4):
        data = ctypes.c_ulong(data)
        self.WriteProcessMemory(phand, address, ctypes.byref(data), length, None)

    def asm_code_inject(self, phand):
        addr = self.VirtualAllocEx(phand, 0, self.length, 0x00001000, 0x40)
        if not addr:
            return
        for pos in self.calls_pos:
            call_addr = int.from_bytes(self.code[pos: pos + 4], 'little')
            call_addr -= (addr + pos + 4)
            self.code[pos: pos + 4] = call_addr.to_bytes(4, 'little', signed=True)
        write_size = ctypes.c_int(0)
        data = ctypes.create_string_buffer(bytes(self.code))
        self.lock.acquire()
        ret = self.WriteProcessMemory(phand, addr, ctypes.byref(data), self.length, ctypes.byref(write_size))
        self.lock.release()
        if ret == 0 or write_size.value != self.length:
            self.VirtualFreeEx(phand, addr, 0, 0x00008000)
            return
        thread = self.CreateRemoteThread(phand, None, 0, addr, None, 0, None)
        if not thread:
            self.VirtualFreeEx(phand, addr, 0, 0x00008000)
            return
        self.WaitForSingleObject(thread, -1)
        self.CloseHandle(thread)
        self.VirtualFreeEx(phand, addr, 0, 0x00008000)