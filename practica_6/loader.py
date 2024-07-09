from hardware import *
from log import logger

class Loader:

    def __init__(self):
        self._kernel = None

    @property
    def kernel(self):
        return self._kernel
    
    @kernel.setter
    def kernel(self, kernel):
        self._kernel = kernel


    def load(self, pcb):
        # loads the program in main memory
        progSize = len(pcb.instructions)
        if self.kernel.memoryManager.hasFreeMemoryFor(progSize):
            frames = self.kernel.memoryManager.getFrames(progSize)
            for page in range(0, len(frames)) :
                pcb.page_table[page] = frames[page]
            for index in range(0, progSize):
                inst = pcb.instructions[index]
                frame_index = frames[index // HARDWARE.mmu.frameSize]
                displacement = index % HARDWARE.mmu.frameSize
                fisicalDir = HARDWARE.mmu.frameSize * frame_index + displacement
                HARDWARE.memory.write(fisicalDir, inst)
            return True
        else:
            logger.error("No hay espacio suficiente en memoria")
            return False
        
LOADER = Loader()
