# Frogger
# 07/16/18
# Author: Jason Tian
import pygame
import random
import time

pygame.init()
display_width = 350
display_height = 400

white = (255, 255, 255)

screen = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption('Frogger')
clock = pygame.time.Clock()

all_sprites = pygame.sprite.Group()
turtles = pygame.sprite.Group()
frogs = pygame.sprite.Group()

frogUpImg = pygame.image.load('images/frog10.gif')
frogDead = pygame.image.load('images/frog11.png')

yellowCarImg = pygame.image.load('images/yellowCar.gif')  # 2nd Row
dozerImg = pygame.image.load('images/dozer.gif')  # 3rd Row
purpleCarImg = pygame.image.load('images/purpleCar.gif')  # 4th Row
greenCarImg = pygame.image.load('images/greenCar.gif')  # 5th Row
truckImg = pygame.image.load('images/truck.gif')  # 6th Row

logShortImg = pygame.image.load('images/logShort.gif')
logMediumImg = pygame.image.load('images/logMedium.gif')
logLongImg = pygame.image.load('images/logLong.gif')

turtleTwoImg = pygame.image.load('images/turtletwo.gif')
turtleTwoDownImg = pygame.image.load('images/turtletwodown.gif')
turtleThreeImg = pygame.image.load('images/turtlethree.gif')
turtleThreeDownImg = pygame.image.load('images/turtlethreedown.gif')

backgroundImg = pygame.image.load('images/background.gif')

frogsNum = 100  # Number of frogs spawned per generation
done = False   # Application is still running
turtleCounter = 0  # Timer for turtle state
fps = 20  # Simulation speed (actions per second)

# Classes


class Population:
    bestFrog = 0  # The index for the best (most fit) frog
    minStep = 1000  # The fastest route to get to the highest fitness
    fitnessSum = 0  # Sum of all frogs' fitness
    frogs_alive = frogsNum  # All frogs are alive at the beginning
    isFinished = False  # Whether or not a frog has ever reached the end
    generation = 1

    def __init__(self, tests, size):  # Constructor
        self.frogs_alive = tests
        self.size = size
        self.tests = tests
        self.randomize()

    # Randomizes the frog's directions
    def randomize(self):
        for i in range(0, self.tests):
            directions = []
            for z in range(0, self.size):
                randomNum = random.randint(0, 4)
                directions.append(randomNum)

            b = Brain(1000, directions)
            frogs.add(Frog(167.5, 350, self.size, b))

    # Randomly selecting a parent frog from previous generation
    def selectParent(self):
        self.setFitnessSum()
        rand = random.randint(frogsNum, self.fitnessSum)
        runningSum = 0

        for i in frogs:
            runningSum += i.fitness
            if runningSum >= rand:
                return i.brain.directions

    # Finding the sum of all the fitnesses from previous generation
    def setFitnessSum(self):
        sum = 0
        for i in frogs:
            sum += i.fitness
        self.fitnessSum = sum

    # Selecting a new generation of frogs
    def selection(self):
        temp = list(self.bestFrog())
        newFrogs = []
        if (self.isFinished == False):
            d = list(temp)
            b = Brain(1000, d)
            newFrogs.append(Frog(167.5, 350, self.size, b))

            for x in range(1, frogsNum):
                d = list(self.selectParent())
                b = Brain(1000, mutate(d))
                newFrogs.append(Frog(167.5, 350, self.size, b))
            Population.frogs_alive = frogsNum

            frogs.empty()
            for i in newFrogs:
                frogs.add(i)
        else:
            frogs.empty()
            for x in range(0, 1):
                d = list(temp)
                b = Brain(1000, d)
                frogs.add(Frog(167.5, 350, self.size, b))
            Population.frogs_alive = 1

    # Determining the best frog from the previous generation and returning its directions
    def bestFrog(self):
        if (self.isFinished == False):

            fitnessList = []
            stepsList = []
            for sprite in frogs:
                stepsList.append(sprite.brain.step)
                fitnessList.append(sprite.fitness)

            for i in range(0, frogsNum - 1):
                for j in range(0, frogsNum - 1):
                    if (fitnessList[j] > fitnessList[j + 1]):
                        temp = fitnessList[j]
                        fitnessList[j] = fitnessList[j + 1]
                        fitnessList[j + 1] = temp

                        temp = stepsList[j]
                        stepsList[j] = stepsList[j + 1]
                        stepsList[j + 1] = temp

            print(fitnessList[frogsNum - 1])
            print(stepsList[frogsNum - 1])

            best = frogsNum - 1
            for h in range(0, frogsNum - 1):
                if stepsList[h] < stepsList[frogsNum - 1] and fitnessList[frogsNum - 1] == fitnessList[h]:
                    best = h

            print(fitnessList[best])
            print(stepsList[best])

            if (fitnessList[best] == 13):
                self.isFinished = True
            else:
                self.generation += 1

            for sprite in frogs:
                if (fitnessList[best] == sprite.fitness and stepsList[best] == sprite.brain.step):
                    bestFrog = list(sprite.brain.directions)
                    print(str(sprite.fitness) + '   ' + str(sprite.brain.step))
                    break

            return bestFrog

        else:
            for sprite in frogs:
                bestFrog = list(sprite.brain.directions)
            return bestFrog


class Brain:
    step = 0

    def __init__(self, size, directions):
        self.size = size
        self.directions = directions


class Turtle(pygame.sprite.Sprite):
    def __init__(self, dive, size, startX, startY, width, height, speed):
        pygame.sprite.Sprite.__init__(self)
        self.dive = dive  # 1 - does not dive. 2 - dives
        self.size = size
        self.speed = speed
        self.width = width
        self.height = height
        self.state = 0  # State 0 - Not diving. State 1 - Diving

        self.image = pygame.Surface((self.width, self.height))
        self.rect = self.image.get_rect()
        self.rect.x = startX
        self.rect.y = startY

        if (self.size == 2):
            self.image = turtleTwoImg
        elif (self.size == 3):
            self.image = turtleThreeImg

    # Updating its new location
    def update(self):
        self.rect.x += self.speed

        if (self.size == 2):
            if (self.rect.x + 50 < 0):
                self.rect.x = display_width + 50
        elif (self.size == 3):
            if (self.rect.x + 75 < 0):
                self.rect.x = display_width + 75

        self.collision()

    # Checking if frog is on turtle. Frog dies if turtle is diving.
    def collision(self):
        for f in frogs:
            if f.rect.colliderect(self) and f.dead == False:
                if self.state == 1:
                    f.die()
                else:
                    f.rect.x += self.speed


class Frog(pygame.sprite.Sprite):
    dead = False
    reachedGoal = False
    fitness = 0

    def __init__(self, xpos, ypos, size, brain):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((25, 25))
        self.rect = self.image.get_rect()
        self.image = frogUpImg
        self.rect.x = xpos
        self.rect.y = ypos
        self.size = size
        self.brain = brain

    # Update frog position
    def update(self):
        stepNum = self.brain.step
        if stepNum < self.size and self.dead == False:
            if self.brain.directions[stepNum] == 1:
                self.rect.y -= 25
                self.fitness += 1
            elif self.brain.directions[stepNum] == 2 and self.rect.y < 375:
                self.rect.y += 25
                self.fitness -= 1
            elif self.brain.directions[stepNum] == 3 and self.rect.x > 25:
                self.rect.x -= 25
            elif self.brain.directions[stepNum] == 4 and self.rect.x < 300:
                self.rect.x += 25

            self.brain.step += 1

        # If frog is in the river
        if self.rect.y <= 175 and self.rect.y != 50 and self.dead == False:
            crash = False
            for x in all_sprites:
                if x.rect.colliderect(self):
                    crash = True
                    break
            for x in turtles:
                if x.rect.colliderect(self):
                    crash = True
                    break
            if crash == False:
                self.die()
        elif self.rect.y == 50 and self.dead == False:
            self.fitness = 13
            self.dead = True
            Population.frogs_alive -= 1

    # If the frog dies
    def die(self):
        self.image = frogDead
        self.dead = True
        Population.frogs_alive -= 1
        print('Frogs alive: ' + str(Population.frogs_alive))


class Log(pygame.sprite.Sprite):
    def __init__(self, startX, startY, size, width, height, speed):  # Constructor
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.speed = speed
        self.width = width
        self.height = height

        self.image = pygame.Surface((self.width, self.height))
        self.rect = self.image.get_rect()
        self.rect.x = startX
        self.rect.y = startY

        if (self.size == 'short'):
            self.image = logShortImg
        elif (self.size == 'medium'):
            self.image = logMediumImg
        elif (self.size == 'long'):
            self.image = logLongImg

    # Updating log position
    def update(self):
        self.rect.x += self.speed

        if (self.size == 'short' or self.size == 'medium'):
            if (self.rect.x - 100 > display_width):
                self.rect.x = -100
        else:
            if (self.rect.x - 200 > display_width):
                self.rect.x = -200

        self.collision()

    # Checking for collision with frog.
    def collision(self):
        for f in frogs:
            if f.rect.colliderect(self) and f.dead == False:
                f.rect.x += self.speed


# Car Object
class Car(pygame.sprite.Sprite):
    def __init__(self, startX, startY, img, speed, direction, width, height):  # Constructor
        pygame.sprite.Sprite.__init__(self)
        self.img = img
        self.speed = speed
        self.direction = direction  # (-1)-left (1)-right
        self.width = width
        self.height = height

        self.image = pygame.Surface((self.width, self.height))
        self.rect = self.image.get_rect()
        self.rect.x = startX
        self.rect.y = startY

        if (self.img == 'yellow'):
            self.image = yellowCarImg
        elif (self.img == 'green'):
            self.image = greenCarImg
        elif (self.img == 'truck'):
            self.image = truckImg
        elif (self.img == 'dozer'):
            self.image = dozerImg
        elif (self.img == 'purple'):
            self.image = purpleCarImg

    # Update Car position
    def update(self):
        if (self.direction == -1):
            self.rect.x += self.speed
        elif (self.direction == 1):
            self.rect.x -= self.speed

        if (self.direction == -1 and self.rect.x - 75 > display_width):
            self.rect.x = -75
        elif (self.direction == 1 and self.rect.x + 75 < 0):
            self.rect.x = display_width + 75
        self.collision()

    # Checks car collision with frogs
    def collision(self):
        for f in frogs:
            if (self.rect.colliderect(f) and f.dead == False):
                f.die()

# Randomly mutates the direction vectors of the given frog


def mutate(d):
    for i in range(0, len(d)):
        randomNum = random.randint(0, 4)
        if randomNum == 1:
            d[i] = random.randint(0, 4)
    return d

# Reset game board


def reset():
    for r in turtles:
        r.kill()
    for r in all_sprites:
        r.kill()

    turtleCounter = 0

    # Creation of objects
    #(x, y, img, speed, direction, width, height)
    for i in range(0, 12):
        if i < 3:
            all_sprites.add(Car(100 + 75 * (3 - i), 325, 'yellow', 6, 1, 25, 25))
        elif i < 6:
            all_sprites.add(Car(-150 + 75 * (6 - i), 300, 'dozer', 2, -1, 25, 25))
        elif i < 9:
            all_sprites.add(Car(50 + 75 * (9 - i), 275, 'purple', 4, 1, 25, 25))
        elif i < 10:
            all_sprites.add(Car(25 + 75 * (10 - i), 250, 'green', 10, -1, 25, 25))
        elif i < 12:
            all_sprites.add(Car(50 + 150 * (12 - i), 225, 'truck', 3, 1, 50, 25))

    for i in range(0, 9):
        if i < 3:
            all_sprites.add(Log(-100 + 150 * (3 - i), 150, 'short', 62.5, 25, 3))
        elif i < 6:
            all_sprites.add(Log(-150 + 200 * (6 - i), 125, 'long', 150, 25, 4))
        elif i < 9:
            all_sprites.add(Log(-200 + 150 * (9 - i), 75, 'medium', 87.5, 25, 6))

    for i in range(0, 8):
            # dive, size, startX, startY, width, height, speed
        if i < 4:
            if i == 2:
                turtles.add(Turtle(2, 3, 100 * (4 - i), 175, 75, 25, -2))
            else:
                turtles.add(Turtle(1, 3, 100 * (4 - i), 175, 75, 25, -2))
        elif i < 8:
            if i == 7:
                turtles.add(Turtle(2, 2, 87.5 * (8 - i), 100, 50, 25, -2))
            else:
                turtles.add(Turtle(1, 2, 87.5 * (8 - i), 100, 50, 25, -2))


def text_objects(text, font):
    textSurface = font.render(text, True, white)
    return textSurface, textSurface.get_rect()


def message_display(text):
    largeText = pygame.font.Font('freesansbold.ttf', 12)
    TextSurf, TextRect = text_objects(text, largeText)
    TextRect.center = ((display_width / 2), 10)
    screen.blit(TextSurf, TextRect)


pop = Population(frogsNum, 1000)
reset()

# Event handling loop (game loop)
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    screen.blit(backgroundImg, (0, 0))

    # If all frogs are dead, reset game board
    if (Population.frogs_alive == 0):
        pop.selection()
        reset()
        time.sleep(1)

    message_display('generation: ' + str(pop.generation))
    all_sprites.update()
    all_sprites.draw(screen)
    turtles.update()
    turtles.draw(screen)
    frogs.update()
    frogs.draw(screen)

    pygame.display.update()

    clock.tick(fps)

    # Handling diving of turtle. Dives only at certain times
    turtleCounter += 1
    if turtleCounter == 50:
        turtleCounter = 0
        for t in turtles:
            if t.dive == 2:
                if t.state == 0:
                    t.state = 1
                    if t.size == 2:
                        t.image = turtleTwoDownImg
                    else:
                        t.image = turtleThreeDownImg
                else:
                    t.state = 0
                    if t.size == 2:
                        t.image = turtleTwoImg
                    else:
                        t.image = turtleThreeImg

pygame.quit()
quit()
