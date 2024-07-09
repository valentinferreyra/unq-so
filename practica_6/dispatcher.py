import hardware
from hardware import *
from pcb import *

class Dispatcher:

    def load(self, pcb):
        HARDWARE.cpu.pc = pcb.pc
        HARDWARE.mmu.resetTLB()
        for page in pcb.page_table.keys():
            frame = pcb.page_table[page]
            HARDWARE.mmu.setPageFrame(page, frame)
        HARDWARE.timer.reset()

    def save(self, pcb):
        pcb.pc = HARDWARE.cpu.pc
        HARDWARE.cpu.pc = -1

DISPATCHER = Dispatcher()
