from common import *
import random

def findClosestTokens(tokens):
    closest = [(Position(), -1)]
    for token in tokens:
        if robotPos.distance(token[0]) < robotPos.distance(closest[0][0]):
            closest = [token]
        elif robotPos.distance(token[0]) == robotPos.distance(closest[0][0]):
            closest.append(token)
    return closest

def logTokens(tokens):
    for token in tokens:
        log('strategy', 'Team: ' + str(token[1]) + ' : ' + str((token[0].x, token[0].y)) + ' : ' + str(robotPos.distance(token[0])))


robotPos = Position(random.randint(0, 80)/10, random.randint(0, 80)/10)

tokens = []
for i in range(12):
    tokens.append(( Position(random.randint(0, 80)/10, random.randint(0, 80)/10), random.randint(0, 3) ))

log('strategy', 'robotPos:' + str((robotPos.x, robotPos.y)))
log('strategy', 'All Tokens:')
logTokens(tokens)
tokens = findClosestTokens(tokens)
log('strategy', 'Closest Tokens:')
logTokens(tokens)