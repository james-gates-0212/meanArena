# tallon.py
#
# The code that defines the behaviour of Tallon. This is the place
# (the only place) where you should write code, using access methods
# from world.py, and using makeMove() to generate the candidate move.
#
# Written by: Simon Parsons
# Last Modified: 12/01/22

import config
import world
import random
import utils
from utils import Directions, Pose

config.nonDeterministic = None

class Tallon():

    freeDistanceLimit   = 0
    allBonuses          = []
    currentPose         = None
    targetPose          = None
    allMeanies          = []
    allMeaniesToAvoid   = []
    allPits             = []

    def __init__(self, arena):

        # Make a copy of the world an attribute, so that Tallon can
        # query the state of the world
        self.gameWorld = arena

        # What moves are possible.
        self.moves = [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]

        # Make the distance limit between Tallon and Meanies
        if config.partialVisibility:
            self.freeDistanceLimit = config.visibilityLimit / 2
        else:
            self.freeDistanceLimit = config.senseDistance / 2

        if self.freeDistanceLimit < 3:
            self.freeDistanceLimit = 3

    def filterPoses(self, poses, blockPoses = []):
        filtered = []
        for pose in poses:
            if not utils.containedIn(pose, blockPoses):
                filtered.append(pose)
        return filtered

    def poseByMaxSeparation(self, poses, targets):
        if len(poses) == 0 or len(targets) == 0:
            return None
        sepas = []
        for pose in poses:
            sepa = 0
            for target in targets:
                sepa += utils.separation(pose, target)
            sepas.append(sepa)
        return poses[sepas.index(max(sepas))]

    # Generate all poses for moving in the world
    def availablePoses(self, poses, target = None):
        candidatePoses = []
        offsets =  [
            { 'x': 0, 'y': +1 }, # North
            { 'x': 0, 'y': -1 }, # South
            { 'x': +1, 'y': 0 }, # Eest
            { 'x': -1, 'y': 0 }, # West
        ]
        for pose in poses:
            for offset in offsets:
                candidatePose = Pose();
                candidatePose.x = pose.x + offset['x']
                candidatePose.y = pose.y + offset['y']
                if (
                    target != None and
                    ( pose.x == target.x or pose.y == target.y )
                ):
                    candidatePose.x = self.gameWorld.reduceDifference(pose.x, target.x)
                    candidatePose.y = self.gameWorld.reduceDifference(pose.y, target.y)
                candidatePose.x = utils.checkBounds(self.gameWorld.maxX, candidatePose.x)
                candidatePose.y = utils.checkBounds(self.gameWorld.maxY, candidatePose.y)
                candidatePoses.append(candidatePose)
        return candidatePoses

    def blockPoses(self, pose = None, noCandidate = False):
        allMeaniesCandidatePoses = []
        if not noCandidate:
            allMeaniesCandidatePoses = self.availablePoses(self.allMeanies, pose)
        return self.allPits + self.allMeanies + allMeaniesCandidatePoses

    def candidatePoses(self, pose = None):
        if pose == None:
            return []
        # Filter the available poses to avoid the Pits, Meanies and Meanies's candidate poses
        candidatePoses = self.filterPoses(self.availablePoses([pose]), self.blockPoses(pose))

        return candidatePoses

    def filterByFreeDistanceLimit(self, poses, target):
        filtered = []
        for pose in poses:
            if utils.separation(pose, target) <= self.freeDistanceLimit:
                filtered.append(pose)
        return filtered

    def targetPoseToAvoidMeanies(self):
        self.allMeaniesToAvoid = self.filterByFreeDistanceLimit(self.allMeanies, self.currentPose)
        self.targetPose = self.poseByMaxSeparation(self.candidatePoses(self.currentPose), self.allMeaniesToAvoid)

    # Get the pose was moved by offsetX and offsetY from the given pose
    def offset(self, pose, offsetX = 0, offsetY = 0):
        newPose = Pose()
        newPose.x = utils.checkBounds(self.gameWorld.maxX, pose.x + offsetX)
        newPose.y = utils.checkBounds(self.gameWorld.maxY, pose.y + offsetY)
        return newPose

    # Get the direction between current pose and target pose without block poses
    def direction(self, blocks = []):
        # If not at the same x coordinate, reduce the difference
        if self.targetPose.x > self.currentPose.x and not utils.containedIn(self.offset(self.currentPose, +1, 0), blocks):
            return Directions.EAST
        if self.targetPose.x < self.currentPose.x and not utils.containedIn(self.offset(self.currentPose, -1, 0), blocks):
            return Directions.WEST
        # If not at the same y coordinate, reduce the difference
        if self.targetPose.y < self.currentPose.y and not utils.containedIn(self.offset(self.currentPose, 0, -1), blocks):
            return Directions.NORTH
        if self.targetPose.y > self.currentPose.y and not utils.containedIn(self.offset(self.currentPose, 0, +1), blocks):
            return Directions.SOUTH
        return None

    def selfMoveDirection(self):
        direction = self.moves[random.randint(0, 3)]
        # If not at the same x coordinate, reduce the difference
        if direction == Directions.EAST and not utils.containedIn(self.offset(self.currentPose, +1, 0), self.allPits):
            return Directions.EAST
        if direction == Directions.WEST and not utils.containedIn(self.offset(self.currentPose, -1, 0), self.allPits):
            return Directions.WEST
        # If not at the same y coordinate, reduce the difference
        if direction == Directions.NORTH and not utils.containedIn(self.offset(self.currentPose, 0, -1), self.allPits):
            return Directions.NORTH
        if direction == Directions.SOUTH and not utils.containedIn(self.offset(self.currentPose, 0, +1), self.allPits):
            return Directions.SOUTH
        return None

    def makeMove(self):
        # This is the function you need to define

        # For now we have a placeholder, which always moves Tallon
        # directly towards any existing bonuses. It ignores Meanies
        # and pits.
        #
        # Get the location of the Bonuses.
        self.allBonuses = self.gameWorld.getBonusLocation()

        # Get the location of the Tallon.
        self.currentPose = self.gameWorld.getTallonLocation()

        # Get the location of the Meanies.
        self.allMeanies = self.gameWorld.getMeanieLocation()

        # Get the location of the Pits.
        self.allPits = self.gameWorld.getPitsLocation()

        self.targetPoseToAvoidMeanies()

        # Found the Meanies to avoid.
        foundMeanies = len(self.allMeaniesToAvoid) > 0

        direction = None

        if foundMeanies and self.targetPose:
            direction = self.direction()

        if direction == None:
            # if there are still bonuses, move towards the candidate one.
            allBlocks = self.blockPoses(self.currentPose)
            if len(self.allBonuses) > 0:
                self.targetPose = self.allBonuses[0]
                direction = self.direction(allBlocks)

        # if there are no meanies to avoid and no candidate bonus, Tallon travels itself.
        if not foundMeanies and direction == None:
            direction = self.selfMoveDirection()

        # if there are no meanies to avoid and no more bonus, Tallon doesn't move
        if direction == None:
            return

        return direction
