import pygame
import numpy as np
import random
import time
import math
import matplotlib.pyplot as plt



#2 表示有车道路
#1 表示无车道路
#0 表示非道路

def car_count(matrix):
    return np.count_nonzero(matrix[1:,:])

def get_adjacent_positions(row, col, i, j):
    adjacent_positions = []
    if i > 0:
        adjacent_positions.append((i-1, j))
    if i < row-1:
        adjacent_positions.append((i+1, j))
    if j > 0:
        adjacent_positions.append((i, j-1))
    if j < col-1:
        adjacent_positions.append((i, j+1))
    return adjacent_positions

def generate_cars(matrix, lanes, p_auto, p_generate):
    n_rows, n_cols = matrix.shape
    car_in=0
    for j in range(n_cols):
        if matrix[n_rows-1,j] == 0 and np.random.random() < p_generate:
            #matrix[n_rows-1,j] = 1
            sign = random.choices([-1, 1],[p_auto,1-p_auto])[0]
            matrix[n_rows-1,j]=random.randint(1,lanes)*sign
            car_in+=1
    return (matrix,car_in)

def wash_matrix(matrix):
    # 将矩阵中的所有ghost替换为0
    matrix = np.where(matrix == 100, 0, matrix)
    matrix = np.where(matrix == 1000, 0, matrix)
    return matrix

def change_lane(matrix):
    n_rows, n_cols = matrix.shape
    for i in range(1,n_rows):
        j=0
        while j<(n_cols):
            if (int(matrix[i][j])!=0 and int(matrix[i][j])!=100):#保证方格里有车
                val=abs(int(matrix[i][j]))
                sgn=int(math.copysign(1,matrix[i][j]))

                #如果不在目标车道则需要换道
                if j+1!=val:
                    if val<j+1: #如果目标车道在左侧
                        if matrix[i][j-1]==0 or (matrix[i][j-1]==100 and sgn==-1): #如果左侧为空车道
                            matrix[i][j-1]=val*sgn
                            matrix[i][j]=1000 #设置为幽灵位，只有自动驾驶车辆才能在同一时刻占据幽灵位

                    else:
                        if matrix[i][j+1]==0 or (matrix[i][j+1]==100 and sgn==-1): #如果右侧为空车道
                            matrix[i][j+1]=val*sgn
                            matrix[i][j]=1000 #设置为幽灵位，只有自动驾驶车辆才能在同一时刻占据幽灵位
                            j+=1
            j+=1

def move_forward(matrix):
    n_rows, n_cols = matrix.shape
    car_out=0
    bad_pass=0
    for i in range(1,n_rows):
        for j in range(n_cols):
            if matrix[i][j]==(0 or 100):
                 continue
            
            val=abs(int(matrix[i][j]))
            sgn=int(math.copysign(1,matrix[i][j]))

            #检查左右两侧车辆是否车道正确
            right=0 if j==n_cols-1 else abs(matrix[i][j+1])


            if (right>=j+2 or right==0): #如果右方车辆需要左变道，则右方车辆优先，左方车辆减速避让
                    if j+1==val:
                        if i==1:
                            matrix[i][j]=0 #到达终点直接消失
                            car_out+=1
                        elif i==2:         #走两步直接消失
                            if matrix[i-1][j]==0 or (matrix[i-1][j]==100 and sgn==-1):
                                matrix[i-1][j]=100
                                matrix[i][j]=0
                                car_out+=1

                        else:
                            if matrix[i-1][j]==0 or (matrix[i-1][j]==100 and sgn==-1):
                                matrix[i-1][j]=val*sgn
                                matrix[i][j]=0
                                if matrix[i-2][j]==0 or (matrix[i-2][j]==100 and sgn==-1):
                                    matrix[i-2][j]=val*sgn
                                    matrix[i-1][j]=100
                                    matrix[i][j]=0
                    else:
                        if (matrix[i-1][j]==0 or (matrix[i-1][j]==100 and sgn==-1)) and i!=1:
                            matrix[i-1][j]=val*sgn
                            matrix[i][j]=0
            else:
                    if i==1:
                        matrix[i][j]=0 #到达终点,即使没有到达指定的车道也要直接消失
                        car_out+=1
                        bad_pass+=1
                    elif i==2:         #到达终点,即使没有到达指定的车道走两步直接消失
                        if matrix[i-1][j]==0 or (matrix[i-1][j]==100 and sgn==-1):
                                matrix[i-1][j]=100
                                matrix[i][j]=0
                                car_out+=1
                                bad_pass+=1

                    # else:
                        continue
    return (car_out,bad_pass)


def generate_colormap(n):
    rainbow_colors = [(255,0,0), (255,127,0), (255,255,0), (0,255,0), (0,0,255), (148,0,211)]
    if n <= 1:
        return {0: (255, 255, 255)}
    elif n <= 6:
        step = 6 // n
        colormap = {}
        for i in range(n):
            colormap[i+1] = rainbow_colors[i*step]
            colormap[-(i+1)] = rainbow_colors[i*step]
        colormap[0] = (255, 255, 255)
        return colormap
    else:
        step = 6 / (n-1)
        colormap = {}
        for i in range(n):
            x = i * step
            r, g, b = 0, 0, 0
            if x <= 1:
                r, g = 255, int(x*255)
            elif x <= 2:
                r, g = int((2-x)*255), 255
            elif x <= 3:
                g, b = 255, int((x-2)*255)
            elif x <= 4:
                g, b = int((4-x)*255), 255
            elif x <= 5:
                r, b = int((x-4)*255), 255
            else:
                r, b = 255, int((6-x)*255)
            colormap[i+1] = (r, g, b)
            colormap[-(i+1)] = (r, g, b)
        colormap[0] = (255, 255, 255)
        return colormap
    




def play_game(length,lanes,p_auto,p_generate,sti_time):

    matrix=np.zeros((length,lanes))


    color_map= generate_colormap(lanes)


    for i in range(lanes):
        matrix[0,i]=i+1

    # 初始化Pygame
    pygame.init()

    # 设置窗口尺寸
    WINDOW_SIZE = (480, 960)
    screen = pygame.display.set_mode(WINDOW_SIZE)

    # 设置字体
    font = pygame.font.SysFont(None, 25)


    # 设置网格尺寸和间隔
    CELL_SIZE = 8
    CELL_SPACING = 1

    # 设置网格左上角的坐标
    grid_x = (WINDOW_SIZE[0] - (CELL_SIZE + CELL_SPACING) * matrix.shape[1] + CELL_SPACING) / 2
    grid_y = (WINDOW_SIZE[1] - (CELL_SIZE + CELL_SPACING) * matrix.shape[0] + CELL_SPACING) / 2

    # 设置颜色映射


    # 游戏循环
    running = True
    game_time=0
    in_time=0
    out_time=0
    car_num=0
    bad_pass=0

    while running:
        #事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False


        if game_time<sti_time:
            data0=generate_cars(matrix,lanes,p_auto,p_generate)
            matrix=data0[0]
            car_in=data0[1]
            in_time+=car_in*game_time
            car_num+=car_in

        data1=move_forward(matrix)
        car_out=data1[0]
        bad_pass+=data1[1]

        out_time+=car_out*game_time

        change_lane(matrix)
        matrix=wash_matrix(matrix)
        time.sleep(0.2)
        game_time+=1


        if car_count(matrix)==0 and game_time>=100:
            #print("Autopilot Rate:",p_auto," Avg Passing Time:",(out_time-in_time)/car_num, " Bad Pass:", bad_pass/car_num)
            print(p_auto,",",round((out_time-in_time)/car_num,3), ",",bad_pass/car_num)
            break

        #绘制网格
        for i in range(matrix.shape[0]):
            for j in range(matrix.shape[1]):
                cell_x = grid_x + j * (CELL_SIZE + CELL_SPACING)
                cell_y = grid_y + i * (CELL_SIZE + CELL_SPACING)
                if matrix[i, j] < 0:
                    pygame.draw.rect(screen, color_map[0], [cell_x, cell_y, CELL_SIZE, CELL_SIZE])
                    pygame.draw.circle(screen, color_map[int(matrix[i, j])], [int(cell_x + CELL_SIZE/2), int(cell_y + CELL_SIZE/2)], int(CELL_SIZE/2) - CELL_SPACING)
                else:
                    pygame.draw.rect(screen, color_map[int(matrix[i, j])], [cell_x, cell_y, CELL_SIZE, CELL_SIZE])


        # 显示网格
        pygame.display.flip()

    # 退出Pygame
    pygame.quit()



length=50
lanes=6
p_auto=0.5
p_generate=0.8
sti_time=1000


play_game(length,lanes,p_auto,p_generate,sti_time)

