# world.py
#
# A file that represents the Mean Arena, keeping track of the position
# of all the objects: sludge pits, Blue Meanies, bonus packs, and
# Tallon, and moving them when necessary.
#
# Written by: Simon Parsons
# Last Modified: 12/01/22
#
# Thanks to Ethan Henderson for tracking down several bugs.

import random
import config
import utils
from utils import Pose
from utils import Directions
from utils import State

class World():

    def __init__(self):

        # Import boundaries of the world. because we index from 0,
        # these are one less than the number of rows and columns.
        self.maxX = config.worldLength - 1
        self.maxY = config.worldBreadth - 1

        # Keep a list of locations that have been used.
        self.locationList = []

        # Add the initial set of Meanies
        self.mLoc = []
        for i in range(config.numberOfMeanies):
            newLoc = utils.pickUniquePose(self.maxX, self.maxY, self.locationList)
            self.mLoc.append(newLoc)
            self.locationList.append(newLoc)

        # Add Tallon
        newLoc = utils.pickUniquePose(self.maxX, self.maxY, self.locationList)
        self.tLoc = newLoc
        self.locationList.append(newLoc)

        # Add Bonuses
        self.bLoc = []
        for i in range(config.numberOfBonuses):
            newLoc = utils.pickUniquePose(self.maxX, self.maxY, self.locationList)
            self.bLoc.append(newLoc)
            self.locationList.append(newLoc)

        # Pits
        self.pLoc = []
        for i in range(config.numberOfPits):
            newLoc = utils.pickUniquePose(self.maxX, self.maxY, self.locationList)
            self.pLoc.append(newLoc)
            self.locationList.append(newLoc)

        # Game state
        self.status = State.PLAY

        # Clock
        self.clock = 0

        # Score
        self.score = 0

        # Did Tallon just successfully grab a bonus?
        self.grabbed = False
        
    #
    # Access Methods
    #
    # These are the functions that should be used by Tallon to access
    # information about the world.

    # Where is/are the Meanies?
    def getMeanieLocation(self):
        return self.distanceFiltered(self.mLoc)

    # Where is Tallon?
    def getTallonLocation(self):
        return self.tLoc

    # Where are the Bonuses?
    def getBonusLocation(self):
        return self.distanceFiltered(self.bLoc)

    # Where are the Pits?
    def getPitsLocation(self):
        return self.distanceFiltered(self.pLoc)

    # Clock value
    def getClock(self):
        return self.clock

    # Current score
    def getScore(self):
        return self.score

    # Did we just grab a bonus?
    def justGrabbed(self):
        return self.grabbed

    # What is the current game state?
    def getGameState(self):
        return self.status

    # Does Tallon feel the wind?
    def tallonWindy(self):
        return self.isWindy(self.tLoc)

    # Does Tallon smell the Meanie?
    def tallonSmelly(self):
        return self.isSmelly(self.tLoc)

    # Does Tallon see the glow?
    def tallonGlow(self):
        return self.isGlowing(self.tLoc)
 
    #
    # Methods
    #
    # These are the functions that are used to update and report on
    # world information.

    def isEnded(self):
        dead = False
        won = False
        # Has Tallon met a Meanie?
        for i in range(len(self.mLoc)):
            if utils.sameLocation(self.tLoc, self.mLoc[i]):
                print("Oops! Met a Meanie")
                dead = True
                self.status = State.LOST
                
        # Did Tallon fall in a Pit?
        for i in range(len(self.pLoc)):
            if utils.sameLocation(self.tLoc, self.pLoc[i]):
                print("Arghhhhh! Fell in a pit")
                dead = True
                self.status = State.LOST

        # Did Tallon grab all the bonuses?
        if len(self.bLoc) == 0:
            self.status
            # Right now this does not trigger anything in terms of game state.
            #print("Got the last bonus!")
            
        if dead == True:
            print("Game Over!")
            return True
            
    # Implements the move chosen by Tallon
    def updateTallon(self, direction):
        # Set the bonus grabbed flag to False
        # Correction due to Rachel Trimble here
        self.grabbed = False
        # Implement non-determinism if appropriate
        direction = self.probabilisticMotion(direction)
        # Note that y increases *down* the grid. Correction due to
        # Ethan Henderson and Negar Pourmoazemi here.
        if direction == Directions.SOUTH:
            if self.tLoc.y < self.maxY:
                self.tLoc.y = self.tLoc.y + 1
            
        if direction == Directions.NORTH:
            if self.tLoc.y > 0:
                self.tLoc.y = self.tLoc.y - 1
                
        if direction == Directions.EAST:
            if self.tLoc.x < self.maxX:
                self.tLoc.x = self.tLoc.x + 1
                
        if direction == Directions.WEST:
            if self.tLoc.x > 0:
                self.tLoc.x = self.tLoc.x - 1

        # Did Tallon just grab a bonus?
        match = False
        index = 0
        for i in range(len(self.bLoc)):
            if utils.sameLocation(self.tLoc, self.bLoc[i]):
                match = True
                index = i
                self.grabbed = True
                self.updateScoreWithBonus()

        # Assumes that bonuses have different locations (now true). 
        if match:
            self.bLoc.pop(index)
            if len(self.bLoc) == 0:
                print("Got the last bonus!")
            else:
                print("Bonus, yeah!")

    # Implement nondeterministic motion, if appropriate.
    def probabilisticMotion(self, direction):
        if config.nonDeterministic:
            dice = random.random()
            if dice < config.directionProbability:
                return direction
            else:
                return self.sideMove(direction)
        else:
            return direction
        
    # Move at 90 degrees to the original direction.
    def sideMove(self, direction):
        # Do we head left or right of the intended direction?
        dice =  random.random()
        if dice > 0.5:
            left = True
        else:
            left = False
        if direction == Directions.NORTH:
            if left:
                return Directions.WEST
            else:
                return Directions.EAST

        if direction == Directions.SOUTH:
            if left:
                return Directions.EAST
            else:
                return Directions.WEST

        if direction == Directions.WEST:
            if left:
                return Directions.SOUTH
            else:
                return Directions.NORTH

        if direction == Directions.EAST:
            if left:
                return Directions.NORTH
            else:
                return Directions.SOUTH
            
    # Move the Meanie if that is appropriate
    #
    # Need a decrementDifference function to tidy things up
    #
    def updateMeanie(self):
        if config.dynamic:
            for i in range(len(self.mLoc)):
                if utils.separation(self.mLoc[i], self.tLoc) < config.senseDistance:
                    self.moveToTallon(i)
                else:
                    self.makeRandomMove(i)

    # Head towards Tallon
    def moveToTallon(self, i):
        target = self.tLoc
        # If same x-coordinate, move in the y direction
        if self.mLoc[i].x == target.x:
            self.mLoc[i].y = self.reduceDifference(self.mLoc[i].y, target.y)        
        # If same y-coordinate, move in the x direction
        elif self.mLoc[i].y == target.y:
            self.mLoc[i].x = self.reduceDifference(self.mLoc[i].x, target.x)        
        # If x and y both differ, approximate a diagonal
        # approach by randomising between moving in the x and
        # y direction.
        else:
            dice = random.random()
            if dice > 0.5:
                self.mLoc[i].y = self.reduceDifference(self.mLoc[i].y, target.y)        
            else:
                self.mLoc[i].x = self.reduceDifference(self.mLoc[i].x, target.x)        

    # Move value towards target.
    def reduceDifference(self, value, target):
        if value < target:
            return value+1
        elif value > target:
            return value-1
        else:
            return value

    # Randomly pick to change either x or y coordinate, and then
    # randomly make a change in that coordinate.
    def makeRandomMove(self, i):
        dice = random.random()
        if dice > 0.5:
            xChange = random.randint(0, 2) - 1
            self.mLoc[i].x = utils.checkBounds(self.maxX, self.mLoc[i].x - xChange)
        else:
            yChange = random.randint(0, 2) - 1
            self.mLoc[i].y = utils.checkBounds(self.maxY, self.mLoc[i].y - yChange)

    # Add a meanie at intervals
    def addMeanie(self):
        if (self.clock % config.meanieInterval) == 0:
            newLoc = utils.pickUniquePose(self.maxX, self.maxY, self.locationList)
            self.mLoc.append(newLoc)
            
            self.locationList.append(newLoc)
            
    # Increment the clock every time the function is called
    def updateClock(self):
        self.clock +=1

    # Increment the score at intervals
    def updateScore(self):
        if (self.clock % config.scoreInterval) == 0: 
            self.score +=1

    # Update the score with bonus
    def updateScoreWithBonus(self):
        self.score += config.bonusValue
        
    # Is the given location smelly?
    #
    # A location is smelly if it is next to a Meanie
    def isSmelly(self, location):
        if self.isAjacent(self.mloc, location):
            return True
        else:
            return False

    # Is the given location windy?
    #
    # A location is windy if it is near a pit
    def isWindy(self, location):
        if self.isAjacent(self.ploc, location):
            return True
        else:
            return False

    # Does the given location glow?
    #
    # The bonus stations glow
    def isGlowing(self, location):
        if self.isAjacent(self.bloc, location):
            return True
        else:
            return False
        
    # Is the location loc next to any of the locations in locList.
    #
    # To be adjacent in this sense, you either have to be at the same
    # x coordinate and have a y coordinate that differs by 1, or in
    # the same y coordinate and have an x coordinate that differs by
    # one.
    def isAjacent(self, locList, loc):
        for aloc in locList:
            # Ajacency holds if it holds for any location in locList.
            if aloc.x == loc.x:
                if aloc.y == loc.y + 1 or aloc.y == loc.y - 1:
                    return True
                else:
                    return False
            elif aloc.y == loc.y:
                if aloc.x == loc.x + 1 or aloc.x == loc.x - 1:
                    return True
                else:
                    return False
            else:
                return False

    # Use the visibilityLimit to filter information that Tallon gets
    # about the world when appropriate
    def distanceFiltered(self, locations):
        if config.partialVisibility:
            filteredLocations = []
            for loc in locations:
                if utils.separation(self.tLoc, loc) <= config.visibilityLimit:
                    filteredLocations.append(loc)
            return filteredLocations
        else:
            return locations
            
            
