#!/usr/bin/env python
from __future__ import print_function
import numpy as np
from itertools import permutations
import sys
import math
import time
import json
from itertools import permutations
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from numpy.core.fromnumeric import ptp
from pyswarm import pso
import dynamic_reconfigure.client

#########################################################
# ALGORITHM PARAMETERS                                  #
#########################################################
N = 30                 # Define here the population size
GENOME = 7              # Define here the chromosome length
GENERATION_MAX = 500   # Define here the maximum number of


class PSO:
    pBest = []
    pBestFitness = []
    gBest = None
    gBestFitness = np.inf

    # 初始化
    def __init__(self, bounds, swarmSize=100, w=0.5, wp=0.5, wg=0.5):
        '''
        v = w*v + wp*(pBest-x) + wg*(gBest-x)
        '''
        self.dclient = dynamic_reconfigure.client.Client(
            "core", timeout=30, config_callback=None)

        cfg = self.dclient.get_configuration()
        self.item = []
        # Hadamard gate
        j = 1
        for i in range(0, int(cfg['ITEM_BUY'])):
            self.item.append(i)
        # self.item = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.Load_sample_pso(self.item)
        self.swarmSize = swarmSize
        self.fitness = self.fitnessArray
        self.pNum = len(bounds)
        self.bounds = bounds
        self.w = w
        self.wp = wp
        self.wg = wg

        # 初始化粒子和速度
        self.particles = np.zeros((self.swarmSize, self.pNum))

        self.v = np.zeros((self.swarmSize, self.pNum))
        for i, b in enumerate(self.bounds):
            self.particles[:, i] = np.random.uniform(
                b[0], b[1], self.swarmSize)
            self.v[:, i] = np.random.uniform(-b[1] +
                                             b[0], b[1]-b[0], self.swarmSize)

        # 初始化 fitness
        self.pBest = np.zeros((self.swarmSize, self.pNum))
        self.pBestFitness = np.ones(self.swarmSize) * np.inf
        self.updateFitness()

    def fitnessArray(self, x):
        return self.rt[int(x[0])]

    def Load_sample_pso(self, itemBuy):
        # for i in range(int(math.pow(2, GENOME))):
        #     self.rt[i] = float("inf")

        self.itemArr = []
        data = open('/home/damn/timda-mobile/test2.dat', 'r')
        stepList = json.load(data)
        data.close()

        x = list(permutations(itemBuy, len(itemBuy)))
        self.rt = np.zeros(len(x))
        for i in x:
            stepArr = []
            stepArr.append(i)
            # print(i)
            y = 0
            for k in range(len(i)):
                # 判斷是否為第一項，之後再加上到初始點的距離
                if k == 0:
                    y = y + stepList["initial"][str(i[k])]
                y = y + stepList[str(i[k])][str(i[k+1])]
                # 判斷是否為最後一項，之後再加上對初始點的距離
                if (k+1) == len(i)-1:
                    y = y + stepList[str(i[k+1])]["initial"]
                    break
            stepArr.append(y)
            self.itemArr.append(stepArr)
        k = 0
        for j in self.itemArr:
            self.rt[k] = j[1]
            k = k + 1

    # 更新 fitness
    def updateFitness(self):
        for i, p in enumerate(self.particles):
            fit = self.fitness(p)
            if fit < self.pBestFitness[i]:
                self.pBest[i] = p
                self.pBestFitness[i] = fit

                if fit < self.gBestFitness:
                    self.gBest = p
                    self.gBestFitness = fit

    def run(self, threshold=0.01, updateThreshold=1e-4, maxiter=200):
        n = 0
        generation = 0
        while self.gBestFitness > threshold and n < maxiter:
            # 更新粒子速度
            rp = np.random.rand()
            rg = np.random.rand()
            self.v = self.w*self.v + self.wp*rp * \
                (self.pBest-self.particles) + \
                self.wg*rg*(self.gBest-self.particles)

            # 更新粒子
            self.particles = self.particles + self.v
            for i, b in enumerate(self.bounds):
                self.particles[:, i] = np.clip(
                    self.particles[:, i], b[0], b[1])

            # 計算 fitness
            old = self.gBestFitness
            self.updateFitness()

            f = open(
                "/home/damn/timda-mobile/src/strategy/script/timda-advance/output_pso.dat", "a")
            # f.write(str(generation)+" "+str(fitness_average)+"\n")
            f.write(str(generation)+" "+str(self.gBestFitness)+"\n")
            f.write(" \n")
            f.close()

            # 若更新小於 0.001，持續 maxiter 次，則中止

            if old == self.gBestFitness:
                n += 1
            else:
                n = 0
            if n > maxiter:
                break
            generation += 1
        # print("gBest:", self.gBest)
        # print("gBestFitness:", self.gBestFitness)
        print("the best step:", self.itemArr[int(self.gBest)][0])

        return self.gBest, self.gBestFitness, self.itemArr[int(self.gBest)][0]

        # xopt, fopt = pso(func=fitness, lb=(-1e10,-1e10,-1e10), ub=(1e10,1e10,1e10))
        # print("套件：{} {}".format(fopt, xopt))
