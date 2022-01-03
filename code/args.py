IMAGE_FOLDER           = "../images"                                 # The folder which contains map pictures.
WORLD_IMAGE            = "map2.png"                                  # The name of the map picture you want to use. 

BACKGROUND_DPI         = 100                                         # DPI of pictures in GUI.
WINDOW_SIZE            = 512                                         # Size of the map.
PANEL_SIZE             = 200                                         # Size of the panel on the right.
LABEL_WIDTH            = 20                                          # Width of labels in the right panel.
LABEL_HEIGHT           = 2                                           # Height of labels in the right panel.
LABEL_Y_START          = 30                                          # Top y value of the right panel.
TOTAL_TIME_PLACE       = [WINDOW_SIZE // 2, WINDOW_SIZE + 20]        # Location of the bottom panel.

WORLD_TAG              = "World"                                     # Tag of the world picture.
PHEROMONE_TAG          = "Pheromone"                                 # Tag of the pheromone picture.
HOME_CODE              = 0.2                                         # Code of the home of ants.
FOOD_CODE              = 0.5                                         # Code of foods.
MAX_PHEROMONE          = 400                                         # Maximum value of pheromone.
MIN_PHEROMONE          = 1e-3                                        # Minimum value of pheromone.
PHEROMONE_EVAPORATION  = 0.99                                        # Evaporation rate of pheromone.
HOME_FOOD_SIZE         = 15                                          # Size of the cubes that represent home and foods.
FOOD_PLACES            = [[400, 480], [30, 200], [250, 400]]         # Locations of foods.

ANT_INIT_PLACE         = [30, 30]                                    # Location of the home of ants.
ANT_INIT_NUMBER        = 128                                         # Initial number of ants.
ANT_MAX_NUMBER         = 512                                         # Maximum number of ants.
ANT_ADD_NUMBER         = 32                                          # Increasing number of ants when there is enough food.
ANT_SIZE               = 3                                           # Size of each ant.
ANT_SPEED              = 15                                          # Speed of each ant.
ANT_CHECK_RANGE        = 20                                          # The range to look for maximum pheromone direction of each ant.
ANT_PHEROMONE_BASE     = 100                                         # Initial pheromone value of each ant.
ANT_PHEROMONE_DECREASE = 0.96                                        # Discount rate of pheromone of each ant.
ANT_RANDOM_WALK_PROB   = 0.5                                         # Probability to random walk of each ant.
ANT_MOMENTUM           = 0.7                                         # Intensity of momentum of each ant.
ANT_LIFE               = 1000                                        # Longevity of each ant. Will be reset when the state of the ant changes.


