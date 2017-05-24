#!/usr/bin/env python3

import json
import pygame
import sys
import xbox360_controller

pygame.mixer.pre_init()
pygame.init()

# Window settings
TITLE = "Alien"
WIDTH = 960
HEIGHT = 640
FPS = 60
GRID_SIZE = 64

# Options
sound_on = True

# KB+M
LEFT = pygame.K_a
RIGHT = pygame.K_d
MUTE = pygame.K_m
JUMP = pygame.K_SPACE

# Levels
levels = ["levels/earth.json"]

# Colors
TRANSPARENT = (0, 0, 0, 0)
DARK_BLUE = (16, 86, 103)
WHITE = (255, 255, 255)

# Fonts
FONT_SM = pygame.font.Font("fonts/kenpixel.ttf", 32)
FONT_MD = pygame.font.Font("fonts/kenpixel.ttf", 64)
FONT_LG = pygame.font.Font("fonts/kenpixel.ttf", 72)


# Helper functions
def load_image(file_path, width=GRID_SIZE, height=GRID_SIZE):
    img = pygame.image.load(file_path)
    img = pygame.transform.scale(img, (width, height))

    return img


def load_char(file_path, width=GRID_SIZE, height=GRID_SIZE):
    img = pygame.image.load(file_path)
    img = pygame.transform.scale(img, (width, height * 2))

    return img


def play_sound(sound, loops=0, maxtime=0, fade_ms=0):
    if sound_on:
        sound.play(loops, maxtime, fade_ms)


def play_music():
    if sound_on:
        pygame.mixer.music.play(-1)
    else:
        pygame.mixer.music.stop()


# Images
alien_walk1 = load_char("assets/Players/128x256/Blue/alienBlue_walk1.png")
alien_walk2 = load_char("assets/Players/128x256/Blue/alienBlue_walk2.png")
alien_jump = load_char("assets/Players/128x256/Blue/alienBlue_jump.png")
alien_stand = load_char("assets/Players/128x256/Blue/alienBlue_stand.png")
alien_hit = load_char("assets/Players/128x256/Blue/alienBlue_hit.png")
alien_images = {"run": [alien_walk1, alien_walk2],
                "jump": alien_jump,
                "stand": alien_stand,
                "hit": alien_hit}

block_images = {"GL": load_image("assets/Ground/Grass/grassLeft.png"),
                "GM": load_image("assets/Ground/Grass/grassMid.png"),
                "GCR": load_image("assets/Ground/Grass/grassCliff_right.png"),
                "GR": load_image("assets/Ground/Grass/grassRight.png"),
                "GCL": load_image("assets/Ground/Grass/grassCliff_left.png"),
                "G": load_image("assets/Ground/Grass/grass.png"),
                "GC": load_image("assets/Ground/Grass/grassCenter.png"),
                "GHM": load_image("assets/Ground/Grass/grassHalf_mid.png"),
                "GHR": load_image("assets/Ground/Grass/grassHalf_right.png"),
                "GHL": load_image("assets/Ground/Grass/grassHalf_left.png")}

coin_img = load_image("assets/Items/coinGold.png")
heart_img = load_image("assets/HUD/hudHeart_full.png")
heart_empty_img = load_image("assets/HUD/hudHeart_empty.png")
oneup_img = load_image("assets/Items/gemBlue.png")
flag_img = load_image("assets/Items/flagBlue1.png")
flagpole_img = load_image("assets/Items/flagBlue1.png")  # My asset pack didn't come with a flag pole :(
soundon_img = load_image("assets/HUD/hudJewel_blue.png")
soundoff_img = load_image("assets/HUD/hudJewel_blue_empty.png")

Bee_img1 = load_image("assets/Enemies/bee.png")
Bee_img2 = load_image("assets/Enemies/bee_move.png")
Bee_images = [Bee_img1, Bee_img2]

# Sounds
# JUMP_SOUND = pygame.mixer.Sound("assets/sounds/jump.wav")
# COIN_SOUND = pygame.mixer.Sound("assets/sounds/pickup_coin.wav")
# POWERUP_SOUND = pygame.mixer.Sound("assets/sounds/powerup.wav")
# HURT_SOUND = pygame.mixer.Sound("assets/sounds/hurt.ogg")
# DIE_SOUND = pygame.mixer.Sound("assets/sounds/death.wav")
# LEVELUP_SOUND = pygame.mixer.Sound("assets/sounds/level_up.wav")
# GAMEOVER_SOUND = pygame.mixer.Sound("assets/sounds/game_over.wav")


class Entity(pygame.sprite.Sprite):

    def __init__(self, x, y, image):
        super().__init__()

        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.vy = 0
        self.vx = 0

    def apply_gravity(self, level):
        self.vy += level.gravity
        self.vy = min(self.vy, level.terminal_velocity)


class Block(Entity):

    def __init__(self, x, y, image):
        super().__init__(x, y, image)


class Character(Entity):

    def __init__(self, images):
        super().__init__(0, 0, images['stand'])

        self.image_idle_right = images['stand']
        self.image_idle_left = pygame.transform.flip(self.image_idle_right, 1, 0)
        self.images_run_right = images['run']
        self.images_run_left = [pygame.transform.flip(img, 1, 0) for img in self.images_run_right]
        self.image_jump_right = images['jump']
        self.image_jump_left = pygame.transform.flip(self.image_jump_right, 1, 0)
        self.image_hit_right = images['hit']
        self.image_hit_left = pygame.transform.flip(self.image_hit_right, 1, 0)

        self.running_images = self.images_run_right
        self.image_index = 0
        self.steps = 0

        self.speed = 5
        self.jump_power = 20

        self.vx = 0
        self.vy = 0
        self.facing_right = True
        self.on_ground = True

        self.score = 0
        self.lives = 3
        self.hearts = 3
        self.max_hearts = 3
        self.invincibility = 0

    def move_left(self):
        self.vx = -self.speed
        self.facing_right = False

    def move_right(self):
        self.vx = self.speed
        self.facing_right = True

    def stop(self):
        self.vx = 0

    def jump(self, blocks):
        self.rect.y += 1

        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        if len(hit_list) > 0:
            self.vy = -self.jump_power
            # play_sound(JUMP_SOUND)

        self.rect.y -= 1

    def check_world_boundaries(self, level):
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > level.width:
            self.rect.right = level.width

    def move_and_process_blocks(self, blocks):
        self.rect.x += self.vx
        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        for block in hit_list:
            if self.vx > 0:
                self.rect.right = block.rect.left
                self.vx = 0
            elif self.vx < 0:
                self.rect.left = block.rect.right
                self.vx = 0

        self.on_ground = False
        self.rect.y += self.vy + 1 # the +1 is hacky. not sure why it helps.
        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        for block in hit_list:
            if self.vy > 0:
                self.rect.bottom = block.rect.top
                self.vy = 0
                self.on_ground = True
            elif self.vy < 0:
                self.rect.top = block.rect.bottom
                self.vy = 0

        if self.rect.y > 10 * GRID_SIZE:
            self.hearts = 0

    def process_coins(self, coins):
        hit_list = pygame.sprite.spritecollide(self, coins, True)

        for coin in hit_list:
            # play_sound(COIN_SOUND)
            self.score += coin.value

    def process_enemies(self, enemies):
        hit_list = pygame.sprite.spritecollide(self, enemies, False)

        if len(hit_list) > 0 and self.invincibility == 0:
            if self.vy > 0:
                [e.kill() for e in hit_list]
                self.score += 1  # temp value
                self.vy = -self.jump_power
                return
            # play_sound(HURT_SOUND)
            if self.vx > 0:  # right facing hit
                self.rect.x += -self.jump_power
            elif self.vx < 0:  # left facing hit
                self.rect.x += self.jump_power
            self.hearts -= 1
            self.invincibility = int(0.75 * FPS)

    def process_powerups(self, powerups):
        hit_list = pygame.sprite.spritecollide(self, powerups, True)

        for p in hit_list:
            # play_sound(POWERUP_SOUND)
            p.apply(self)

    def check_flag(self, level):
        hit_list = pygame.sprite.spritecollide(self, level.flag, False)

        if len(hit_list) > 0:
            level.completed = True
            # play_sound(LEVELUP_SOUND)

    def set_image(self):
        if self.on_ground:
            if self.vx != 0:
                if self.facing_right:
                    self.running_images = self.images_run_right
                else:
                    self.running_images = self.images_run_left

                self.steps = (self.steps + 1) % self.speed  # Works well with 2 images, try lower number if more frames are in animation

                if self.steps == 0:
                    self.image_index = (self.image_index + 1) % len(self.running_images)
                    self.image = self.running_images[self.image_index]
            else:
                if self.facing_right:
                    self.image = self.image_idle_right
                else:
                    self.image = self.image_idle_left
        else:
            if self.facing_right:
                self.image = self.image_jump_right
            else:
                self.image = self.image_jump_left

    def die(self):
        self.lives -= 1

        if self.lives > 0:
            pass
            # play_sound(DIE_SOUND)
        else:
            pass
            # play_sound(GAMEOVER_SOUND)

    def respawn(self, level):
        self.rect.x = level.start_x
        self.rect.y = level.start_y
        self.hearts = self.max_hearts
        self.invincibility = 0
        self.facing_right = True

    def update(self, level):
        self.process_enemies(level.enemies)
        self.apply_gravity(level)
        self.move_and_process_blocks(level.blocks)
        self.check_world_boundaries(level)
        self.set_image()

        if self.hearts > 0:
            self.process_coins(level.coins)
            self.process_powerups(level.powerups)
            self.check_flag(level)

            if self.invincibility > 0:
                self.invincibility -= 1
        else:
            self.die()


class Coin(Entity):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)

        self.value = 5


class Enemy(Entity):
    def __init__(self, x, y, images):
        super().__init__(x, y, images[0])

        self.images_left = images
        self.images_right = [pygame.transform.flip(img, 1, 0) for img in images]
        self.current_images = self.images_left
        self.image_index = 0
        self.steps = 0

    def reverse(self):
        self.vx *= -1

        if self.vx < 0:
            self.current_images = self.images_left
        else:
            self.current_images = self.images_right

        self.image = self.current_images[self.image_index]

    def check_world_boundaries(self, level):
        if self.rect.left < 0:
            self.rect.left = 0
            self.reverse()
        elif self.rect.right > level.width:
            self.rect.right = level.width
            self.reverse()

    def move_and_process_blocks(self, blocks):
        self.rect.x += self.vx
        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        for block in hit_list:
            if self.vx > 0:
                self.rect.right = block.rect.left
                self.reverse()
            elif self.vx < 0:
                self.rect.left = block.rect.right
                self.reverse()

        self.rect.y += self.vy # the +1 is hacky. not sure why it helps.
        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        for block in hit_list:
            if self.vy > 0:
                self.rect.bottom = block.rect.top
                self.vy = 0
            elif self.vy < 0:
                self.rect.top = block.rect.bottom
                self.vy = 0

    def set_images(self):
        if self.steps == 0:
            self.image = self.current_images[self.image_index]
            self.image_index = (self.image_index + 1) % len(self.current_images)

        self.steps = (self.steps + 1) % 20  # Nothing significant about 20. It just seems to work okay.

    def is_near(self, hero):
        return abs(self.rect.x - hero.rect.x) < 2 * WIDTH

    def update(self, level, hero):
        if self.is_near(hero):
            self.apply_gravity(level)
            self.move_and_process_blocks(level.blocks)
            self.check_world_boundaries(level)
            self.set_images()

    def reset(self):
        self.rect.x = self.start_x
        self.rect.y = self.start_y
        self.vx = self.start_vx
        self.vy = self.start_vy
        self.current_images = self.images_left
        self.image = self.current_images[0]
        self.steps = 0


class Bee(Enemy):
    def __init__(self, x, y, images):
        super().__init__(x, y, images)

        self.start_x = x
        self.start_y = y
        self.start_vx = -2
        self.start_vy = 0

        self.vx = self.start_vx
        self.vy = self.start_vy

    def move_and_process_blocks(self, blocks):
        reverse = False

        self.rect.x += self.vx
        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        for block in hit_list:
            if self.vx > 0:
                self.rect.right = block.rect.left
                self.reverse()
            elif self.vx < 0:
                self.rect.left = block.rect.right
                self.reverse()

        self.rect.y += self.vy + 1 # the +1 is hacky. not sure why it helps.
        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        reverse = True

        for block in hit_list:
            if self.vy >= 0:
                self.rect.bottom = block.rect.top
                self.vy = 0

                if self.vx > 0 and self.rect.right <= block.rect.right:
                    reverse = False

                elif self.vx < 0 and self.rect.left >= block.rect.left:
                    reverse = False

            elif self.vy < 0:
                self.rect.top = block.rect.bottom
                self.vy = 0

        if reverse:
            self.reverse()


class OneUp(Entity):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)

    def apply(self, character):
        character.lives += 1


class Heart(Entity):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)

    def apply(self, character):
        character.hearts += 1
        character.hearts = min(character.hearts, character.max_hearts)


class Flag(Entity):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)


class Level():

    def __init__(self, file_path):
        self.starting_blocks = []
        self.starting_enemies = []
        self.starting_coins = []
        self.starting_powerups = []
        self.starting_flag = []

        self.blocks = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.flag = pygame.sprite.Group()

        self.active_sprites = pygame.sprite.Group()
        self.inactive_sprites = pygame.sprite.Group()

        with open(file_path, 'r') as f:
            data = f.read()

        map_data = json.loads(data)

        self.name = map_data['name']

        self.width = map_data['width'] * GRID_SIZE
        self.height = map_data['height'] * GRID_SIZE

        self.start_x = map_data['start'][0] * GRID_SIZE
        self.start_y = map_data['start'][1] * GRID_SIZE

        for item in map_data['blocks']:
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE
            img = block_images[item[2]]
            self.starting_blocks.append(Block(x, y, img))

        for item in map_data['bees']:
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE
            self.starting_enemies.append(Bee(x, y, Bee_images))

        for item in map_data['coins']:
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE
            self.starting_coins.append(Coin(x, y, coin_img))

        for item in map_data['oneups']:
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE
            self.starting_powerups.append(OneUp(x, y, oneup_img))

        for item in map_data['hearts']:
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE
            self.starting_powerups.append(Heart(x, y, heart_img))

        for i, item in enumerate(map_data['flag']):
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE

            if i == 0:
                img = flag_img
            else:
                img = flagpole_img

            self.starting_flag.append(Flag(x, y, img))

        self.background_layer = pygame.Surface([self.width, self.height], pygame.SRCALPHA, 32)
        self.scenery_layer = pygame.Surface([self.width, self.height], pygame.SRCALPHA, 32)
        self.inactive_layer = pygame.Surface([self.width, self.height], pygame.SRCALPHA, 32)
        self.active_layer = pygame.Surface([self.width, self.height], pygame.SRCALPHA, 32)

        if map_data['background-color'] != "":
            self.background_layer.fill(map_data['background-color'])

        if map_data['background-img'] != "":
            background_img = pygame.image.load(map_data['background-img']).convert_alpha()

            if map_data['background-fill-y']:
                h = background_img.get_height()
                w = int(background_img.get_width() * HEIGHT / h)
                background_img = pygame.transform.scale(background_img, (w, HEIGHT))

            if "top" in map_data['background-position']:
                start_y = 0
            elif "bottom" in map_data['background-position']:
                start_y = self.height - background_img.get_height()

            if map_data['background-repeat-x']:
                for x in range(0, self.width, background_img.get_width()):
                    self.background_layer.blit(background_img, [x, start_y])
            else:
                self.background_layer.blit(background_img, [0, start_y])

        if map_data['scenery-img'] != "":
            scenery_img = pygame.image.load(map_data['scenery-img']).convert_alpha()

            if map_data['scenery-fill-y']:
                h = scenery_img.get_height()
                w = int(scenery_img.get_width() * HEIGHT / h)
                scenery_img = pygame.transform.scale(scenery_img, (w, HEIGHT))

            if "top" in map_data['scenery-position']:
                start_y = 0
            elif "bottom" in map_data['scenery-position']:
                start_y = self.height - scenery_img.get_height()

            if map_data['scenery-repeat-x']:
                for x in range(0, self.width, scenery_img.get_width()):
                    self.scenery_layer.blit(scenery_img, [x, start_y])
            else:
                self.scenery_layer.blit(scenery_img, [0, start_y])

        pygame.mixer.music.load(map_data['music'])

        self.gravity = map_data['gravity']
        self.terminal_velocity = map_data['terminal-velocity']

        self.completed = False

        self.blocks.add(self.starting_blocks)
        self.enemies.add(self.starting_enemies)
        self.coins.add(self.starting_coins)
        self.powerups.add(self.starting_powerups)
        self.flag.add(self.starting_flag)

        self.active_sprites.add(self.coins, self.enemies, self.powerups)
        self.inactive_sprites.add(self.blocks, self.flag)

        # with this speed up blitting on slower computers?
        for s in self.active_sprites:
            s.image.convert()

        for s in self.inactive_sprites:
            s.image.convert()

        self.inactive_sprites.draw(self.inactive_layer)

        # is converting layers helpful at all?
        self.background_layer.convert()
        self.scenery_layer.convert()
        self.inactive_layer.convert()
        self.active_layer.convert()

    def reset(self):
        self.enemies.add(self.starting_enemies)
        self.coins.add(self.starting_coins)
        self.powerups.add(self.starting_powerups)

        self.active_sprites.add(self.coins, self.enemies, self.powerups)

        for e in self.enemies:
            e.reset()


class Game():

    SPLASH = 0
    START = 1
    PLAYING = 2
    PAUSED = 3
    LEVEL_COMPLETED = 4
    GAME_OVER = 5
    VICTORY = 6

    def __init__(self):
        self.window = pygame.display.set_mode([WIDTH, HEIGHT])
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.done = False
        # Controller
        try:
            self.gamepad = xbox360_controller.Controller(0)
        except:
            self.gamepad = None

        self.reset()

    def start(self):
        self.level = Level(levels[self.current_level])
        self.level.reset()
        self.hero.respawn(self.level)

    def advance(self):
        self.current_level += 1
        self.start()
        self.stage = Game.START

    def reset(self):
        self.hero = Character(alien_images)
        self.current_level = 0
        self.start()
        self.stage = Game.SPLASH

    def display_splash(self, surface):
        line1 = FONT_LG.render(TITLE, 1, DARK_BLUE)
        line2 = FONT_SM.render("Press any key to start.", 1, WHITE)

        x1 = WIDTH / 2 - line1.get_width() / 2
        y1 = HEIGHT / 3 - line1.get_height() / 2

        x2 = WIDTH / 2 - line2.get_width() / 2
        y2 = y1 + line1.get_height() + 16

        surface.blit(line1, (x1, y1))
        surface.blit(line2, (x2, y2))

    def display_message(self, surface, primary_text, secondary_text):
        line1 = FONT_MD.render(primary_text, 1, WHITE)
        line2 = FONT_SM.render(secondary_text, 1, WHITE)

        x1 = WIDTH / 2 - line1.get_width() / 2
        y1 = HEIGHT / 3 - line1.get_height() / 2

        x2 = WIDTH / 2 - line2.get_width() / 2
        y2 = y1 + line1.get_height() + 16

        surface.blit(line1, (x1, y1))
        surface.blit(line2, (x2, y2))

    def display_stats(self, surface):
        global sound_on

        lives_text = FONT_SM.render("Lives: " + str(self.hero.lives), 1, WHITE)
        score_text = FONT_SM.render("Score: " + str(self.hero.score), 1, WHITE)
        lvl_score = FONT_SM.render(self.level.name, 1, WHITE)

        # Music status icon
        if sound_on:
            surface.blit(soundon_img, (32, 128))
        else:
            surface.blit(soundoff_img, (32, 128))

        surface.blit(score_text, (WIDTH - score_text.get_width() - 32, 32))
        surface.blit(lives_text, (32, 64))
        surface.blit(lvl_score, (32, 96))

        # Manages heart counter
        spacing = 32
        curr_max = self.hero.max_hearts * 2
        multi = [i for i in range(1, curr_max, 2)]

        for i in multi:
            surface.blit(heart_empty_img, (spacing * i, 0))

        for i in multi[:self.hero.hearts]:
            surface.blit(heart_img, (spacing * i, 0))

    def process_events(self):
        global sound_on
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.done = True
            if self.gamepad:
                if event.type == pygame.JOYBUTTONDOWN:
                    if self.stage == Game.SPLASH or self.stage == Game.START:
                        self.stage = Game.PLAYING
                        play_music()

                    elif self.stage == Game.PLAYING:
                        if event.button == xbox360_controller.A:
                            self.hero.jump(self.level.blocks)

                    elif self.stage == Game.PAUSED:
                        pass

                    elif self.stage == Game.LEVEL_COMPLETED:
                        self.advance()

                    elif self.stage == Game.VICTORY or self.stage == Game.GAME_OVER:
                        if event.button == xbox360_controller.A:
                            self.reset()
            elif event.type == pygame.KEYDOWN and self.gamepad is None:
                if self.stage == Game.SPLASH or self.stage == Game.START:
                    self.stage = Game.PLAYING
                    play_music()

                elif self.stage == Game.PLAYING:
                    if event.key == JUMP:
                        self.hero.jump(self.level.blocks)
                    if event.key == MUTE:
                        if sound_on:
                            sound_on = False
                            play_music()
                        else:
                            sound_on = True
                            play_music()

                elif self.stage == Game.PAUSED:
                    pass

                elif self.stage == Game.LEVEL_COMPLETED:
                    self.advance()

                elif self.stage == Game.VICTORY or self.stage == Game.GAME_OVER:
                    if event.key == pygame.K_r:
                        self.reset()

        if self.gamepad:
            self.left_x, self.left_y = self.gamepad.get_left_stick()
            self.right_x, self.right_y = self.gamepad.get_right_stick()
            if self.stage == Game.PLAYING:
                if self.left_x < 0:
                    self.hero.move_left()
                elif self.left_x > 0:
                    self.hero.move_right()
                else:
                    self.hero.stop()
        elif self.gamepad is None:
            pressed = pygame.key.get_pressed()
            if self.stage == Game.PLAYING:
                if pressed[LEFT]:
                    self.hero.move_left()
                elif pressed[RIGHT]:
                    self.hero.move_right()
                else:
                    self.hero.stop()

    def update(self):
        if self.stage == Game.PLAYING:
            self.hero.update(self.level)
            self.level.enemies.update(self.level, self.hero)

        if self.level.completed:
            if self.current_level < len(levels) - 1:
                self.stage = Game.LEVEL_COMPLETED
            else:
                self.stage = Game.VICTORY
            pygame.mixer.music.stop()

        elif self.hero.lives == 0:
            self.stage = Game.GAME_OVER
            pygame.mixer.music.stop()

        elif self.hero.hearts == 0:
            self.level.reset()
            self.hero.respawn(self.level)

    def calculate_offset(self):
        x = -1 * self.hero.rect.centerx + WIDTH / 2

        if self.hero.rect.centerx < WIDTH / 2:
            x = 0
        elif self.hero.rect.centerx > self.level.width - WIDTH / 2:
            x = -1 * self.level.width + WIDTH

        return x, 0

    def draw(self):
        offset_x, offset_y = self.calculate_offset()

        self.level.active_layer.fill(TRANSPARENT)
        self.level.active_sprites.draw(self.level.active_layer)

        if self.hero.invincibility % 3 < 2:
            self.level.active_layer.blit(self.hero.image, [self.hero.rect.x, self.hero.rect.y])

        self.window.blit(self.level.background_layer, [offset_x / 3, offset_y])
        self.window.blit(self.level.scenery_layer, [offset_x / 2, offset_y])
        self.window.blit(self.level.inactive_layer, [offset_x, offset_y])
        self.window.blit(self.level.active_layer, [offset_x, offset_y])

        self.display_stats(self.window)

        if self.stage == Game.SPLASH:
            self.display_splash(self.window)
        elif self.stage == Game.START:
            self.display_message(self.window, "Ready?!!!", "Press any key to start.")
        elif self.stage == Game.PAUSED:
            pass
        elif self.stage == Game.LEVEL_COMPLETED:
            self.display_message(self.window, "Level Complete", "Press any key to continue.")
        elif self.stage == Game.VICTORY:
            self.display_message(self.window, "You Win!", "Press 'R' to restart.")
        elif self.stage == Game.GAME_OVER:
            self.display_message(self.window, "Game Over", "Press 'R' to restart.")

        pygame.display.flip()

    def loop(self):
        while not self.done:
            self.process_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)


if __name__ == "__main__":
    game = Game()
    game.start()
    game.loop()
    pygame.quit()
    sys.exit()
