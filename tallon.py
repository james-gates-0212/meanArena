# tallon.py
#
# The code that defines the behaviour of Tallon. This is the place
# (the only place) where you should write code, using access methods
# from world.py, and using makeMove() to generate the next move.
#
# Written by: Simon Parsons
# Last Modified: 12/01/22

import world
import random
import utils
from utils import Directions

class Tallon():

    def __init__(self, arena):

        # Make a copy of the world an attribute, so that Tallon can
        # query the state of the world
        self.gameWorld = arena

        # What moves are possible.
        self.moves = [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]
        
    def makeMove(self):
        # This is the function you need to define

        # For now we have a placeholder, which always moves Tallon
        # directly towards any existing bonuses. It ignores Meanies
        # and pits.
        # 
        # Get the location of the Bonuses.
        allBonuses = self.gameWorld.getBonusLocation()

        # if there are still bonuses, move towards the next one.
        if len(allBonuses) > 0:
            nextBonus = allBonuses[0]
            myPosition = self.gameWorld.getTallonLocation()
            # If not at the same x coordinate, reduce the difference
            if nextBonus.x > myPosition.x:
                return Directions.EAST
            if nextBonus.x < myPosition.x:
                return Directions.WEST
            # If not at the same y coordinate, reduce the difference
            if nextBonus.y < myPosition.y:
                return Directions.NORTH
            if nextBonus.y > myPosition.y:
                return Directions.SOUTH

        # if there are no more bonuses, Tallon doesn't move
