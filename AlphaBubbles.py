import sys
import os
import pygame
import pygame.locals
import random
import pymunk
import random
import math

ScreenSize = ()
FrameRate = 60.0

def InvY(y):
    return ScreenSize[1] - y

def InvCoord(coord):
    return (coord[0], InvY(coord[1]))

class Bubble:
    Size = (100, 100)
    Mass = 1
    Friction = 0.5
    def __init__(self, screen, space, displayChar):
        self.__screen = screen
        self.__space = space

        radius = random.randint(30, 80)
        diameter = radius * 2
        self.__rect = pygame.Rect((0, 0), (diameter, diameter))

        self.__image = pygame.Surface(self.__rect.size, flags=pygame.SRCALPHA)
        pygame.transform.smoothscale(bubbleImage, self.__rect.size, self.__image)

        self.__body = pymunk.Body(Bubble.Mass, pymunk.inf)
        self.__body.position = (random.randint(0, ScreenSize[0]), InvY(0))
        self.__shape = pymunk.Circle(self.__body, radius)
        self.__shape.friction = Bubble.Friction
        self.__space.add(self.__body, self.__shape)

        force = (random.randint(-100, 100), 0)
        self.__body.apply_impulse(force)

        font = pygame.font.Font(None, diameter)
        self.__charGlyph = font.render(displayChar.upper(), True, (255, 255, 255))
        self.__creationTime = pygame.time.get_ticks()
        self.__lifeTime = random.randint(5000, 20000)
    
    def GetBody(self):
        return self.__body

    def GetShape(self):
        return self.__shape

    def Render(self):
        if self.IsDead():
            return

        diameter = self.__shape.radius * 2
        bubbleRect = pygame.Rect(0, 0, diameter, diameter)
        bubbleRect.centerx = self.__body.position[0]
        bubbleRect.centery = InvY(self.__body.position[1])

        glyphPos = self.__charGlyph.get_rect()
        glyphPos.centerx = bubbleRect.centerx
        glyphPos.centery = bubbleRect.centery
        
        self.__screen.blit(self.__image, bubbleRect.topleft)
        self.__screen.blit(self.__charGlyph, glyphPos)


    def IsDead(self):
        age = pygame.time.get_ticks() - self.__creationTime
        if age >= self.__lifeTime:
            return True

        return False

pygame.init()

ScreenSize = pygame.display.list_modes(32)[0]
screen = pygame.display.set_mode(ScreenSize, pygame.locals.FULLSCREEN)
clock = pygame.time.Clock()
font = pygame.font.Font(None, 1024)
bubbleImage = pygame.image.load("bubble.png")
bubblePopSound = pygame.mixer.Sound("bubblepop.wav")

# init pymunk and space
space = pymunk.Space()
space.gravity = (0.0, -10.0)

# setup four side of screen
segments = [
            ((            0, ScreenSize[1]), (ScreenSize[0], ScreenSize[1])),
            ((ScreenSize[0], ScreenSize[1]), (ScreenSize[0],             0)),
            ((ScreenSize[0],             0), (            0,             0)),
            ((            0,             0), (            0, ScreenSize[1])),
            ]

for segment in segments:
    body = pymunk.Body(pymunk.inf, pymunk.inf)
    shape = pymunk.Segment(body, InvCoord(segment[0]), InvCoord(segment[1]), 0.0)
    shape.friction = 0.5
    space.add_static(shape)

bubbles = []
isRunning = True
while isRunning:
    for event in pygame.event.get():
        if event.type == pygame.locals.QUIT:
            isRunning = False
        elif event.type == pygame.locals.KEYDOWN:
            if event.key == pygame.locals.K_ESCAPE:
                isRunning = False
            elif (event.key >= pygame.locals.K_a and event.key <= pygame.locals.K_z) or \
                 (event.key >= pygame.locals.K_0 and event.key <= pygame.locals.K_9):
                bubbles.append(Bubble(screen, space, chr(event.key)),)

    space.step(1 / FrameRate)
    i = 0
    while i < len(bubbles):
        if bubbles[i].IsDead():
            space.remove(bubbles[i].GetBody(), bubbles[i].GetShape())
            bubbles.remove(bubbles[i])
            bubblePopSound.play()
        else:
            i += 1

    screen.fill((0, 0, 0))

    for bubble in bubbles:
        bubble.Render()

    pygame.display.flip()
    clock.tick(FrameRate)
