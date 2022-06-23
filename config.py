# config.py
#
# Configuration information for the Mean Arena. These are elements
# to play with as you develop your solution, and when you do your
# evaluation.
#
# Written by: Simon Parsons
# Last Modified: 12/01/22

# Dimensions in terms of the numbers of rows and columns
worldLength = 10
worldBreadth = 10

# Features
numberOfMeanies = 1 # How many we start with
numberOfPits = 3
numberOfBonuses = 2

# Control dynamism
#
# If dynamic is True, then the Meanies will move.
dynamic = True

# Control observability
#
# If partialVisibility is True, Tallon will only see part of the
# environment.
partialVisibility = True
#
# The limits of visibility when visibility is partial
visibilityLimit = 6

# Control determinism
#
# If nonDeterministic is True, Tallon's action model will be
# nonDeterministic.
nonDeterministic = False
#
# If Tallon is nondeterministic, probability that they carry out the
# intended action:
directionProbability = 0.95

# How far away can the Meanies sense Tallon.
senseDistance = 5

# Value of bonuses
bonusValue = 10

# How often we update the score
scoreInterval = 2

# How often we add a Meanie
meanieInterval = 5

# Control images
#
# If useImage is True, then we use images for Tallon, Meanies and
# Bonuses. If it is False, then we use simple colored objects.
useImage = True
