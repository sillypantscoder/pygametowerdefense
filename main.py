from tkinter.tix import CELL
import pygame
import random
import math

pygame.font.init()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
TAN = (120, 100, 100)

BOARDSIZE = [10, 10]
SCREENSIZE = [550, 500]
screen = pygame.display.set_mode(SCREENSIZE, pygame.RESIZABLE)
CELLSIZE = 50

BOARD = [random.choices([0, random.randint(1, 99)], weights=[20, 1], k=BOARDSIZE[0]) for x in range(BOARDSIZE[1])]
ROUTE = [[random.randint(0, 10), random.randint(0, 10)] for x in range(5)]
FONT = pygame.font.SysFont(pygame.font.get_default_font(), 40)
FONTHEIGHT = FONT.render("0", True, BLACK).get_height()

def routecopy(r: "list[list[int]]" = ROUTE) -> "list[list[int]]":
	e = []
	for i in r: e.append(i.copy())
	return e

def dist(p1: "tuple[int, int]", p2: "tuple[int, int]") -> float:
	dX = p1[0] - p2[0]
	dY = p1[1] - p2[1]
	com = abs(dX) + abs(dY)
	return math.sqrt(com)

def insideBoard(x, y):
	return (x >= 0) and (y >= 0) and (x < BOARDSIZE[0]) and (y < BOARDSIZE[1])

class Entity:
	speed = 0.01
	def __init__(self, x: float, y: float):
		entities.append(self)
		self.pos = [x, y]
		self.initcustom()
	def frame(self):
		self.tick()
		if self in entities:
			s = self.draw()
			x = cellno_to_pixel(self.pos[0])# - (s.get_width() / 2)
			y = cellno_to_pixel(self.pos[1]) - (s.get_height() / 2)
			screen.blit(s, (x, y))
	def draw(self):
		r = pygame.Surface((10, 10))
		r.fill((0, 0, 0))
		return r
	def tick(self):
		self.tickcustom()
	def die(self):
		if self in entities:
			self.despawn()
			entities.remove(self)
		else:
			print(f"Entity {self} was removed twice!")
	def despawn(self): pass
	def tickcustom(self): pass
	def initcustom(self): pass

class Mob(Entity):
	speed = 0.01
	def __init__(self, route: "list[list[int]]" = ROUTE):
		self.route = routecopy(route)
		self.pos = self.route[0].copy()
		self.prevpos = self.route.pop(0)
		self.ticks = 0
		entities.append(self)
		self.initcustom()
	def tick(self):
		global defense
		if len(self.route) == 0:
			self.die()
			defense -= 1
			return;
		dx = self.route[0][0] - self.prevpos[0]
		dy = self.route[0][1] - self.prevpos[1]
		numticks = math.sqrt(abs(dx) + abs(dy)) / self.speed
		if self.ticks + 1 < numticks:
			self.ticks += 1
			self.pos[0] += dx / numticks
			self.pos[1] += dy / numticks
		else:
			self.prevpos = self.route.pop(0)
			self.ticks = 0
		self.tickcustom()

class Enemy(Mob):
	speed = 0.03
	def despawn(self):
		Coins(self.pos[0] + (random.choice(range(-40, 40, 5)) / 100), self.pos[1] + (random.choice(range(-40, 40, 5)) / 100))

class Coins(Entity):
	def draw(self):
		r = pygame.Surface((8, 8), pygame.SRCALPHA)
		r.fill((255, 255, 255, 0))
		pygame.draw.circle(r, (252, 186, 3, self.ticks), (4, 4), 4)
		return r
	def initcustom(self):
		self.ticks = 255
		self.totalticks = 150
	def tickcustom(self):
		global money
		self.totalticks -= 1
		if self.ticks < 255 or self.totalticks <= 0:
			self.ticks -= 4
		elif dist(pygame.mouse.get_pos(), cellnos_to_pixels(*self.pos)) < 3:
			self.ticks = 254
		if self.ticks <= 0:
			money += 1
			self.die()

entities: "list[Entity]" = []
cellno_to_pixel = (lambda x: round((x * CELLSIZE) + (0.5 * CELLSIZE)))
pixel_to_cellno = (lambda x: (x - (0.5 * CELLSIZE)) / CELLSIZE)
cellnos_to_pixels = (lambda x, y: (cellno_to_pixel(x), cellno_to_pixel(y)))
pixels_to_cellnos = (lambda x, y: (pixel_to_cellno(x), pixel_to_cellno(y)))
wave_lvl = 0
wave_time = 60 * 5
wave = False
defense = 10
money = 6
headertext = FONT.render(f"{'Wave' if wave else 'Finished wave'} {wave_lvl} ({str(round(wave_time / 60, ndigits=2)).replace('.', ':')}); Money: $", True, BLACK)
textures = {
	"ground": pygame.transform.scale(pygame.image.load("ground.png"), (CELLSIZE, CELLSIZE)),
	"tower_active": pygame.transform.scale(pygame.image.load("tower_active.png"), (CELLSIZE, CELLSIZE)),
	"tower": pygame.transform.scale(pygame.image.load("tower.png"), (CELLSIZE, CELLSIZE))
}
tower_row = [{"id": 99, "image": "tower", "cost": 3}]
dragging_thing = None

c = pygame.time.Clock()
running = True
while running:
	tower_row_rect = pygame.Rect(0, SCREENSIZE[1] - CELLSIZE, SCREENSIZE[0], CELLSIZE)
	tower_row_rect_mouse = pygame.Rect(0, (SCREENSIZE[1] - CELLSIZE) - FONTHEIGHT, SCREENSIZE[0], CELLSIZE)
	pos = [*pygame.mouse.get_pos()]
	pos[1] -= FONTHEIGHT
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		elif event.type == pygame.VIDEORESIZE:
			SCREENSIZE = [*event.dict["size"]]
			screen = pygame.display.set_mode(SCREENSIZE, pygame.RESIZABLE)
		elif event.type == pygame.MOUSEBUTTONDOWN:
			if tower_row_rect_mouse.collidepoint(*pos):
				idx = (pos[0] - tower_row_rect.left) / SCREENSIZE[0]
				idx = math.floor(idx)
				if idx < len(tower_row):
					dragging_thing = tower_row[idx]
		elif event.type == pygame.MOUSEBUTTONUP and dragging_thing != None:
			if tower_row_rect_mouse.collidepoint(*pos):
				# let go within the tower row, so ignore it.
				pass
			else:
				x = math.floor(pos[0] / CELLSIZE)
				y = math.floor(pos[1] / CELLSIZE)
				if insideBoard(x, y) and money >= 3 and BOARD[x][y] == 0:
					BOARD[x][y] = dragging_thing['id']
					money -= 3
			dragging_thing = None
	# Drawing
	screen.fill(WHITE)
	# Board
	board = pygame.Surface((CELLSIZE * 10, CELLSIZE * 10))
	board.fill(WHITE)
	for x in range(len(BOARD)):
		for y in range(len(BOARD[x])):
			cellrect = pygame.Rect(x * CELLSIZE, y * CELLSIZE, CELLSIZE, CELLSIZE)
			board.blit(textures["ground"], cellrect)
			if BOARD[x][y] == 0:
				# Just ground here, nothing to do.
				# I'm so bored...
				pass
				#board.blit(textures["ground"], cellrect)
			elif BOARD[x][y] == 1:
				board.blit(textures["tower_active"], cellrect)
				es = []
				for e in entities:
					if isinstance(e, Enemy): es.append(e)
				es.sort(key=lambda z: dist((x, y), z.pos))
				if len(es) > 0:
					e = es[0]
					if dist((x, y), e.pos) < 2:
						pygame.draw.line(board, RED, cellnos_to_pixels(x, y), cellnos_to_pixels(*e.pos))
						e.die()
						BOARD[x][y] = 99
			elif BOARD[x][y] < 100:
				board.blit(textures["tower"], cellrect)
				BOARD[x][y] -= 1
	screen.blit(board, (0, FONTHEIGHT))
	# Route
	for i in range(len(ROUTE) - 1):
		start = (cellno_to_pixel(ROUTE[i][0]), cellno_to_pixel(ROUTE[i][1]))
		end = (cellno_to_pixel(ROUTE[i + 1][0]), cellno_to_pixel(ROUTE[i + 1][1]))
		pygame.draw.line(screen, RED, start, end, round(0.3 * CELLSIZE))
	# Entities
	for e in entities:
		e.frame()
	# Spawning
	if wave and random.random() < 0.08 * wave_lvl: Enemy()
	wave_time -= 1
	if wave_time <= 0:
		wave_time = 60 * 10
		wave = not wave
		if wave: wave_lvl += 1
	# Text
	headertext = FONT.render(f"{'Wave' if wave else 'Finished wave'} {wave_lvl} ({str(round(wave_time / 60, ndigits=2)).replace('.', ':')}); Money: ${money}, defenses left: {defense}", True, BLACK)
	screen.blit(headertext, (0, 0))
	if SCREENSIZE[0] < headertext.get_width():
		SCREENSIZE[0] = headertext.get_width()
		screen = pygame.display.set_mode(SCREENSIZE, pygame.RESIZABLE)
	if defense <= 0:
		running = False
	headertext = FONT.render(f"{'Wave' if wave else 'Finished wave'} {wave_lvl} ({str(round(wave_time / 60, ndigits=2)).replace('.', ':')}); Money: $", True, BLACK)
	# Bottom row of towers
	pygame.draw.rect(screen, WHITE, tower_row_rect)
	for t in tower_row:
		screen.blit(textures[t["image"]], (0, SCREENSIZE[1] - 50))
	# Dragging tower
	x = math.floor(pos[0] / CELLSIZE)
	y = math.floor(pos[1] / CELLSIZE)
	if dragging_thing:
		drag_target = pygame.Rect(x * CELLSIZE, (y * CELLSIZE) + FONTHEIGHT, CELLSIZE, CELLSIZE)
		if insideBoard(x, y) and money >= 3 and BOARD[x][y] == 0:
			pygame.draw.rect(screen, (0, 255, 0), drag_target, 5)
		else:
			pygame.draw.rect(screen, (255, 0, 0), drag_target, 5)
		screen.blit(textures[dragging_thing["image"]], [pos[0] - (CELLSIZE / 2), pos[1] + (FONTHEIGHT - (CELLSIZE / 2))])
	# Flip
	pygame.display.flip()
	c.tick(60)

running = True
headertext = FONT.render(f"You survived until wave {wave_lvl} and you had ${money}", True, BLACK)
SCREENSIZE = [headertext.get_width(), headertext.get_height()]
screen = pygame.display.set_mode(SCREENSIZE, pygame.RESIZABLE)
while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		elif event.type == pygame.MOUSEBUTTONDOWN:
			running = False
	screen.fill(WHITE)
	screen.blit(headertext, (0, 0))
	pygame.display.flip()
	c.tick(60)
