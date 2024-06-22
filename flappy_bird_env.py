import pygame, random, time
from pygame.locals import *
from gym import Env, spaces


#VARIABLES
SCREEN_WIDHT = 400
SCREEN_HEIGHT = 600
SPEED = 20
GRAVITY = 2.5
GAME_SPEED = 15

GROUND_WIDHT = 2 * SCREEN_WIDHT
GROUND_HEIGHT= 100

PIPE_WIDHT = 80
PIPE_HEIGHT = 500

PIPE_GAP = 150

wing = 'assets/audio/wing.wav'
hit = 'assets/audio/hit.wav'

random.seed(0)


class Bird(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.images =  [pygame.image.load('assets/sprites/bluebird-upflap.png').convert_alpha(),
                        pygame.image.load('assets/sprites/bluebird-midflap.png').convert_alpha(),
                        pygame.image.load('assets/sprites/bluebird-downflap.png').convert_alpha()]

        self.speed = SPEED

        self.current_image = 0
        self.image = pygame.image.load('assets/sprites/bluebird-upflap.png').convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)

        self.rect = self.image.get_rect()
        self.rect[0] = SCREEN_WIDHT / 6
        self.rect[1] = SCREEN_HEIGHT / 2

    def update(self):
        self.current_image = (self.current_image + 1) % 3
        self.image = self.images[self.current_image]
        self.speed += GRAVITY

        #UPDATE HEIGHT
        self.rect[1] += self.speed

    def bump(self):
        self.speed = -SPEED

    def begin(self):
        self.current_image = (self.current_image + 1) % 3
        self.image = self.images[self.current_image]
    
    def roofed(self):
        return self.rect[1] < 0




class Pipe(pygame.sprite.Sprite):

    def __init__(self, inverted, xpos, ysize):
        pygame.sprite.Sprite.__init__(self)

        self. image = pygame.image.load('assets/sprites/pipe-green.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (PIPE_WIDHT, PIPE_HEIGHT))


        self.rect = self.image.get_rect()
        self.rect[0] = xpos

        if inverted:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect[1] = - (self.rect[3] - ysize)
        else:
            self.rect[1] = SCREEN_HEIGHT - ysize


        self.mask = pygame.mask.from_surface(self.image)


    def update(self):
        self.rect[0] -= GAME_SPEED

        

class Ground(pygame.sprite.Sprite):
    
    def __init__(self, xpos):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('assets/sprites/base.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (GROUND_WIDHT, GROUND_HEIGHT))

        self.mask = pygame.mask.from_surface(self.image)

        self.rect = self.image.get_rect()
        self.rect[0] = xpos
        self.rect[1] = SCREEN_HEIGHT - GROUND_HEIGHT
    def update(self):
        self.rect[0] -= GAME_SPEED

def is_off_screen(sprite):
    return sprite.rect[0] < -(sprite.rect[2])

def get_random_pipes(xpos):
    size = random.randint(100, 300)
    pipe = Pipe(False, xpos, size)
    pipe_inverted = Pipe(True, xpos, SCREEN_HEIGHT - size - PIPE_GAP)
    return pipe, pipe_inverted


def get_state(bird, pipe_group, ground_group):

        # get pipe pair in front
        next_pipes = []
        for i, pipe in enumerate(pipe_group.sprites()):
            if (pipe.rect[0] + pipe.rect[2]) > bird.rect[0]:
                next_pipes.append(pipe_group.sprites()[i])
                next_pipes.append(pipe_group.sprites()[i+1])
                break
        
        ceiling_gap = bird.rect[1]
        ground_gap = ground_group.sprites()[0].rect[1] - (bird.rect[1] + bird.rect[3]) 
        upper_pipe_gap = bird.rect[1] - (next_pipes[1].rect[1] + next_pipes[1].rect[3])
        lower_pipe_gap = next_pipes[0].rect[1] - (bird.rect[1] + bird.rect[3])
        front_pipe_gap = next_pipes[0].rect[0] - (bird.rect[0] + bird.rect[2])
        rear_pipe_gap = (next_pipes[0].rect[0] + next_pipes[0].rect[2]) - (bird.rect[0])
        speed = bird.speed

        return ceiling_gap, ground_gap, upper_pipe_gap, lower_pipe_gap, front_pipe_gap, rear_pipe_gap, speed



class FlappyBirdEnv(Env):


    def __init__(self, render):
        self.render = render

        self.screen = None
        self.bird = None
        self.ground_group = None
        self.bird_group = None
        self.pipe_group = None

        self.score = None
        self.clock = None

        self.BACKGROUND = None

        #self.action_space = spaces.Discrete(2, start=0)
        self.observation_space = spaces.Box(low=-1000.0, high=1000.0, shape=(5,))
        self.reward_range = (0,1)
        


    def reset(self):

        pygame.init()

        if self.render:
            self.screen = pygame.display.set_mode((SCREEN_WIDHT, SCREEN_HEIGHT))
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDHT, SCREEN_HEIGHT), flags=pygame.HIDDEN)

        pygame.display.set_caption('Flappy Bird')

        self.BACKGROUND = pygame.image.load('assets/sprites/background-day.png')
        self.BACKGROUND = pygame.transform.scale(self.BACKGROUND, (SCREEN_WIDHT, SCREEN_HEIGHT))
        BEGIN_IMAGE = pygame.image.load('assets/sprites/message.png').convert_alpha()

        self.bird_group = pygame.sprite.Group()
        self.bird = Bird()
        self.bird_group.add(self.bird)

        self.ground_group = pygame.sprite.Group()

        for i in range (2):
            ground = Ground(GROUND_WIDHT * i)
            self.ground_group.add(ground)

        self.pipe_group = pygame.sprite.Group()
        for i in range (2):
            pipes = get_random_pipes(SCREEN_WIDHT * i + 800)
            self.pipe_group.add(pipes[0])
            self.pipe_group.add(pipes[1])


        self.clock = pygame.time.Clock()

        self.bird.bump()

        self.screen.blit(self.BACKGROUND, (0, 0))
        self.screen.blit(BEGIN_IMAGE, (120, 150))

        if is_off_screen(self.ground_group.sprites()[0]):
            self.ground_group.remove(self.ground_group.sprites()[0])

            new_ground = Ground(GROUND_WIDHT - 20)
            self.ground_group.add(new_ground)

        self.bird.begin()
        self.ground_group.update()

        self.bird_group.draw(self.screen)
        self.ground_group.draw(self.screen)

        pygame.display.update()

        self.score = 0

        return get_state(self.bird, self.pipe_group, self.ground_group)



    def step(self, action):
        


        if action == 1:
            self.bird.bump()

        self.screen.blit(self.BACKGROUND, (0, 0))

        if is_off_screen(self.ground_group.sprites()[0]):
            self.ground_group.remove(self.ground_group.sprites()[0])

            new_ground = Ground(GROUND_WIDHT - 20)
            self.ground_group.add(new_ground)

        if is_off_screen(self.pipe_group.sprites()[0]):
            self.pipe_group.remove(self.pipe_group.sprites()[0])
            self.pipe_group.remove(self.pipe_group.sprites()[0])

            pipes = get_random_pipes(SCREEN_WIDHT * 2)

            self.pipe_group.add(pipes[0])
            self.pipe_group.add(pipes[1])

        self.bird_group.update()
        self.ground_group.update()
        self.pipe_group.update()

        self.bird_group.draw(self.screen)
        self.pipe_group.draw(self.screen)
        self.ground_group.draw(self.screen)

        pygame.display.update()


        if (pygame.sprite.groupcollide(self.bird_group, self.ground_group, False, False, pygame.sprite.collide_mask) or
                pygame.sprite.groupcollide(self.bird_group, self.pipe_group, False, False, pygame.sprite.collide_mask)
                or self.bird.roofed()):
            time.sleep(1)
            return get_state(self.bird, self.pipe_group, self.ground_group), 0, True, False, {}
        else:
            self.score += 1
            return get_state(self.bird, self.pipe_group, self.ground_group), 1, False, False, {}
        

    




