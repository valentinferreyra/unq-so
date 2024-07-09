from hardware import *
from PriorityQueueScheduler import *
from RoundRobinScheduler import *
from ShortestJobFirstScheduler import *
from so import *
import log
from memoryManager import *


def seleccionar_scheduler(): 
    def first_come_first_served():
        return FirstComeFirstServedScheduler()
    
    def priority_queue_nonpreemptive():
        return priorityQueueSchedulerNonPreemptive(6)
    
    def priority_queue_preemptive():
        return priorityQueueSchedulerPreemptive(15)
    
    def round_robin():
        return RoundRobinScheduler(3)

    def shortest_job_first_preemptive():
        return shortestJobFirstPreemptive()

    def shortest_job_first_nonpreemptive():
        return shortestJobFirstNonPreemptive()

    schedulers = {
        "1": first_come_first_served,
        "2": priority_queue_nonpreemptive,
        "3": priority_queue_preemptive,
        "4": round_robin,
        "5": shortest_job_first_preemptive,
        "6": shortest_job_first_nonpreemptive
    }
    
    while True:
        print("1. First Come First Served")
        print("2. Priority Queue (Nonpreemptive, Max priority: 5)")
        print("3. Priority Queue (Preemptive, Max priority: 5)")
        print("4. Round Robin (Default quantum: 3)")
        print("5. Shortest Job First (Preemptive)")
        print("6. Shortest Job First (Nonpreemptive)")
        
        choice = input("Ingrese el número correspondiente al algoritmo de scheduling deseado: ")
        
        if choice in schedulers:
            return schedulers[choice]()
        else:
            print("Opción inválida")

def seleccionar_ajuste_memoria():
    def first_fit():
        return FirstFitStrategy()
    
    def best_fit():
        return BestFitStrategy()
    
    def worst_fit():
        return WorstFitStrategy()
    
    fitStrategies = {
        "1": first_fit,
        "2": best_fit,
        "3": worst_fit
    }

    while True:
        print("1. First Fit")
        print("2. Best Fit")
        print("3. Worst Fit")
        
        choice = input("Ingrese el número correspondiente al algoritmo de ajuste de memoria deseado: ")
        
        if choice in fitStrategies:
            return fitStrategies[choice]()
        else:
            print("Opción inválida")

if __name__ == '__main__':
    log.setupLogger()
    log.logger.info('Starting emulator')

    ## setup our hardware and set memory size to 25 "cells"
    HARDWARE.setup(20)
    HARDWARE.cpu.enable_stats = True

    # prg1 = Program("prg1.exe", [ASM.CPU(4), ASM.IO(), ASM.CPU(3), ASM.IO(), ASM.CPU(2)])
    # prg2 = Program("prg2.exe", [ASM.CPU(7)])
    # prg3 = Program("prg3.exe", [ASM.CPU(4), ASM.IO(), ASM.CPU(1)])

    # pruebas aging
    # prg4 = Program("prg4.exe", [ASM.CPU(6), ASM.IO(), ASM.CPU(2), ASM.IO(), ASM.CPU(2),])
    # prg5 = Program("prg5.exe", [ASM.CPU(6), ASM.IO(), ASM.CPU(5)])
    # prg6 = Program("prg6.exe", [ASM.CPU(4), ASM.IO(), ASM.CPU(6)])

    # pruebas compactacion
    # prg1 = Program("prg1.exe", [ASM.CPU(7)])
    # prg2 = Program("prg2.exe", [ASM.CPU(5)])
    # prg3 = Program("prg3.exe", [ASM.CPU(3)])
    # prg4 = Program("prg4.exe", [ASM.CPU(7)])

    # kernel = Kernel(seleccionar_scheduler(), seleccionar_ajuste_memoria())
    # HARDWARE.switchOn()
    
    # kernel.run(prg1, 4)
    # kernel.run(prg2, 1)
    # kernel.run(prg3, 4)

    # kernel.crontab.add_job(7, prg4, 1)
    
    # pruebas fit strategies (first, best, worst)
    prg1 = Program("prg1.exe", [ASM.CPU(4)])
    prg2 = Program("prg2.exe", [ASM.CPU(5)])
    prg3 = Program("prg3.exe", [ASM.CPU(3)])
    prg4 = Program("prg4.exe", [ASM.CPU(3)])
    prg5 = Program("prg5.exe", [ASM.CPU(2)])

    kernel = Kernel(seleccionar_scheduler(), seleccionar_ajuste_memoria())
    HARDWARE.switchOn()
    
    kernel.run(prg1, 1)
    kernel.run(prg2, 3)
    kernel.run(prg3, 1)
    kernel.run(prg4, 4)

    kernel.crontab.add_job(12, prg5, 1)
    
    # execute all programs "concurrently"
    #kernel.run(prg1)
    #kernel.run(prg2)
    #kernel.run(prg3)
    # kernel.run(prg4, 3)
    # kernel.run(prg6, 10)
    # kernel.run(prg5, 6)

    # kernel.crontab.add_job(4 ,prg2, 1)  # En el tick 13 corre el prg6 con prioridad 4
    # kernel.crontab.add_job(9 ,prg3, 5)

