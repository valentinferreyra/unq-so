from hardware import HARDWARE


class Crontab():

    def __init__(self, kernel):
        self._kernel = kernel
        # nos subscribimos al Clock para recibir cada click
        HARDWARE.clock.addSubscriber(self)
        ## Completar con lo que se necesite
        self._jobs = {}

    def add_job(self, tickNbr, program, prioridad):
        if self._jobs.get(tickNbr):
            self._jobs[tickNbr].append((program, prioridad))
        else:
            self._jobs[tickNbr] = [(program, prioridad)]


    def tick(self, tickNbr):
        if tickNbr in self._jobs:
            for program, prioridad in self._jobs[tickNbr]:
                self._kernel.run(program, prioridad)
