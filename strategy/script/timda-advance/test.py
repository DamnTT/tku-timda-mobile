import matplotlib.pyplot as plt
import numpy as np
import math
from itertools import permutations
import json


rt = np.zeros(6)
obj = [[0, 0], [-4, 6], [-1, 9], [3, 1]]
test = 10.256

def computeDist(dna):
    dist = np.zeros((dna, dna))

    for i in range(dna):
        for j in range(i+1, dna):
            d = np.sqrt(np.square(obj[i][0]-obj[j][0]) + np.square(obj[i][1]-obj[j][1]))
            dist[i][j] = d
            dist[j][i] = d
    return dist

def main():
    tmp = ''
    
    # itembuy()
    item = [0, 1, 2, 3]
    item2="123"
    itemRoll = np.roll(item,-1)
    tmp = str(itemRoll[0])
    tmp = tmp + str(itemRoll[1])
    print(tmp)
    #x = list(permutations(item, len(item)))
    #print(x)
    #print(item)
    #print(itemRoll)
    #for i in itemRoll:
    #    print(type(i))
    #for i in item:
    #    print(type(i))
    #print(len(item))
    #dist = computeDist(len(item))
    #print(dist[item,itemRoll])
    #print(np.sum(dist[item,itemRoll]))

    # list = ['a', 'b', 'c', 'd', 'e']
    # if list.count('z') > 0:
    #     print("fuck")
    # else:
    #     print("fuck u to ")
    # plt.plot([1, 2, 3, 4])
    # plt.show()
    # a = np.array([[0], [1]])
    # chromosome = np.empty([3, 2])
    # chchcc = np.random.random((3, 2))
    # i = 0
    # k = 1
    # table = "table" + str(k)
    # print(table)
    # cal_tmp2 = ["a", "b", "c"]
    # jj = 0
    # str1 = '454'.join(str(k) for i in cal_tmp2[jj])
    # print(str1)
    # for i in range(1, 3):
    #     for j in range(1, 3):
    #         print(i, j)
    # for k in range(4):
    # #     print(k)
    # for j in range(1, 4):
    #     route = distance((obj[j][0]-obj[0][0]), (obj[j][1]-obj[0][1]))
    #     print("j is:", j)
    #     for l in range(1, 4):
    #         if l == j:
    #             continue
    #         print("l is:", l)
    #         route = route + \
    #             distance((obj[l][0]-obj[j][0]), (obj[l][1]-obj[j][1]))
    #         for a in range(1, 4):
    #             if a == l or a == j:
    #                 continue
    #             print("a is:", a)
    #             print(j, l, a, "\n")
    #             route = route + \
    #                 distance((obj[l][0]-obj[j][0]),
    #                          (obj[l][1]-obj[j][1]))
    #             route = route + \
    #                 distance((obj[0][0]-obj[l][0]),
    #                          (obj[0][1]-obj[l][1]))
    #             rt[i] = route
    #             i += 1
    # print(rt)
    # print(distance(3, 4))

    # dict = {}
    # dict['test1'] = 1
    # dict['test2'] = 2
    # dict['test3'] = 3
    # print(dict(1))
    # cal = [1, 2, 3]
    # dic = {'test1': 123, 'test2': 234, 'test3': 345}
    # dic_2 = [123, 234, 345]
    # cal_2 = list(itertools.permutations(cal, len(cal)))

    # for i in cal_2:
    #     for j in i:
    #         print(j)
    # # for i in dict:
    # #     print(dict[i])
    #     list = [1, 2, 3, 4]
    # #
    #     arr = [1, 2, 3]
    #     str1 = ','.join(str(i) for i in arr)
    #     print(len(list))
    #     print(str1)
    # cal(1, 0, 0)
    # cal_t(1, 0, 4)
    # for i in range(1, 5):
    #     for j in range(1, 5):
    #         if j == i:
    #             continue
    #         for l in range(1, 5):
    #             if l == i or l == j:
    #                 continue
    #             for a in range(1, 5):
    #                 if a == i or a == j or a == l:
    #                     continue
    #                 for b in range(1, 10):
    #                     if b == i or b == j or b == l or b == a:
    #                         continue
    #                     for c in range(1, 10):
    #                         if c == i or c == j or c == l or c == a or c == b:
    #                             continue
    #                         for d in range(1, 10):
    #                             if d == i or d == j or d == l or d == a or d == b or d == c:
    #                                 continue
    #                             for e in range(1, 10):
    #                                 if e == i or e == j or e == l or e == a or e == b or e == c or e == d:
    #                                     continue
    #                                 for f in range(1, 10):
    #                                     if f == i or f == j or f == l or f == a or f == b or f == c or f == d or f == e:
    #                                         continue
    #                                     for g in range(1, 10):
    #                                         if g == i or g == j or g == l or g == a or g == b or g == c or g == d or g == e or g == f:
    #                                             continue
    #                                         print(i, j, l, a, b, c, d, e, f, g)
    #                                         print("")


def distance(x, y):
    r = math.sqrt(pow(x, 2) + pow(y, 2))
    return r


def itembuy(itemBuy):
    xx = LoadData()
    y = 0
    itemArr = []
    x = list(permutations(itemBuy, len(itemBuy)))

    for i in x:
        stepArr = []
        stepArr.append(i)
        print(i)
        y = 0
        for k in range(len(i)):
            # 判斷是否為第一項，之後再加上到初始點的距離
            if k == 0:
                y = y + xx["initial"][i[k+1]]
                print("initial", " plus ", i[k], "is", y)

            y = y + xx[i[k]][i[k+1]]
            print(i[k], " plus ", i[k+1], "is", y)

            # 判斷是否為最後一項，之後再加上對初始點的距離
            if (k+1) == len(i)-1:
                y = y + xx[i[k+1]]["initial"]
                print(i[k+1], " plus ", "initial", "is", y)
                break
        print("total:", y)
        stepArr.append(y)
        itemArr.append(stepArr)
    print(itemArr)


def MakeData():
    y = dict()
    f = open("oo.dat", "w")
    x = dict()
    xx = dict()
    for j in range(0, 10):
        x["initial"] = 1
        for i in range(0, 10):
            x[str(i)] = i
        if j == 0:
            xx["initial"] = x
        xx[str(j)] = x
    json.dump(xx, f)
    print(xx)
    f.close()


def LoadData():
    y = dict()
    xx = dict()
    data = open('oo.dat', 'r')
    y = json.load(data)
    data.close()
    return y


def cal(goa, beg, route):
    route_new = route + distance((obj[goa][0]-obj[beg][0]),
                                 (obj[goa][1]-obj[beg][1]))
    for i in range(goa, 4):
        if goa == 4:
            break
        cal(i, goa, route_new)

    print(route_new)


def LoadData_bck():
    y = dict()
    xx = dict()
    data = open('oo.dat', 'r')
    while 1:
        key = True
        tmpK = ""
        tmpV = ""
        rt_tmp = data.readline()
        if not rt_tmp:
            break
        for i in rt_tmp:
            if i == ":":
                key = False
                continue
            elif i == "\n":
                break
            if key:
                tmpK = tmpK + i
            else:
                tmpV = tmpV + i
        y[tmpK] = tmpV
    yy = y['1'][2]
    data.close()
    return xx


def saveItemBuyDis():
    test = {1, 2, 3, 4, 5, 6}
    test2 = {1, 2, 3, 4, 5, 7}
    icon = [[test, 10], [test2, 20]]
    print(icon[1][0])


# LoadData2()
main()
# MakeData()
