import pygame
import math
from queue import PriorityQueue


LENGTH= 800
WIN=pygame.display.set_mode((LENGTH,LENGTH))
pygame.display.set_caption("A* Visualizer")

WHITE=(255,255,255) #Grid
BLACK=(0,0,0)#obstacle
RED=(255,0,0) #Seen
GREEN=(0,255,0) #Start
BLUE=(0,0,255)#OpenSet
YELLOW=(255,255,0) #End
PINK=(255,0,255) #Path
ORANGE=(255,165,0)
PURPLE=(128,0,128)
GREY=(128,128,128) #gridlines

class Cube:
    def __init__(self,row,col,length,total_rows):
        self.row=row
        self.col=col
        self.x=row*length
        self.y=col*length
        self.colour=WHITE
        self.neighbours=[]
        self.length=length
        self.total_rows=total_rows

    def position(self):
        return self.row,self.col

    def seen(self):
        return self.colour==RED

    def openset(self):
        return self.colour==BLUE

    def obstacle(self):
        return self.colour==BLACK

    def start(self):
        return self.colour==GREEN

    def end(self):
        return self.colour==YELLOW

    def reset(self):
        self.colour=WHITE

    def make_start(self):
        self.colour=GREEN

    def make_closed(self):
        self.colour=RED

    def make_open(self):
        self.colour=BLUE

    def make_barrier(self):
        self.colour=BLACK

    def make_end(self):
        self.colour=YELLOW

    def make_path(self):
        self.colour=PINK

    def draw(self):
        pygame.draw.rect(WIN,self.colour,(self.x,self.y,self.length,self.length))

    def update_neighbours(self,grid):
        self.neighbours = []
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].obstacle(): #TO CHECK DOWN
             self.neighbours.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].obstacle():   #TO CHECK UP
            self.neighbours.append(grid[self.row - 1][self.col])

        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].obstacle(): #CHECK LEFT
            self.neighbours.append(grid[self.row][self.col + 1])

        if self.col > 0 and not grid[self.row][self.col - 1].obstacle():  #CHECK RIGHT
            self.neighbours.append(grid[self.row][self.col - 1])

    def __lt__(self,other):
        return False


def heuristic(p1,p2):
    x1,y1=p1
    x2,y2=p2
    return abs(x2-x1)+abs(y2-y1)

def path(came_from,current,draw):
    while current in came_from:
        current=came_from[current]
        current.make_path()
        draw()

def algorithm(draw,grid,start,end):
    count=0
    open_set=PriorityQueue()
    open_set.put((0,count,start))
    came_from={}
    g_score={cube:float('inf') for row in grid for cube in row }
    g_score[start]=0
    f_score={cube:float('inf') for row in grid for cube in row }
    f_score[start]= heuristic(start.position(),end.position())

    open_set_hash={start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current=open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            path(came_from,end,draw)
            end.make_end()
            return True
        for neighbour  in current.neighbours:
            temp_g_score=g_score[current]+1
            if temp_g_score<g_score[neighbour]:
                came_from[neighbour]=current
                g_score[neighbour]=temp_g_score
                f_score[neighbour]=temp_g_score + heuristic(neighbour.position(),end.position())
                if neighbour not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbour],count,neighbour))
                    open_set_hash.add(neighbour)
                    neighbour.make_open()
            draw()
        if current!=start:
            current.make_closed()
    return False


def create_grid(rows,width):
    grid=[]
    gap=width//rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            cube=Cube(i,j,gap,rows)
            grid[i].append(cube)

    return grid

def draw_grid(win,rows,width):
    gap=width//rows
    for i in range(rows):
        pygame.draw.line(win,GREY,(0,i*gap),(width,i*gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j*gap,0), (j*gap,width))


def draw(win,grid,rows,width):
    win.fill(WHITE)

    for row in grid:
        for cube in row:
            cube.draw()

    draw_grid(win,rows,width)
    pygame.display.update()

def click_position(position,rows,width):
    gap = width//rows
    y,x=position

    row=y//gap
    col=x//gap

    return row,col

def main(win,length):
    ROWS= 50
    grid= create_grid(ROWS,length)

    start= None
    end= None

    run = True
    started = False

    while run:
        draw(win,grid,ROWS,length)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if started:
                continue

            if pygame.mouse.get_pressed()[0]:
                position = pygame.mouse.get_pos()
                row,col = click_position(position,ROWS,length)
                cube=grid[row][col]
                if not start and cube != end:
                    start=cube
                    start.make_start()

                elif not end and cube != start:
                    end=cube
                    end.make_end()

                elif cube != end and cube != start:
                    cube.make_barrier()


            elif pygame.mouse.get_pressed()[2]:
                position = pygame.mouse.get_pos()
                row,col = click_position(position,ROWS,length)
                cube=grid[row][col]
                cube.reset()
                if cube == start:
                    start=None
                elif cube == end:
                    end=None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not started:
                    for row in  grid:
                        for cube in row:
                            cube.update_neighbours(grid)

                    algorithm(lambda: draw(win,grid,ROWS,length),grid,start,end )
                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = create_grid(ROWS, length)

    pygame.quit()

main(WIN,LENGTH)
