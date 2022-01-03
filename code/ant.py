import random
import numpy as np

class AntState:
    LOOK_AT_HOME = 0
    LOOK_AT_FOOD = 1

    def Reverse(state):
        return int(not state)


class Ant:
    def __init__(self, canvas, world, colony, initPos, size, speed, checkRange, pheromBase, pheromDecrease, probRandomWalk, life, momentum):
        self.canvas         = canvas
        self.world          = world
        self.colony         = colony
        self.size           = size
        self.checkRange     = checkRange
        self.pheromBase     = pheromBase
        self.pheromDecrease = pheromDecrease
        self.probRandomWalk = probRandomWalk
        self.life           = life
        self.momentum       = momentum
        self.elemID         = canvas.create_oval(initPos[0] - size, initPos[1] - size, 
                                                 initPos[0] + size, initPos[1] + size, 
                                                 fill="blue2")

        self.__worldMap    = self.world.map
        self.__state       = AntState.LOOK_AT_FOOD
        self.__choices     = [speed, -speed, 0]
        self.__nextPherom  = pheromBase
        self.__lastDirect  = np.array([0, 0])
        self.__stepsNoFood = 0
        self.__stepsNoHome = 0

        self.__moveEvents          = []
        self.__beforeMoveEvents    = []
        self.__findFoodEvents      = []
        self.__findHomeEvents      = []
        self.__resetToHomeEvents   = []
        self.__resetFindFoodEvents = []

        assert size > 1, "Size of Ants must > 1 ."
    
    @property
    def position(self):
        coord = self.canvas.coords(self.elemID)
        h, w  = self.__worldMap.shape
        x, y  = (coord[0] + coord[2]) // 2, (coord[1] + coord[3]) // 2
        return np.array([np.clip(x, 0, w - 1), np.clip(y, 0, h - 1)], dtype=int), np.array(coord, dtype=int), np.array([x, y], dtype=int)
    
    @property
    def pheromone(self):
        return self.__nextPherom
    
    @property
    def state(self):
        return self.__state
    
    @state.setter
    def state(self, state):
        if state == AntState.LOOK_AT_HOME:
            self.__nextPherom = self.pheromBase
            self.__state = state
            self.canvas.itemconfig(self.elemID, fill="purple1")
        elif state == AntState.LOOK_AT_FOOD:
            self.__nextPherom = self.pheromBase
            self.__state = state
            self.canvas.itemconfig(self.elemID, fill="blue2")
        else:
            raise ValueError("The state must be AntState.LOOK_AT_HOME (= 0) or AntState.LOOK_AT_FOOD (= 1).")

    def Move(self, pherom):
        self.InvokeBeforeMoveEvents()
        position, coord, realPosition = self.position
        direct = self.SampleDirect(pherom, position)
        direct = self.AdjustDirect(direct, position, coord)
        self.MoveOneStep(direct, realPosition)
        self.InvokeMoveEvents()
        self.UpdateState()

    def MoveOneStep(self, direct, realPosition):
        j, i = realPosition + direct
        h, w = self.__worldMap.shape
        if i <= 0 or j <= 0 or i >= h - 1 or j >= w - 1 or self.__worldMap[i, j] == 1:
            self.__lastDirect = direct // 2
        else:
            self.canvas.move(self.elemID, *direct)
    
    def RandomSampleDirect(self):
        x = random.choice(self.__choices)
        y = random.choice(self.__choices)
        return np.int32((np.array([x, y]) + self.__lastDirect) * 0.5)
    
    def SampleDirect(self, pherom, position):
        if random.uniform(0, 1) < self.probRandomWalk:
            return self.RandomSampleDirect()
        else:
            navigate = pherom.GetNavigation(position, self.state)
            if navigate[-1]:
                if self.state == AntState.LOOK_AT_HOME or random.uniform(0, 1) < (1 - self.probRandomWalk):
                    return self.RandomSampleDirect()
                else:
                    navigate = pherom.GetNavigation(position, AntState.Reverse(self.state))
                    if navigate[-1]:
                        return self.RandomSampleDirect()
                    else:
                        return np.int32((position - navigate[:2]) * (1 - self.momentum) + self.__lastDirect * self.momentum)

            else:
                return np.int32((navigate[:2] - position) * (1 - self.momentum) + self.__lastDirect * self.momentum)
    
    def AdjustDirect(self, direct, position, coord):
        worldMap          = self.__worldMap
        h, w, d           = worldMap.shape[0], worldMap.shape[1], self.__choices[0] // 2
        x, y              = np.clip(position[0], 0, w - 1), np.clip(position[1], 0, h - 1)
        xl, yl, xr, yr    = coord[0] - d, coord[1] - d, coord[2] + d, coord[3] + d
        self.__lastDirect = direct
        
        if   xl <  d     or worldMap[y, np.clip(xl, 0, w - 1)] == 1:
            direct[0] =  abs(direct[0])
        elif xr >= w - d or worldMap[y, np.clip(xr, 0, w - 1)] == 1:
            direct[0] = -abs(direct[0])
        
        if   yl <  d     or worldMap[np.clip(yl, 0, h - 1), x] == 1:
            direct[1] =  abs(direct[1])
        elif yr >= h - d or worldMap[np.clip(yr, 0, h - 1), x] == 1:
            direct[1] = -abs(direct[1])
        
        return np.clip(direct, self.__choices[1], self.__choices[0])
        
    def SetMoveSpeed(self, speed):
        self.__choices  = [speed, -speed, 0]
    
    def UpdateState(self):
        if self.state == AntState.LOOK_AT_FOOD:
            self.__stepsNoFood += 1
        else:
            self.__stepsNoHome += 1
        
        self.CheckReset()

        if self.state == AntState.LOOK_AT_FOOD and self.IsFindFood():
            self.__stepsNoFood = 0
            self.state = AntState.LOOK_AT_HOME
            self.InvokeFindFoodEvents()
        elif self.state == AntState.LOOK_AT_HOME and self.IsFindHome():
            self.__stepsNoHome = 0
            self.state = AntState.LOOK_AT_FOOD
            self.InvokeHomeFoodEvents()
        
        self.__nextPherom *= self.pheromDecrease
    
    def IsFindFood(self):
        j, i = self.position[0]
        return self.__worldMap[i, j] == self.world.antFoodCode
    
    def IsFindHome(self):
        j, i = self.position[0]
        return self.__worldMap[i, j] == self.world.antHomeCode
    
    def CheckReset(self):
        if self.__stepsNoFood > self.life:
            self.__stepsNoFood = 0
            if random.uniform(0, 1) < 0.5:
                direct = self.world.antHomePos - self.position[0]
                self.canvas.move(self.elemID, *direct)
                self.state = AntState.LOOK_AT_FOOD
                self.InvokeResetToHomeEvents()
        
        if self.__stepsNoHome > self.life:
            self.__stepsNoHome = 0
            if random.uniform(0, 1) < 0.5:
                self.state = AntState.LOOK_AT_FOOD
                self.__nextPherom = 0.
                self.InvokeResetFindFoodEvents()
    
    # ----------------- Events -----------------
    
    def AddMoveEvent(self, event):
        if event not in self.__moveEvents:
            self.__moveEvents.append(event)
    
    def AddBeforeMoveEvent(self, event):
        if event not in self.__beforeMoveEvents:
            self.__beforeMoveEvents.append(event)
    
    def AddFindFoodEvent(self, event):
        if event not in self.__findFoodEvents:
            self.__findFoodEvents.append(event)
    
    def AddFindHomeEvent(self, event):
        if event not in self.__findHomeEvents:
            self.__findHomeEvents.append(event)

    def AddResetToHomeEvent(self, event):
        if event not in self.__resetToHomeEvents:
            self.__resetToHomeEvents.append(event)
    
    def AddResetFindFoodEvent(self, event):
        if event not in self.__resetFindFoodEvents:
            self.__resetFindFoodEvents.append(event)
    
    def InvokeMoveEvents(self):
        if self.__moveEvents:
            for event in self.__moveEvents:
                event(self)
    
    def InvokeBeforeMoveEvents(self):
        if self.__beforeMoveEvents:
            for event in self.__beforeMoveEvents:
                event(self)

    def InvokeFindFoodEvents(self):
        if self.__findFoodEvents:
            for event in self.__findFoodEvents:
                event(self)
    
    def InvokeHomeFoodEvents(self):
        if self.__findHomeEvents:
            for event in self.__findHomeEvents:
                event(self)
    
    def InvokeResetToHomeEvents(self):
        if self.__resetToHomeEvents:
            for event in self.__resetToHomeEvents:
                event(self)
    
    def InvokeResetFindFoodEvents(self):
        if self.__resetFindFoodEvents:
            for event in self.__resetFindFoodEvents:
                event(self)


class AntColony:
    def __init__(self, canvas, world, pherom, initNum, maxNum, addNum, antHomePos, antSize, antSpeed, antCheckRange, antPheromBase, antPheromDecrease, antRamdomWalkProb, antLife, antMomentum):
        self.checkRange = antCheckRange
        self.maxAntNum  = maxNum
        self.nowAntNum  = 0
        self.addAntNum  = addNum
        self.pherom     = pherom
        self.colony     = np.empty([0], dtype=Ant)

        self.__nAntLookForFood = 0
        self.__nAntLookForHome = 0
        self.__totalFoodScore  = 0
        self.__tempFoodScore   = 0

        self.move                  = lambda x: x.Move(pherom)
        self.moveVector            = np.vectorize(lambda x: x.Move(pherom))
        self.addMoveEvent          = np.vectorize(lambda x, event: x.AddMoveEvent(event))
        self.addBeforeMoveEvent    = np.vectorize(lambda x, event: x.AddBeforeMoveEvent(event))
        self.addFoodEvent          = np.vectorize(lambda x, event: x.AddFindFoodEvent(event))
        self.addHomeEvent          = np.vectorize(lambda x, event: x.AddFindHomeEvent(event))
        self.addResetToHomeEvent   = np.vectorize(lambda x, event: x.AddResetToHomeEvent(event))
        self.addResetFindFoodEvent = np.vectorize(lambda x, event: x.AddResetFindFoodEvent(event))
        self.generateNewAnt        = lambda: Ant(canvas, world, self, antHomePos, antSize, antSpeed, antCheckRange, antPheromBase, antPheromDecrease, antRamdomWalkProb, antLife, antMomentum)

        self.GenerateNewAnts(initNum)
        
    @property
    def statistics(self):
        return self.__totalFoodScore, self.__tempFoodScore, self.__nAntLookForFood, self.__nAntLookForHome
    
    def GenerateNewAnts(self, n):
        if self.nowAntNum < self.maxAntNum:
            numNewAnts             = min(n, self.maxAntNum - self.nowAntNum)
            newAnts                = np.array([self.generateNewAnt() for _ in range(numNewAnts)], dtype=Ant)
            self.colony            = np.append(self.colony, newAnts)
            self.nowAntNum         += numNewAnts
            self.__nAntLookForFood += numNewAnts

            self.AddMoveEvent(self.pherom.UpdateMap)
            self.AddFindFoodEvent(self.FindFood)
            self.AddFindHomeEvent(self.FindHome)
            self.AddFindHomeEvent(self.AddScore)
            self.AddResetFindFoodEvent(self.FindHome)
    
    def CheckIsGenerateAnts(self):
        if self.__tempFoodScore >= self.nowAntNum // 2:
            self.__tempFoodScore = 0
            self.GenerateNewAnts(self.addAntNum)

    def Move(self):
        self.moveVector(self.colony)
    
    def AddMoveEvent(self, event):
        self.addMoveEvent(self.colony, event)
    
    def AddBeforeMoveEvent(self, event):
        self.addBeforeMoveEvent(self.colony, event)
    
    def AddFindFoodEvent(self, event):
        self.addFoodEvent(self.colony, event)

    def AddFindHomeEvent(self, event):
        self.addHomeEvent(self.colony, event)

    def AddResetToHomeEvent(self, event):
        self.addResetToHomeEvent(self.colony, event)
    
    def AddResetFindFoodEvent(self, event):
        self.addResetFindFoodEvent(self.colony, event)
    
    def FindFood(self, ant):
        self.__nAntLookForHome += 1
        self.__nAntLookForFood -= 1
    
    def FindHome(self, ant):
        self.__nAntLookForHome -= 1
        self.__nAntLookForFood += 1
    
    def AddScore(self, ant):
        self.__totalFoodScore += 1
        self.__tempFoodScore  += 1
    