import pygame
from config import BLUE # Using BLUE as a placeholder color, can be changed

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color=BLUE):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        # self.image is not strictly necessary if we're just drawing rects,
        # but good practice if we later want to use sprite drawing routines
        # or add textures.
        self.image = pygame.Surface([width, height])
        self.image.fill(self.color)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

# Example usage (optional, for testing this file directly)
if __name__ == '__main__':
    pygame.init()
    screen_width = 800
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Platform Test")

    platform1 = Platform(100, screen_height - 100, 200, 20)
    platform2 = Platform(400, screen_height - 200, 150, 20, (0, 255, 0)) # Green platform

    all_sprites = pygame.sprite.Group() # Example if using sprite groups
    all_sprites.add(platform1)
    all_sprites.add(platform2)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((30, 30, 30))  # Dark grey background
        
        # Using the platform's own draw method
        platform1.draw(screen)
        platform2.draw(screen)
        
        # Or if using sprite groups and self.image is set up:
        # all_sprites.draw(screen) # This would draw self.image at self.rect

        pygame.display.flip()

    pygame.quit()
