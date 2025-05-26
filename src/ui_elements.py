import pygame
import config # Import the config file

class Button:
    def __init__(self, text, rect, font, text_color, button_color, hover_color, sound_manager=None, action=None, action_args=None):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.text_color = text_color
        self.button_color = button_color
        self.original_button_color = button_color
        self.hover_color = hover_color
        self.action = action
        self.action_args = action_args if action_args is not None else []
        self.is_hovered = False
        self.sound_manager = sound_manager
        self.click_sound = "ui_click" # Conceptual sound name
        self.text_surface = self.font.render(self.text, True, self.text_color)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)

    def draw(self, surface):
        current_color = self.hover_color if self.is_hovered else self.original_button_color
        pygame.draw.rect(surface, current_color, self.rect)
        surface.blit(self.text_surface, self.text_rect)

    def handle_event(self, event):
        triggered_action = False
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.is_hovered:
                if self.sound_manager:
                    self.sound_manager.play_sound(self.click_sound)
                if self.action:
                    if self.action_args:
                        self.action(*self.action_args)
                    else:
                        self.action()
                    triggered_action = True
        return triggered_action

if __name__ == '__main__':
    pygame.init()
    class MockSoundManager:
        def play_sound(self, sound_name):
            print(f"MockSoundManager: Playing sound {sound_name}")

    mock_sm = MockSoundManager()
    # Use screen dimensions from config
    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    pygame.display.set_caption("Button Test")
    # Use font settings from config
    ui_font = pygame.font.SysFont(config.UI_FONT_FAMILY, config.UI_FONT_SIZE)

    def test_action_no_args():
        print("Test Action (no args) Triggered!")

    def test_action_with_args(message, number):
        print(f"Test Action (with args) Triggered! Message: {message}, Number: {number}")

    button1_rect = pygame.Rect(screen_width // 2 - 100, screen_height // 2 - 70, 200, 50)
    button1 = Button(
        text="No Args Action", rect=button1_rect, font=ui_font,
        text_color=config.WHITE, button_color=config.BLUE, # Use config colors
        hover_color=(100, 100, 255), sound_manager=mock_sm, action=test_action_no_args # Slightly lighter blue for hover
    )

    button2_rect = pygame.Rect(config.SCREEN_WIDTH // 2 - 100, config.SCREEN_HEIGHT // 2, 200, 50)
    button2 = Button(
        text="Args Action", rect=button2_rect, font=ui_font,
        text_color=config.WHITE, button_color=config.GREEN, # Use config colors
        hover_color=(100, 255, 100), sound_manager=mock_sm, # Slightly lighter green for hover
        action=test_action_with_args, action_args=["Hi", 123]
    )

    buttons = [button1, button2]
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            for btn in buttons:
                btn.handle_event(event)

        screen.fill(config.BLACK) # Use config color
        for btn in buttons:
            btn.draw(screen)
        pygame.display.flip()

    pygame.quit()
