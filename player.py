import pygame
from settings import *
from support import import_folder
from entity import Entity


class Player(Entity):
    def __init__(self, pos, groups, obstacle_sprites, create_weapon, destroy_weapon, create_skill):
        super().__init__(groups)
        self.image = pygame.image.load('../graphics/test/player.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(-6, HITBOX_OFFSET['player'])

        # Graphics setup
        self.import_player_assets()
        self.status = 'down'

        # Movement
        self.isAttacking = False
        self.attacking_CD = 400
        self.attack_time = None

        self.obstacle_sprites = obstacle_sprites

        # Weapon
        self.create_weapon = create_weapon
        self.destroy_weapon = destroy_weapon
        self.weapon_index = 0
        self.weapon = list(weapon_data.keys())[self.weapon_index]
        self.isSwitchingWeapon = False
        self.switching_CD = 200
        self.weapon_switch_time = None

        # Skills
        self.create_skill = create_skill
        self.skill_index = 0
        self.skill = list(skill_data.keys())[self.skill_index]
        self.isSwitchingSkill = False
        self.skill_switch_time = None

        # Stats
        self.stats = {'health': 100, 'energy': 60, 'attack': 10, 'skill': 4, 'speed': 5}
        self.max_stats = {'health': 300, 'energy': 140, 'attack': 20, 'skill': 10, 'speed': 10}
        self.upgrade_cost = {'health': 100, 'energy': 100, 'attack': 100, 'skill': 100, 'speed': 100}
        self.health = self.stats['health']
        self.energy = self.stats['energy']
        self.exp = 500
        self.speed = self.stats['speed']

        # Damage Timer
        self.isInvincible = False
        self.hit_time = None
        self.invincibility_Duration = 500

        # Import a sound
        self.weapon_attack_sound = pygame.mixer.Sound('../audio/sword.wav')
        self.weapon_attack_sound.set_volume(0.4)

    def import_player_assets(self):
        character_path = '../graphics/player/'
        self.animations = {
            'up': [], 'down': [], 'left': [], 'right': [],
            'up_idle': [], 'down_idle': [], 'left_idle': [], 'right_idle': [],
            'up_attack': [], 'down_attack': [], 'left_attack': [], 'right_attack': []
        }

        for animation in self.animations.keys():
            animation_path = character_path + animation
            self.animations[animation] = import_folder(animation_path)

    def input(self):
        if not self.isAttacking:
            keys = pygame.key.get_pressed()
            # Move input
            if keys[pygame.K_UP]:
                self.direction.y = -1
                self.status = 'up'
            elif keys[pygame.K_DOWN]:
                self.direction.y = 1
                self.status = 'down'
            else:
                self.direction.y = 0

            if keys[pygame.K_LEFT]:
                self.direction.x = -1
                self.status = 'left'
            elif keys[pygame.K_RIGHT]:
                self.direction.x = 1
                self.status = 'right'
            else:
                self.direction.x = 0

            # Attack input
            if keys[pygame.K_SPACE]:
                self.isAttacking = True
                self.attack_time = pygame.time.get_ticks()
                self.create_weapon()
                self.weapon_attack_sound.play()

            # Skill input
            if keys[pygame.K_LCTRL]:
                self.isAttacking = True
                self.attack_time = pygame.time.get_ticks()
                style = list(skill_data.keys())[self.skill_index]
                strength = list(skill_data.values())[self.skill_index]['strength'] + self.stats['skill']
                cost = list(skill_data.values())[self.skill_index]['cost']
                self.create_skill(style, strength, cost)

            if keys[pygame.K_q] and not self.isSwitchingWeapon:
                self.isSwitchingWeapon = True
                self.weapon_switch_time = pygame.time.get_ticks()

                if self.weapon_index >= len(list(weapon_data.keys())) - 1:
                    self.weapon_index = 0
                else:
                    self.weapon_index += 1

                self.weapon = list(weapon_data.keys())[self.weapon_index]

            if keys[pygame.K_e] and not self.isSwitchingSkill:
                self.isSwitchingSkill = True
                self.skill_switch_time = pygame.time.get_ticks()

                if self.skill_index >= len(list(skill_data.keys())) - 1:
                    self.skill_index = 0
                else:
                    self.skill_index += 1

                self.skill = list(skill_data.keys())[self.skill_index]

    def get_status(self):
        # Idle status
        if self.direction.x == 0 and self.direction.y == 0:
            if 'idle' not in self.status and 'attack' not in self.status:
                self.status = self.status + '_idle'

        if self.isAttacking:
            self.direction.x = self.direction.y = 0

            if 'attack' not in self.status:
                if 'idle' in self.status:
                    # Overwrite idle
                    self.status = self.status.replace('_idle', '_attack')
                else:
                    self.status = self.status + '_attack'

    def cooldowns(self):
        current_time = pygame.time.get_ticks()
        if self.isAttacking:
            if current_time - self.attack_time >= self.attacking_CD + weapon_data[self.weapon]['cooldown']:
                self.isAttacking = False
                self.status = self.status.replace('_attack', '')
                self.destroy_weapon()

        if self.isSwitchingWeapon:
            if current_time - self.weapon_switch_time >= self.switching_CD:
                self.isSwitchingWeapon = False

        if self.isSwitchingSkill:
            if current_time - self.skill_switch_time >= self.switching_CD:
                self.isSwitchingSkill = False

        if self.isInvincible:
            if current_time - self.hit_time >= self.invincibility_Duration:
                self.isInvincible = False

    def animate(self):
        animation = self.animations[self.status]

        # Loop over frame_index
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0

        # Set the image
        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center=self.hitbox.center)

        # Flicker
        if self.isInvincible:
            alpha = self.wave_value()
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255)

    def get_full_weapon_damage(self):
        base_damage = self.stats['attack']
        weapon_damage = weapon_data[self.weapon]['damage']
        return base_damage + weapon_damage

    def get_full_skill_damage(self):
        base_damage = self.stats['skill']
        skill_damage = skill_data[self.skill]['strength']
        return base_damage + skill_damage

    def get_value_by_index(self, index):
        return list(self.stats.values())[index]

    def get_cost_by_index(self, index):
        return list(self.upgrade_cost.values())[index]

    def energy_recover(self):
        if self.energy < self.stats['energy']:
            self.energy += 0.01 * self.stats['skill']
        else:
            self.energy = self.stats['energy']

    def update(self):
        self.input()
        self.cooldowns()
        self.get_status()
        self.animate()
        self.move(self.stats['speed'])
        self.energy_recover()
