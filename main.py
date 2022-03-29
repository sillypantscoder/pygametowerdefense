import pygame
import random
import math

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
TAN = (120, 100, 100)

SCREENSIZE = [500, 500]
screen = pygame.display.set_mode(SCREENSIZE, pygame.RESIZABLE)
CELLSIZE = 50

BOARD = [[random.choice([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, random.randint(1, 99)]) for y in range(10)] for x in range(10)]
ROUTE = [[random.randint(0, 10), random.randint(0, 10)] for x in range(5)]

def routecopy(r: "list[list[int]]" = ROUTE) -> "list[list[int]]":
	e = []
	for i in r: e.append(i.copy())
	return e

def dist(p1: "tuple[int, int]", p2: "tuple[int, int]") -> float:
	dX = p1[0] - p2[0]
	dY = p1[1] - p2[1]
	com = abs(dX) + abs(dY)
	return math.sqrt(com)

class Entity:
	speed = 0.01
	def __init__(self, route: "list[list[int]]" = ROUTE):
		self.route = routecopy(route)
		self.pos = self.route[0].copy()
		self.prevpos = self.route.pop(0)
		self.ticks = 0
		entities.append(self)
	def draw(self):
		r = pygame.Surface((10, 10))
		r.fill((0, 0, 0))
		return r
	def tick(self):
		if len(self.route) == 0:
			self.die()
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
	def die(self):
		if self in entities:
			self.despawn()
			entities.remove(self)
		else:
			print(f"Entity {self} was removed twice!")
	def despawn(self): pass
	def tickcustom(self): pass

class Enemy(Entity):
	speed = 0.03

entities = []
entities.append(Enemy())
cellno_to_pixel = (lambda x: round((x * CELLSIZE) + (0.5 * CELLSIZE)))
pixel_to_cellno = (lambda x: (x - (0.5 * CELLSIZE)) / CELLSIZE)
cellnos_to_pixels = (lambda x, y: (cellno_to_pixel(x), cellno_to_pixel(y)))
pixels_to_cellnos = (lambda x, y: (pixel_to_cellno(x), pixel_to_cellno(y)))

c = pygame.time.Clock()
running = True
while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		elif event.type == pygame.VIDEORESIZE:
			SCREENSIZE = [*event.dict["size"]]
			screen = pygame.display.set_mode(SCREENSIZE, pygame.RESIZABLE)
	# Drawing
	screen.fill(WHITE)
	# Board
	for x in range(len(BOARD)):
		for y in range(len(BOARD[x])):
			cellrect = pygame.Rect(x * CELLSIZE, y * CELLSIZE, CELLSIZE, CELLSIZE)
			if BOARD[x][y] == 0:
				pygame.draw.rect(screen, BLACK, cellrect, 1)
			elif BOARD[x][y] == 1:
				pygame.draw.rect(screen, RED, cellrect)
				es = []
				for e in entities:
					if isinstance(e, Enemy): es.append(e)
				es.sort(key=lambda z: dist((x, y), z.pos))
				if len(es) > 0:
					e = es[0]
					if dist((x, y), e.pos) < 3:
						pygame.draw.line(screen, RED, cellnos_to_pixels(x, y), cellnos_to_pixels(*e.pos))
						e.die()
						BOARD[x][y] = 99
			elif BOARD[x][y] < 100:
				pygame.draw.rect(screen, BLACK, cellrect)
				BOARD[x][y] -= 1
			elif BOARD[x][y] == 100:
				pygame.draw.rect(screen, RED, cellrect)
				es = []
				for e in entities:
					if isinstance(e, Enemy): es.append(e)
				es.sort(key=lambda z: dist((x, y), z.pos))
				if len(es) > 0:
					e = es[0]
					if dist((x, y), e.pos) < 1.5:
						pygame.draw.line(screen, RED, cellnos_to_pixels(x, y), cellnos_to_pixels(*e.pos))
						e.die()
						BOARD[x][y] = 119
			elif BOARD[x][y] < 120:
				pygame.draw.rect(screen, TAN, cellrect)
				BOARD[x][y] -= 1
	# Route
	for i in range(len(ROUTE) - 1):
		start = (cellno_to_pixel(ROUTE[i][0]), cellno_to_pixel(ROUTE[i][1]))
		end = (cellno_to_pixel(ROUTE[i + 1][0]), cellno_to_pixel(ROUTE[i + 1][1]))
		pygame.draw.line(screen, RED, start, end, round(0.3 * CELLSIZE))
	# Entities
	for e in entities:
		e.tick()
		s = e.draw()
		x = cellno_to_pixel(e.pos[0])# - (s.get_width() / 2)
		y = cellno_to_pixel(e.pos[1]) - (s.get_height() / 2)
		screen.blit(s, (x, y))
	# Spawning
	if random.random() < 0.07: Enemy()
	#pygame.draw.line(screen, BLACK, [cellno_to_pixel(e.prevpos[0]), cellno_to_pixel(e.prevpos[1])], [cellno_to_pixel(e.route[0][0]), cellno_to_pixel(e.route[0][1])], 1)
	# Flip
	pygame.display.flip()
	c.tick(20)
