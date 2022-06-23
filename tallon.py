# tallon.py
#
# The code that defines the behaviour of Tallon. This is the place
# (the only place) where you should write code, using access methods
# from world.py, and using makeMove() to generate the candidate move.
#
# Written by: Simon Parsons
# Last Modified: 12/01/22

import world
import random
import utils
from utils import Directions, Pose
class Tallon():

    def __init__(self, arena):

        # Make a copy of the world an attribute, so that Tallon can
        # query the state of the world
        self.gameWorld = arena

        # What moves are possible.
        self.moves = [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]

    def filterPoses(self, poses, blockPoses):
        filtered = []
        for pose in poses:
            if not utils.containedIn(pose, blockPoses):
                filtered.append(pose)
        return filtered

    def maxSeparationPose(self, poses, targets):
        if len(poses) == 0 or len(targets) == 0:
            return False
        sepas = []
        for pose in poses:
            sepa = 0
            for target in targets:
                sepa += utils.separation(pose, target)
            sepas.append(sepa)
        return poses[sepas.index(max(sepas))]

    # Generate all poses for moving in the world
    def availablePoses(self, poses, target = False):
        candidatePoses = []
        offsets =  [
            Pose(0, +1), # North
            Pose(0, -1), # South
            Pose(+1, 0), # Eest
            Pose(-1, 0), # West
        ]
        for pose in poses:
            for offset in offsets:
                candidateX = pose.x + offset.x
                candidateY = pose.y + offset.y
                if (
                    target != False and
                    (
                        pose.x == target.x or
                        pose.y == target.y
                    )
                ):
                    candidateX = self.gameWorld.reduceDifference(pose.x, target.x)
                    candidateY = self.gameWorld.reduceDifference(pose.y, target.y)
                candidatePoses.append(
                    Pose(
                        utils.checkBounds(self.gameWorld.maxX, candidateX),
                        utils.checkBounds(self.gameWorld.maxY, candidateY)
                    )
                )
        return candidatePoses

    def candidatePoses(self, pose):
        # Get the location of the Meanies.
        allMeanies = self.gameWorld.getMeanieLocation()

        # Get the location of the Pits.
        allPits = self.gameWorld.getPitsLocation()

        allMeaniesCandidatePoses = self.availablePoses(allMeanies, pose)
        originalCandidatePoses = self.availablePoses([pose])

        # Filter the available poses to avoid the Pits, Meanies and Meanies's candidate poses
        candidatePoses = self.filterPoses(originalCandidatePoses, allPits + allMeaniesCandidatePoses + allMeanies)

        return candidatePoses

    def targetMaxPose(self, pose):
        # Get the location of the Meanies.
        allMeanies = self.gameWorld.getMeanieLocation()

        return self.maxSeparationPose(self.candidatePoses(pose), allMeanies)

    def makeMove(self):
        # This is the function you need to define

        # For now we have a placeholder, which always moves Tallon
        # directly towards any existing bonuses. It ignores Meanies
        # and pits.
        #
        # Get the location of the Bonuses.
        allBonuses = self.gameWorld.getBonusLocation()

        # Get the location of the Pits.
        allPits = self.gameWorld.getPitsLocation()

        # Get the location of the Meanies.
        allMeanies = self.gameWorld.getMeanieLocation()

        # Get the location of the Tallon.
        myPosition = self.gameWorld.getTallonLocation()

        foundMeanies = len(allMeanies) > 0

        myTargetPose = self.targetMaxPose(myPosition)

        if foundMeanies and myTargetPose != False:
            # If not at the same x coordinate, reduce the difference
            if myTargetPose.x > myPosition.x:
                print('avoid - EAST')
                return Directions.EAST
            if myTargetPose.x < myPosition.x:
                print('avoid - WEST')
                return Directions.WEST
            # If not at the same y coordinate, reduce the difference
            if myTargetPose.y < myPosition.y:
                print('avoid - NORTH')
                return Directions.NORTH
            if myTargetPose.y > myPosition.y:
                print('avoid - SOUTH')
                return Directions.SOUTH

        # if there are still bonuses, move towards the candidate one.
        allBlocks = allPits + allMeanies
        if len(allBonuses) > 0:
            candidateBonus = allBonuses[0]
            # If not at the same x coordinate, reduce the difference
            if candidateBonus.x > myPosition.x and not utils.containedIn(myPosition.offset(+1, 0), allBlocks):
                print('bonus - EAST')
                return Directions.EAST
            if candidateBonus.x < myPosition.x and not utils.containedIn(myPosition.offset(-1, 0), allBlocks):
                print('bonus - WEST')
                return Directions.WEST
            # If not at the same y coordinate, reduce the difference
            if candidateBonus.y < myPosition.y and not utils.containedIn(myPosition.offset(0, -1), allBlocks):
                print('bonus - NORTH')
                return Directions.NORTH
            if candidateBonus.y > myPosition.y and not utils.containedIn(myPosition.offset(0, +1), allBlocks):
                print('bonus - SOUTH')
                return Directions.SOUTH

        # if there are no more bonuses, Tallon doesn't move
