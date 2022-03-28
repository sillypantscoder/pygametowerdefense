import pygame

WHITE = (255, 255, 255)

SCREENSIZE = [500, 500]
screen = pygame.display.set_mode(SCREENSIZE)

c = pygame.time.Clock()
running = True
while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
	# Drawing
	screen.fill(WHITE)
	# Flip
	pygame.display.flip()
	c.tick(60)
