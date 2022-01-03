import time
import tkinter as tk

from args  import *
from utils import *
from world import *
from panel import *
from ant   import *


def MainLoop():
    # Setting of the TK window:
    root = tk.Tk()
    root['bg'] = "bisque"
    root.title("Ants Simulation 309612092")
    root.geometry(f"{WINDOW_SIZE + PANEL_SIZE}x{WINDOW_SIZE + (TOTAL_TIME_PLACE[1] - WINDOW_SIZE) * 2}")
    root.resizable(0, 0)

    # Setting of the canvas in the TK window:
    canvas = tk.Canvas(root, width=WINDOW_SIZE, height=WINDOW_SIZE, highlightthickness=0)
    canvas.place(x=0, y=0, anchor='nw')

    # Some important objects:
    world  = World(root, 
                   canvas, 
                   WORLD_IMAGE, 
                   ANT_INIT_PLACE, 
                   FOOD_PLACES, 
                   HOME_FOOD_SIZE, 
                   HOME_CODE, 
                   FOOD_CODE, 
                   WINDOW_SIZE, 
                   BACKGROUND_DPI, 
                   WORLD_TAG)
    pherom = PheromoneMap(canvas, 
                          world, 
                          WINDOW_SIZE, 
                          BACKGROUND_DPI, 
                          PHEROMONE_TAG, 
                          WORLD_TAG, 
                          PHEROMONE_EVAPORATION, 
                          MIN_PHEROMONE, 
                          MAX_PHEROMONE)
    colony = AntColony(canvas, 
                       world, 
                       pherom, 
                       ANT_INIT_NUMBER, 
                       ANT_MAX_NUMBER, 
                       ANT_ADD_NUMBER, 
                       ANT_INIT_PLACE, 
                       ANT_SIZE, 
                       ANT_SPEED, 
                       ANT_CHECK_RANGE, 
                       ANT_PHEROMONE_BASE, 
                       ANT_PHEROMONE_DECREASE, 
                       ANT_RANDOM_WALK_PROB,
                       ANT_LIFE, 
                       ANT_MOMENTUM)
    panel  = Panel(root, 
                   WINDOW_SIZE + PANEL_SIZE // 2, 
                   TOTAL_TIME_PLACE, 
                   LABEL_WIDTH, 
                   LABEL_HEIGHT, 
                   LABEL_Y_START)

    # Main loop:
    nIter, t = 0, time.time()
    while True:
        # Record the running time for each loop:
        t0, nIter = time.time(), nIter + 1

        # Generate the navigation map for all ants:
        pherom.GenerateNavigate(colony.checkRange)

        # Move all ants according to the navigation map:
        colony.Move()

        # Evaporate the pheromones:
        pherom.Evaporate()

        # If score exceeds the threshold, double the number of ants:
        colony.CheckIsGenerateAnts()

        # Update TK:
        world.Update()
        panel.Update(nIter, *colony.statistics, time.time() - t0, time.time() - t, colony.maxAntNum)


if __name__ == '__main__':

    MainLoop()


