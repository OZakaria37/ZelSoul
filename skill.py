import pygame
from settings import *
from random import randint


class SkillPlayer():
    def __init__(self, animation_player):
        self.animation_player = animation_player
        self.sounds = {
            'heal': pygame.mixer.Sound('../audio/heal.wav'),
            'flame': pygame.mixer.Sound('../audio/fire.wav')
        }

    def heal(self, player, strength, cost, sprite_groups):
        if player.energy >= cost:
            self.sounds['heal'].play()
            player.health += strength
            player.energy -= cost
            if player.health > player.stats['health']:
                player.health = player.stats['health']
            self.animation_player.create_particles('aura', player.rect.center, sprite_groups)
            self.animation_player.create_particles('heal', player.rect.center + pygame.math.Vector2(0, -60), sprite_groups)

    def flame(self, player, cost, sprite_groups):
        if player.energy >= cost:
            player.energy -= cost
            self.sounds['flame'].play()
            player_direction = player.status.split('_')[0]

            if player_direction == 'right': direction = pygame.math.Vector2(1, 0)
            elif player_direction == 'left': direction = pygame.math.Vector2(-1, 0)
            elif player_direction == 'up': direction = pygame.math.Vector2(0, -1)
            else: direction = pygame.math.Vector2(0, 1)

            for i in range(1, 6):
                if direction.x:  # Horizontal
                    offset_x = (direction.x * i) * TILESIZE
                    x = player.rect.centerx + offset_x + randint(-TILESIZE // 3, TILESIZE // 3)
                    y = player.rect.centery + randint(-TILESIZE // 3, TILESIZE // 3)
                    self.animation_player.create_particles('flame', (x, y), sprite_groups)
                else:  # Vertical
                    offset_y = (direction.y * i) * TILESIZE
                    x = player.rect.centerx + randint(-TILESIZE // 3, TILESIZE // 3)
                    y = player.rect.centery + offset_y + randint(-TILESIZE // 3, TILESIZE // 3)
                    self.animation_player.create_particles('flame', (x, y), sprite_groups)