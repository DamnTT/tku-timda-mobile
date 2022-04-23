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
import json
from itertools import permutations
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from numpy.core.fromnumeric import ptp


#########################################################
# ALGORITHM PARAMETERS                                  #
#########################################################
N = 50                  # Define here the population size
GENOME = 22              # Define here the chromosome length
GENERATION_MAX = 450    # Define here the maximum number of
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
        self.fitness = np.empty([self.popSize])
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
        self.generation = 0
        #########################################################
        # QUANTUM POPULATION INITIALIZATION                     #
        #########################################################
        self.test = []
        self.Load_sample("1234587")

    # def Load_sample_bck(self):
    #     self.rt = np.zeros(int(math.pow(2, GENOME)))
    #     for i in range(int(math.pow(2, GENOME))):
    #         self.rt[i] = 99999999999
    #     self.data = np.loadtxt(
    #         '/home/damn/timda-mobile/src/strategy/script/timda-advance/output_2.dat')
    #     # plot the first column as x, and second column as y
    #     rt_tmp = self.data[:, 1]
    #     k = 0
    #     for j in rt_tmp:
    #         self.rt[k] = j
    #         k += 1
    #     print("Finish data load")

    def Load_sample(self, itemBuy):
        self.rt = np.zeros(int(math.pow(2, GENOME)))
        for i in range(int(math.pow(2, GENOME))):
            self.rt[i] = 99999999999
        itemArr = []
        data = open('oo.dat', 'r')
        stepList = json.load(data)
        data.close()

        x = list(permutations(itemBuy, len(itemBuy)))
        for i in x:
            stepArr = []
            stepArr.append(i)
            print(i)
            y = 0
            for k in range(len(i)):
                # 判斷是否為第一項，之後再加上到初始點的距離
                if k == 0:
                    y = y + stepList["initial"][i[k+1]]
                    print("initial", " plus ", i[k], "is", y)

                y = y + stepList[i[k]][i[k+1]]
                print(i[k], " plus ", i[k+1], "is", y)

                # 判斷是否為最後一項，之後再加上對初始點的距離
                if (k+1) == len(i)-1:
                    y = y + stepList[i[k+1]]["initial"]
                    print(i[k+1], " plus ", "initial", "is", y)
                    break
            print("total:", y)
            stepArr.append(y)
            itemArr.append(stepArr)
        k = 0
        for j in itemArr:
            self.rt[k] = j[1]
            k = k + 1
        print("Finish data load")

    def Init_population(self):
        # Hadamard gate
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
        for i in range(1, self.popSize):
            self.fitness[i] = 0

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
                y = self.rt[x]
                self.fitness[i] = y * 100
#########################################################

            # print("fitness", i, "=", self.fitness[i])
            fitness_total = fitness_total + self.fitness[i]
        fitness_average = fitness_total/N
        i = 1
        while i <= N:
            # sum_sqr = sum_sqr+pow(fitness[i]-fitness_average, 2)
            sum_sqr = sum_sqr + \
                pow(self.fitness[i]-fitness_average, 2)
            i = i+1
        variance = sum_sqr/N
        if variance <= 1.0e-4:
            variance = 0.0
        # Best chromosome selection
        self.the_best_chrom = 0
        fitness_max = self.fitness[1]
        for i in range(1, self.popSize):
            if self.fitness[i] <= fitness_max:
                fitness_max = self.fitness[i]
                self.the_best_chrom = i
        self.best_chrom[generation] = self.the_best_chrom
        # Statistical output
        print("the best num is:", self.the_best_chrom)
        print("the distance is :", fitness_max/100)
        f = open(
            "/home/damn/timda-mobile/src/strategy/script/timda-advance/output.dat", "a")
        # f.write(str(generation)+" "+str(fitness_average)+"\n")
        f.write(str(generation)+" "+str(fitness_max/100)+"\n")
        f.write(" \n")
        f.close()
        if generation == 449:
            return fitness_max/100
        else:
            return 0
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
                if self.fitness[i] < self.fitness[int(self.best_chrom[self.generation])]:
                  # if chromosome[i,j]==0 and chromosome[best_chrom[generation],j]==0:
                    if self.chromosome[i, j] == 0 and self.chromosome[int(self.best_chrom[self.generation]), j] == 1:
                        # Define the rotation angle: delta_theta (e.g. 0.0785398163)
                        delta_theta = 0.0785398163
                        rot[0, 0] = math.cos(delta_theta)
                        rot[0, 1] = -math.sin(delta_theta)
                        rot[1, 0] = math.sin(delta_theta)
                        rot[1, 1] = math.cos(delta_theta)
                        self.nqpv[i, j, 0] = (rot[0, 0]*self.qpv[i, j, 0]) + \
                            (self.rot[0, 1]*self.qpv[i, j, 1])
                        self.nqpv[i, j, 1] = (rot[1, 0]*self.qpv[i, j, 0]) + \
                            (rot[1, 1]*self.qpv[i, j, 1])
                        self.qpv[i, j, 0] = round(self.nqpv[i, j, 0], 2)
                        self.qpv[i, j, 1] = round(1-self.nqpv[i, j, 0], 2)
                    if self.chromosome[i, j] == 1 and self.chromosome[int(self.best_chrom[self.generation]), j] == 0:
                        # Define the rotation angle: delta_theta (e.g. -0.0785398163)
                        delta_theta = -0.0785398163
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
            '/home/damn/timda-mobile/src/strategy/script/timda-advance/output_2.dat')
        # plot the first column as x, and second column as y
        x = data[:, 0]
        y = data[:, 1]
        # f = plt.figure()
        plt.plot(x, y)
        plt.xlabel('Generation')
        plt.ylabel('Fitness average')
        plt.xlim(0.0, 550.0)
        plt.show()

########################################################
#                                                      #
# MAIN PROGRAM                                         #
#                                                      #
########################################################

    def Q_GA(self):
        self.generation = 0
        print("============== GENERATION: ", self.generation,
              " =========================== ")
        print()
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
            print("The best of generation [",
                  self.generation, "] ", self.best_chrom[self.generation])
            print()
            print("============== GENERATION: ", self.generation +
                  1, " =========================== ")
            print()
            self.rotation()
            self.mutation(0.01, 0.001)
            self.generation = self.generation+1
            self.Measure(0.5)
            re = self.Fitness_evaluation(self.generation)
        return re
