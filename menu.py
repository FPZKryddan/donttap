import pygame
import os
import math

import ui
import game as g
from settings import *


class Menu:
    def __init__(self, screen) -> None:
        self.screen = screen
        self.game = g.Game(self.screen)
        self.statsMode = ENDURANCE
        self.headerText = pygame.font.SysFont('Monocraft', 100)
        self.header2Text = pygame.font.SysFont('Monocraft', 65)

    def draw_background(self):
        self.screen.fill(BACKGROUND_COLOR)
        pygame.draw.rect(self.screen, color=(0,0,0), rect=(GAME_START_POS_X, 0, GAME_WIDTH, SCREEN_HEIGHT))

    def button_clicked(self, buttons, pos):
        posX, posY = pos
        
        for button in buttons:
            if posX > button.x and posX < button.x + button.width and posY > button.y and posY < button.y + button.height:
                return button
        return -1
    
    def start_game(self, mode):
        gameStats = self.game.start_game(mode)
        self.game_over_screen(gameStats)

    def quit_clicked(self):
        exit()

    def replay_clicked(self, mode):
        self.start_game(mode)
        return True

    def back_to_menu_clicked(self):
        return True

    def read_stats(self, mode, sort=True):
        scores = []
        
        filePath = str(mode) + SAVE_PATH
        if not os.path.isfile(filePath):
            return scores
        
        with open(filePath, 'r') as file:
            for line in file:
                stats = line.split(' ')
                if mode is PATTERN:
                    scores.append(float("{:.2f}".format(float(stats[0].strip('\n')))))
                else:
                    print(stats[0])
                    scores.append(int(stats[0].strip('\n')))
        
        # Sort in descending order if mode is pattern
        reverse = True
        if mode is PATTERN:
            reverse = False
        
        if sort:
            scores.sort(reverse=reverse)
        return scores
    
    def change_stats_display_gamemode(self, mode):
        self.statsMode = mode
        return False
    
    def draw_plot(self, scores):
        entries = len(scores)

        HEIGHT = 250
        WIDTH = 500
        x0 = GAME_START_POS_X + GAME_WIDTH / 2 - WIDTH / 2
        y0 = GAME_START_POS_Y + GAME_HEIGHT / 2 

        # draw axises
        if self.statsMode is ENDURANCE:
            title = "Endurance stats"
        elif self.statsMode is PATTERN:
            title = "Pattern stats"
        else:
            title = "Frenzy stats"
        text = self.header2Text.render(title, False, INFO_TEXT_COLOR)
        self.screen.blit(text, (GAME_START_POS_X + GAME_WIDTH / 2 - text.get_width() / 2, y0 - TEXT_MARGIN - HEIGHT - text.get_height()))
        pygame.draw.line(self.screen, (255, 0, 0), (x0, y0), (x0, y0 - HEIGHT), 2)  # Vertical axis
        pygame.draw.line(self.screen, (255, 0, 0), (x0, y0), (x0 + WIDTH, y0), 2)  # Horizontal axis

        # if enough scores saved then display stats
        if entries > 2:
            data_points = []
            for i, score in enumerate(scores):
                data_points.append((int(i * (WIDTH / (entries - 1))), score))


            dataMin = min(scores)
            dataMax = max(scores)
            scalar = (HEIGHT) / (dataMax - dataMin)

            statsFont = pygame.font.SysFont('Monocraft', 25)
            verticalMaxText = statsFont.render(str(dataMax), False, INFO_TEXT_COLOR)
            verticalMinText = statsFont.render(str(dataMin), False, INFO_TEXT_COLOR)

            self.screen.blit(verticalMaxText, (x0 - verticalMaxText.get_width() - TEXT_MARGIN, y0 - HEIGHT))
            self.screen.blit(verticalMinText, (x0 - verticalMinText.get_width() - TEXT_MARGIN, y0 - verticalMinText.get_height()))


            horizontalSegments = 8
            horizontalJump = int(entries / horizontalSegments)
            for i in range(horizontalSegments):
                x = i + 1 + (horizontalJump * i)
                text = statsFont.render(str(x), False, INFO_TEXT_COLOR)
                self.screen.blit(text, (x0 + (i * (WIDTH / (horizontalSegments - 1)) - text.get_width() / 2), y0 + TEXT_MARGIN))


            for i, point in enumerate(data_points):
                x1, y1 = x0, y0
                x1 += point[0]
                y1 -= point[1] * scalar

                x2 = x0 + data_points[i + 1][0] if i < entries - 1 else x1
                y2 = y0 - data_points[i + 1][1] * scalar if i < entries - 1 else y1
                pygame.draw.line(self.screen, (255, 255, 0), (x1, y1), (x2, y2), 2)
        else: # otherwise display error message
            pass

    def game_over_screen(self, gameStats):
        exitStatus = False
        mode = gameStats['mode']
        buttons = []

        # Create menu buttons
        buttonsStartY = GAME_START_POS_Y + GAME_HEIGHT - 200
        buttonsYMargin = 20
        buttonsWidth = GAME_WIDTH / 2
        buttonsHeight = 70
        buttons.append(ui.Button(self.screen, GAME_START_POS_X + GAME_WIDTH / 2 - buttonsWidth / 2, buttonsStartY + (buttonsHeight + buttonsYMargin) * len(buttons), buttonsWidth, buttonsHeight, "Replay", (255, 255, 255), (0, 125, 255), lambda: self.replay_clicked(mode)))
        buttons.append(ui.Button(self.screen, GAME_START_POS_X + GAME_WIDTH / 2 - buttonsWidth / 2, buttonsStartY + (buttonsHeight + buttonsYMargin) * len(buttons), buttonsWidth, buttonsHeight, "Back to menu", (255, 255, 255), (217, 110, 106), self.back_to_menu_clicked))

        # Save score 
        if gameStats['save_score']: 
            with open(str(mode) + SAVE_PATH, 'a') as file:
                file.write(str(gameStats['score']) + "\n")

        # Get highscores
        topScores = self.read_stats(mode)[:10]

        # Draw ui
        self.draw_background()
        
        # Draw title text
        if mode is PATTERN:
            text = "You scored: " + str("{:.2f}".format(float(gameStats['score'])))
        else:
            text = "You score:  " + str(gameStats['score'])
        titleText = self.header2Text.render(text, False, INFO_TEXT_COLOR)
        self.screen.blit(titleText, (GAME_START_POS_X + GAME_WIDTH / 2 - titleText.get_width() / 2, GAME_START_POS_Y))

        # Display top scores
        if len(topScores) > 0:
            scoreFont = pygame.font.SysFont('Monocraft', 25)
            scoreStartY = GAME_START_POS_Y + titleText.get_height() + 100
            scoreYMargin = 35
            for i, score in enumerate(topScores):
                print(str(i + 1) + ". " + str(score))
                scoreText = scoreFont.render(str(i + 1) + ". " + str(score), False, INFO_TEXT_COLOR)
                self.screen.blit(scoreText, (GAME_START_POS_X + GAME_WIDTH / 2 - scoreText.get_width() / 2, scoreStartY + scoreYMargin * i))

        # Draw buttons
        for button in buttons:
            button.draw()
        
        # Render ui
        pygame.display.flip()

        # Menu loop
        while True:
            # 
            if exitStatus:
                break

            # Handle user events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    break
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: # left click
                        mousePos = event.pos
                        button_clicked = self.button_clicked(buttons, mousePos)
                        if button_clicked != -1:
                            exitStatus = button_clicked.action()

    def stat_page(self):
        exitStatus = False
        buttons = []

        # buttons
        buttonsStartY = GAME_START_POS_Y + GAME_HEIGHT / 2 + 200
        buttonsYMargin = 20
        buttonsWidth = GAME_WIDTH / 3
        buttonsHeight = 50
        buttons.append(ui.Button(self.screen, GAME_START_POS_X + GAME_WIDTH / 2 - buttonsWidth / 2, buttonsStartY + (buttonsHeight + buttonsYMargin) * len(buttons), buttonsWidth, buttonsHeight, "Endurance", (255, 255, 255), (217, 201, 111), lambda: self.change_stats_display_gamemode(ENDURANCE)))
        buttons.append(ui.Button(self.screen, GAME_START_POS_X + GAME_WIDTH / 2 - buttonsWidth / 2, buttonsStartY + (buttonsHeight + buttonsYMargin) * len(buttons), buttonsWidth, buttonsHeight, "Pattern", (255, 255, 255), (217, 201, 111), lambda: self.change_stats_display_gamemode(PATTERN)))
        buttons.append(ui.Button(self.screen, GAME_START_POS_X + GAME_WIDTH / 2 - buttonsWidth / 2, buttonsStartY + (buttonsHeight + buttonsYMargin) * len(buttons), buttonsWidth, buttonsHeight, "Frenzy", (255, 255, 255), (217, 201, 111), lambda: self.change_stats_display_gamemode(FRENZY)))
        buttons.append(ui.Button(self.screen, GAME_START_POS_X + GAME_WIDTH / 2 - buttonsWidth / 2, buttonsStartY + (buttonsHeight + buttonsYMargin) * len(buttons), buttonsWidth, buttonsHeight, "Back to menu", (255, 255, 255), (217, 110, 106), self.back_to_menu_clicked))

        # draw background
        self.draw_background()

        # draw menu ui
        # Draw buttons
        for button in buttons:
            button.draw()

        # Retrieve stats
        scores = self.read_stats(ENDURANCE, False)

        # Draw graph
        self.draw_plot(scores)

        lastMode = self.statsMode
        # menu loop
        while True:
            print(self.statsMode)
            if exitStatus:
                break

            if lastMode is not self.statsMode:
                # Redraw
                # draw background
                self.draw_background()

                # draw menu ui
                # Draw buttons
                for button in buttons:
                    button.draw()
                self.draw_plot(self.read_stats(self.statsMode, False))
                print("hej")
                lastMode = self.statsMode

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    break
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: # left click
                        mousePos = event.pos
                        button_clicked = self.button_clicked(buttons, mousePos)
                        if button_clicked != -1:
                            exitStatus = button_clicked.action()
            
            # Render
            pygame.display.flip()


    def main_menu(self):

        buttons = []

        # buttons
        buttonsStartY = GAME_START_POS_Y + 250
        buttonsYMargin = 20
        buttonsWidth = GAME_WIDTH / 2
        buttonsHeight = 70
        buttons.append(ui.Button(self.screen, GAME_START_POS_X + GAME_WIDTH / 2 - (GAME_WIDTH / 4), buttonsStartY + (buttonsHeight + buttonsYMargin) * len(buttons), buttonsWidth, buttonsHeight, "Endurance", (255, 255, 255), (217, 201, 111), lambda: self.start_game(ENDURANCE)))
        buttons.append(ui.Button(self.screen, GAME_START_POS_X + GAME_WIDTH / 2 - (GAME_WIDTH / 4), buttonsStartY + (buttonsHeight + buttonsYMargin) * len(buttons), buttonsWidth, buttonsHeight, "Pattern", (255, 255, 255), (217, 201, 111), lambda: self.start_game(PATTERN)))
        buttons.append(ui.Button(self.screen, GAME_START_POS_X + GAME_WIDTH / 2 - (GAME_WIDTH / 4), buttonsStartY + (buttonsHeight + buttonsYMargin) * len(buttons), buttonsWidth, buttonsHeight, "Frenzy", (255, 255, 255), (217, 201, 111), lambda: self.start_game(FRENZY)))
        buttons.append(ui.Button(self.screen, GAME_START_POS_X + GAME_WIDTH / 2 - (GAME_WIDTH / 4), buttonsStartY + (buttonsHeight + buttonsYMargin) * len(buttons), buttonsWidth, buttonsHeight, "Stats", (255, 255, 255), (217, 201, 111), self.stat_page))
        buttons.append(ui.Button(self.screen, GAME_START_POS_X + GAME_WIDTH / 2 - (GAME_WIDTH / 4), buttonsStartY + (buttonsHeight + buttonsYMargin) * len(buttons), buttonsWidth, buttonsHeight, "Quit", (255, 255, 255), (217, 110, 106), self.quit_clicked))

        titleBounceIteration = 0

        # menu loop
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    break
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: # left click
                        mousePos = event.pos
                        button_clicked = self.button_clicked(buttons, mousePos)
                        if button_clicked != -1:
                            button_clicked.action()

            # draw background
            self.draw_background()

            # draw menu ui
            titleText = self.headerText.render("Don't Tap", False, (255, 255, 255))
            
            titleYBounce = math.sin(titleBounceIteration)
            titleYBounceScale = 25
            self.screen.blit(titleText, (GAME_START_POS_X + GAME_WIDTH / 2 - titleText.get_width() / 2, GAME_START_POS_Y + 50 + titleYBounce * titleYBounceScale))

            # Draw buttons
            for button in buttons:
                button.draw()

            # Render
            pygame.display.flip()

            titleBounceIteration += 0.01
            titleBounceIteration = titleBounceIteration % 90

