from abc import abstractmethod

class Scheduler():

    @property
    @abstractmethod
    def getReadyQueue(self):
        pass

    @property
    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def add(self, pcb):
        pass

    @abstractmethod
    def isEmpty(self):
        pass

    @abstractmethod
    def pop(self):
        pass

    @abstractmethod
    def mustExpropiate(self, pcbInCPU, pcbToAdd):
        pass

    @abstractmethod
    def tick(self):
        pass

    def isValidPriority(self, priority):
        return True