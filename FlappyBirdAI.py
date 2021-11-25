import pygame
import os
import neat
import random

class Bird:
    img = pygame.image.load(r"G:\Computer Science\Projects\Flappy bird AI\Images\bird1.png")
    gravity = 0.6
    contor = 1
    def __init__(self, nn, genome):
        self.brain = nn
        self.genome = genome
        self.x = 100
        self.y = 400
        self.image = Bird.img
        self.rect = self.image.get_rect(center=(100,400))
        self.jumpFlag = False
        self.yMovement = 0
    def update(self, pipesXY):
        self.yMovement += Bird.gravity
        self.rect.centery += self.yMovement
        self.rect.centerx += 0.5
        self.genome.fitness += 0.1 # Each frame the bird stays alive it increases it fitness
        self.think(pipesXY)
        if self.jumpFlag:
            self.yMovement = 0
            self.yMovement -= 10
            self.jumpFlag = False
    def think(self, pipesXY):
        y = self.rect.centery
        output = self.brain.activate((y, pipesXY[0], pipesXY[1], pipesXY[2]))
        if output[0] > 0.5: self.jumpFlag = True

class Pipe:
    def __init__(self, flag=False):
        self.random1 = random.randrange(0, 200)
        self.random2 = random.randint(0, 1)
        if self.random2 == 0:
            self.imageBot = pygame.transform.scale(
                pygame.image.load(r"G:\Computer Science\Projects\Flappy bird AI\Images\pipe.png"),
                (100, 250 + self.random1))
            self.imageTop = pygame.transform.scale(
                pygame.image.load(r"G:\Computer Science\Projects\Flappy bird AI\Images\pipe.png"),
                (100, 250 - self.random1))
        else:
            self.imageBot = pygame.transform.scale(
                pygame.image.load(r"G:\Computer Science\Projects\Flappy bird AI\Images\pipe.png"),
                (100, 250 - self.random1))
            self.imageTop = pygame.transform.scale(
                pygame.image.load(r"G:\Computer Science\Projects\Flappy bird AI\Images\pipe.png"),
                (100, 250 + self.random1))
        self.imageTop = pygame.transform.rotate(self.imageTop, 180)
        if flag:
            self.rectBot = self.imageBot.get_rect(midbottom=(700, 670))
            self.rectTop = self.imageTop.get_rect(midtop=(700, 0))
        else:
            self.rectBot = self.imageBot.get_rect(midbottom=(850, 670))
            self.rectTop = self.imageTop.get_rect(midtop=(850, 0))
    def update(self):
        self.rectBot.centerx -= 10
        self.rectTop.centerx -= 10


class FlappyBird:
    window = pygame.display.set_mode((800, 800))
    def __init__(self):
        self.initNeat()
    def initWorld(self):
        pygame.init()
        # Background
        self.background = pygame.transform.scale(pygame.image.load(r"G:\Computer Science\Projects\Flappy bird AI\Images\bg.png"), (800,800))
        # Base
        self.base = pygame.transform.scale(pygame.image.load(r"G:\Computer Science\Projects\Flappy bird AI\Images\base.png"), (800, 200))
        self.baseXY = [0,670]
        self.gravity = 10
        # Sound
        pygame.mixer.init()
        self.flapSound = pygame.mixer.Sound("G:\Computer Science\Projects\Flappy bird AI\Sound\sfx_wing.wav")
        self.dieSound = pygame.mixer.Sound("G:\Computer Science\Projects\Flappy bird AI\Sound\sfx_hit.wav")
        pygame.mixer.music.load(r"G:\Computer Science\Projects\Flappy bird AI\Sound\background.mp3")
        pygame.mixer.music.play(100)
        # Clock
        self.clock = pygame.time.Clock()
        # Quit flag
        self.quit = False
    def initBirds(self, genomes, config):
        self.birds = []
        for genome_id, genome in genomes:
            genome.fitness = 0
            network = neat.nn.FeedForwardNetwork.create(genome, config)
            self.birds.append(Bird(network, genome))
    def initPipes(self):
        self.pipeImg = pygame.image.load(r"G:\Computer Science\Projects\Flappy bird AI\Images\pipe.png")
        self.pipes = [Pipe(True)]
        self.pipesContor = 0
        self.spawnPipe = pygame.USEREVENT
        pygame.time.set_timer(self.spawnPipe, 1800)
    def initNeat(self):
        local_dir = os.path.dirname(__file__)
        config_path = os.path.join(local_dir, r"G:\Computer Science\Projects\Flappy bird AI\config.txt")
        config = neat.config.Config(neat.DefaultGenome,
                                    neat.DefaultReproduction,
                                    neat.DefaultSpeciesSet,
                                    neat.DefaultStagnation,
                                    config_path)
        self.population = neat.Population(config)
        self.population.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        self.population.add_reporter(stats)
    def checkCollision(self):
        for bird in self.birds:
            # If bird collides with the top or bottom of the world
            if bird.rect.top <= 0 or bird.rect.bottom >= 670:
                self.birds.remove(bird)
                self.dieSound.play()
                bird.genome.fitness -= 1
            # If the bird collides with one of the pipes
            for pipe in self.pipes:
                if bird.rect.colliderect(pipe.rectBot) or bird.rect.colliderect(pipe.rectTop):
                    if bird in self.birds: self.birds.remove(bird)
                    self.dieSound.play()
                    bird.genome.fitness -= 1 # If a bird collides with a pipe we decrease it fitness by 1
    def getClosestPipeXY(self):
        minPipe = self.pipes[0]
        for pipe in self.pipes:
            if pipe.rectTop.topleft[0] < minPipe.rectTop.topleft[0]:
                minPipe = pipe
        return [minPipe.rectTop.topleft[0], minPipe.rectTop.bottomleft[1], minPipe.rectBot.topleft[1]] # this function returns the x coordinate of the top and bottom pipe (the x is the same) and the y coordiantes of the top and bot pipe

    def processInput(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit = True
            if event.type == self.spawnPipe:
                self.pipes.append(Pipe())
                for bird in self.birds:
                    bird.genome.fitness += 1
    def updateGame(self):
        # Move the base
        self.baseXY[0] -= 10
        if self.baseXY[0] <= -800: self.baseXY[0] = 0
        # Move the pipes
        for pipe in self.pipes:
            if pipe.rectBot.centerx < -50:
                self.pipes.remove(pipe)
                self.pipesContor -= 1
            pipe.update()
        # Check for bird collision
        self.checkCollision()
        # Draw the birds
        for bird in self.birds:
            bird.update(self.getClosestPipeXY())
    def generateOutput(self):
        # Draw the background and base
        FlappyBird.window.blit(self.background, (0, 0))
        FlappyBird.window.blit(self.base, self.baseXY)
        FlappyBird.window.blit(self.base, (self.baseXY[0] + 800, self.baseXY[1]))
        for bird in self.birds:
            FlappyBird.window.blit(bird.image, bird.rect)
        for pipe in self.pipes:
            FlappyBird.window.blit(pipe.imageTop, pipe.rectTop)
            FlappyBird.window.blit(pipe.imageBot, pipe.rectBot)
        pygame.display.update()
        self.clock.tick(30)
    def runGame(self, genome, config):
        self.init(genome, config)
        while self.quit == False:
            if len(self.birds) == 0:
                break
            self.processInput()
            self.updateGame()
            self.generateOutput()
    def learn(self):
        self.population.run(self.runGame, 100)
    def init(self, genome, config):
        self.initWorld()
        self.initBirds(genome, config)
        self.initPipes()


game = FlappyBird()
game.learn()