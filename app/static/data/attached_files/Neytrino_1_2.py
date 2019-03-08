import json
import os
import sys
from random import randint, choice
from ctypes import windll

import pygame
from pygame.sprite import Group

pygame.init()
size = width, height = windll.user32.GetSystemMetrics(0), windll.user32.GetSystemMetrics(1)
screen_rect = (0, 0, width, height)
screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
player_sprite = pygame.sprite.Group()
enemies_sprite = pygame.sprite.Group()
bullets_sprite = pygame.sprite.Group()
sparks_sprite = pygame.sprite.Group()
meteorits_sprite = pygame.sprite.Group()
fuels_sprite = pygame.sprite.Group()
upgrades_sprite = pygame.sprite.Group()
raptor_group = pygame.sprite.Group()
fairing_group = pygame.sprite.Group()
raptor_icon_group = pygame.sprite.Group()
fairing_icon_group = pygame.sprite.Group()
gameover_group = pygame.sprite.Group()
screen.fill((0, 0, 0))
fps = 100
PATH_TO_RECORD_FILE = 'record.json'
PATH_TO_START_SCREEN = 'img/start_screen.jpg'
PATH_TO_BUTTON_START_GAME = 'img/button_start_game.png'
PATH_TO_FONS = 'img/fons/'
PATH_TO_ROCKET_SPRITES = 'img/sprites/rockets'
PATH_TO_ENEMIES_SPRITES = 'img/sprites/enemies'
PATH_TO_BULLETS_SPRITES = 'img/sprites/enemies/bullets'
PATH_TO_METEORITES_SPRITES = 'img/sprites/meteorites'
PATH_TO_SPARKS_SPRITE = 'img/sprites/particles/sparks'
PATH_TO_FUEL_SPRITE = 'img/sprites/drops/fuel.png'
PATH_TO_UPGRADE_SPRITE = 'img/sprites/drops/upgrades.png'
PATH_TO_FAIRING_SPRITE = 'img/sprites/drops/titan_fairing.png'
PATH_TO_FAIRING_ICON_SPRITE = 'img/sprites/drops/titan_fairing_icon.png'
PATH_TO_RAPTOR_SPRITE = 'img/sprites/drops/raptor.png'
PATH_TO_RAPTOR_ICON_SPRITE = 'img/sprites/drops/raptor_icon.png'
RAPTOR_SOUND = pygame.mixer.Sound('sounds/raptor.wav')
RAPTOR_SOUND.set_volume(0.4)
FUEL_SOUND = pygame.mixer.Sound('sounds/fuel.wav')
FAIRING_SOUND = pygame.mixer.Sound('sounds/fairing.wav')
FAIRING_SOUND.set_volume(0.5)
UPGRADE_SOUND = pygame.mixer.Sound('sounds/upgrade.wav')
CRASH_SOUND = pygame.mixer.Sound('sounds/crash.wav')
CRASH_SOUND.set_volume(0.3)
BULLET_SOUND = pygame.mixer.Sound('sounds/bullet.wav')
BULLET_SOUND.set_volume(0.1)
BULLET_CRASH_SOUND = pygame.mixer.Sound('sounds/bullet_crash.wav')
BULLET_CRASH_SOUND.set_volume(0.3)
COUNT_SPARCKS = 5
COUNT_ROCKETS = 1
COUNT_ENEMIES = 2
COUNT_BULLETS = 2
COUNT_METEORITES = 3
ROCKET_SPRITES = [[], [], [], []]


def stop_all_sounds():
    RAPTOR_SOUND.stop()
    FUEL_SOUND.stop()
    FAIRING_SOUND.stop()
    UPGRADE_SOUND.stop()
    CRASH_SOUND.stop()
    BULLET_SOUND.stop()
    BULLET_CRASH_SOUND.stop()


def load_image(name, colorkey=None):
    try:
        image = pygame.image.load(name)
        return image
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)


for i in range(1, 14):
    ROCKET_SPRITES[0].append(load_image(PATH_TO_ROCKET_SPRITES + '/1/' + str(i) + '.png'))
    ROCKET_SPRITES[1].append(load_image(PATH_TO_ROCKET_SPRITES + '/2/' + str(i) + '.png'))
    ROCKET_SPRITES[2].append(load_image(PATH_TO_ROCKET_SPRITES + '/3/' + str(i) + '.png'))
    ROCKET_SPRITES[3].append(load_image(PATH_TO_ROCKET_SPRITES + '/4/' + str(i) + '.png'))
BULLET_SPRITE_1 = load_image(PATH_TO_BULLETS_SPRITES + '/1.png')
BULLET_SPRITE_2 = load_image(PATH_TO_BULLETS_SPRITES + '/2.png')
ENEMIES_SPRITE_1 = load_image(PATH_TO_ENEMIES_SPRITES + '/1.png')
ENEMIES_SPRITE_2 = load_image(PATH_TO_ENEMIES_SPRITES + '/2.png')
METEORITES_SPRITE_1 = load_image(PATH_TO_METEORITES_SPRITES + '/1.png')
METEORITES_SPRITE_2 = load_image(PATH_TO_METEORITES_SPRITES + '/2.png')
METEORITES_SPRITE_3 = load_image(PATH_TO_METEORITES_SPRITES + '/3.png')
FUEL_SPRITE = load_image(PATH_TO_FUEL_SPRITE)
UPGRADE_SPRITE = load_image(PATH_TO_UPGRADE_SPRITE)
RAPTOR_SPRITE = load_image(PATH_TO_RAPTOR_SPRITE)
RAPTOR_ICON_SPRITE = load_image(PATH_TO_RAPTOR_ICON_SPRITE)
FAIRING_SPRITE = load_image(PATH_TO_FAIRING_SPRITE)
FAIRING_ICON_SPRITE = load_image(PATH_TO_FAIRING_ICON_SPRITE)


class ButtonStartGame:
    def __init__(self, x, y, img_path):
        self.x = x
        self.y = y
        self.img = pygame.image.load(img_path)

    def render(self):
        screen.blit(self.img, (self.x, self.y))

    def is_clicked(self, event_pos):
        mouse_x, mouse_y = event_pos
        w, h = list(self.img.get_rect())[2:]
        if mouse_x > self.x and mouse_x < self.x + w and mouse_y > self.y and mouse_y < self.y + h:
            return True
        else:
            return False


class Experience:
    def __init__(self, xp, need_xp):
        self.xp = xp
        self.need_xp = need_xp
        self.height = 100
        self.update()

    def update(self):
        if self.xp > 0:
            procent = (self.xp / (self.need_xp / 100)) / 100
            if self.xp <= self.need_xp:
                pygame.draw.rect(screen2, (255, 0, 0),
                                 (10, height - 20, self.height * procent, 10))
            else:
                pygame.draw.rect(screen2, (255, 0, 0),
                                 (10, height - 20, self.height, 10))
            pygame.draw.rect(screen2, (0, 0, 0), (9, height - 21, self.height + 2, 12), 1)
            font = pygame.font.Font(None, 20).render(str(self.xp) + '/' + str(self.need_xp) + ' xp', 1,
                                                     pygame.Color('white'))
        else:
            font = pygame.font.Font(None, 20).render(str(self.xp) + '/' + str(self.need_xp) + ' xp', 1,
                                                     pygame.Color('white'))
            pygame.draw.rect(screen2, (0, 0, 0), (9, height - 21, self.height + 2, 12), 1)
        screen2.blit(font, (120, height - 23))
        screen.blit(screen2, (0, 0))

    def get_xp(self, count):
        self.xp += count

    def get_need_xp(self, new):
        self.need_xp = new
        self.xp = 0


class Score:
    def __init__(self, score):
        self.score = score
        self.update()

    def update(self):
        font = pygame.font.Font(None, 20).render(str(self.score) + ' км', 1, pygame.Color('white'))
        screen2.blit(font, (670, 8))
        screen.blit(screen2, (0, 0))

    def get_score(self, count):
        self.score += count


class Health:
    def __init__(self, health, all_health):
        self.height = 100
        pygame.draw.rect(screen2, (0, 255, 0), (500, 10, self.height, 10))
        pygame.draw.rect(screen2, (0, 0, 0), (499, 9, self.height + 2, 12), 1)
        font = pygame.font.Font(None, 20).render('100 %', 1, pygame.Color('white'))
        screen2.blit(font, (605, 8))
        self.health = health
        self.all_health = all_health
        screen.blit(screen2, (0, 0))

    def update(self):
        if self.health > 0:
            procent = (self.health / (self.all_health / 100)) / 100
            pygame.draw.rect(screen2, (0, 255, 0),
                             (500, 10, self.height * procent, 10))
            pygame.draw.rect(screen2, (0, 0, 0), (499, 9, self.height + 2, 12), 1)
            font = pygame.font.Font(None, 20).render(str(int(procent * 100)) + ' %', 1, pygame.Color('white'))
            screen2.blit(font, (605, 8))
        else:
            pygame.draw.rect(screen2, (0, 0, 0), (499, 4, self.height + 2, 12), 1)
            font = pygame.font.Font(None, 20).render('0 %', 1, pygame.Color('white'))
            screen2.blit(font, (605, 8))

    def take_health(self, count):
        self.health -= count

    def get_health(self, count):
        self.health += count

    def update_all_health(self, new_health):
        self.all_health = new_health
        self.health = self.all_health


class RaptorIcon(pygame.sprite.Sprite):
    def __init__(self, image, time):
        super().__init__(raptor_icon_group)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = 400
        self.rect.y = 5
        self.time = time
        font = pygame.font.Font(None, 20).render(str(self.time), 1, pygame.Color('white'))
        screen2.blit(font, (420, 8))

    def update(self, is_low_time):
        font = pygame.font.Font(None, 20).render(str(self.time), 1, pygame.Color('white'))
        screen2.blit(font, (420, 8))
        if is_low_time:
            self.low_time()
        if self.time <= 0:
            self.kill()

    def low_time(self):
        self.time -= 1


class FairingIcon(pygame.sprite.Sprite):
    def __init__(self, image, count):
        super().__init__(fairing_icon_group)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = 450
        self.rect.y = 5
        self.count = count
        font = pygame.font.Font(None, 20).render(str(self.count), 1, pygame.Color('white'))
        screen2.blit(font, (470, 8))

    def update(self, is_low_count):
        font = pygame.font.Font(None, 20).render(str(self.count), 1, pygame.Color('white'))
        screen2.blit(font, (470, 8))
        if is_low_count:
            self.low_count()
        if self.count <= 0:
            self.kill()

    def low_count(self):
        self.count -= 1


class Background:
    def __init__(self):
        self.fon_img = pygame.image.load(PATH_TO_FONS + 'fon' + str(randint(1, 3)) + '.jpg')
        screen.blit(self.fon_img, (0, 0))
        self.speed = 1
        self.count_iter = 0
        self.DELAY_TABLE = [[70, 50], [60, 40], [50, 30], [40, 20]]
        self.delay = self.DELAY_TABLE[0]

    def get_fon(self):
        return self.fon_img

    def update_level(self):
        self.speed += 1
        self.delay = self.DELAY_TABLE[self.speed - 1]

    def update(self):
        player.get_score(self.speed)
        who_is = randint(1, 3)
        if who_is == 3 and self.count_iter % self.delay[1] == 0:
            Enemy(randint(1, 2), randint(10, width - 200), -120, self.speed)
        elif (who_is == 1 or who_is == 2) and self.count_iter % self.delay[1] == 0:
            Meteorite(randint(1, 3), randint(10, width - 70), -20, self.speed)
        drop = randint(1, 25)
        if drop == 7 and self.count_iter % 50 == 0:
            Fuel(randint(10, width - 50), 0, self.speed)
        if player.is_xp_drop():
            Upgrade(randint(10, width - 60), -10, self.speed)
        if drop == 24 and self.count_iter % 80 == 0:
            Raptor(randint(10, width - 50), -10, self.speed)
        if drop == 3 and self.count_iter % 80 == 0:
            Fairing(randint(10, width - 50), -10, self.speed)
        self.update_enemies()
        self.update_meteorites()
        self.update_sparks()
        self.update_fuels()
        self.update_upgrades()
        self.update_raptor()
        self.update_fairing()
        self.count_iter += 1
        if self.count_iter > 1000:
            self.count_iter = 0

    def update_raptor(self):
        raptor_group.update(False)
        raptor_group.draw(screen2)
        screen.blit(screen2, (0, 0))

    def update_fairing(self):
        fairing_group.update(False)
        fairing_group.draw(screen2)
        screen.blit(screen2, (0, 0))

    def update_enemies(self):
        enemies_sprite.update(False)
        bullets_sprite.update(False)
        enemies_sprite.draw(screen2)
        bullets_sprite.draw(screen2)
        screen.blit(screen2, (0, 0))

    def update_meteorites(self):
        meteorits_sprite.update(False)
        meteorits_sprite.draw(screen2)
        screen.blit(screen2, (0, 0))

    def update_sparks(self):
        sparks_sprite.update()
        sparks_sprite.draw(screen2)
        screen.blit(screen2, (0, 0))

    def update_fuels(self):
        fuels_sprite.update(False)
        fuels_sprite.draw(screen2)
        screen.blit(screen2, (0, 0))

    def update_upgrades(self):
        upgrades_sprite.update(False)
        upgrades_sprite.draw(screen2)
        screen.blit(screen2, (0, 0))


class Drops(pygame.sprite.Sprite):
    def __init__(self, sprite_group, image, x, y, speed):
        super().__init__(sprite_group)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = speed
        self.mask = pygame.mask.from_surface(self.image)

    def is_collidle(self, elem, sound):
        if pygame.sprite.collide_mask(self, elem):
            BULLET_SOUND.stop()
            sound.play()
            self.kill()
            return True
        return False

    def in_screen(self):
        if self.rect.colliderect(screen_rect):
            return True
        else:
            self.kill()
            return False

    def update_speed(self):
        self.speed += 1


class Sparks(pygame.sprite.Sprite):
    def __init__(self, x, y, dx, dy, speed):
        super().__init__(sparks_sprite)
        image = pygame.image.load(PATH_TO_SPARKS_SPRITE + '/' + str(randint(1, COUNT_SPARCKS)) + '.png')
        sparks = [image]
        for scale in (5, 10):
            sparks.append(pygame.transform.scale(sparks[0], (scale, scale)))
        self.image = choice(sparks)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.velocity = [dx, dy]
        self.speed = speed

    def update(self):
        self.velocity[1] += self.speed
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        self.in_screen()

    def in_screen(self):
        if self.rect.y < width:
            return True
        else:
            self.kill()
            return False


class Meteorite(Drops):
    # В этом классе генерируются метеориты и есть функция контроля пересечения метеорита и игрока
    def __init__(self, sprite_random, x, y, speed):
        self.sprite_random = sprite_random
        if self.sprite_random == 1:
            image = METEORITES_SPRITE_1
        elif self.sprite_random == 2:
            image = METEORITES_SPRITE_2
        else:
            image = METEORITES_SPRITE_3
        super().__init__(meteorits_sprite, image, x, y, speed)

    def update(self, is_update_speed):
        self.rect.y += self.speed
        self.in_screen()
        if self.is_collidle(player, CRASH_SOUND):
            for i in range(50):
                nums = range(-6, 10)
                Sparks(self.rect.x, self.rect.y, choice(nums), choice(nums), self.speed)
            player.take_health(300)
        if is_update_speed:
            self.update_speed()


class Enemy(Drops):
    # В этом классе генерируются враги все их функции
    def __init__(self, sprite_random, x, y, speed):
        self.sprite_random = sprite_random
        if self.sprite_random == 1:
            image = ENEMIES_SPRITE_1
        else:
            image = ENEMIES_SPRITE_2
        super().__init__(enemies_sprite, image, x, y, speed)

        self.count_iter = 0
        self.bullet = []
        self.iter_for_bullets = 0

    def update(self, is_update_speed):
        if is_update_speed:
            self.update_speed()
        if player.rocket_level > 2:
            is_gui = True
        else:
            is_gui = False
        if self.count_iter == 1:
            if is_gui:
                if player.rect.x > self.rect.x:
                    self.rect.x += self.speed
                elif player.rect.x < self.rect.x:
                    self.rect.x -= self.speed
            self.rect.y += self.speed
        self.count_iter += 1
        if self.count_iter > 1:
            self.count_iter = 0

        if self.iter_for_bullets % (170 - self.speed * 20) == 0:
            self.shoot()
        if self.is_collidle(player, CRASH_SOUND):
            for i in range(50):
                nums = range(-6, 10)
                Sparks(self.rect.x, self.rect.y, choice(nums), choice(nums), self.speed)
            player.take_health(200)
        self.iter_for_bullets += 1

    def shoot(self):
        y = self.rect.y + 130
        if self.sprite_random == 1:
            x = self.rect.x + 35
        elif self.sprite_random == 2:
            x = self.rect.x
        BULLET_SOUND.play()
        Bullet(self.sprite_random, self.speed * 4, x, y)


class Bullet(Drops):
    # В этом классе генерируются пули врагов и отслеживается их пересечение с игроком
    def __init__(self, sprite_path, speed, x, y):
        if sprite_path == 1:
            image = BULLET_SPRITE_1
        elif sprite_path == 2:
            image = BULLET_SPRITE_2
        super().__init__(bullets_sprite, image, x, y, speed)

    def update(self, is_update_speed):
        self.in_screen()
        if is_update_speed:
            self.update_speed()
        if self.is_collidle(player, BULLET_CRASH_SOUND):
            for i in range(50):
                nums = range(-6, 10)
                Sparks(self.rect.x, self.rect.y, choice(nums), choice(nums), self.speed)
            player.take_health(200)

        self.rect.y += self.speed


class Player(pygame.sprite.Sprite):
    # Это класс игрока. В нем отслеживается его уровень, рекорд, скорость, здоровье,
    # подобранный дроп и все, связанное с ракетой
    def __init__(self, sprite_path, x, y):
        super().__init__(player_sprite)
        self.image = pygame.image.load(sprite_path)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.path_ro_sprite = sprite_path
        self.rocket_level = 1
        self.health = 1000
        self.all_health = 1000
        self.sprite_number = 1
        self.rect.x = x
        self.speed = 10
        self.score = 0
        self.height = 200
        self.score_label = Score(self.score)
        self.rect.y = y
        self.line_health = Health(self.health, self.all_health)
        self.XP_TABLE = [1000, 5000, 15000, 30000]
        # self.XP_TABLE = [0, 100, 100, 100]
        self.xp = 0
        self.need_xp = self.XP_TABLE[0]
        self.xp_label = Experience(self.xp, self.need_xp)
        self.xp_drop = 0
        self.is_game = True
        self.HEIGHT_TABLE = [110, 142, 142, 166]
        self.HEALTH_TABLE = [600, 1200, 2000, 3000]
        self.SPEED_TABLE = [10, 15, 20, 25]
        self.raptor_time = 0
        self.frames = 0
        self.is_raptor = False
        self.titan_damage = 0

    def update(self):
        if self.sprite_number < 13:
            self.sprite_number += 1
        else:
            self.sprite_number = 1
        self.image = ROCKET_SPRITES[self.rocket_level - 1][self.sprite_number - 1]
        player_sprite.draw(screen2)
        self.line_health.update()
        self.score_label.update()
        self.xp_label.update()
        if self.is_raptor:
            self.frames += 1
            if self.frames % (FPS // 2) == 0:
                self.raptor_time -= 1
                raptor_icon_group.update(True)
            if self.raptor_time <= 0:
                self.is_raptor = False
                self.speed -= 5
            raptor_icon_group.update(False)
            raptor_icon_group.draw(screen2)
        fairing_icon_group.update(False)
        fairing_icon_group.draw(screen2)
        screen.blit(screen2, (0, 0))

    def move(self, key):
        w, h = list(self.image.get_rect())[2:]
        if key[276] == 1:
            if self.rect.x > 5:
                self.rect.x -= self.speed
            else:
                self.rect.x = width - w
        if key[275] == 1:
            if self.rect.x < width - w:
                self.rect.x += self.speed
            else:
                self.rect.x = 5
        if key[273] == 1 and self.rect.y > 20:
            self.rect.y -= self.speed
        if key[274] == 1 and self.rect.y < height - self.HEIGHT_TABLE[self.rocket_level - 1]:
            self.rect.y += self.speed

    def take_health(self, count):
        if self.titan_damage != 0:
            self.titan_damage -= 1
            fairing_icon_group.update(True)
            return
        self.health -= count
        self.line_health.take_health(count)
        print(self.health)
        if self.health <= 0:
            print('Вы проиграли')
            if self.is_game:
                self.is_game = False
                data = json.loads(open(PATH_TO_RECORD_FILE).read())
                if int(data['record'][0]) < self.score:
                    os.remove(PATH_TO_RECORD_FILE)
                    data['record'] = [str(self.score)]
                    data = open(PATH_TO_RECORD_FILE, mode='w').write(json.dumps(data, ensure_ascii=False))

    def get_health(self, count):

        if self.health + count <= self.all_health:
            self.line_health.get_health(count)
            self.health += count
        else:
            self.line_health.get_health(self.all_health - self.health)
            self.health = self.all_health
        print(self.health)

    def get_score(self, count):
        self.score += count
        self.xp_drop += count
        self.score_label.get_score(count)

    def return_score(self):
        return self.score

    def update_xp(self, count):
        self.xp += count
        if self.xp < self.need_xp:
            self.xp_label.get_xp(count)
        else:
            self.xp = 0
            if self.rocket_level < 4:
                self.rocket_level += 1
                self.need_xp = self.XP_TABLE[self.rocket_level - 1]
                self.xp_label.get_need_xp(self.need_xp)
                self.update_sprite()
                self.update_health()
                self.update_speed()

    def update_sprite(self):
        self.image = ROCKET_SPRITES[self.rocket_level - 1][self.sprite_number - 1]
        x, y = self.rect.x, self.rect.y
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

    def update_health(self):
        self.all_health = self.HEALTH_TABLE[self.rocket_level - 1]
        self.health = self.all_health
        self.line_health.update_all_health(self.all_health)
        print(self.health)

    def update_speed(self):
        self.speed = self.SPEED_TABLE[self.rocket_level - 1]
        background.update_level()
        enemies_sprite.update(True)
        meteorits_sprite.update(True)
        fuels_sprite.update(True)
        upgrades_sprite.update(True)
        bullets_sprite.update(True)
        raptor_group.update(True)
        fairing_group.update(True)

    def is_xp_drop(self):  # Проверяет, пора ли дропать запчасти
        if self.xp_drop > 500 and self.rocket_level < 4:
            self.xp_drop = 0
            return True
        return False

    def update_speed_raptor(self):  # Вызывается при собирании дропа Raptor
        self.is_raptor = True
        if self.raptor_time <= 0:
            self.speed += 5
        self.raptor_time += 20
        raptor_icon_group.empty()
        RaptorIcon(RAPTOR_ICON_SPRITE, self.raptor_time)

    def get_titan_fairing(self):  # Вызывается при собирании дропа Fairing
        self.titan_damage += 2
        fairing_icon_group.empty()
        FairingIcon(FAIRING_ICON_SPRITE, self.titan_damage)


class Raptor(Drops):
    # В этом классе создается дроп - двигатель раптор, котороый увеличивает скорость на 50 %
    #  и отслеживается время его действия
    def __init__(self, x, y, speed):
        image = RAPTOR_SPRITE
        super().__init__(raptor_group, image, x, y, speed)

    def update(self, is_update_speed):
        if is_update_speed:
            self.update_speed()
        self.rect.y += self.speed
        self.in_screen()
        if self.is_collidle(player, RAPTOR_SOUND):
            player.update_speed_raptor()


class Fairing(Drops):
    # В этом классе создается дроп - титановый обтекатель, который позволяет ракете выдержать 3 удара
    # и отслеживается его состояние
    def __init__(self, x, y, speed):
        image = FAIRING_SPRITE
        super().__init__(fairing_group, image, x, y, speed)

    def update(self, is_update_speed):
        if is_update_speed:
            self.update_speed()
        self.rect.y += self.speed
        self.in_screen()
        if self.is_collidle(player, FAIRING_SOUND):
            player.get_titan_fairing()


class Fuel(Drops):
    # В этом классе создается дроп - топливо, которое повышает здоровье игрока на 20%.
    def __init__(self, x, y, speed):
        image = FUEL_SPRITE
        super().__init__(fuels_sprite, image, x, y, speed)

    def update(self, is_update_speed):
        if is_update_speed:
            self.update_speed()
        self.rect.y += self.speed
        self.in_screen()
        if self.is_collidle(player, FUEL_SOUND):
            player.get_health(300)


class Upgrade(Drops):
    # В этом классе создается дроп - запчасии. Они увеличивают опыт игрока и с помощью них игрок сменяет ракеты,
    # когда накопит нужное количество опыта.
    def __init__(self, x, y, speed):
        image = UPGRADE_SPRITE
        super().__init__(upgrades_sprite, image, x, y, speed)

    def update(self, is_update_speed):
        if is_update_speed:
            self.update_speed()
        self.rect.y += self.speed
        self.in_screen()
        if self.is_collidle(player, UPGRADE_SOUND):
            player.update_xp(100)


def start_screen():
    record = json.loads(open(PATH_TO_RECORD_FILE).read())['record'][-1]
    record = 'Ваш рекорд: ' + record + ' км'
    background = pygame.image.load(PATH_TO_START_SCREEN)
    screen.blit(background, (0, 0))
    font = pygame.font.Font(None, 90).render(record, 1, pygame.Color('white'))
    screen.blit(font, (10, height-100))
    button_pos = (584, 443)
    button = ButtonStartGame(button_pos[0], button_pos[1], PATH_TO_BUTTON_START_GAME)
    button.render()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONUP:
                if button.is_clicked(event.pos):
                    return
            if event.type == pygame.KEYDOWN:
                if event.key == 27:
                    sys.exit()
        pygame.display.flip()


class Gameover(pygame.sprite.Sprite):
    def __init__(self, img):
        super().__init__(gameover_group)
        self.image = img
        self.rect = self.image.get_rect()
        self.scx = 810
        self.scy = 455

    def update(self, img):
        self.image = img


start_screen()

running = True
background = Background()
screen2 = pygame.Surface(screen.get_size())
player = Player(PATH_TO_ROCKET_SPRITES + '/1/1.png', 500, 700)
clock = pygame.time.Clock()
FPS = 60
gameover = Gameover(load_image('img/fons/gameover.jpg'))
count = 0
MUSICS = ['space_oddity.mp3', 'life_on_mars.mp3', 'starman.mp3', 'under_pressure.mp3']
pygame.mixer.init()
gameover_sound = pygame.mixer.Sound('sounds/gameover.wav')
pygame.mixer.music.load('sounds/' + MUSICS[randint(0, 3)])
pygame.mixer.music.set_volume(0.1)
pygame.mixer.music.play(-1)
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == 27:
                player.take_health(10000)
                sys.exit()
    player.move(pygame.key.get_pressed())

    clock.tick(FPS)
    if player.is_game:
        screen2.blit(background.get_fon(), (0, 0))
        background.update()
        player.update()
    else:
        if count == 0:
            pygame.mixer.music.stop()
            stop_all_sounds()
            gameover_sound.play()
            clock.tick(1)
        count += 1
        if count == 300:
            gameover_group.update(load_image('img/fons/gameover2.jpg'))
        if count == 750:
            sys.exit()
        gameover_group.draw(screen2)
        screen.blit(screen2, (0, 0))

    pygame.display.flip()
