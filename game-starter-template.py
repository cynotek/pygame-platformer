#!/usr/bin/env python3

import pygame

pygame.init()

# Window settings
WIDTH = 960
HEIGHT = 640
window = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption("My Platform Game")
FPS = 60
clock = pygame.time.Clock()

# Colors
SKY_BLUE = (135, 206, 235)

# Fonts
font_small = pygame.font.Font(None, 32)
font_big = pygame.font.Font(None, 64)

# Images
hero_img = pygame.image.load("assets/character/adventurer_walk1.png")
hero_img = pygame.transform.scale(hero_img, (64, 64))

block_img = pygame.image.load("assets/tiles/top_middle.png")
block_img = pygame.transform.scale(block_img, (64, 64))

# Controls
LEFT = pygame.K_LEFT
RIGHT = pygame.K_RIGHT
JUMP = pygame.K_SPACE


class Entity(pygame.sprite.Sprite):

    def __init__(self, x, y, image):
        super().__init__()

        self.image = pygame.Surface([64, 64])
        self.image.blit(image, [0, 0])

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Block(Entity):

    def __init__(self, x, y, image):
        super().__init__(x, y, image)


class Character(Entity):

    def __init__(self, x, y, image):
        super().__init__(x, y, image)

        self.speed = 5
        self.jump_power = 20

        self.vx = 0
        self.vy = 0

    def apply_gravity(self):
        pass

    def process_blocks(self, blocks):

        self.rect.x += self.vx
        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        for block in hit_list:
            if self.vx > 0:
                self.rect.right = block.rect.left
                self.vx = 0
            elif self.vx < 0:
                self.rect.left = block.rect.right
                self.vx = 0

        self.rect.y += self.vy
        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        for block in hit_list:
            if self.vy > 0:
                self.rect.bottom = block.rect.top
                self.vy = 0
            elif self.vy < 0:
                self.rect.top = block.rect.bottom
                self.vy = 0

    def move_left(self):
        self.vx = -self.speed

    def move_right(self):
        self.vx = self.speed

    def stop(self):
        self.vx = 0

    def jump(self, blocks):
        pass

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy


class Coin():
    pass


class Enemy():
    pass


class Game():

    def __init__(self, hero, blocks):
        self.hero = hero
        self.blocks = blocks

        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(hero, blocks)

    def play(self):
        # game loop
        done = False

        while not done:
            # event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == JUMP:
                        self.hero.jump(self.blocks)

            pressed = pygame.key.get_pressed()

            # game logic
            if pressed[LEFT]:
                self.hero.move_left()
            elif pressed[RIGHT]:
                self.hero.move_right()
            else:
                self.hero.stop()

            self.hero.update()

            # Drawing
            window.fill(SKY_BLUE)
            self.all_sprites.draw(window)

            # Update window
            pygame.display.update()
            clock.tick(FPS)

        # Close window on quit
        pygame.quit()


def main():
    # Make sprites
    hero = Character(500, 512, hero_img)

    blocks = pygame.sprite.Group()

    for i in range(0, WIDTH, 64):
        b = Block(i, 576, block_img)
        blocks.add(b)

    blocks.add(Block(192, 448, block_img))
    blocks.add(Block(256, 448, block_img))
    blocks.add(Block(320, 448, block_img))

    blocks.add(Block(448, 320, block_img))
    blocks.add(Block(512, 320, block_img))

    # Start game
    game = Game(hero, blocks)
    game.play()


if __name__ == "__main__":
    main()
