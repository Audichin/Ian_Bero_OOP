import pygame
import sys

# Initialize Pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 500, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rectangle with Border and Transparent Center")

# Colors (R, G, B)
BORDER_COLOR = (255, 0, 0)  # Red border
BG_COLOR = (0, 0, 255)      # Blue background

# Create a transparent surface for the rectangle
rect_surface = pygame.Surface((200, 150), pygame.SRCALPHA)  # SRCALPHA enables per-pixel alpha

# Draw only the border (width > 0 means outline only)
pygame.draw.rect(rect_surface, BORDER_COLOR, rect_surface.get_rect(), width=5)

# Main loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Fill background
    screen.fill(BG_COLOR)

    # Blit the transparent rectangle surface
    screen.blit(rect_surface, (150, 125))

    # Update display
    pygame.display.flip()
