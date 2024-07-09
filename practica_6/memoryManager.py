import math
from hardware import HARDWARE
from log import logger

class MemoryManager():

    def __init__(self, kernel):
        self._kernel = kernel 
        self.memoryFrameSize = HARDWARE.mmu.frameSize # tamaño de cada celda de memoria (4 bytes)
        memorySize = HARDWARE.memory.size # capacidad total de memoria (16 celdas)
        self.free_frames = [i for i in range(memorySize // self.memoryFrameSize)]

    def hasFreeMemoryFor(self, size):
        return len(self.free_frames) * self.memoryFrameSize >= size
    
    def getFrames(self, progSize):
        pagesForProg = math.ceil(progSize / self.memoryFrameSize)
        progPages = []
        while (pagesForProg != 0):
            page = self.free_frames.pop(0)
            progPages.append(page)
            pagesForProg -= 1
        return progPages
    
    def freeFrames(self, page_table):
        for page in page_table.keys():
            self.free_frames.append(page_table[page])

    def __repr__(self) -> str:
        total_memory = HARDWARE.memory.size
        used_memory = total_memory - len(self.free_frames) * self.memoryFrameSize
        used_percentage = used_memory * 100 // total_memory
        free_percentage = 100 - used_percentage

        return (
            f"MemoryManager: \n"
            f"Free Frames Count: {len(self.free_frames)}\n"
            f"Usando {used_percentage}% | Libre {free_percentage}%\n"
            f"Free Frames List: {self.free_frames}\n"
        )

    def gantt(self) -> str:
        total_memory = HARDWARE.memory.size
        used_memory = total_memory - len(self.free_frames) * self.memoryFrameSize
        used_percentage = used_memory * 100 // total_memory
        free_percentage = 100 - used_percentage
        mem_bar = "".join(["█" * (used_memory), "▒" * (total_memory - used_memory)])

        
        return (
            f"MemoryManager: \n"
            f"Estructura: \n"
            f"Free Frames: {self.free_frames}\n"
            f"Usando {used_percentage}% | Libre {free_percentage}%\n"
            f"MEM_BAR: {mem_bar}")