"""
Shooting Game (single-file)
Dependencies: pygame

Features:
- Responsive event loop using delta time (improved time response)
- Bullet pooling for performance
- Smooth movement and shooting
- Colored gradient background with animated stars
- HUD: score, lives, level
- Pause, restart, and fullscreen toggle

Controls:
- Arrow keys / WASD to move
- Space to shoot
- P to pause
- F to toggle fullscreen
- R to restart after game over

Run:
$ pip install pygame
$ python shooting_game.py

"""

import pygame
import random
import math
from collections import deque

# --- Config
WIDTH, HEIGHT = 900, 600
FPS = 120
PLAYER_SPEED = 450      # pixels per second
BULLET_SPEED = 900
ENEMY_SPEED_MIN = 80
ENEMY_SPEED_MAX = 200
FIRE_RATE = 0.16        # seconds between shots
MAX_BULLETS = 40
ENEMY_SPAWN_TIME = 0.8

# Colors
WHITE = (255,255,255)
BLACK = (0,0,0)
HUD_COLOR = (230,230,230)

# Initialize
pygame.init()
pygame.display.set_caption('Caii - Fast Shooter')
flags = 0
screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)
clock = pygame.time.Clock()
font = pygame.font.SysFont('consolas', 20)
large_font = pygame.font.SysFont('consolas', 44)

# Utility
def clamp(x, a, b):
    return max(a, min(b, x))

# Bullet pooling
class Bullet(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((6,14), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (255,220,80), self.image.get_rect())
        self.rect = self.image.get_rect()
        self.speed = BULLET_SPEED
        self.active = False

    def activate(self, x, y):
        self.rect.center = (x, y)
        self.active = True

    def update(self, dt):
        if not self.active:
            return
        self.rect.y -= int(self.speed * dt)
        if self.rect.bottom < 0:
            self.active = False

    def draw(self, surface):
        if self.active:
            surface.blit(self.image, self.rect)

# Player
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.size = 40
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, (100,200,255), [(0,self.size),(self.size/2,0),(self.size,self.size)])
        self.rect = self.image.get_rect(center=(WIDTH//2, HEIGHT - 60))
        self.speed = PLAYER_SPEED
        self.shoot_timer = 0
        self.lives = 3

    def update(self, dt, keys):
        vx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            vx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            vx += 1
        self.rect.x += int(vx * self.speed * dt)
        self.rect.x = clamp(self.rect.x, 0, WIDTH - self.rect.width)
        self.shoot_timer = max(0, self.shoot_timer - dt)

# Enemy
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.size = random.randint(20,44)
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255,100,100), (self.size//2, self.size//2), self.size//2)
        self.rect = self.image.get_rect()
        self.speed = random.uniform(ENEMY_SPEED_MIN, ENEMY_SPEED_MAX)
        self.health = 1
        self.active = False

    def spawn(self):
        self.rect.x = random.randint(0, WIDTH - self.size)
        self.rect.y = -self.size - random.randint(0, 200)
        self.speed = random.uniform(ENEMY_SPEED_MIN, ENEMY_SPEED_MAX)
        self.health = 1
        self.active = True

    def update(self, dt):
        if not self.active:
            return
        self.rect.y += int(self.speed * dt)
        if self.rect.top > HEIGHT:
            self.active = False

    def draw(self, surface):
        if self.active:
            surface.blit(self.image, self.rect)

# Simple pool helper
class Pool:
    def __init__(self, cls, size):
        self.pool = [cls() for _ in range(size)]
        self.queue = deque(self.pool)

    def get(self):
        for item in self.pool:
            if not getattr(item, 'active', True):
                return item
        # fallback - recycle oldest
        item = self.pool[0]
        item.active = False
        return item

    def active_list(self):
        return [p for p in self.pool if getattr(p, 'active', False)]

# Stars for background
class Star:
    def __init__(self):
        self.reset(True)

    def reset(self, init=False):
        self.x = random.uniform(0, WIDTH)
        self.y = random.uniform(0, HEIGHT if init else -50)
        self.speed = random.uniform(10, 120)
        self.size = random.randint(1,3)
        self.alpha = random.randint(80,255)

    def update(self, dt):
        self.y += self.speed * dt
        if self.y > HEIGHT:
            self.reset()

    def draw(self, surf):
        s = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        s.fill((255,255,255, self.alpha))
        surf.blit(s, (int(self.x), int(self.y)))

# Game class
class Game:
    def __init__(self):
        self.running = True
        self.fullscreen = False
        self.player = Player()
        self.bullets = Pool(Bullet, MAX_BULLETS)
        self.enemies = [Enemy() for _ in range(24)]
        self.enemy_timer = 0
        self.score = 0
        self.paused = False
        self.game_over = False
        self.stars = [Star() for _ in range(80)]

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        global screen
        if self.fullscreen:
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
        else:
            screen = pygame.display.set_mode((WIDTH, HEIGHT))

    def spawn_enemy(self):
        for e in self.enemies:
            if not e.active:
                e.spawn()
                break

    def shoot(self):
        b = self.bullets.get()
        b.activate(self.player.rect.centerx, self.player.rect.top - 6)

    def update(self, dt, keys):
        if self.paused or self.game_over:
            return
        self.player.update(dt, keys)
        # shooting
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP]) and self.player.shoot_timer <= 0:
            self.player.shoot_timer = FIRE_RATE
            self.shoot()
        # update bullets
        for b in self.bullets.pool:
            b.update(dt)
        # update enemies
        for e in self.enemies:
            e.update(dt)
        # spawn enemies
        self.enemy_timer += dt
        if self.enemy_timer >= ENEMY_SPAWN_TIME:
            self.enemy_timer = 0
            self.spawn_enemy()
        # collision bullet-enemy
        for b in self.bullets.active_list():
            for e in self.enemies:
                if e.active and b.active and e.rect.colliderect(b.rect):
                    e.active = False
                    b.active = False
                    self.score += 10
                    break
        # enemy-player collision
        for e in self.enemies:
            if e.active and e.rect.colliderect(self.player.rect):
                e.active = False
                self.player.lives -= 1
                if self.player.lives <= 0:
                    self.game_over = True

    def draw_background(self, surf, t):
        # gradient background
        top_color = (12, 25, 68)
        bottom_color = (18, 83, 53)
        for y in range(0, HEIGHT, 6):
            ratio = y / HEIGHT
            r = int(top_color[0] * (1-ratio) + bottom_color[0] * ratio)
            g = int(top_color[1] * (1-ratio) + bottom_color[1] * ratio)
            b = int(top_color[2] * (1-ratio) + bottom_color[2] * ratio)
            pygame.draw.rect(surf, (r,g,b), (0,y,WIDTH,6))
        # moving stars
        for s in self.stars:
            s.update(t)
            s.draw(surf)

    def draw(self, surf):
        t = clock.get_time() / 1000.0
        self.draw_background(surf, t)
        # draw bullets
        for b in self.bullets.pool:
            b.draw(surf)
        # draw enemies
        for e in self.enemies:
            e.draw(surf)
        # draw player
        surf.blit(self.player.image, self.player.rect)
        # HUD
        score_surf = font.render(f'Score: {self.score}', True, HUD_COLOR)
        lives_surf = font.render(f'Lives: {self.player.lives}', True, HUD_COLOR)
        surf.blit(score_surf, (10,10))
        surf.blit(lives_surf, (WIDTH - 110, 10))
        if self.paused:
            p = large_font.render('PAUSED', True, WHITE)
            surf.blit(p, (WIDTH//2 - p.get_width()//2, HEIGHT//2 - p.get_height()//2))
        if self.game_over:
            go = large_font.render('GAME OVER', True, (255,140,140))
            sub = font.render('Press R to Restart', True, HUD_COLOR)
            surf.blit(go, (WIDTH//2 - go.get_width()//2, HEIGHT//2 - 50))
            surf.blit(sub, (WIDTH//2 - sub.get_width()//2, HEIGHT//2 + 10))

    def restart(self):
        self.__init__()

# Main
def main():
    g = Game()
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0  # delta time in seconds
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    g.paused = not g.paused
                elif event.key == pygame.K_f:
                    g.toggle_fullscreen()
                elif event.key == pygame.K_r and g.game_over:
                    g.restart()
                elif event.key == pygame.K_ESCAPE:
                    running = False
        # Update
        g.update(dt, keys)
        # Draw
        g.draw(screen)
        pygame.display.flip()
    pygame.quit()

if __name__ == '__main__':
    main()
