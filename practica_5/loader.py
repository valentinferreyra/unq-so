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
            baseDir = self.kernel.memoryManager.getFreeBlock(progSize)
            if baseDir == None:
                self.kernel.runCompactation()
                baseDir = self.kernel.memoryManager.getFreeBlock(progSize)
            for index in range(0, progSize):
                inst = pcb.instructions[index]
                HARDWARE.memory.write(baseDir + index, inst)
            return baseDir
        else:
            return logger.error("No hay espacio suficiente en memoria")
        
LOADER = Loader()
