import pygame
from pygame.constants import (QUIT, K_KP_PLUS, K_KP_MINUS, K_ESCAPE, KEYDOWN, K_SPACE, K_1, K_LEFT, K_RIGHT, K_2, K_3)
import os


class Settings(object):
    window_width = 600
    window_height = 400
    fps = 60
    title = "Animation Yven Klein"
    path = {}
    path['file'] = os.path.dirname(os.path.abspath(__file__))
    path['image'] = os.path.join(path['file'], "images")
    directions = {'stop':(0, 0), 'down':(0,  1), 'up':(0, -1), 'left':(-1, 0), 'right':(1, 0)}
    player_vel = 5
    attack_cooldown = 100
    overallcooldown = 0
    jump_decay = 0
    jump_indicator = 1
    animation_indicator = 1
    constantwalk_indicator = 0
    jump_deny = 1
    jump = False
    animation_image = "walk0.png"
    isjump = False
    isright = False
    isleft = False
    idleimage = "walk0.png"
    rightimages = "walk1.png"


    @staticmethod
    def dim():
        return (Settings.window_width, Settings.window_height)

    @staticmethod
    def filepath(name):
        return os.path.join(Settings.path['file'], name)

    @staticmethod
    def imagepath(name):
        return os.path.join(Settings.path['image'], name)


class Timer(object):
    def __init__(self, duration, with_start = True):
        self.duration = duration
        if with_start:
            self.next = pygame.time.get_ticks()
        else:
            self.next = pygame.time.get_ticks() + self.duration

    def is_next_stop_reached(self):
        if pygame.time.get_ticks() > self.next:
            self.next = pygame.time.get_ticks() + self.duration
            return True
        return False

    def change_duration(self, delta=10):
        self.duration += delta
        if self.duration < 0:
            self.duration = 0


class Animation(object):
    def __init__(self, namelist, endless, animationtime, colorkey=None):
        self.images = []
        self.endless = endless
        self.timer = Timer(animationtime)
        for filename in namelist:
            if colorkey == None:
                bitmap = pygame.image.load(Settings.imagepath(filename)).convert_alpha()
            else:
                bitmap = pygame.image.load(Settings.imagepath(filename)).convert()
                bitmap.set_colorkey(colorkey)           # Transparenz herstellen §\label{srcAnimation0101}§
            self.images.append(bitmap)
        self.imageindex = -1

    def next(self):
        if self.timer.is_next_stop_reached():
            self.imageindex += 1
            if self.imageindex >= len(self.images):
                if self.endless:
                    self.imageindex = 0
                else:
                    self.imageindex = len(self.images) - 1
        return self.images[self.imageindex]

    def is_ended(self):
        if self.endless:
            return False
        elif self.imageindex >= len(self.images) - 1:
            return True
        else:
            return False


class Fighter(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.animation=Animation([f"Idle{i}.png" for i in range(1)], False, 100) # §\label{srcAnimation0102}§
        self.image = self.animation.next()
        self.rect = self.image.get_rect()
        self.rect.top = Settings.window_height - self.get_height()  # Spawnpoint des Players (Unten mittig)
        self.rect.left = Settings.window_width / 2 - self.rect.width / 2  # Spawnpoint des Players (Unten mittig)
        self.jump()

    def kick_animation(self):
        if Settings.animation_indicator == 1:
            self.animation = Animation([f"kick{i}.png" for i in range(8)], False, 200)
            Settings.animation_indicator = 0

    def flip_animation(self):
        if Settings.animation_indicator == 1:
            self.animation = Animation([f"flip{i}.png" for i in range(5)], False, 300)
            Settings.animation_indicator = 0

    def walkcount(self):
        Settings.constantwalk_indicator += 1

    def walkleft_animation(self):
        self.animation = Animation([f"left{i}.png" for i in range(4)], False, 100)
        if Settings.constantwalk_indicator <= 80:
            self.animation = Animation([f"left{i}.png" for i in range(4)], False, 100)
            Settings.constantwalk_indicator = 0

    def walkright_animation(self):
        self.animation = Animation([f"right{i}.png" for i in range(5)], False, 100)
        if Settings.constantwalk_indicator <= 80:
            self.animation = Animation([f"right{i}.png" for i in range(5)], False, 100)
            Settings.constantwalk_indicator = 0

    def jump_animation(self):
        if Settings.animation_indicator == 1:
            self.animation = Animation([f"Jump{i}.png" for i in range(7)], False, 170)
            Settings.animation_indicator = 0

    def attack_animation(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_1] and Settings.animation_indicator == 1:
            self.animation = Animation([f"Hadouken{i}.png" for i in range(5)], False, 300)
            Settings.animation_indicator = 0


    def overall_cooldown(self):
        print(Settings.overallcooldown)
        if Settings.animation_indicator == 0:
            Settings.overallcooldown += 1
            if Settings.overallcooldown >= 100:
                Settings.animation_indicator = 1
                Settings.overallcooldown = 0
                self.animation = Animation([f"Idle{i}.png" for i in range(1)], False, 100)

    def get_width(self):
        return self.rect.width

    def get_height(self):
        return self.rect.height

    def get_center(self):
        return self.rect.center

    def update(self):
        self.jump()
        self.image = self.animation.next()
        self.movement()
        self.attack_animation()
        self.overall_cooldown()
        self.walkcount()

    def movement(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left - Settings.player_vel > 0 and Settings.animation_indicator == 1:  # links movement
            self.rect.left -= Settings.player_vel
            if self.rect.top == Settings.window_height - self.get_height():
                Settings.isleft = True
        elif keys[pygame.K_RIGHT] and self.rect.left + Settings.player_vel + self.get_width() < Settings.window_width and Settings.animation_indicator == 1:  # rechts movement
            self.rect.left += Settings.player_vel
            if self.rect.top == Settings.window_height - self.get_height():
                Settings.isright = True

        elif keys[pygame.K_SPACE] and self.rect.top - Settings.player_vel > 0 and Settings.jump_indicator == 1 and Settings.jump_deny == 1 and Settings.animation_indicator == 1:  # jump
            self.jump_animation()
            Settings.jump = True
            Settings.isjump = True
            Settings.jump_deny = 3

        elif keys[pygame.K_DOWN] and self.rect.top + Settings.player_vel + self.get_height() < Settings.window_height:  # nach unten movement
            self.rect.top += Settings.player_vel

        else:
            Settings.isleft = False
            Settings.isright = False
            Settings.isjump = False
            if Settings.animation_indicator == 1:
                self.animation = Animation([f"Idle{i}.png" for i in range(1)], False, 100)

    def jump(self):
        if Settings.jump == True:
            self.rect.top -= Settings.player_vel
            Settings.jump_decay += 1
            if Settings.jump_decay >= 30:
                Settings.jump_indicator = 0
                Settings.jump_deny = 2
                Settings.jump = False

        if not self.rect.top == Settings.window_height - self.get_height() and Settings.jump_indicator == 0:
            self.rect.top += Settings.player_vel

        if self.rect.top == Settings.window_height - self.get_height() and Settings.jump_deny == 2:
            Settings.jump_decay = 0
            Settings.jump_indicator = 1
            Settings.jump_deny = 1
            Settings.isjump = False


class FighterAnimation(object):
    def __init__(self) -> None:
        super().__init__()
        os.environ['SDL_VIDEO_WINDOW_POS'] = "10, 50"
        pygame.init()
        self.screen = pygame.display.set_mode(Settings.dim())
        pygame.display.set_caption(Settings.title)
        self.clock = pygame.time.Clock()
        self.fighter = pygame.sprite.GroupSingle(Fighter())
        self.running = False

    def run(self) -> None:
        self.running = True
        while self.running:
            self.clock.tick(Settings.fps)
            self.watch_for_events()
            self.update()
            self.draw()
        pygame.quit()

    def watch_for_events(self) -> None:
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.running = False
                elif event.key == K_1:
                    self.fighter.sprite.attack_animation()
                elif event.key == K_LEFT:
                    self.fighter.sprite.walkleft_animation()
                elif event.key == K_RIGHT:
                    self.fighter.sprite.walkright_animation()
                elif event.key == K_2:
                    self.fighter.sprite.flip_animation()
                elif event.key == K_3:
                    self.fighter.sprite.kick_animation()

    def update(self) -> None:
        self.fighter.update()

    def draw(self) -> None:
        self.screen.fill((200, 200, 200))
        self.fighter.draw(self.screen)
        pygame.display.flip()


if __name__ == '__main__':
    anim = FighterAnimation()
    anim.run()

