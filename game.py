# game.py
#
# The top level loop that runs the game until Tallon eventually loses.
#
# run this using:
#
# python3 game.py
#
# Written by: Simon Parsons
# Last Modified: 12/01/22

from world import World
from tallon import Tallon
from arena import Arena
import utils
import time

# How we set the game up. Create a world, then connect player and
# display to it.
gameWorld = World()
player = Tallon(gameWorld)
display = Arena(gameWorld)

# Uncomment this for a printout of world state at the start
# utils.printGameState(gameWorld)

# Now run...
while not(gameWorld.isEnded()):
    gameWorld.updateTallon(player.makeMove())
    gameWorld.updateMeanie()
    gameWorld.updateClock()
    gameWorld.addMeanie()
    gameWorld.updateScore()
    display.update()
    # Uncomment this for a printout of world state every step
    # utils.printGameState(gameWorld)
    time.sleep(1)

print("Final score:", gameWorld.getScore())
