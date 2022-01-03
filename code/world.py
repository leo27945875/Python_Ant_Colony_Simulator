import numpy as np
from matplotlib.figure import Figure
from PIL import ImageTk
from numba import cuda
from utils import *
from ant import AntState


INF = float("inf")


class BG_Manager:
    def __init__(self, canvas, size, dpi, tag="BG", aboveTag=None):
        self.canvas   = canvas
        self.size     = size
        self.dpi      = dpi
        self.tag      = tag
        self.aboveTag = aboveTag
        self.imgID    = None
        self.newBG    = None
        self.CreateFig(size, dpi)
    
    def __call__(self, img, cmap=None):
        return self.ChangeBG(self.CreateNewBG(img, cmap))

    def CreateFig(self, size, dpi):
        fig = Figure(figsize=(size / dpi, size / dpi), dpi=dpi)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)
        self.fig, self.ax = fig, ax

    def CreateNewBG(self, img, cmap=None):
        self.ax.clear()
        self.ax.imshow(img, cmap=cmap)
        self.newBG = ImageTk.PhotoImage(ToPIL(self.fig))
        return self.newBG

    def ChangeBG(self, newBG):
        if self.imgID is not None: 
            self.canvas.delete(self.imgID)
            
        self.imgID = self.canvas.create_image((0, 0), anchor='nw', image=newBG, tag=self.tag)

        if self.aboveTag is None:
            self.canvas.tag_lower(self.tag)
        else:
            self.canvas.tag_raise(self.tag, self.aboveTag)
        
        return self.imgID


class World(BG_Manager):
    def __init__(self, gui, canvas, baseImgName, antHomePos, antFoodPoss, antHomeFoodSize, antHomeCode, antFoodCode, size, dpi, tag):
        super().__init__(canvas, size, dpi, tag)
        self.gui          = gui
        self.map          = ReadImage(baseImgName, isBinary=True, resize=size) * 1.
        self.antHomeCode  = antHomeCode
        self.antHomePos   = antHomePos
        self.antHomeRange = np.array([antHomePos[0] - antHomeFoodSize, antHomePos[1] - antHomeFoodSize, antHomePos[0] + antHomeFoodSize, antHomePos[1] + antHomeFoodSize])
        self.antHomeID    = canvas.create_rectangle(*self.antHomeRange, fill="cyan2")
        self.antHomeTextID = canvas.create_text(*antHomePos, text="H", width=16, fill="gray1")
        self.map[self.antHomeRange[1]: self.antHomeRange[3] + 1, self.antHomeRange[0]: self.antHomeRange[2] + 1] = self.antHomeCode
        
        self.antFoodCode = antFoodCode
        self.antFoodPoss = antFoodPoss
        self.antFoodRanges, self.antFoodIDs, self.antFoodTextIDs = [], [], []
        for i, antFoodPos in enumerate(antFoodPoss):
            antFoodRange  = np.array([antFoodPos[0] - antHomeFoodSize, antFoodPos[1] - antHomeFoodSize, antFoodPos[0] + antHomeFoodSize, antFoodPos[1] + antHomeFoodSize])
            antFoodID     = canvas.create_rectangle(*antFoodRange, fill="deep pink")
            antFoodTextID = canvas.create_text(*antFoodPos, text=f"{i}", width=16, fill="white")
            self.map[antFoodRange[1]: antFoodRange[3] + 1, antFoodRange[0]: antFoodRange[2] + 1] = self.antFoodCode
            self.antFoodRanges.append(antFoodRange)
            self.antFoodIDs.append(antFoodID)
            self.antFoodTextIDs.append(antFoodTextID)

        self.mapID = self(self.map, cmap="gray")
    
    def Update(self):
        self.gui.update()


class PheromoneMap(BG_Manager):
    def __init__(self, canvas, world, size, dpi, tag, aboveTag, evapo, minValue, maxValue):
        super().__init__(canvas, size, dpi, tag, aboveTag)
        self.canvas = canvas
        self.world  = world
        self.size   = size
        self.evapo  = evapo
        self.range  = [minValue, maxValue]
        self.map    = self.GetInitMap()
        self.mapID  = self(self.map)

        self.__checkRange     = -1
        self.__navigateField  = None

    def GetNavigation(self, position, state):
        x, y = position
        return self.__navigateField[state, x * self.size + y].copy_to_host()[::-1]

    def GetInitMap(self):
        worldMap = (self.world.map == 1) * 1.
        hr       = self.world.antHomeRange
        pMap     = np.zeros([self.size, self.size])
        pMap     = pMap + worldMap
        pMap     = np.repeat(pMap[... , np.newaxis], 3, axis=-1)
        pMap[hr[1]: hr[3] + 1, hr[0]: hr[2] + 1, 0] = INF

        for fr in self.world.antFoodRanges:
            pMap[fr[1]: fr[3] + 1, fr[0]: fr[2] + 1, 1] = INF

        return pMap
    
    def Evaporate(self):
        r = self.range
        map = self.map[:, :, :2]
        map[self.world.map == 0] *= self.evapo
        if not (r[0] == 0 and r[1] == INF):
            map = np.clip(map, *r)

        self.mapID = self(np.clip(self.map, 0, 1))
    
    def UpdateMap(self, ant):
        j, i = ant.position[0]
        if self.world.map[i, j] == 0:
            self.map[i, j, AntState.Reverse(ant.state)] += ant.pheromone
    
    def GenerateNavigate(self, checkRange):
        if self.__navigateField is None or self.__checkRange != checkRange:
            self.__checkRange    = checkRange
            self.__navigateField = cuda.device_array([2, self.size ** 2, 3])
        
        pMap = cuda.to_device(self.map)
        FindDirectField[self.size, self.size](pMap, self.__checkRange, self.__navigateField, AntState.LOOK_AT_HOME)
        FindDirectField[self.size, self.size](pMap, self.__checkRange, self.__navigateField, AntState.LOOK_AT_FOOD)
        cuda.synchronize()


########################################
#  Core engine of this simulation !!!  #
########################################
@cuda.jit
def FindDirectField(pMap, checkRange, result, antState):
    x, y = cuda.blockIdx.x, cuda.threadIdx.x
    h, w = pMap.shape[:2]
    idx  = y + x * cuda.blockDim.x

    if idx < h * w:
        result = result[antState][idx]
        xl, yt = max(x - checkRange, 0    ), max(y - checkRange, 0    )
        xr, yb = min(x + checkRange, w - 1), min(y + checkRange, h - 1)
        isSame = True
        for i in range(yt, yb + 1):
            for j in range(xl, xr + 1):
                if pMap[i, j, -1] != 1 and not (i == y and j == x):
                    if i == yt and j == xl: 
                        result[0]  = pMap[i, j, antState]
                        result[1:] = i, j
                    else:
                        value = pMap[i, j, antState]
                        if value != result[0]:
                            isSame = False
                            if value > result[0]:
                                result[0]  = value
                                result[1:] = i, j
        if isSame:
            result[0] = 1
        else:
            result[0] = 0


if __name__ == '__main__':
    c   = [20, 30]
    l   = 256
    r   = 2
    s   = 1
    a   = cuda.to_device(np.random.randn(l, l, 3)); a[c[1], c[0]] = 9
    res = cuda.device_array([2, l ** 2, 3])
    a[:, :, -1] = 0
    res[:] = -1
    FindDirectField[l, l](a, r, res, s)
    print(res.copy_to_host()[s, c[0] * l + c[1]])
    print(a[c[1] - r: c[1] + r + 1, c[0] - r: c[0] + r + 1, s].copy_to_host())
