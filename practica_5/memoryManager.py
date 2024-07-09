from hardware import HARDWARE
from log import logger

class MemoryManager():

    def __init__(self, kernel, fitStrategy):
        self.fitStrategy = fitStrategy # estrategia de selección de bloque de memoria
        self._kernel = kernel 
        memorySize = HARDWARE.memory.size # capacidad total de memoria (16 celdas)
        self.max_dir = memorySize - 1 # dirección máxima de memoria (15)
        self.free_cells_in_memory = memorySize # cantidad de celdas libres de memoria (16)

        self._map_free_blocks_ab = {0 : self.max_dir} # diccionario de bloques libres (0:15)
        self._map_free_blocks_ba = {self.max_dir : 0} # diccionario de bloques libres (15:0)
        self._size_map = {memorySize : [(0, self.max_dir)]} # diccionario de bloques libres por tamaño (16: [(0, 15)])

    def freeBlock(self, baseDir, size):
        self.free_cells_in_memory += size # incrementa la cantidad de celdas libres en memoria
        self.addNewBlock(baseDir, baseDir + size-1) # agrega un nuevo bloque de memoria libre a partir de la dirección baseDir

    def hasFreeMemoryFor(self, size):
        return self.free_cells_in_memory >= size

    def getFreeBlock(self, size):
        key = self.findKey(size) 
        if key is None:
            return None
        self.free_cells_in_memory -= size
        return self.findFreeBlock(key, size)
    
    def findFreeBlock(self, key, size):
        old_block = self._size_map[key][0]
        if self._blockSize(old_block) == size:
            self.removeBlock(old_block)
        else:
            new_block = (old_block[0] + size, old_block[1])
            self.updateBlock(old_block, new_block)
        return old_block[0]
    
    def removeBlock(self, block):
        self.removeToSizeMap(block)
        self.removeToBothMaps(block)

    def removeToBothMaps(self, block):
        del self._map_free_blocks_ab[block[0]]
        del self._map_free_blocks_ba[block[1]]
    
    def updateBlock(self, old_block, new_block):
        self.removeToSizeMap(old_block) # elimina el bloque de memoria libre old_block del diccionario de bloques libres por tamaño
        self.addBlockToSizeMap(new_block) # agrega el bloque de memoria libre new_block al diccionario de bloques libres por tamaño
        self.updateBothMaps(old_block, new_block) # actualiza los diccionarios de bloques libres

    def reset(self):
        self.free_cells_in_memory = self.max_dir + 1
        self._map_free_blocks_ab = {0 : self.max_dir}
        self._map_free_blocks_ba = {self.max_dir : 0}
        self._size_map = {self.max_dir + 1 : [(0, self.max_dir)]}

    def updateBothMaps(self, old_block, new_block):
        self._map_free_blocks_ab[new_block[0]] = new_block[1]
        self._map_free_blocks_ba[old_block[1]] = new_block[0]
        del self._map_free_blocks_ab[old_block[0]]

    def findKey(self, size):
        return self.fitStrategy.findKey(size, self._size_map)
            
    def addNewBlock(self, initialDir, endDir):
        mergedBlock = self.mergeDirs(initialDir, endDir) # obtiene el bloque de memoria libre a partir de las direcciones initialDir y endDir
        self.addToBothMaps(mergedBlock)
        self.addBlockToSizeMap(mergedBlock)

    def mergeDirs(self, initialDir, endDir):
        return (self.getMergedInit(initialDir), self.getMergedEnd(endDir))
    
    def getMergedInit(self, initialDir):
        left_block = self._getLeftBlock(initialDir)
        init_l, end_l = left_block
        if init_l is not None:
            self.removeToSizeMap(left_block)
            self._splitInit(end_l)
            return init_l
        return initialDir
    
    def getMergedEnd(self, endDir):
        right_block = self._getRightBlock(endDir)
        init_r, end_r = right_block
        if end_r is not None:
            self.removeToSizeMap(right_block)
            self._splitEnd(init_r)
            return end_r
        return endDir
    
    def _splitInit(self, end_l):
        del self._map_free_blocks_ba[end_l]

    def _splitEnd(self, init_r):
        del self._map_free_blocks_ab[init_r]

    def removeToSizeMap(self, block):
        size = self._blockSize(block)
        self._size_map[size].remove(block)
        if self._size_map[size] == []:
            del self._size_map[size]
    
    def _blockSize(self, block):
        return block[1] - block[0] + 1
    
    def _getLeftBlock(self, initialDir):
        return (self._map_free_blocks_ba.get(initialDir - 1, None), initialDir - 1)
    
    def _getRightBlock(self, endDir):
        return (endDir + 1, self._map_free_blocks_ab.get(endDir + 1, None))

    def addBlockToSizeMap(self, block):
        initialDir, endDir = block
        block_size = endDir - initialDir + 1
        if self._size_map.get(block_size, None):
            self._size_map[block_size].append((initialDir, endDir))
        else:
            self._size_map[block_size] = [(initialDir, endDir)]

    def addToBothMaps(self, block):
        initialDir, endDir = block
        self._map_free_blocks_ab[initialDir] = endDir
        self._map_free_blocks_ba[endDir] = initialDir

    def blockList(self):
        return sorted([(k, v) for k, v in self._map_free_blocks_ab.items()])
            
    def gantt(self) -> str:
        total_memory = HARDWARE.memory.size
        used_memory = total_memory - self.free_cells_in_memory
        used_percentage = used_memory * 100 // total_memory
        free_percentage = 100 - used_percentage
        blocks_count = len(self._map_free_blocks_ab)
        max_block_size = max(self._size_map.keys(), default=0)
        mem_bar = "".join(["█" * (used_memory), "▒" * (self.free_cells_in_memory)])

        
        return (
            f"MemoryManager: \n"
            f"Fit strategy: {self.fitStrategy.__class__.__name__}\n"
            f"Estructura: \n"
            f"\t map: base -> limit: {self._map_free_blocks_ab} \n"
            f"\t map: limit -> base: {self._map_free_blocks_ba} \n"
            f"\t size_map: size -> [(base, limit)]: {self._size_map} \n"
            f"Free Blocks list: {self.blockList()}\n"
            f"Free cells: {self.free_cells_in_memory}/{total_memory}\n"
            f"Cantidad de bloques disponibles: {blocks_count}\n"
            f"Tamaño máximo de bloque: {max_block_size}\n"
            f"Usando {used_percentage}% | Libre {free_percentage}%\n"
            f"MEM_BAR: {mem_bar}"
        )
    
    def __repr__(self) -> str:
        total_memory = HARDWARE.memory.size
        used_memory = total_memory - self.free_cells_in_memory
        used_percentage = used_memory * 100 // total_memory
        free_percentage = 100 - used_percentage

        return (
            f"MemoryManager: \n"
            f"Fit strategy: {self.fitStrategy.__class__.__name__}\n"
            f"Free cells: {self.free_cells_in_memory}/{total_memory}\n"
            f"Usando {used_percentage}% | Libre {free_percentage}%\n"
            f"Free Blocks List: {self.blockList()}\n"
        )

# abstract class FitStrategy

class FitStrategy:
    
        def findKey(self, size, size_map):
            pass

class FirstFitStrategy(FitStrategy):
    
    def findKey(self, size, size_map):
        for key in size_map.keys():
            if key >= size:
                return key
        return None
    
class BestFitStrategy(FitStrategy):
        
    def findKey(self, size, size_map):
        keys = list(size_map.keys())
        keys.sort()
        for key in keys:
            if key >= size:
                return key
        return None
    
class WorstFitStrategy(FitStrategy):
        
    def findKey(self, size, size_map):
        keys = list(size_map.keys())
        keys.sort(reverse=True)
        for key in keys:
            if key >= size:
                return key
        return None