import pygame
import random as rnd

import ui
from settings import *

class Game:

    COMBO_THRESHOLD = 500
    COMBO_GAIN = 45
    COMBO_LOSS_PER_FRAME = 2.5

    COMBO_UI_WIDTH = GAME_WIDTH / 2
    COMBO_UI_HEIGHT = 25
    COMBO_UI_BACKGROUND_COLOR = (91, 91, 91)
    COMBO_UI_COLOR = (255, 255, 255)

    TIME_NORMAL_COLOR = (0, 255, 0)
    TIME_WARNING_COLOR = (255, 179, 0 )
    TIME_DANGER_COLOR = (255, 0, 0)

    def __init__(self, screen, mode=ENDURANCE) -> None:
        self.running = True
        self.tiles = [0] * (SIZE * SIZE)
        self.blackTiles = 0
        self.score = 0
        self.timer = 0
        self.combo = 0
        self.patternsCleared = 0
        self.bonusActive = False
        self.mode = mode # 0 endurance 1 pattern 2 frenzy
        self.screen = screen
        self.infoText = pygame.font.SysFont('Monocraft', INFO_TEXT_SIZE)
        self.numericalText = pygame.font.SysFont('Monocraft', NUMERICAL_TEXT_SIZE)
        self.tempTextsObJs = []

    def init_tiles(self):
        tilesToSpawn = BLACK_TILES if self.mode is not PATTERN else PATTERN_SIZE
        for i in range(tilesToSpawn):
            self.make_random_tile_black()
    
    def make_random_tile_black(self, ignore_tile=None):
        candidates = [i for i in range(SIZE * SIZE)]

        if ignore_tile is not None:
            candidates.remove(ignore_tile)

        while True:
            # If all tiles already black then return
            if len(candidates) <= 0:
                return -1
            
            # choose a random tile, if white turn it black otherwise remove it from candidates and try another
            consideredCandidate = rnd.choice(candidates)
            if self.tiles[consideredCandidate] == 0:
                self.tiles[consideredCandidate] = 1
                self.blackTiles += 1
                return 0
            else:
                candidates.remove(consideredCandidate)

    def make_all_tiles_black(self):
        self.blackTiles = SIZE*SIZE
        for i in range(len(self.tiles)):
            self.tiles[i] = 1

    def make_tile_black(self, tileIdx):
        self.tiles[tileIdx] = 1

    def make_tile_white(self, tileIdx):
        self.tiles[tileIdx] = 0
        self.blackTiles -= 1

    def get_tile_from_pos(self, pos):
        posX = pos[0]
        posY = pos[1]
        
        # check if pos in game window
        if ( posX < GAME_START_POS_X
            or posX > GAME_START_POS_X + GAME_WIDTH
            or posY < GAME_START_POS_Y
            or posY > GAME_START_POS_Y + GAME_HEIGHT
            ):
            return -1

        x = int((posX - GAME_START_POS_X) / TILE_WIDTH)
        y = int((posY - GAME_START_POS_Y) / TILE_HEIGHT)
        return ((x + 1) + (y * SIZE)) - 1

    def click_tile(self, tileIdx):
        # Handle clicking on white tile
        if self.tiles[tileIdx] == 0:
            self.running = False
        else: # Handle clicking on black tile
            self.make_tile_white(tileIdx)

            # create new black tile if not bonus active
            if not self.bonusActive and self.mode is not PATTERN:
                self.make_random_tile_black(tileIdx)
            if self.bonusActive or self.mode is PATTERN: # if complete bonus spawn new set of black tiles
                if self.blackTiles == 0:
                    self.bonusActive = False
                    self.init_tiles()
                    if self.mode is PATTERN:
                        self.patternsCleared += 1

            scoreGain = 1
            if self.mode is FRENZY:
                scoreGain = int((self.combo * FRENZY_SCORE_STEPS) / self.COMBO_THRESHOLD) + 1
            elif self.mode is PATTERN:
                scoreGain = 0

            self.score += scoreGain

            if self.mode is not PATTERN:
                self.combo += self.COMBO_GAIN
            
            if self.mode is ENDURANCE:
                if self.score % ENDURANCE_TIME_GAIN_THRESHOLD == 0:
                    self.endurance_add_time()

            tilePosX = GAME_START_POS_X + int(tileIdx % SIZE) * TILE_WIDTH + TILE_WIDTH / 2
            tilePosY = GAME_START_POS_Y + int(tileIdx / SIZE) * TILE_HEIGHT + TILE_HEIGHT / 2
            self.tempTextsObJs.append(ui.TempText(self.screen, tilePosX, tilePosY, "+" + str(scoreGain), (0,255,0), self.infoText, 255, False, 20))

    def draw_background(self):
        self.screen.fill(BACKGROUND_COLOR)
        pygame.draw.rect(self.screen, color=self.COMBO_UI_BACKGROUND_COLOR, rect=(GAME_START_POS_X, 0, GAME_WIDTH, SCREEN_HEIGHT))
        pygame.draw.rect(self.screen, color=self.COMBO_UI_COLOR, rect=(GAME_START_POS_X, GAME_START_POS_Y, GAME_WIDTH, GAME_HEIGHT))

    def draw_temp_text_objs(self):
        for text in self.tempTextsObJs:
            text.draw()
            text.update()
            if text.transparency <= 0:
                self.tempTextsObJs.remove(text)

    def draw_tiles(self):
        for i, tile in enumerate(self.tiles):
            pos = (GAME_START_POS_X + TILE_WIDTH * int((i%SIZE)), GAME_START_POS_Y + TILE_HEIGHT * (int((i/SIZE) % SIZE)))
            color = WHITE_TILE_COLOR if tile == 0 else BLACK_TILE_COLOR
            pygame.draw.rect(self.screen, color=color, rect=(pos, (TILE_WIDTH, TILE_HEIGHT)))                                # draw tile
            pygame.draw.rect(self.screen, color=TILE_BORDER_COLOR, rect=(pos, (TILE_WIDTH, TILE_HEIGHT)), width=TILE_BORDER) # draw tile border
        
    def draw_combo(self):
        pygame.draw.rect(self.screen, color=(0,0,0), rect=(GAME_START_POS_X + GAME_WIDTH / 2 - self.COMBO_UI_WIDTH / 2, GAME_START_POS_Y + GAME_HEIGHT + self.COMBO_UI_HEIGHT, self.COMBO_UI_WIDTH, self.COMBO_UI_HEIGHT))
        pygame.draw.rect(self.screen, color=(255, 255, 255), rect=(GAME_START_POS_X + GAME_WIDTH / 2 - self.COMBO_UI_WIDTH / 2, GAME_START_POS_Y + GAME_HEIGHT + self.COMBO_UI_HEIGHT, self.combo / self.COMBO_THRESHOLD * self.COMBO_UI_WIDTH, self.COMBO_UI_HEIGHT))

    def display_information(self):
        infoScoreText = self.infoText.render("SCORE", False, INFO_TEXT_COLOR)
        infoTimeText = self.infoText.render("TIME", False, INFO_TEXT_COLOR)
        scoreText = self.numericalText.render(str(self.score), False, NUMERICAL_TEXT_COLOR)

        if self.timer > 5:
            timeText = self.numericalText.render(str("{:.1f}".format(self.timer)), False, self.TIME_NORMAL_COLOR)
        elif self.timer > 2:
            timeText = self.numericalText.render(str("{:.1f}".format(self.timer)), False, self.TIME_WARNING_COLOR)
        else:
            timeText = self.numericalText.render(str("{:.1f}".format(self.timer)), False, self.TIME_DANGER_COLOR)

        if self.mode is not PATTERN:
            self.screen.blit(infoScoreText, (GAME_START_POS_X + (GAME_WIDTH / 2) - (infoScoreText.get_width() / 2), GAME_START_POS_Y - ( INFO_TEXT_SIZE + NUMERICAL_TEXT_SIZE + TEXT_MARGIN)))
            self.screen.blit(scoreText, (GAME_START_POS_X + (GAME_WIDTH / 2) - (scoreText.get_width() / 2), GAME_START_POS_Y - (NUMERICAL_TEXT_SIZE + TEXT_MARGIN)))

        self.screen.blit(infoTimeText, (GAME_START_POS_X + (GAME_WIDTH - (timeText.get_width() / 2 + infoTimeText.get_width() / 2) - TEXT_MARGIN), GAME_START_POS_Y - (INFO_TEXT_SIZE + NUMERICAL_TEXT_SIZE + TEXT_MARGIN)))
        self.screen.blit(timeText, (GAME_START_POS_X + (GAME_WIDTH - timeText.get_width() - TEXT_MARGIN), GAME_START_POS_Y - (NUMERICAL_TEXT_SIZE + TEXT_MARGIN)))
    
    def endurance_add_time(self):
        self.timer += EUNDRANCE_TIME_GAIN
        self.tempTextsObJs.append(ui.TempText(self.screen, GAME_START_POS_X + GAME_WIDTH / 2, GAME_START_POS_Y + GAME_HEIGHT / 2, "+" + str(EUNDRANCE_TIME_GAIN) + "seconds", (255, 225, 0), self.infoText, 255, False, 5))

    def endurance_spawn_bonus(self):
        self.make_all_tiles_black()
        self.combo = 0
        self.bonusActive = True
            
    def start_game(self, mode=ENDURANCE):
        # init values
        self.running = True
        self.tiles = [0] * (SIZE*SIZE)
        self.score = 0
        self.combo = 0
        self.blackTiles = 0
        self.patternsCleared = 0
        self.mode = mode

        if self.mode is ENDURANCE:
            self.timer = ENDURANCE_START_TIMER
        elif self.mode is PATTERN:
            self.timer = PATTERN_START_TIMER
        elif self.mode is FRENZY:
            self.timer = FRENZY_START_TIMER

        clock = pygame.time.Clock()
        dt = 0
        saveScore = True

        # init random black tiles
        self.init_tiles()

        # Game loop
        while self.running:
            # If user exits then exit
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    break
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: # left click
                        mousePos = event.pos
                        tileClicked = self.get_tile_from_pos(mousePos)
                        if tileClicked != -1:
                            self.click_tile(tileClicked)

            # if endurance mode
            if self.mode is ENDURANCE:
                # if combo exceeds threshold spawn bonus
                if self.combo >= self.COMBO_THRESHOLD:
                    self.endurance_spawn_bonus()

            # Render
            self.draw_background()
            self.draw_tiles()
            
            if self.mode is not PATTERN:
                self.draw_combo()
            
            self.draw_temp_text_objs()
            self.display_information()
            pygame.display.flip()
            
            dt = clock.tick(REFRESH_RATE) / 1000
            self.combo -= self.COMBO_LOSS_PER_FRAME if self.combo > 0 else 0
            
            if self.mode is ENDURANCE or self.mode is FRENZY:
                self.timer -= dt
            else:
                self.timer += dt

            # clamp combo value to max value if playing frenzy
            if self.mode is FRENZY:
                self.combo = self.COMBO_THRESHOLD if self.combo > self.COMBO_THRESHOLD else self.combo

            if (self.timer <= 0 or
                (self.mode is PATTERN and self.patternsCleared >= PATTERN_AMOUNT)):
                self.running = False

        # If we didn't complete all patterns when playing PATTERN, then dont save result
        if self.mode is PATTERN and self.patternsCleared < PATTERN_AMOUNT:
            saveScore = False

        return {
            'score': self.score if self.mode is not PATTERN else self.timer,
            'mode': self.mode,
            'save_score': saveScore
        }
