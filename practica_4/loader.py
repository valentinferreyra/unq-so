from hardware import *


class Loader:

    def __init__(self):
        self._nextBaseDir = 0

    def load(self, program):
        # loads the program in main memory
        progSize = len(program.instructions)
        for index in range(0, progSize):
            inst = program.instructions[index]
            HARDWARE.memory.write(self._nextBaseDir + index, inst)
        baseDir = self._nextBaseDir
        self._nextBaseDir += progSize
        return baseDir

LOADER = Loader()
