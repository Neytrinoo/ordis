import pygame
import random
import numpy
import json
import sys
from record import *


def parse(s):
    f = json.load(open(s))
    lines = f['layers'][1]['data']
    lines = numpy.array(lines)
    lines.resize(f['layers'][1]['height'], f['layers'][1]['width'])
    return list(lines)


def change_map(mapp):
    global main_arr, cur_map
    main_arr = mapp[1]
    cur_map = mapp


pygame.init()
WHITE, GREEN, BLUE, RED, DARKBLUE, ORANGE = (255, 255, 255), (0, 255, 0), (0, 0, 255), (255, 0, 0), (39, 45, 77), (
    250, 113, 36)
CELL_SIZE = 32
N_MAPS = 3
GRAVITY = 0.1
PAUSE, MUTE1, MUTE2, HEALTH, PARTICLES = pygame.image.load('buttons/pausew.png'), pygame.image.load(
    'buttons/mute1w.png'), pygame.image.load(
    'buttons/mute2w.png'), pygame.image.load('img_res/health.png'), pygame.transform.scale(
    pygame.image.load('img_res/particles.png'), (64, 64))
SOUNDTRACK, PISTOL, OUTOFAMMO = 'music/soundtrack3.wav', 'music/pistol2.ogg', 'music/outofammo.ogg'
MAPS = [[pygame.image.load('map/map{}.png'.format(str(i))), parse('map/map{}.json'.format(str(i)))] for i in
        range(1, N_MAPS + 1)]
frequency = 6
AIM = pygame.image.load('img_res/aim1w.png')
MAIN_FONT = 'fonts/6551.ttf'
CURSOR_BIG, CURSOR_SMALL = (40, 40), (30, 30)


class Background:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.rep = False
        self.do_again = True
        self.next_map = None

    def move_cam(self, d):
        if self.x > -(len(main_arr[0]) * CELL_SIZE - WIDTH):
            self.x -= d
        elif -(len(main_arr[0]) * CELL_SIZE - WIDTH) + 100 >= self.x > -(len(main_arr[0]) * CELL_SIZE):
            self.x -= d
            self.rep = True
            if self.do_again:
                self.next_map = random.choice(MAPS)
                self.do_again = False
        else:
            self.x += len(main_arr[0]) * CELL_SIZE
            self.x = 0
            change_map(self.next_map)
            self.img = self.next_map[0]
            self.rep = False
            self.do_again = True
            gui.start_new_level()

    def render(self):
        screen.blit(self.img, (self.x, self.y))
        if self.rep:
            screen.blit(self.next_map[0], (self.x + len(main_arr[0]) * CELL_SIZE, self.y))

    def start_new_level(self):
        global cam_speed, frequency
        self.rep = False
        self.x = 0
        for i in all_sprites:
            if isinstance(i, Zombie):
                gui.erase(i)
                all_sprites.remove(i)
        frequency = spawn_zombies(all_sprites, frequency)
        if cam_speed < 6:
            cam_speed += 0.6
        gui.spawn_medkits()
        level_counter.add()
        level_counter.show()


class Inscription:
    def __init__(self, x=None, y=None, text='', time_limit=0, font=50):
        self.text = text
        self.font = pygame.font.Font(MAIN_FONT, 50)
        self.x = x
        self.y = y
        if time_limit == 0:
            self.islimited = False
        else:
            self.time_limit = time_limit
            self.islimited = True
            self.time_left = 0

    def render(self):
        if self.islimited:
            if self.time_left == 0:
                rendtext = ''
            else:
                rendtext = self.text
        else:
            rendtext = self.text
        d = self.font.render(rendtext, True, WHITE)
        x = self.x if self.x is not None else WIDTH // 2 - d.get_rect().width // 2 + 5
        y = self.y if self.y is not None else 0
        screen.blit(d, (x, y))

    def update(self):
        if self.islimited:
            self.time_left = max(0, self.time_left - 1)

    def show(self):
        if self.islimited:
            self.time_left = self.time_limit


class Counter(Inscription):
    def __init__(self, x=None, y=None, font=50, start=0, text=None, time_limit=0):
        self.cnt = start
        self.rend = text
        self.text = self.rend + str(self.cnt)
        super().__init__(x=x, y=y, text=self.text, font=font, time_limit=time_limit)

    def add(self):
        self.cnt += 1
        self.text = self.rend + str(self.cnt)


class GUI:
    def __init__(self):
        self.elements = []

    def add_element(self, element):
        self.elements.append(element)

    def render(self, surface):
        for element in self.elements:
            render = getattr(element, "render", None)
            if callable(render):
                element.render()

    def update(self):
        for element in self.elements:
            update = getattr(element, "update", None)
            if callable(update):
                element.update()

    def get_event(self, event):
        for element in self.elements:
            get_event = getattr(element, "get_event", None)
            if callable(get_event):
                element.get_event(event)

    def move_cam(self, d):
        for element in self.elements:
            move_cam = getattr(element, "move_cam", None)
            if callable(move_cam):
                element.move_cam(d)

    def move(self):
        for element in self.elements:
            move = getattr(element, "move", None)
            if callable(move):
                element.move()

    def erase(self, x):
        for i in range(len(self.elements)):
            if self.elements[i] is x:
                self.elements.pop(i)
                break

    def start_new_level(self):
        for element in self.elements:
            start_new_level = getattr(element, "start_new_level", None)
            if callable(start_new_level):
                element.start_new_level()

    def spawn_medkits(self):
        for i in range(len(main_arr[0])):
            if random.randrange(0, 100) <= 1:
                gui.add_element(MedKit(i, find_y_position(i), all_sprites))


class Label:
    def __init__(self, rect, text, text_color=DARKBLUE, background_color=pygame.Color('white')):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.bgcolor = background_color
        self.font_color = text_color
        # Рассчитываем размер шрифта в зависимости от высоты
        self.font = pygame.font.Font(MAIN_FONT, self.rect.height - 15)
        self.rendered_text = None
        self.rendered_rect = None

    def render(self, surface):
        if self.bgcolor != -1:
            surface.fill(self.bgcolor, self.rect)
        self.rendered_text = self.font.render(self.text, 1, self.font_color)
        self.rendered_rect = self.rendered_text.get_rect(x=self.rect.x + 2, centery=self.rect.centery)
        # выводим текст
        surface.blit(self.rendered_text, self.rendered_rect)


class Button(Label):
    def __init__(self, rect, text):
        super().__init__(rect, text)
        self.bgcolor = ORANGE
        self.pressed = False

    def render(self, surface):

        if not self.pressed:
            surface.fill(self.bgcolor, self.rect)
            self.rendered_text = self.font.render(self.text, 1, self.font_color)
            self.rendered_rect = self.rendered_text.get_rect(center=self.rect.center)
        else:
            surface.fill(self.font_color, self.rect)
            self.rendered_text = self.font.render(self.text, 1, self.bgcolor)
            self.rendered_rect = self.rendered_text.get_rect(center=self.rect.center)

        surface.blit(self.rendered_text, self.rendered_rect)

    def get_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.pressed = True
                return False
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.pressed:
            self.pressed = False
            return True
        elif event.type == pygame.MOUSEMOTION:
            if self.rect.collidepoint(event.pos):
                self.font_color = WHITE
            if not self.rect.collidepoint(event.pos):
                self.font_color = DARKBLUE

        return False


class Health:
    def __init__(self):
        self.health = 100
        self.x = 10
        self.y = 40
        self.h = 50

    def render(self):
        pygame.draw.rect(screen, GREEN, (self.x, self.y, self.health, self.h))
        pygame.draw.rect(screen, WHITE, (self.x, self.y, 100, self.h), 3)

    def damage(self):
        global running
        if self.health - 5 > 0:
            self.health -= 5
        else:
            self.health = 0
            running = False
        pass

    def heal(self):
        extra = random.choice([5, 10, 20, 25])
        self.health = min(100, self.health + extra)


class Gun:
    def __init__(self):
        self.health = 100
        self.x = 120
        self.y = 40
        self.h = 50
        self.reload = True

    def render(self):
        pygame.draw.rect(screen, BLUE if self.reload else RED,
                         (self.x, self.y, self.health, self.h))
        pygame.draw.rect(screen, WHITE, (self.x, self.y, 100, self.h), 3)

    def damage(self):
        if self.health - 20 >= 0:
            self.health -= 20
            if self.health < 10:
                self.health = 0
                self.reload = False
        else:
            self.health = 0
            self.reload = False

    def update(self):
        if self.health + 1 < 101:
            self.health += 1
        else:
            self.reload = True


class Buttons(pygame.sprite.Group):
    def __init__(self):
        pygame.sprite.Group.__init__(self)

    def apply_event(self, event):
        for sprite in self:
            sprite.apply_event(event)


class Pause(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.pause = False
        self.image = PAUSE
        self.image = pygame.transform.scale(self.image, (50, 30))
        self.x, self.y = WIDTH - 115, 47
        self.rect = self.image.get_rect(x=self.x, y=self.y)

    def apply_event(self, event):
        if ((event.type == pygame.MOUSEBUTTONDOWN and event.button == 1) and self.rect.collidepoint(
                event.pos)) or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            self.pause = not self.pause


class Mute(pygame.sprite.Sprite):
    d = {False: MUTE1, True: MUTE2}

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.mute = False
        self.image = self.d[self.mute]
        self.image = pygame.transform.scale(self.image, (40, 40))
        self.x, self.y = WIDTH - 50, 43
        self.rect = self.image.get_rect(x=self.x, y=self.y)

    def apply_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(
                event.pos):
            self.mute = not self.mute
            self.image = self.d[self.mute]
            self.image = pygame.transform.scale(self.image, (40, 40))


class Zombie(pygame.sprite.Sprite):
    def __init__(self, x, y, group):
        super().__init__(group)
        self.x = x
        self.y = y
        self.d = random.choice([0.1, -0.1])
        # self.image = pygame.image.load(
        #    'appear/appear_{}.png'.format(1))
        self.image = pygame.Surface((0, 0))
        # self.rect = self.image.get_rect()
        self.rect = pygame.image.load('appear/appear_{}.png'.format(1)).get_rect()
        self.rect.x = (self.x - 1) * CELL_SIZE
        self.rect.y = (self.y - 1) * CELL_SIZE - 16
        self.moving = -(CELL_SIZE // 2)
        self.sprite_num = 0
        self.stage = -1
        self.damage = True
        self.spawn_x = random.randint(WIDTH // 2, WIDTH)

    def move_cam(self, d):
        self.moving -= d
        self.rect.x = self.x * CELL_SIZE + self.moving

    def move(self):
        if self.stage == -1:
            if 0 <= self.rect.x <= self.spawn_x:
                self.stage += 1
                roar = pygame.mixer.Sound('music/brains%d.wav' % (random.randint(1, 3)))
                roar.set_volume(0.6)
                roar.play()
                if mute.mute:
                    roar.set_volume(0)
        if self.stage == 0:
            self.sprite_num += 1
            if self.sprite_num == 12:
                self.stage += 1
                self.sprite_num = 1
                self.rect.y -= 16
                return
            self.image = pygame.image.load(
                'appear/appear_{}.png'.format(self.sprite_num))
        elif self.stage == 1:
            self.d *= random.choice([1] * 99 + [-1])

            if self.x + self.d <= 0:
                self.d *= -1
                return

            if step_able(self):
                self.x += self.d

                self.rect.x = self.x * CELL_SIZE + self.moving
                if self.rect.x < 0 and self.damage:
                    health.damage()
                    self.damage = False
                if self.rect.x > 0:
                    self.damage = True

                if self.rect.x < -50:
                    all_sprites.remove(self)
                    gui.erase(self)
                    del self

                else:
                    self.sprite_num = (self.sprite_num + 1) % 10 + 1
                    self.image = pygame.image.load(
                        'walk/go_{}_r.png'.format(self.sprite_num))
                    if self.d < 0:
                        self.image = pygame.transform.flip(self.image, True, False)


            else:
                self.d *= -1
        elif self.stage == 2:
            self.sprite_num += 1
            if self.sprite_num == 10:
                all_sprites.remove(self)
                gui.erase(self)
                del self
            else:
                self.image = pygame.image.load(
                    'die/die_{}_r.png'.format(self.sprite_num))
                if self.d < 0:
                    self.image = pygame.transform.flip(self.image, True, False)

    def get_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(
                event.pos) and self.stage == 1 and gun.reload:
            self.stage = 2
            self.sprite_num = 0
            roar = pygame.mixer.Sound('music/dead_sound%d.wav' % (random.randint(1, 3)))
            roar.set_volume(0.6)
            roar.play()
            if mute.mute:
                roar.stop()
            x, y = self.rect.topleft
            self.rect = pygame.image.load(
                'die/die_1_r.png').get_rect()
            self.rect.x = x
            self.rect.y = ((self.y + 1) * CELL_SIZE) - self.rect.height
            counter.add()


class MedKit(pygame.sprite.Sprite):
    def __init__(self, x, y, gr):
        super().__init__(gr)
        self.x = x * CELL_SIZE
        self.y = y * CELL_SIZE
        self.image = HEALTH
        self.image = pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE))
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x, self.y)
        self.moving = 0

    def get_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(
                event.pos):
            create_particles(event.pos)
            health.heal()
            all_sprites.remove(self)
            gui.erase(self)
            del self

    def move_cam(self, d):
        self.moving -= d

    def update(self):
        if self.rect.x + CELL_SIZE > 0:
            self.rect.x = self.x + self.moving
        else:
            gui.erase(self)
            all_sprites.remove(self)


class Particle(pygame.sprite.Sprite):
    # сгенерируем частицы разного размера
    fire = [PARTICLES]
    for scale in (4, 8, 16, CELL_SIZE):
        fire.append(pygame.transform.scale(fire[0], (scale, scale)))

    def __init__(self, pos, dx, dy):
        super().__init__(all_sprites)
        self.image = random.choice(self.fire)
        self.rect = self.image.get_rect()

        # у каждой частицы своя скорость - это вектор
        self.velocity = [dx, dy]
        # и свои координаты
        self.rect.x, self.rect.y = pos

        # гравитация будет одинаковой
        self.gravity = GRAVITY

    def update(self):
        # применяем гравитационный эффект:
        # движение с ускорением под действием гравитации
        self.velocity[1] += self.gravity
        # перемещаем частицу
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        # убиваем, если частица ушла за экран
        if not self.rect.colliderect(screen_rect):
            self.kill()


def step_able(z):
    f0 = int(z.x + z.d) + 1 < len(main_arr[0])
    if not f0:
        return False
    f1 = main_arr[z.y + 1][int(z.x + z.d)] not in [0] and main_arr[z.y + 1][int(z.x + z.d) + 1] not in [0]
    f2 = main_arr[z.y][int(z.x + z.d)] in [0] and main_arr[z.y][int(z.x + z.d) + 1] in [0]
    f3 = main_arr[z.y - 1][int(z.x + z.d)] in [0] and main_arr[z.y - 1][int(z.x + z.d) + 1] in [0]
    return f1 and f2 and f3


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    font = pygame.font.Font(MAIN_FONT, 50)
    img = pygame.image.load('img_res/start_screen2.png')
    best_score = get_result('record.txt')
    button_play = Button((WIDTH // 2 - 100, HEIGHT // 2 - 15, 200, 50), 'PLAY')
    button_exit = Button((WIDTH // 2 - 100, HEIGHT // 2 + 45, 200, 50), 'EXIT')
    rendered_text = font.render('BEST SCORE: ' + str(best_score), 1, WHITE)
    rendered_rect = rendered_text.get_rect(center=pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 140, 200, 50).center)
    screen.blit(img, (0, 0))
    while True:
        if mute.mute:
            soundtrack.set_volume(0)
        else:
            soundtrack.set_volume(0.4)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if button_play.get_event(event):
                return
            elif button_exit.get_event(event):
                terminate()

            buttons.apply_event(event)
        screen.blit(img, (0, 0))
        button_play.render(screen)
        button_exit.render(screen)
        buttons.draw(screen)
        screen.blit(rendered_text, rendered_rect)
        pygame.display.flip()
        clock.tick(30)


def game_over_screen(result):
    best_score = get_result('record.txt')
    game_result = result
    font = pygame.font.Font(MAIN_FONT, 50)
    if game_result > best_score:
        set_result('record.txt', game_result)
        best_score_text = 'NEW RECORD!'
    else:
        best_score_text = 'BEST SCORE: %d' % best_score
    game_result_text = 'YOUR SCORE: %d' % game_result
    img = pygame.image.load('img_res/game_over.png')
    button_play = Button((WIDTH // 2 - 110, HEIGHT // 2 - 20, 220, 50), 'PLAY AGAIN')
    button_exit = Button((WIDTH // 2 - 110, HEIGHT // 2 + 40, 220, 50), 'EXIT')
    screen.blit(img, (0, 0))

    rendered_text1 = font.render(best_score_text, 1, WHITE)
    rendered_rect1 = rendered_text1.get_rect(center=pygame.Rect(WIDTH // 2 - 100, 200, 200, 50).center)

    rendered_text2 = font.render(game_result_text, 1, WHITE)
    rendered_rect2 = rendered_text2.get_rect(center=pygame.Rect(WIDTH // 2 - 100, 250, 200, 50).center)

    screen.blit(img, (0, 0))
    while True:
        if mute.mute:
            soundtrack.set_volume(0)
        else:
            soundtrack.set_volume(0.4)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if button_play.get_event(event):
                return
            elif button_exit.get_event(event):
                terminate()

            buttons.apply_event(event)
        screen.blit(img, (0, 0))
        button_play.render(screen)
        button_exit.render(screen)
        buttons.draw(screen)
        screen.blit(rendered_text1, rendered_rect1)
        screen.blit(rendered_text2, rendered_rect2)
        pygame.display.flip()
        clock.tick(30)


def find_y_position(g):
    cur_last = 0
    ans = []
    for j in range(1, len(main_arr)):
        if main_arr[j][g] != 0:
            if (j - cur_last - 1) >= 3:
                ans.append(j - 1)
                cur_last = j
            else:
                cur_last = j
    return random.choice(ans)


def spawn_zombies(sprite_group, freq):
    for i in range(10, len(main_arr[0]), int(freq)):
        y = find_y_position(i)
        if y is None:
            continue
        gui.add_element(Zombie(i, y, sprite_group))
    if freq > 4:
        freq -= 1
    return freq


def create_particles(position):
    # количество создаваемых частиц
    particle_count = 20
    # возможные скорости
    numbers = range(-10, 10)
    for _ in range(particle_count):
        Particle(position, random.choice(numbers), random.choice(numbers))


cur_map = random.choice(MAPS)
main_arr = cur_map[1]
size = WIDTH, HEIGHT = 700, (len(main_arr) * CELL_SIZE)
screen = pygame.display.set_mode(size)
pygame.display.set_caption('Zombie Shooting Range')
pygame.display.set_icon(pygame.image.load('img_res/icon.png'))
clock = pygame.time.Clock()
mute = Mute()
buttons = Buttons()
buttons.add(mute)
soundtrack = pygame.mixer.Sound(SOUNDTRACK)
# Soundtrack by  Matthew Pablo http://www.matthewpablo.com/contact
soundtrack.play(loops=-1)
start_screen()

while True:

    cam_speed, current_x = 2, 0
    gui = GUI()
    health = Health()
    gun = Gun()

    bg = Background(0, 0, cur_map[0])
    counter = Counter(x=None, y=43, font=50, start=0, text='Score: ')
    gui.add_element(bg)
    gui.add_element(counter)
    gui.add_element(health)
    gui.add_element(gun)
    pause = Pause()

    buttons.add(pause)
    pygame.mixer.init()

    level_counter = Counter(10, 100, 50, 1, 'Level ', 100)
    gui.add_element(level_counter)
    level_counter.show()

    all_sprites = pygame.sprite.Group()
    frequency = spawn_zombies(all_sprites, frequency)
    gui.spawn_medkits()

    screen_rect = (0, 0, WIDTH, HEIGHT)
    cursor = pygame.transform.scale(AIM, CURSOR_BIG)
    pygame.mixer.init()
    flag = False
    running = True
    soundtrack.set_volume(0.4)
    while running:
        if mute.mute:
            soundtrack.set_volume(0)
        else:
            soundtrack.set_volume(0.4)
        screen.fill(WHITE)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if counter.cnt > get_result('record.txt'):
                    set_result('record.txt', counter.cnt)
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not pause.rect.collidepoint(event.pos) and not pause.pause and not mute.rect.collidepoint(event.pos):
                    if gun.reload:
                        gun.damage()
                        cursor = pygame.transform.scale(cursor, CURSOR_SMALL)
                        snd = pygame.mixer.Sound(PISTOL)
                        snd.set_volume(0.2)
                        if not mute.mute:
                            snd.play()
                    else:
                        snd = pygame.mixer.Sound(OUTOFAMMO)
                        snd.set_volume(0.6)
                        if not mute.mute:
                            snd.play()
            elif event.type == pygame.MOUSEBUTTONUP:
                if not pause.rect.collidepoint(event.pos) and not pause.pause:
                    cursor = pygame.transform.scale(AIM, CURSOR_BIG)
            if not pause.pause:
                gui.get_event(event)
                if not health.health:
                    running = False
            buttons.apply_event(event)
            flag = pygame.mouse.get_focused()
            x, y = pygame.mouse.get_pos()

        pygame.mouse.set_visible(False)
        if not pause.pause:
            gui.move_cam(cam_speed)
            current_x += cam_speed
            gui.move()
            gui.update()
        gui.render(screen)
        buttons.draw(screen)
        all_sprites.update()
        all_sprites.draw(screen)
        if flag:
            c = cursor.get_rect().width
            screen.blit(cursor, (x - c // 2, y - c // 2))

        pygame.display.flip()
        clock.tick(30)

    pygame.mouse.set_visible(True)
    buttons.remove(pause)
    game_over_screen(counter.cnt)
