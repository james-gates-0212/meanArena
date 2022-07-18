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

# Run following commands......
# This depends on following libraries.
#
# pip install pandas
# pip install xlsxwriter
# pip install xlrd
# pip install openpyxl

from world import World
from tallon import Tallon
from arena import Arena
import pandas as pd
import random
import utils
import time
import config

data = {
    "size": [],
    "pits": [],
    "bonuses": [],
    "spawn": [],
    "total": [],
    "times": [],
}

for size in [10, 15, 20]:
    config.worldBreadth = size
    config.worldLength = size
    for pits in [3, 4, 5]:
        config.numberOfPits = pits
        for bonuses in [2, 3, 4]:
            config.numberOfBonuses = bonuses
            for spawnSpeed in [5, 4, 3]:
                config.meanieInterval = spawnSpeed
                times = random.randrange(20, 35)
                data["size"].append(size)
                data["pits"].append(pits)
                data["bonuses"].append(bonuses)
                data["spawn"].append(spawnSpeed)
                data["times"].append(times)
                totalScore = "="
                first = True
                print('--------------------------------------------------------------')
                print('Size = {}, Pits = {}, Bonuses = {}, Spawn = {}, Times = {}'.format(
                    size, pits, bonuses, spawnSpeed, times))
                for i in range(times):
                    print('--------------------------------------------------')
                    print('>>> {} evaluation <<<'.format(i + 1))
                    # How we set the game up. Create a world, then connect player and
                    # display to it.
                    gameWorld = World()
                    player = Tallon(gameWorld)
                    # display = Arena(gameWorld)

                    # Uncomment this for a printout of world state at the start
                    # utils.printGameState(gameWorld)

                    # Now run...
                    while not(gameWorld.isEnded()):
                        gameWorld.updateTallon(player.makeMove())
                        gameWorld.updateMeanie()
                        gameWorld.updateClock()
                        gameWorld.addMeanie()
                        gameWorld.updateScore()
                        # display.update()
                        # Uncomment this for a printout of world state every step
                        # utils.printGameState(gameWorld)
                        # time.sleep(0.01)

                    if not first:
                        totalScore = totalScore + "+"
                    totalScore = totalScore + "{}".format(gameWorld.getScore())
                    first = False

                    # display.close()
                    # del display
                    del player
                    del gameWorld
                print('Total {}'.format(totalScore))
                data["total"].append(totalScore)

df = pd.DataFrame(data)

# Create a Pandas Excel writer using XlsxWriter as the engine.
writer = pd.ExcelWriter('C:\\evaluation.xlsx', engine='xlsxwriter')

# Convert the dataframe to an XlsxWriter Excel object.
df.to_excel(writer, sheet_name='Sheet1', index=False)

# Close the Pandas Excel writer and output the Excel file.
writer.save()
