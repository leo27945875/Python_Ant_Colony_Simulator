import tkinter as tk


class Panel:
    def __init__(self, gui, xCenter, totalTimePlace, width, height, yStart, textBGColor="gray2", valueBGColor="gray11", textFGColor="lime green", valueFGColor="cyan"):
        self.gui               = gui
        self.totalScoreVar     = tk.StringVar()
        self.tempScoreVar      = tk.StringVar()
        self.antLookForFoodVar = tk.StringVar()
        self.antLookForHomeVar = tk.StringVar()
        self.iterCountVar      = tk.StringVar()
        self.updateTimeVar     = tk.StringVar()
        self.totalTimeVar      = tk.StringVar()

        self.totalScoreTextLabel     = tk.Label(gui, text="Total Score:"       , bg=textBGColor, width=width, height=height, fg=textFGColor)
        self.tempScoreTextLabel      = tk.Label(gui, text="Temp Score:"        , bg=textBGColor, width=width, height=height, fg=textFGColor)
        self.antLookForFoodTextLabel = tk.Label(gui, text="Ants Look At Food:" , bg=textBGColor, width=width, height=height, fg=textFGColor)
        self.antLookForHomeTextLabel = tk.Label(gui, text="Ants Look At Home:" , bg=textBGColor, width=width, height=height, fg=textFGColor)
        self.iterCountTextLabel      = tk.Label(gui, text="Iteration:"         , bg=textBGColor, width=width, height=height, fg=textFGColor)
        self.updateTimeTextLabel     = tk.Label(gui, text="Time Every Iter:"   , bg=textBGColor, width=width, height=height, fg=textFGColor)

        self.totalScoreValueLabel     = tk.Label(gui, textvariable=self.totalScoreVar    , bg=valueBGColor, width=width    , height=height, fg=valueFGColor)
        self.tempScoreValueLabel      = tk.Label(gui, textvariable=self.tempScoreVar     , bg=valueBGColor, width=width    , height=height, fg=valueFGColor)
        self.antLookForFoodValueLabel = tk.Label(gui, textvariable=self.antLookForFoodVar, bg=valueBGColor, width=width    , height=height, fg=valueFGColor)
        self.antLookForHomeValueLabel = tk.Label(gui, textvariable=self.antLookForHomeVar, bg=valueBGColor, width=width    , height=height, fg=valueFGColor)
        self.iterCountValueLabel      = tk.Label(gui, textvariable=self.iterCountVar     , bg=valueBGColor, width=width    , height=height, fg=valueFGColor)
        self.updateTimeValueLabel     = tk.Label(gui, textvariable=self.updateTimeVar    , bg=valueBGColor, width=width    , height=height, fg=valueFGColor)
        self.totalTimeValueLabel      = tk.Label(gui, textvariable=self.totalTimeVar     , bg=valueBGColor, width=width * 3, height=height, fg=valueFGColor)

        self.totalScoreTextLabel     .place(x=xCenter, y=yStart      , anchor='center')
        self.totalScoreValueLabel    .place(x=xCenter, y=yStart + 35 , anchor="center")
        self.tempScoreTextLabel      .place(x=xCenter, y=yStart + 80 , anchor="center")
        self.tempScoreValueLabel     .place(x=xCenter, y=yStart + 115, anchor="center")
        self.antLookForFoodTextLabel .place(x=xCenter, y=yStart + 160, anchor="center")
        self.antLookForFoodValueLabel.place(x=xCenter, y=yStart + 195, anchor="center")
        self.antLookForHomeTextLabel .place(x=xCenter, y=yStart + 240, anchor="center")
        self.antLookForHomeValueLabel.place(x=xCenter, y=yStart + 275, anchor="center")
        self.iterCountTextLabel      .place(x=xCenter, y=yStart + 320, anchor="center")
        self.iterCountValueLabel     .place(x=xCenter, y=yStart + 355, anchor="center")
        self.updateTimeTextLabel     .place(x=xCenter, y=yStart + 400, anchor="center")
        self.updateTimeValueLabel    .place(x=xCenter, y=yStart + 435, anchor="center")
        self.totalTimeValueLabel     .place(x=totalTimePlace[0], y=totalTimePlace[1], anchor="center")
    
    def Update(self, nIter, totalScore, tempScore, nAntLookForFood, nAntLookForHome, updateTime, totalTime, maxNumAnt):
        nAnt = nAntLookForFood + nAntLookForHome
        self.totalScoreVar    .set(f"{totalScore}")
        self.tempScoreVar     .set(f"{tempScore} / {nAnt // 2}")
        self.antLookForFoodVar.set(f"{nAntLookForFood} / {nAnt}")
        self.antLookForHomeVar.set(f"{nAntLookForHome} / {nAnt}")
        self.iterCountVar     .set(f"{nIter}")
        self.updateTimeVar    .set(f"{updateTime:.4f}")
        self.totalTimeVar     .set(f"Total Time: {totalTime:.0f}   Max Ant Number: {maxNumAnt}")