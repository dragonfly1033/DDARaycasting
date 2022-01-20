import pygame as pg
from vector import Vector
import math
import time
import random

class Label:
    def __init__(self, screen, text, rect, font, bg, fg, align='left', justify='centre', zlayer=0, addSelf=True):
        self.display = screen
        self.text = text
        self.font = font
        self.rect = rect
        self.bg = bg
        self.fg = fg
        self.align = align
        self.justify = justify
        self.zlayer = zlayer
        self.update()


    def show(self):
        pg.draw.rect(self.display, self.bg, self.rect)
        self.display.blit(self.label, self.label_rect)

    def update(self):
        
        self.label = self.font.render(self.text, True, self.fg)
        self.label_rect = self.label.get_rect()

        self.label_rect.x = self.rect[0]
        self.label_rect.y = self.rect[1]

        if self.align == 'right':
            self.label_rect.right = self.rect[0] + self.rect[2]
        elif self.align == 'left':
            self.label_rect.left = self.rect[0]
        elif self.align in ['centre','center']:
            self.label_rect.left = self.rect[0] + ((self.rect[2]/2) - (self.label_rect.width/2))//1
            
        if self.justify == 'top':
            self.label_rect.top = self.rect[1]
        elif self.justify == 'bottom':
            self.label_rect.bottom = self.rect[1] + self.rect[3]
        elif self.justify in ['centre','center']:
            self.label_rect.top = self.rect[1] + ((self.rect[3]/2) - (self.label_rect.height/2))//1

        self.show()

class Player:
    def __init__(self, x, y, fov=90):
        self.pos = Vector(x, y)
        self.facing = 0
        self.vel = 100
        self.fov = fov * (2*math.pi/360)
        self.dirMag = 1 

    @property
    def dir(self):
        return Vector(math.cos(self.facing), math.sin(self.facing)).scale(self.dirMag)

    @property
    def plane(self):
        return Vector(-math.sin(self.facing), math.cos(self.facing)).scale(self.dirMag*math.tan(self.fov/2))

    def show(self):
        pg.draw.circle(display, (200, 200, 200), (self.pos.x, self.pos.y), 5)

    def calc(self, side, sideDist, deltaDist, rayDir, pMap, i, last_height, step):

        cell = grid[pMap.y][pMap.x]

        if side == 0:
            perpWallDist = (sideDist.x - deltaDist.x)
        else:
            perpWallDist = (sideDist.y - deltaDist.y)  
        fisheye = perpWallDist * math.cos(rayDir.angle()-self.facing)

        dist = min(l2w(perpWallDist), renderDist)
        fish_dist = min(l2w(fisheye), renderDist)

        height, coeff = DIM[0]*heightConst/fish_dist, cell.height
        colour = hsl(cell.colour, (1- fish_dist/renderDist)**lightDropoffConst)
        new_h = DIM[1]/2 - (height*(coeff-0.5))
        if last_height == None:
            pg.draw.rect(display, colour, (i*lineWidth , new_h + offset, lineWidth, height*coeff))
            return new_h
        elif last_height > new_h:
            pg.draw.rect(display, colour, (i*lineWidth , new_h + offset, lineWidth, min(height*coeff, last_height-new_h+1)))
            pass

        return min(new_h, last_height)

    def cast(self):

        for i in range(resolution):
            cameraX = (2*i/resolution -1)
            rayDir = self.dir + self.plane.scale(cameraX)

            if rayDir.x == 0 or rayDir.y == 0:
                deltaDist = Vector(1e30, 1e30)
            else:
                deltaDist = Vector(math.sqrt(1 + (rayDir.y/rayDir.x)**2), math.sqrt(1 + (rayDir.x/rayDir.y)**2))

            step = Vector(0,0)
            sideDist = Vector(0,0)
            pMap = Vector(math.floor(w2l(self.pos.x)), math.floor(w2l(self.pos.y)))
            
            if rayDir.x < 0:
                step.x = -1
                sideDist.x = (w2l(self.pos.x) - pMap.x) * deltaDist.x
            else:
                step.x = 1
                sideDist.x = (pMap.x + 1 - w2l(self.pos.x)) * deltaDist.x   

            if rayDir.y < 0:
                step.y = -1
                sideDist.y = (w2l(self.pos.y) - pMap.y) * deltaDist.y
            else:
                step.y = 1
                sideDist.y = (pMap.y + 1 - w2l(self.pos.y)) * deltaDist.y    

            last_height = None
            done = False
            side = None
            while not done:
                old_pMap = Vector(pMap.x, pMap.y)
                if sideDist.x < sideDist.y:
                    sideDist.x += deltaDist.x
                    pMap.x += step.x
                    side = 0
                else:
                    sideDist.y += deltaDist.y
                    pMap.y += step.y
                    side = 1
                
                if not (0<=pMap.x<gridDIM[0] and 0<=pMap.y<gridDIM[1]):
                    done = True
                    self.calc(side, sideDist, deltaDist, rayDir, old_pMap, i, last_height, step)
                    continue
                if grid[pMap.y][pMap.x].isWall:
                    last_height = self.calc(side, sideDist, deltaDist, rayDir, pMap, i, last_height, step)
                    cache = Vector(pMap.x, pMap.y)
                    if grid[pMap.y][pMap.x].height < 0.5:
                        if sideDist.x < sideDist.y:
                            sideDist.x += deltaDist.x
                            pMap.x += step.x
                            side = 0
                        else:
                            sideDist.y += deltaDist.y
                            pMap.y += step.y
                            side = 1
                        if not grid[pMap.y][pMap.x].isWall:
                            pMap = cache
                        last_height = self.calc(side, sideDist, deltaDist, rayDir, pMap, i, last_height, step)
                    # done = True

class Cell:
    def __init__(self, x, y):
        self.pos = Vector(x, y)
        self.isWall = False
        self.contact = False
        self.height = 1
        self.colour = (255,255,255)

    def show(self):
        if not self.isWall:
            bg = (0,0,0)
        else:
            bg = self.colour

        pg.draw.rect(display, bg, (l2w(self.pos.x), l2w(self.pos.y), cellW, cellW))
        if self.isWall:
            l = Label(display, str(self.height), (l2w(self.pos.x), l2w(self.pos.y), cellW, cellW), smallFont, bg, (0,0,0), align='centre')


def lerp(m, M, t):
    return m + (M-m)*t

def l2w(vec):
    return vec*(cellW+borderW) + borderW

def w2l(vec):
    return (vec - borderW)*(1/(cellW+borderW))

def getCell(x, y):
    return grid[math.floor(w2l(y))][math.floor(w2l(x))]

def hsl(rgb, bright):
    return [int(lerp(0, i,bright)) for i in rgb]

def changeColour():
    return (random.randint(0,255), random.randint(0,255), random.randint(0,255))


pg.init()
pg.font.init()

smallFont = pg.font.SysFont('Calibri', 12)

gridDIM = (72, 48)
cellW = 15
borderW = 1
heightConst = 20
lightDropoffConst = 2
offset = 0
turnSensitivity = 4
floorColour = (100, 100, 100)
ceilingColour = (87, 255, 241)
renderDist = l2w(gridDIM[0])
grid = []

for y in range(gridDIM[1]):
    row = []
    for x in range(gridDIM[0]):
        row.append(Cell(x, y))
    grid.append(row)

DIM = (l2w(gridDIM[0]),l2w(gridDIM[1]))
display = pg.display.set_mode(DIM)
clock = pg.time.Clock()

resolution = DIM[0]//4
lineWidth = DIM[0]/resolution

p = Player(400, 400, 90)

future_x, future_y = p.pos.x, p.pos.y

drawMode = False
eraseMode = False
playMode = False

last_time = time.time()
run = True
while run:
    dt = time.time() - last_time
    last_time = time.time()
    x, y = pg.mouse.get_pos()
    pg.mouse.set_visible(not playMode)
    cell = getCell(x, y)
    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
        if event.type == pg.MOUSEMOTION:
            if not playMode:
                p.facing = (Vector(x, y)-p.pos).angle()
                if drawMode:
                    cell.isWall = True
                if eraseMode:
                    cell.isWall = False
            else:
                dx, dy = pg.mouse.get_rel()
                p.facing += dx * (2*math.pi/360) * turnSensitivity * dt
                offset -= dy  * turnSensitivity**2 * dt 
                offset = max(-DIM[1]/2, min(DIM[1]/2, offset))
                if x == DIM[0]-1:
                    pg.mouse.set_pos(0, y)
                if y == DIM[0]:
                    pg.mouse.set_pos(x, 0)
                if x == 0:
                    pg.mouse.set_pos(DIM[0], y)
                if y == 0:
                    pg.mouse.set_pos(x, DIM[0])
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 3:
                drawMode = True
            elif event.button == 1:
                eraseMode = True
            if cell.isWall:
                if event.button == 4:
                    tmp = cell.height
                    cell.height = round(min(10, tmp+0.1), 1)
                if event.button == 5:
                    tmp = cell.height
                    cell.height = round(max(1, tmp-0.1), 1)
        if event.type == pg.MOUSEBUTTONUP:
            if event.button == 3:
                drawMode = False
            elif event.button == 1:
                eraseMode = False
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_c:
                if cell.isWall:
                    cell.colour = changeColour()
            if event.key == pg.K_p:
                playMode = not playMode
                pg.event.set_grab(playMode)
            if event.key == pg.K_ESCAPE:
                playMode = False
                pg.event.set_grab(playMode)


    keys = pg.key.get_pressed()
    if keys[pg.K_LSHIFT]:
        sprint = 1.5
    else:
        sprint = 1
    if keys[pg.K_w]:
        future_x = p.pos.x + (p.vel * math.cos(p.facing) * sprint * dt)
        future_y = p.pos.y + (p.vel * math.sin(p.facing) * sprint * dt) 
    if keys[pg.K_a]:
        future_x = p.pos.x + (p.vel * math.sin(p.facing) * sprint * dt)
        future_y = p.pos.y - (p.vel * math.cos(p.facing) * sprint * dt) 
    if keys[pg.K_s]:
        future_x = p.pos.x - (p.vel * math.cos(p.facing) * sprint * dt)
        future_y = p.pos.y - (p.vel * math.sin(p.facing) * sprint * dt) 
    if keys[pg.K_d]:
        future_x = p.pos.x - (p.vel * math.sin(p.facing) * sprint * dt)
        future_y = p.pos.y + (p.vel * math.cos(p.facing) * sprint * dt) 

    if 0<=future_x<=DIM[0] and 0<=future_y<=DIM[0] and (not getCell(future_x, future_y).isWall):
        p.pos.x, p.pos.y = future_x, future_y

    if not playMode:
        display.fill((200, 200, 200))
        for row in grid:
            for cell in row:
                cell.show()
        p.show()
        # p.cast()
    else:
        display.fill((0,0,0))
        level = DIM[1]/2+offset
        pg.draw.rect(display, (0,208,255), (0, 0, DIM[0], level))#(0,208,255)
        pg.draw.rect(display, (100, 100, 100), (0, level, DIM[0], DIM[1]-level))
        p.cast()
        pg.draw.circle(display, (255, 0, 255), (DIM[0]/2, level), 2)


    clock.tick(60)
    pg.display.update()

pg.quit()
quit()