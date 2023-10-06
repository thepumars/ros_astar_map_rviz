import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import colors
import matplotlib.patches as pc


def xy2sub(len,x,y):
    r = len - y -1
    c = x
    return [r,c]

def sub2xy(len,r,c):
    x = c
    y = len - r - 1
    return [x,y]


def drawmap_xy(Xs,Ys,obsxy):
    # 其中X和矩阵地图的cols对应
    rows = Ys
    cols = Xs
    # 创建全部为空地的地图栅格，其中空地以数字1表征
    # ！！！注意ones(行列个数，因此rows需要+1)
    field = np.ones([rows,cols])

    # 修改栅格地图中起始点和终点的数值，其中起点以数值4表征，终点以数值5表示



    # 修改栅格地图中障碍物的数值，其中以数值5表示
    for i in range(len(obsxy)):
        obssub = xy2sub(rows,obsxy[i][0],obsxy[i][1])
# =============================================================================
#         field[obssub[0],obssub[1]] = 2
# =============================================================================


    # 设置画布属性
    plt.figure(figsize=(cols,rows))
    plt.xlim(-1, cols)
    plt.ylim(-1, rows)
    plt.axis('off')
    plt.margins(0,0)

    # 绘制障碍物XY位置
    for i in range(len(obsxy)):
        plt.gca().add_patch(pc.Rectangle((obsxy[i][0] - 0.5, obsxy[i][1] - 0.5), 1,1,color='k'))

    # 绘制起点，终点
    

    return field




'''
这里是主函数，将下列地图，用以为坐标XY形式绘制出
# Y/|1. 1. 1. 1. 1.
#   |1. 1. 2. 1. 1.
#   |4. 1. 2. 1. 5.
#   |1. 1. 2. 1. 1.---->X
'''

def point_append(list,x,y):
    if not [x,y] in list:
      list.append([x,y])
      
obsxy = []

def GenerateObstacle(size,obstacle_point):
   obstacle = size//2
   point_append(obstacle_point,size//2,size//2)
   point_append(obstacle_point,size//2,size//2-1)
   for i in range(size):
       for j in range(size):
           
           if i == 0 or i == size - 1 or j == 0 or j == size - 1:
                   obstacle_point.append([i, j])
#       Generate an obstacle in the middle

   for i in range(size//2-4, size//2): 
       point_append(obstacle_point,i,size-i)
       point_append(obstacle_point,i,size-i)
       point_append(obstacle_point,size-i,i)
       point_append(obstacle_point,size-i,i-1)


   for i in range(obstacle-1): 
       x = np.random.randint(0, size)
       y = np.random.randint(0, size)
       point_append(obstacle_point,x,y)

       if (np.random.rand() > 0.5): # Random boolean 
           for l in range(size//4):
               point_append(obstacle_point,x,y+l)
               pass
       else:
           for l in range(size//4):
               point_append(obstacle_point,x+l,y)
               pass
GenerateObstacle(50,obsxy)
Ys = 51
Xs = 50
drawmap_xy(Xs,Ys,obsxy)
# =============================================================================
# plt.rcParams['figure.figsize'] = (10200, 10200)
# plt.rcParams['savefig.dpi'] = 204 #图片像素
# plt.rcParams['figure.dpi'] = 20 #分辨率
# 
# plt.savefig("pic.png", bbox_inches="tight")
# =============================================================================
# 采用XY坐标的优势在于绘制其他参数时候，如在X=2，Y=3 绘制一个大圆点，但是地图矩阵和XY又需要相互转变一下
fig = plt.gcf()
fig.set_size_inches(1.02/1,1.02/1) #dpi = 300, output = 700*700 pixels
plt.gca().xaxis.set_major_locator(plt.NullLocator())
plt.gca().yaxis.set_major_locator(plt.NullLocator())
plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, hspace = 0, wspace = 0)
plt.margins(0,0)
fig.savefig('pic.png', format='png', transparent=False, dpi=100, pad_inches = 0)

