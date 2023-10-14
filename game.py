import pygame
import random
import time
import sys
import queue

# 잡다한 기초설정
pygame.init()
size = [400, 900]
screen = pygame.display.set_mode(size)
pygame.display.set_caption("MY GAME")
clock = pygame.time.Clock()

bullet_list = []  # 미사일 풀
a_list = []  # 몬스터 풀(pool - 웅덩이)
bulletq = queue.Queue()  # 비활성화된 미사일을 "빠르게" 가져오기 위한 큐(비활성화된 미사일의 위치만 담고있음)

class obj: # 화면 위에 보일 수 있는 것들
    def __init__(self, path, size, pos, speed, isActive=True): # 이미지,위치,크기,속도 이것저것 다 초기화를 한번에 해줌
        self.put_img(path) # 이미지 가져오기
        self.change_size(size[0], size[1]) # 크기 변경
        self.x = pos[0] - size[0] / 2 # 좌표 설정
        self.y = pos[1] - size[1] / 2
        self.speed = speed # 속도 설정
        self.isActive = isActive # 보임 여부 설정

    def put_img(self, address):  # 파일 경로를 통해 이미지를 로드하는 함수
        if address[-3:] == "png":
            self.img = pygame.image.load(address).convert_alpha()
        else:
            self.img = pygame.image.load(address)
        self.sx, self.sy = self.img.get_size()

    def change_size(self, sx, sy):  # 로드한 이미지의 크기를 알맞게 바꿔주는 함수
        self.img = pygame.transform.scale(self.img, (sx, sy))
        self.sx, self.sy = self.img.get_size()

    def show(self):
        # 활성화 상태일 때에만 화면에 보이도록 설정
        if self.isActive == True:
            screen.blit(self.img, (self.x, self.y))  # 로드한 이미지를 x와 y값에 따라 실제로 화면에 표시하는 함수

    def move(self, dx, dy): # 위치를 (dx,dy) 만큼 움직임
        self.x += dx
        self.y += dy

        if 0 >= self.x:
            self.x = 0
        if size[0] - self.sx <= self.x:
            self.x = size[0] - self.sx


def crash(a, b):  # a와 b가 닿아있을때 true, 아니면 false
    if (a.x - b.sx <= b.x) and (b.x <= a.x + a.sx):
        if (a.y - b.sy <= b.y) and (b.y <= a.y + a.sy):
            return True
    return False


def find_a(): # 비활성화된 적을 찾는 함수
    for a in a_list:
        if a.isActive == False: # 비활성화 되어있다면
            return a # 걔를 반환함
    return -1 # 모두 활성화되어있는 경우

ss = obj("./fighter.png", (64, 64), (size[0] / 2, size[1] - 64), 5) # 우주선 생성

# 풀을 채우는 부분
for i in range(20): # 풀의 크기 20으로 설정
    bullet_list.append(obj("./missile.png", (10, 10), (0, 0), 15, False)) # 총알 생성해서 풀에 넣음
    bulletq.put(i) # 빠르게 꺼내오기 위해서 위치값 넣어줌

    a_list.append(obj("./monster22.png", (64, 64), (0, 0), 1, False)) # 적을 생성해서 풀에 넣음

# 4.메인 이벤트
k = 0
left_go = False
right_go = False
space_go = False
while True:
    # 4-1.FPS설정
    clock.tick(60)  # FPS를 60으로 즉 1초에 60번 while문을 반복 화면이 1초에 60으로 반복

    # 4-2.각종 입력 감지
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                left_go = True
            elif event.key == pygame.K_RIGHT:
                right_go = True
            elif event.key == pygame.K_SPACE:
                space_go = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                left_go = False
            elif event.key == pygame.K_RIGHT:
                right_go = False
            elif event.key == pygame.K_SPACE:
                space_go = False

    if left_go:
        ss.move(-ss.speed, 0) # 속도만큼 왼쪽(-)로 움직인다
    elif right_go:
        ss.move(ss.speed, 0) # 속도만큼 오른쪽(+)로 움직인다

    # 총알을 쏘는 부분.
    k += 1
    if space_go and k % 6 == 0:
        if not bulletq.empty(): # 비활성화된 총알(큐에 있음)이 남아있다면
            new_bullet = bullet_list[bulletq.get()] # 비활성화 총알을 가져옴
            new_bullet.x = round(ss.x + ss.sx / 2 - new_bullet.sx / 2) # x값 설정
            new_bullet.y = ss.y - new_bullet.sy # y값 설정
            new_bullet.isActive = True # 쐈으니 활성화

    for idx, bullet in enumerate(bullet_list): #총알 한개와, 그 번호를 같이 뽑아옴
        if bullet.isActive: # 활성화된 총알이면
            bullet.move(0, -bullet.speed) # 총알을 위로 움직이기

            if bullet.y <= 0: # 화면 바깥으로 나갔는지 체크
                bullet.isActive = False # 비활성화로 바꿔줌.
                bulletq.put(idx) # 비활성화된 총알을 담는 큐에 넣음

    if random.random() > 0.97: # 확률을 뚫었을 때
        a = find_a() # 비활성화된 적을 찾음
        if a != -1: # 비활성화된 적이 있는 경우
            a.isActive = True # 걔를 활성화함
            a.x = random.randrange(0, size[0]) # 위치 정해주고(랜덤)
            a.y = 10

    for a in a_list: # 사라지는 적 체크
        if a.isActive: # 그 적이 활성화되어있음
            a.move(0, a.speed) # 아래로 움직임
            if a.y >= size[1]:  # 바닥에 부딛힌 경우
                a.isActive = False  # 몬스터를 비활성화한다.
            for bullet in bullet_list: # 총알 리스트 체크
                if bullet.isActive and crash(bullet, a) == True:  # 활성화된 총알과 적이 부딛힌 경우
                    a.isActive = False  # 몬스터를 비활성화한다.

    for a in a_list:
        if a.isActive and crash(ss, a): # 우주선과 활성화된 적이 부딛힌 경우
            time.sleep(1)
            pygame.quit() # 게임 종료
            sys.exit()

    # 4-4그리기
    screen.fill((255, 255, 255))
    ss.show()
    for m in bullet_list:
        m.show()
    for a in a_list:
        a.show()

    # 4-5.업데이트
    pygame.display.flip()