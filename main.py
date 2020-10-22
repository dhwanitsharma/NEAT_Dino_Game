


__author__ = "www.projectnotes.org"

import os
import sys
import pygame
import neat
import random
from pygame import *
pygame.font.init()

STAT_FONT = pygame.font.SysFont("comicsans", 30)

pygame.init()

scr_size = (width,height) = (600,250)
FPS = 60
gravity = 0.6

black = (0,0,0)
white = (255,255,255)
background_col = (235,235,235)

high_score = 0
gen = 0

screen = pygame.display.set_mode(scr_size)
clock = pygame.time.Clock()
pygame.display.set_caption("Dino Run ")

jump_sound = pygame.mixer.Sound('sprites/jump.wav')
die_sound = pygame.mixer.Sound('sprites/die.wav')
checkPoint_sound = pygame.mixer.Sound('sprites/checkPoint.wav')

def load_image(
    name,
    sizex=-1,
    sizey=-1,
    colorkey=None,
    ):

    fullname = os.path.join('sprites', name)
    image = pygame.image.load(fullname)
    #image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, RLEACCEL)

    if sizex != -1 or sizey != -1:
        image = pygame.transform.scale(image, (sizex, sizey))

    return (image, image.get_rect())

def load_sprite_sheet(
        sheetname,
        nx,
        ny,
        scalex = -1,
        scaley = -1,
        colorkey = None,
        ):
    fullname = os.path.join('sprites',sheetname)
    sheet = pygame.image.load(fullname)
    #sheet = sheet.convert()

    sheet_rect = sheet.get_rect()

    sprites = []

    sizex = sheet_rect.width/nx
    sizey = sheet_rect.height/ny

    for i in range(0,ny):
        for j in range(0,nx):
            rect = pygame.Rect((j*sizex,i*sizey,sizex,sizey))
            image = pygame.Surface(rect.size)
            #image = image.convert()
            image.blit(sheet,(0,0),rect)

            if colorkey is not None:
                if colorkey is -1:
                    colorkey = image.get_at((0,0))
                image.set_colorkey(colorkey,RLEACCEL)

            if scalex != -1 or scaley != -1:
                image = pygame.transform.scale(image,(scalex,scaley))

            sprites.append(image)

    sprite_rect = sprites[0].get_rect()

    return sprites,sprite_rect

def disp_gameOver_msg(retbutton_image,gameover_image):
    retbutton_rect = retbutton_image.get_rect()
    retbutton_rect.centerx = width / 2
    retbutton_rect.top = height*0.52

    gameover_rect = gameover_image.get_rect()
    gameover_rect.centerx = width / 2
    gameover_rect.centery = height*0.35

    screen.blit(retbutton_image, retbutton_rect)
    screen.blit(gameover_image, gameover_rect)

def extractDigits(number):
    if number > -1:
        digits = []
        i = 0
        while(number/10 != 0):
            digits.append(number%10)
            number = int(number/10)

        digits.append(number%10)
        for i in range(len(digits),5):
            digits.append(0)
        digits.reverse()
        return digits

class Dino():
    def __init__(self,sizex=-1,sizey=-1):
        self.images,self.rect = load_sprite_sheet('dino.png',5,1,sizex,sizey,-1)
        self.images1,self.rect1 = load_sprite_sheet('dino_ducking.png',2,1,59,sizey,-1)
        self.rect.bottom = int(0.98*height)
        self.rect.left = width/15
        self.image = self.images[0]
        self.index = 0
        self.counter = 0
        self.score = 0
        self.isJumping = False
        self.isDead = False
        self.isDucking = False
        self.isBlinking = False
        self.movement = [0,0]
        self.jumpSpeed = 11.5

        self.stand_pos_width = self.rect.width
        self.duck_pos_width = self.rect1.width

    def draw(self):
        screen.blit(self.image,self.rect)

    def checkbounds(self):
        if self.rect.bottom > int(0.98*height):
            self.rect.bottom = int(0.98*height)
            self.isJumping = False

    def update(self):
        if self.isJumping:
            self.movement[1] = self.movement[1] + gravity

        if self.isJumping:
            self.index = 0
        elif self.isBlinking:
            if self.index == 0:
                if self.counter % 400 == 399:
                    self.index = (self.index + 1)%2
            else:
                if self.counter % 20 == 19:
                    self.index = (self.index + 1)%2

        elif self.isDucking:
            if self.counter % 5 == 0:
                self.index = (self.index + 1)%2
        else:
            if self.counter % 5 == 0:
                self.index = (self.index + 1)%2 + 2

        if self.isDead:
           self.index = 4

        if not self.isDucking:
            self.image = self.images[self.index]
            self.rect.width = self.stand_pos_width
        else:
            self.image = self.images1[(self.index)%2]
            self.rect.width = self.duck_pos_width

        self.rect = self.rect.move(self.movement)
        self.checkbounds()

        if not self.isDead and self.counter % 7 == 6 and self.isBlinking == False:
            self.score += 1
            if self.score % 100 == 0 and self.score != 0:
                if pygame.mixer.get_init() != None:
                    checkPoint_sound.play()

        self.counter = (self.counter + 1)

class Cactus(pygame.sprite.Sprite):
    def __init__(self,speed=5,sizex=-1,sizey=-1):
        pygame.sprite.Sprite.__init__(self,self.containers)
        self.images,self.rect = load_sprite_sheet('cacti-small.png',3,1,sizex,sizey,-1)
        self.rect.bottom = int(0.98*height)
        self.rect.left = width + self.rect.width
        self.image = self.images[random.randrange(0,3)]
        self.movement = [-1*speed,0]

    def draw(self):
        screen.blit(self.image,self.rect)

    def update(self):
        self.rect = self.rect.move(self.movement)

        if self.rect.right < 0:
            self.kill()

class Ptera(pygame.sprite.Sprite):
    def __init__(self,speed=5,sizex=-1,sizey=-1):
        pygame.sprite.Sprite.__init__(self,self.containers)
        self.images,self.rect = load_sprite_sheet('ptera.png',2,1,sizex,sizey,-1)
        #self.ptera_height = [height*0.82,height*0.75,height*0.60]
        self.ptera_height = [height*0.82,height*0.60]
        #self.rect.centery = self.ptera_height[random.randrange(0,3)]
        self.rect.centery = self.ptera_height[random.randrange(0,2)]
        self.rect.left = width + self.rect.width
        self.image = self.images[0]
        self.movement = [-1*speed,0]
        self.index = 0
        self.counter = 0

    def draw(self):
        screen.blit(self.image,self.rect)

    def update(self):
        if self.counter % 10 == 0:
            self.index = (self.index+1)%2
        self.image = self.images[self.index]
        self.rect = self.rect.move(self.movement)
        self.counter = (self.counter + 1)
        if self.rect.right < 0:
            self.kill()


class Ground():
    
    def __init__(self,speed=-5):
        self.image,self.rect = load_image('ground.png',-1,-1,-1)
        self.image1,self.rect1 = load_image('ground.png',-1,-1,-1)
        self.rect.bottom = height
        self.rect1.bottom = height
        self.rect1.left = self.rect.right
        self.speed = speed

    def draw(self):
        screen.blit(self.image,self.rect)
        screen.blit(self.image1,self.rect1)

    def update(self):
        self.rect.left += self.speed
        self.rect1.left += self.speed

        if self.rect.right < 0:
            self.rect.left = self.rect1.right

        if self.rect1.right < 0:
            self.rect1.left = self.rect.right

class Cloud(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self,self.containers)
        self.image,self.rect = load_image('cloud.png',int(90*30/42),30,-1)
        self.speed = 1
        self.rect.left = x
        self.rect.top = y
        self.movement = [-1*self.speed,0]

    def draw(self):
        screen.blit(self.image,self.rect)

    def update(self):
        self.rect = self.rect.move(self.movement)
        if self.rect.right < 0:
            self.kill()

class Scoreboard():
    def __init__(self,x=-1,y=-1):
        self.score = 0
        self.tempimages,self.temprect = load_sprite_sheet('numbers.png',12,1,11,int(11*6/5),-1)
        self.image = pygame.Surface((55,int(11*6/5)))
        self.rect = self.image.get_rect()
        if x == -1:
            self.rect.left = width*0.89
        else:
            self.rect.left = x
        if y == -1:
            self.rect.top = height*0.1
        else:
            self.rect.top = y

    def draw(self):
        screen.blit(self.image,self.rect)

    def update(self,score):
        score_digits = extractDigits(score)
        self.image.fill(background_col)
        for s in score_digits:
            self.image.blit(self.tempimages[s],self.temprect)
            self.temprect.left += self.temprect.width
        self.temprect.left = 0

class GeneCount():

    def draw(self,gen):
        self.label = STAT_FONT.render("Gens: " + str(gen-1),1,(0,0,0))
        screen.blit(self.label, (10, 10))

class Alive():

    def draw(self,playerDinos):
        self.label = STAT_FONT.render("Alive: " + str(len(playerDinos)),1,(0,0,0))
        screen.blit(self.label, (10, 30))


def eval_genomes(genomes,config):
    global high_score,gen 
    gen += 1
    gamespeed = 4
    #startMenu = False
    #gameOver = False
    #gameQuit = False
    #playerDino = Dino(44,47)
    new_ground = Ground(-1*gamespeed)
    scb = Scoreboard()
    highsc = Scoreboard(width*0.78)
    gcc = GeneCount()
    alive = Alive()
    counter = 0

    nets = []
    playerDinos = []
    ge = []
    for genome_id, genome in genomes:
        genome.fitness = 0  # start with fitness level of 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        playerDinos.append(Dino(44,47))
        ge.append(genome)

    cacti = pygame.sprite.Group()
    pteras = pygame.sprite.Group()
    clouds = pygame.sprite.Group()
    last_obstacle = pygame.sprite.Group()

    Cactus.containers = cacti
    Ptera.containers = pteras
    Cloud.containers = clouds

    retbutton_image,retbutton_rect = load_image('replay_button.png',35,31,-1)
    gameover_image,gameover_rect = load_image('game_over.png',190,11,-1)

    temp_images,temp_rect = load_sprite_sheet('numbers.png',12,1,11,int(11*6/5),-1)
    HI_image = pygame.Surface((22,int(11*6/5)))
    HI_rect = HI_image.get_rect()
    HI_image.fill(background_col)
    HI_image.blit(temp_images[10],temp_rect)
    temp_rect.left += temp_rect.width
    HI_image.blit(temp_images[11],temp_rect)
    HI_rect.top = height*0.1
    HI_rect.left = width*0.73
    
    run = True
    while run and len(playerDinos)>0:
        for x, playerDino in enumerate(playerDinos):  # give each bird a fitness of 0.1 for each frame it stays alive
            ge[x].fitness += 0.01
            pteras_distance=0
            pteras_height =0
                # send bird location, top pipe location and bottom pipe location and determine from network whether to jump or not
            for p in pteras:
                pteras_distance = p.rect.left
                pteras_height = p.rect.centery

            for c in cacti:
                output = nets[playerDinos.index(playerDino)].activate((playerDino.stand_pos_width, abs(playerDino.stand_pos_width - c.rect.left),abs(playerDino.stand_pos_width-pteras_distance),abs(playerDino.stand_pos_width-pteras_height)))
                
                if output[0] > 0.2:  # we use a tanh activation function so result will be between -1 and 1. if over 0.5 jump
                    if playerDino.rect.bottom == int(0.98*height):
                        playerDino.isJumping = True
                        playerDino.movement[1] = -1*playerDino.jumpSpeed
        
        for playerDino in playerDinos:
            for c in cacti:
                c.movement[0] = -1*gamespeed
                if pygame.sprite.collide_mask(playerDino,c):
                    playerDino.isDead = True
                    ge[playerDinos.index(playerDino)].fitness -= 5
                    nets.pop(playerDinos.index(playerDino))
                    ge.pop(playerDinos.index(playerDino))
                    playerDinos.pop(playerDinos.index(playerDino))
        
        for playerDino in playerDinos:
            for p in pteras:
                p.movement[0] = -1*gamespeed
                if pygame.sprite.collide_mask(playerDino,p):
                    playerDino.isDead = True
                    ge[playerDinos.index(playerDino)].fitness -= 30
                    nets.pop(playerDinos.index(playerDino))
                    ge.pop(playerDinos.index(playerDino))
                    playerDinos.pop(playerDinos.index(playerDino))

        if len(cacti) < 2:
            if len(cacti) == 0:
                last_obstacle.empty()
                last_obstacle.add(Cactus(gamespeed,40,40))

            else:
                for l in last_obstacle:
                    if l.rect.right < width*0.7 and random.randrange(0,50) == 10:
                        last_obstacle.empty()
                        last_obstacle.add(Cactus(gamespeed, 40, 40))
                        for genome in ge:
                            genome.fitness += 5

        if len(pteras) == 0 and random.randrange(0,200) == 10 and counter > 500:
            for l in last_obstacle:
                if l.rect.right < width*0.8:
                    last_obstacle.empty()
                    last_obstacle.add(Ptera(gamespeed, 46, 40))

        if len(clouds) < 5 and random.randrange(0,300) == 10:
            Cloud(width,random.randrange(height/5,height/2))

        for playerDino in playerDinos: 
            playerDino.update()
        cacti.update()
        pteras.update()
        clouds.update()
        new_ground.update()
        scb.update(playerDino.score)
        highsc.update(high_score)

        if pygame.display.get_surface() != None:
            screen.fill(background_col)
            new_ground.draw()
            clouds.draw(screen)
            scb.draw()
            if high_score != 0:
                highsc.draw()
                screen.blit(HI_image,HI_rect)
            cacti.draw(screen)
            pteras.draw(screen)
            gcc.draw(gen)
            alive.draw(playerDinos)
        for playerDino in playerDinos:    
            playerDino.draw()
            pygame.display.update()
        clock.tick(FPS)

        if playerDino.isDead:
            gameOver = True
            if playerDino.score > high_score:
                high_score = playerDino.score

        if counter%700 == 699:
            new_ground.speed -= 1
            gamespeed += 1

        counter = (counter + 1)
    
'''
def main():
    #isGameQuit = introscreen()
    #if not isGameQuit:
        gameplay()
'''

def run(config_file):
    """
    runs the NEAT algorithm to train a neural network to play flappy bird.
    :param config_file: location of config file
    :return: None
    """
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    #p.add_reporter(neat.Checkpointer(5))
        
    # Run for up to 50 generations.
    winner = p.run(eval_genomes, 50)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))

if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')
    run(config_path)
