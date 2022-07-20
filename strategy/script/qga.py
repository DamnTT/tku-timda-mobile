#!/usr/bin/env python
#########################################################
#                                                       #
#       QUANTUM GENETIC ALGORITHM (24.05.2016)          #
#                                                       #
#               R. Lahoz-Beltra                         #
#                                                       #
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR "AS IS" AND   #
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT #
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY #
# AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  #
# THE SOFWTARE CAN BE USED BY ANYONE SOLELY FOR THE     #
# PURPOSES OF EDUCATION AND RESEARCH.                   #
#                                                       #
#########################################################
from __future__ import print_function
import sys
import math
import time
import json
from itertools import permutations
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from numpy.core.fromnumeric import ptp
from dynamic_reconfigure.server import Server as DynamicReconfigureServer
from strategy.cfg import RobotConfig
import dynamic_reconfigure.client
from pso import PSO


#########################################################
# ALGORITHM PARAMETERS                                  #
#########################################################
N = 30                 # Define here the population size
GENOME = 22             # Define here the chromosome length
GENERATION_MAX = 500   # Define here the maximum number of
# generations/iterations


class Qga(object):
    #########################################################
    # VARIABLES ALGORITHM                                   #
    #########################################################

    def __init__(self, sim=False):
        print("fuxk1")
        self.popSize = N+1
        self.genomeLength = GENOME+1
        self.top_bottom = 3
        self.QuBitZero = np.array([[1], [0]])
        self.QuBitOne = np.array([[0], [1]])
        self.AlphaBeta = np.empty([self.top_bottom])
        self.fitness = np.empty([self.popSize, 2])
        self.probability = np.empty([self.popSize])
        # qpv: quantum chromosome (or population vector, QPV)
        self.qpv = np.empty([self.popSize, self.genomeLength, self.top_bottom])
        self.nqpv = np.empty(
            [self.popSize, self.genomeLength, self.top_bottom])
        # chromosome: classical chromosome
        self.chromosome = np.empty(
            [self.popSize, self.genomeLength], dtype=np.int)
        self.child1 = np.empty(
            [self.popSize, self.genomeLength, self.top_bottom])
        self.child2 = np.empty(
            [self.popSize, self.genomeLength, self.top_bottom])
        self.best_chrom = np.empty([GENERATION_MAX])

        # Initialization global variables
        self.theta = 0
        self.iteration = 0
        self.the_best_chrom = 0
        self.bestStep = []
        self.beststepArr = []
        self.generation = 0
        #########################################################
        # QUANTUM POPULATION INITIALIZATION                     #
        #########################################################

    def Load_sample(self, itemBuy):
        print(itemBuy)
        itemArr = []
        data = open('/home/damn/timda-mobile/test2.dat', 'r')
        self.stepList = json.load(data)
        data.close()

        self.rt = list(permutations(itemBuy, len(itemBuy)))
        self.a = len(self.rt)
        self.genomeLength = len(bin(len(self.rt))) - 1
        print(self.genomeLength)
        print(len(self.rt))
        for _ in range(int(math.pow(2, self.genomeLength-1))-len(self.rt)):
            self.rt.append(None)
        print("Finish data load")

    def Init_population(self):
        self.dclient = dynamic_reconfigure.client.Client(
            "core", timeout=30, config_callback=None)

        cfg = self.dclient.get_configuration()
        self.item = []
        # Hadamard gate
        for i in range(0, int(cfg['ITEM_BUY'])):
            self.item.append(i)
        self.Load_sample(self.item)
        r2 = math.sqrt(2.0)
        h = np.array([[1/r2, 1/r2], [1/r2, -1/r2]])
        # Rotation Q-gate
        self.theta = 0
        rot = np.empty([2, 2])
        # Initial population array (individual x chromosome)
        i = 1
        j = 1
        for i in range(1, self.popSize):
            for j in range(1, self.genomeLength):
                self.theta = np.random.uniform(0, 1)*90
                self.theta = math.radians(self.theta)
                rot[0, 0] = math.cos(self.theta)
                rot[0, 1] = -math.sin(self.theta)
                rot[1, 0] = math.sin(self.theta)
                rot[1, 1] = math.cos(self.theta)
                self.AlphaBeta[0] = rot[0, 0] * \
                    (h[0][0]*self.QuBitZero[0]) + \
                    rot[0, 1]*(h[0][1]*self.QuBitZero[1])
                self.AlphaBeta[1] = rot[1, 0] * \
                    (h[1][0]*self.QuBitZero[0]) + \
                    rot[1, 1]*(h[1][1]*self.QuBitZero[1])
                # alpha squared
                self.qpv[i, j, 0] = np.around(2*pow(self.AlphaBeta[0], 2), 2)
                # beta squared
                self.qpv[i, j, 1] = np.around(2*pow(self.AlphaBeta[1], 2), 2)

    def distance(self, x, y):
        r = math.sqrt(pow(x, 2) * pow(y, 2))
        return r

#########################################################
# SHOW QUANTUM POPULATION                               #
#########################################################

    def Show_population(self):
        i = 1
        j = 1
        for i in range(1, self.popSize):
            print()
            print()
            print("qpv = ", i, " : ")
            print()
            for j in range(1, self.genomeLength):
                print(self.qpv[i, j, 0], end="")
                print(" ", end="")
            print()
            for j in range(1, self.genomeLength):
                print(self.qpv[i, j, 1], end="")
                print(" ", end="")
        print()

#########################################################
# MAKE A MEASURE                                        #
#########################################################
# p_alpha: probability of finding qubit in alpha state

    def Measure(self, p_alpha):
        for i in range(1, self.popSize):
            # print()
            for j in range(1, self.genomeLength):
                if p_alpha <= self.qpv[i, j, 0]:
                    self.chromosome[i, j] = 0
                else:
                    self.chromosome[i, j] = 1
                # print(self.chromosome[i, j], " ", end="")
            # print()

#########################################################
# FITNESS EVALUATION                                    #
#########################################################

    def Fitness_evaluation(self, generation):
        i = 1
        j = 1
        fitness_total = 0
        sum_sqr = 0
        fitness_average = 0
        variance = 0
        stepArr = [0]
        for i in range(1, self.popSize):
            self.fitness[i][0] = 0
            self.fitness[i][1] = 0

#########################################################
# Define your problem in this section. For instance:    #
#                                                       #
# Let f(x)=abs(x-5/2+sin(x)) be a function that takes   #
# values in the range 0<=x<=15. Within this range f(x)  #
# has a maximum value at x=11 (binary is equal to 1011) #
#########################################################
        for i in range(1, self.popSize):
            x = 0
            for j in range(1, self.genomeLength):
                # translate from binary to decimal value
                x = x + self.chromosome[i, j]*pow(2, self.genomeLength-j-1)
                # replaces the value of x in the function f(x)
                # y = np.fabs((x-5)/(2+np.sin(x)))
                # the fitness value is calculated below:
                # (Note that in this example is multiplied
                # by a scale value, e.g. 100)

            y = 0
            stepList = []
            if self.rt[x] is None:
                y = 999999999
                tmp2 = 999999999999999

            else:
                tmp = self.rt[x]
                tmp2 = str(tmp[0])
                for k in range(len(tmp)):
                    # 判斷是否為第一項，之後再加上到初始點的距離
                    if k == 0:
                        y = y + self.stepList["initial"][str(tmp[k])]
                    y = y + self.stepList[str(tmp[k])][str(tmp[k+1])]
                    tmp2 = tmp2 + str(tmp[k+1])
                    # 判斷是否為最後一項，之後再加上對初始點的距離
                    if (k+1) == len(self.rt[x]) - 1:
                        y = y + self.stepList[str(tmp[k+1])]["initial"]
                        break

            stepList.append(x)
            stepList.append(tmp2)
            stepArr.append(stepList)
            self.fitness[i][0] = int(tmp2)
            self.fitness[i][1] = y * 100
#########################################################

            # print("fitness", i, "=", self.fitness[i])
            fitness_total = fitness_total + self.fitness[i][1]
        fitness_average = fitness_total/N
        i = 1
        while i <= N:
            # sum_sqr = sum_sqr+pow(fitness[i]-fitness_average, 2)
            sum_sqr = sum_sqr + pow(self.fitness[i][1]-fitness_average, 2)
            i = i+1
        variance = sum_sqr/N
        if variance <= 1.0e-4:
            variance = 0.0
        # Best chromosome selection
        self.the_best_chrom = 0
        fitness_max = self.fitness[1]
        for i in range(1, self.popSize):
            if self.fitness[i][1] <= fitness_max[1]:
                fitness_max = self.fitness[i]
                self.the_best_chrom = i
        self.bestStep = fitness_max
        self.best_chrom[generation] = self.the_best_chrom
        self.bestArr = stepArr[self.the_best_chrom]
        # Statistical output
        # print("the best num is:", fitness_max[0])
        # print("the distance is :", fitness_max[1]/100)
        f = open(
            "/home/damn/timda-mobile/src/strategy/script/timda-advance/output.dat", "a")
        # f.write(str(generation)+" "+str(fitness_average)+"\n")
        f.write(str(generation)+" "+str(fitness_max[1]/100)+"\n")
        f.write(" \n")
        f.close()
        # if generation == GENERATION_MAX - 1:
        return fitness_max[1]/100
        # else:
        # return 0
        # print("Population size = ", popSize - 1)
        # print("mean fitness = ", fitness_average)
        # print("variance = ", variance, "\n",
        #       " Std. deviation = ", math.sqrt(variance))
        # print("fitness max = ", best_chrom[generation])
        # print("fitness sum = ", fitness_total)

#########################################################
# QUANTUM ROTATION GATE                                 #
#########################################################

    def rotation(self):
        rot = np.empty([2, 2])
        # Lookup table of the rotation angle
        for i in range(1, self.popSize):
            for j in range(1, self.genomeLength):
                if self.fitness[i][1] > self.fitness[int(self.best_chrom[self.generation])][1]:
                  # if chromosome[i,j]==0 and chromosome[best_chrom[generation],j]==0:
                    if self.chromosome[i, j] == 0 and self.chromosome[int(self.best_chrom[self.generation]), j] == 1:
                        # Define the rotation angle: delta_theta (e.g. 0.0785398163)
                        # delta_theta = 0.0785398163
                        delta_theta = 0.0985398163
                        rot[0, 0] = math.cos(delta_theta)
                        rot[0, 1] = -math.sin(delta_theta)
                        rot[1, 0] = math.sin(delta_theta)
                        rot[1, 1] = math.cos(delta_theta)
                        self.nqpv[i, j, 0] = (rot[0, 0]*self.qpv[i, j, 0]) + \
                            (rot[0, 1]*self.qpv[i, j, 1])
                        self.nqpv[i, j, 1] = (rot[1, 0]*self.qpv[i, j, 0]) + \
                            (rot[1, 1]*self.qpv[i, j, 1])
                        self.qpv[i, j, 0] = round(self.nqpv[i, j, 0], 2)
                        self.qpv[i, j, 1] = round(1-self.nqpv[i, j, 0], 2)
                    if self.chromosome[i, j] == 1 and self.chromosome[int(self.best_chrom[self.generation]), j] == 0:
                        # Define the rotation angle: delta_theta (e.g. -0.0785398163)
                        # delta_theta = -0.0785398163
                        delta_theta = -0.0985398163
                        rot[0, 0] = math.cos(delta_theta)
                        rot[0, 1] = -math.sin(delta_theta)
                        rot[1, 0] = math.sin(delta_theta)
                        rot[1, 1] = math.cos(delta_theta)
                        self.nqpv[i, j, 0] = (rot[0, 0]*self.qpv[i, j, 0]) + \
                            (rot[0, 1]*self.qpv[i, j, 1])
                        self.nqpv[i, j, 1] = (rot[1, 0]*self.qpv[i, j, 0]) + \
                            (rot[1, 1]*self.qpv[i, j, 1])
                        self.qpv[i, j, 0] = round(self.nqpv[i, j, 0], 2)
                        self.qpv[i, j, 1] = round(1-self.nqpv[i, j, 0], 2)
                  # if chromosome[i,j]==1 and chromosome[best_chrom[generation],j]==1:

#########################################################
# X-PAULI QUANTUM MUTATION GATE                         #
#########################################################
# pop_mutation_rate: mutation rate in the population
# mutation_rate: probability of a mutation of a bit

    def mutation(self, pop_mutation_rate, mutation_rate):

        for i in range(1, self.popSize):
            up = np.random.random_integers(100)
            up = up/100
            if up <= pop_mutation_rate:
                for j in range(1, self.genomeLength):
                    um = np.random.random_integers(100)
                    um = um/100
                    if um <= mutation_rate:
                        self.nqpv[i, j, 0] = self.qpv[i, j, 1]
                        self.nqpv[i, j, 1] = self.qpv[i, j, 0]
                    else:
                        self.nqpv[i, j, 0] = self.qpv[i, j, 0]
                        self.nqpv[i, j, 1] = self.qpv[i, j, 1]
            else:
                for j in range(1, self.genomeLength):
                    self.nqpv[i, j, 0] = self.qpv[i, j, 0]
                    self.nqpv[i, j, 1] = self.qpv[i, j, 1]
        for i in range(1, self.popSize):
            for j in range(1, self.genomeLength):
                self.qpv[i, j, 0] = self.nqpv[i, j, 0]
                self.qpv[i, j, 1] = self.nqpv[i, j, 1]

#########################################################
# PERFORMANCE GRAPH                                     #
#########################################################
# Read the Docs in http://matplotlib.org/1.4.1/index.html

    def plot_Output(self):
        data = np.loadtxt(
            "/home/damn/timda-mobile/src/strategy/script/timda-advance/output.dat")
        data2 = np.loadtxt(
            "/home/damn/timda-mobile/src/strategy/script/timda-advance/output_pso.dat")
        # plot the first column as x, and second column as y
        x = data[:, 0]
        x2 = data2[:, 0]
        y = data[:, 1]
        y2 = data2[:, 1]
        # f = plt.figure()
        plt.plot(x, y,  color='tab:blue')
        plt.plot(x2, y2, color='tab:orange')
        plt.xlabel('Generation')
        plt.ylabel('Fitness average')
        plt.xlim(0.0, 300.0)
        plt.show()

########################################################
#                                                      #
# MAIN PROGRAM                                         #
#                                                      #
########################################################

    def Q_GA(self):
        start = time.time()

        print("The time used to execute this is given below")

        self.tmpRe = 0
        self.tmp = 0
        self.generation = 0
        # print("============== GENERATION: ", self.generation, " =========================== ")
        # print()
        self.Init_population()
        # self.Show_population()
        self.Measure(0.5)
        self.Fitness_evaluation(self.generation)
        for i in range(0, self.popSize):
            if i == 0:
                for j in range(0, self.genomeLength):
                    self.chromosome[i, j] = 0
            self.chromosome[i, 0] = 0
        while (self.generation < GENERATION_MAX-1):
            # while 1:
            # print("The best of generation [", self.generation,
            #       "] ", self.best_chrom[self.generation])
            # print()
            # print("============== GENERATION: ", self.generation +
            #       1, " =========================== ")
            # print()
            self.rotation()
            self.mutation(0.4, 0.5)
            self.generation = self.generation+1
            self.Measure(0.5)
            re = self.Fitness_evaluation(self.generation)

            if self.tmpRe == re:
                self.tmp = self.tmp + 1
            else:
                self.tmpRe = re
                self.tmp = 0
            if self.tmp >= 200:
                break
        end = time.time()
        print("QGA total time : ", end - start)
        print("the best step is :", self.bestArr[1])
        print("QGA result : {} m".format(re))
        print(
            "------------------------------------------------------------------------------")
        best = [str(a) for a in str(self.bestArr[1])]
        return best

    def fitnessArray(self, x):
        return self.rt[int(x[0])]

    def ppp(self):
        start = time.time()
        xopt, fopt, bestArr = PSO(
            [((self.a-1)*-1, (self.a-1))]).run(threshold=1e-6)
        end = time.time()
        print("PSO total time : ", end - start)
        # print("PSO：{} {}".format(fopt, xopt))
        print("PSO：{} m".format(fopt))
        return bestArr
