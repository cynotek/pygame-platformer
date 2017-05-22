#!/usr/bin/env python3

import pygame

class Physics():
    def __init(self, gravity, terminal_velocity):
        self.gravity = gravity
        self.terminal_velocity = terminal_velocity

    def apply_gravity(entity):
        entity.vy += self.gravity
        entity.vy = min(self.gravity, self.terminal_velocity)

class Scene():
    def __init__():
        pass

    def process_events(self):
        pass

    def render(self):
        pass

    def update(self):
        pass

class Splash(Scene):
    def __init__():
        pass

class Playing(Scene):
    def __init__():
        pass

class GameOver(Scene):
    def __init__():
        pass

class SceneManager():
    def __init__(self, current_scene):
        self.current_scene = current_scene

    def advance(self, next_scene):
        self.current_scene = next_scene

class Entity(pygame.sprite.Sprite):
    def __init__(self):
        pass

    def is_near(self, hero):
        pass

    def update(self):
        pass

class Hero(Entity):
    def __init__(self):
        pass

    def check_level_boundaries(self, level):
        pass

    def move_and_process_blocks(self, blocks):
        pass

    def process_items(self):
        pass

    def process_enemies(self):
        pass

    def update(self, level):
        level.physics_engine.apply_gravity(self)
        check_level_boundaries(level)
        move_and_process_blocks(level.blocks)
        process_items(level.items)
        process_enemies(level.enemies)

class Enemy(Entity):

    def __init__(self, animation_frames):
        pass

    def reverse(self):
        pass

    def update(self, level, hero):
        pass

class Block(Entity):
    def __init__(self):
        pass

class Item(Entity):
    def __init__(self, value=0):
        value = self.value

    def apply(self, character):
        pass

    def update(self):
        pass

class Level():
    def __init__(self, level_file):
        self.level_file = level_file

    def load(self):
        self.physics_engine = Physics(5, 32)

    def reset(self):
        pass

class MyGame():
    def __init__(self):
        pass

    def run(self):
        pass

if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()
    sys.exit()
