import pygame

class TempText:

    TEXT_FLOAT_SPEED = 5

    def __init__(self, screen, x, y, text, textColor, font, transparency, float, decayRate) -> None:
        self.screen = screen
        self.x = x
        self.y = y
        self.text = text
        self.textColor = textColor
        self.font = font
        self.transparency = transparency
        self.float = float
        self.decayRate = decayRate

    def draw(self):
        text = self.font.render(self.text, False, self.textColor)
        text.set_alpha(self.transparency)
        self.screen.blit(text, (self.x - text.get_width() / 2, self.y - text.get_height() / 2))

    def update(self):
        self.transparency -= self.decayRate

class Button:
    BUTTON_FONT_SIZE = 35

    def __init__(self, screen, x, y, width, height, text, textColor, color, action) -> None:
        self.screen = screen
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.textColor = textColor
        self.color = color
        self.action = action
    
    def draw(self):
        pygame.draw.rect(self.screen, self.color, rect=((self.x, self.y), (self.width, self.height)))
        text = pygame.font.SysFont('Monocraft', self.BUTTON_FONT_SIZE)
        buttonText = text.render(self.text, False, self.textColor)
        self.screen.blit(buttonText, (self.x + self.width / 2 - buttonText.get_width() / 2, self.y + self.height / 2 - buttonText.get_height() / 2))