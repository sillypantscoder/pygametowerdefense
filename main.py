import pygame
import random

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

SCREENSIZE = [500, 500]
screen = pygame.display.set_mode(SCREENSIZE, pygame.RESIZABLE)
CELLSIZE = 50

BOARD = [[random.choices([0, 1], weights=[10, 1], k=1)[0] for y in range(10)] for x in range(10)]
ROUTE = [[0, 3], [5, 3], [5, 10]]

c = pygame.time.Clock()
running = True
while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		elif event.type == pygame.VIDEORESIZE:
			screensize = [*event.dict["size"]]
			screen = pygame.display.set_mode(SCREENSIZE, pygame.RESIZABLE)
	# Drawing
	screen.fill(WHITE)
	# Board
	for x in range(len(BOARD)):
		for y in range(len(BOARD[x])):
			cellrect = pygame.Rect(x * CELLSIZE, y * CELLSIZE, CELLSIZE, CELLSIZE)
			if BOARD[x][y] == 0:
				pygame.draw.rect(screen, BLACK, cellrect, 1)
			else:
				pygame.draw.rect(screen, BLACK, cellrect)
	# Route
	for i in range(len(ROUTE) - 1):
		pixeltransform = (lambda x: round((x * CELLSIZE) + (0.5 * CELLSIZE)))
		start = (pixeltransform(ROUTE[i][1]), pixeltransform(ROUTE[i][0]))
		end = (pixeltransform(ROUTE[i + 1][1]), pixeltransform(ROUTE[i + 1][0]))
		pygame.draw.line(screen, RED, start, end, round(0.2 * CELLSIZE))
	# Flip
	pygame.display.flip()
	c.tick(60)
