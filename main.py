import pygame
import random
import os

# Constants 常量
W, H = 288, 512
FPS = 30
score = 0

# Setup 设置
pygame.init()  # 初始化
SCREEN = pygame.display.set_mode((W, H))  # 设置游戏窗口大小
pygame.display.set_caption('Flappy_Bird---by zds')  # 设置标题
CLOCK = pygame.time.Clock()

# Materials 素材
IMAGES = {}  # 用字典保存所有素材 {素材名：load函数}
for image in os.listdir('image'):
    name, extension = os.path.splitext(image)
    path = os.path.join('image', image)
    IMAGES[name] = pygame.image.load(path)

AUDIO = {}
for audio in os.listdir('assets/audio'):
    name, extension = os.path.splitext(audio)
    path = os.path.join('assets/audio', audio)
    AUDIO[name] = pygame.mixer.Sound(path)
# yellow_bird_up = pygame.image.load('image/bird0_0.png')
# yellow_bird_mid = pygame.image.load('image/bird0_1.png')
# yellow_bird_down = pygame.image.load('image/bird0_2.png')
# blue_bird_up = pygame.image.load('image/bird1_0.png')
# blue_bird_mid = pygame.image.load('image/bird1_1.png')
# blue_bird_down = pygame.image.load('image/bird1_2.png')
# bg_day = pygame.image.load('image/bg_day.png')
# bg_night = pygame.image.load('image/bg_night.png')
# game_ready = pygame.image.load('image/text_ready.png')
# game_over = pygame.image.load('image/text_game_over.png')
# land = pygame.image.load('image/land.png')

LAND_Y = H - IMAGES['land'].get_height()


def main():
    while True:
        AUDIO['start'].play()
        IMAGES['bgpic'] = IMAGES[random.choice(['bg_day', 'bg_night'])]
        bird_color = random.choice(['yellow_bird', 'blue_bird', 'red_bird'])
        IMAGES['birds'] = [IMAGES[bird_color + '_up'], IMAGES[bird_color + '_mid'], IMAGES[bird_color + '_down']]
        menu_window()
        result = game_window()
        end_window(result)


def menu_window():
    land_gap = IMAGES['land'].get_width() - W
    land_x = 0

    bird_x = W * 0.2
    bird_y = (H - IMAGES['birds'][0].get_height()) / 2
    bird_y_vel = 1
    bird_y_range = [bird_y - 8, bird_y + 8]

    # 帧循环
    idx = 0
    repeat = 5
    frames = [0] * repeat + [1] * repeat + [2] * repeat

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                AUDIO['flap'].play()
                return

        land_x -= 4
        if land_x <= - land_gap:
            land_x = 0

        bird_y += bird_y_vel
        if bird_y < bird_y_range[0] or bird_y > bird_y_range[1]:
            bird_y_vel *= -1

        idx += 1
        idx %= len(frames)

        SCREEN.blit(IMAGES['bgpic'], (0, 0))
        SCREEN.blit(IMAGES['land'], (land_x, LAND_Y))
        SCREEN.blit(IMAGES['birds'][frames[idx]], (bird_x, bird_y))
        SCREEN.blit(IMAGES['text_ready'],
                    ((W - IMAGES['text_ready'].get_width()) / 2, (LAND_Y - IMAGES['text_ready'].get_height()) / 2))
        pygame.display.update()
        CLOCK.tick(FPS)


def game_window():
    land_gap = IMAGES['land'].get_width() - W
    land_x = 0
    global score
    score = 0

    bird = Bird(W * 0.2, H * 0.4)

    # 初始水管生成
    n = 4
    # pipes = []
    pipe_group = pygame.sprite.Group()
    pipe_y_gap = 130  # 上下水管间距
    for i in range(n):
        pipe_y = random.randint(int(H * 0.3), int(H * 0.7))
        pipe_up = Pipe(W + i * 150, pipe_y, True)
        pipe_down = Pipe(W + i * 150, pipe_y - pipe_y_gap, False)
        # pipes.append(pipe_up)
        # pipes.append(pipe_down)
        pipe_group.add(pipe_up)
        pipe_group.add(pipe_down)

    while True:
        flap = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                flap = True
                AUDIO['flap'].play()
            # if (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE) or \
            #         (bird.rect.y < 0 or bird.rect.y > LAND_Y):
            #     return

        land_x -= 4
        if land_x <= - land_gap:
            land_x = 0

        bird.update(flap)

        # 不断生成新水管

        # first_pipe_up = pipes[0]
        # first_pipe_down = pipes[1]
        first_pipe_up = pipe_group.sprites()[0]
        first_pipe_down = pipe_group.sprites()[1]
        if first_pipe_up.rect.x < 0 - 35:
            # pipes.remove(first_pipe_up)
            # pipes.remove(first_pipe_down)
            first_pipe_up.kill()
            first_pipe_down.kill()
            pipe_y = random.randint(int(H * 0.3), int(H * 0.7))
            new_pipe = Pipe(first_pipe_up.rect.x + n * 150, pipe_y, True)
            # pipes.append(new_pipe)
            pipe_group.add(new_pipe)
            new_pipe = Pipe(first_pipe_down.rect.x + n * 150, pipe_y - pipe_y_gap, False)
            # pipes.append(new_pipe)
            pipe_group.add(new_pipe)
            # del first_pipe_up
            # del first_pipe_down

        # for pipe in pipes:
        #     pipe.update()
        pipe_group.update()

        # 判断小鸟是否与上下边界相撞
        if bird.rect.y < 0 or bird.rect.y > LAND_Y - 20:
            result = {'bird': bird, 'pipe_group': pipe_group, 'score': score}
            AUDIO['die'].play()
            AUDIO['hit'].play()
            return result

        if bird.rect.left + first_pipe_up.x_vel < first_pipe_up.rect.centerx < bird.rect.left:
            AUDIO['score'].play()
            score += 1

        # 判断小鸟是否与水管相撞
        for pipe in pipe_group.sprites():
            rigth_to_left = max(bird.rect.right, pipe.rect.right) - min(bird.rect.left, pipe.rect.left)
            bottom_to_top = max(bird.rect.bottom, pipe.rect.bottom) - min(bird.rect.top, pipe.rect.top)
            if rigth_to_left < bird.rect.width + pipe.rect.width - 20 and \
                    bottom_to_top < bird.rect.height + pipe.rect.height - 20:
                result = {'bird': bird, 'pipe_group': pipe_group, 'score': score}
                AUDIO['die'].play()
                AUDIO['hit'].play()
                return result

        SCREEN.blit(IMAGES['bgpic'], (0, 0))
        # for pipe in pipes:
        #     SCREEN.blit(pipe.image, pipe.rect)
        pipe_group.draw(SCREEN)
        show_score(score)
        SCREEN.blit(IMAGES['land'], (land_x, LAND_Y))
        SCREEN.blit(bird.image, bird.rect)
        pygame.display.update()
        CLOCK.tick(FPS)


def end_window(result):
    bird = result['bird']
    pipe_group = result['pipe_group']
    score = result['score']

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return

        bird.die()

        SCREEN.blit(IMAGES['bgpic'], (0, 0))
        pipe_group.draw(SCREEN)
        show_score(score)
        SCREEN.blit(IMAGES['land'], (0, LAND_Y))
        SCREEN.blit(bird.image, bird.rect)
        SCREEN.blit(IMAGES['text_game_over'],
                    ((W - IMAGES['text_game_over'].get_width()) / 2,
                     (LAND_Y - IMAGES['text_game_over'].get_height()) / 2))
        pygame.display.update()
        CLOCK.tick(FPS)


def show_score(score):
    score_str = str(score)
    n = len(score_str)
    w = IMAGES['number_score_00'].get_width() * 1.1
    x = (W - n * w) / 2
    y = H * 0.1
    for number in score_str:
        SCREEN.blit(IMAGES['number_score_0' + number], (x, y))
        x += w


class Bird:
    def __init__(self, x, y):
        self.frames = [0] * 5 + [1] * 5 + [2] * 5 + [1] * 5
        self.idx = 0
        self.image = IMAGES['birds'][self.frames[self.idx]]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        # y方向速度变化
        self.y_vel = -10
        self.max_y_vel = 10
        self.gravity = 1  # 重力加速度
        # 角度变化
        self.rotate = 45
        self.max_rotate = -20
        self.rotate_vel = -3
        # 拍动翅膀后
        self.y_vel_after_flap = -10
        self.rotate_after_flap = 45

    def update(self, flap=False):
        if flap:
            self.y_vel = self.y_vel_after_flap
            self.rotate = self.rotate_after_flap

        self.y_vel = min(self.y_vel + self.gravity, self.max_y_vel)
        self.rect.y += self.y_vel
        self.rotate = max(self.rotate + self.rotate_vel, self.max_rotate)

        self.idx += 1
        self.idx %= len(self.frames)
        self.image = IMAGES['birds'][self.frames[self.idx]]
        self.image = pygame.transform.rotate(self.image, self.rotate)

    def die(self):
        if self.rect.y < LAND_Y - 20:
            # self.y_vel = self.max_y_vel
            self.rect.y += self.max_y_vel
            self.rotate = -90
            self.image = IMAGES['birds'][self.frames[self.idx]]
            self.image = pygame.transform.rotate(self.image, self.rotate)


class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, upwards=True):
        global score
        pygame.sprite.Sprite.__init__(self)
        if upwards:
            self.image = IMAGES['pipe_up']
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
        else:
            self.image = IMAGES['pipe_down']
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.bottom = y
        self.x_vel = -4  # 水管移动速度

    def update(self):
        self.rect.x += self.x_vel


main()

'''
while True:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            bird = pygame.transform.flip(bird, True, False)

    color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    SCREEN.fill(color)
    SCREEN.blit(bird, (150, 200))
    pygame.display.update()
    CLOCK.tick(10)  # 每秒10帧
'''
