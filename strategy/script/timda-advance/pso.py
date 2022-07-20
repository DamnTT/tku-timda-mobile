import numpy as np
from pyswarm import pso
 
class PSO:
    pBest = []
    pBestFitness = []
    gBest = None
    gBestFitness = np.inf
    
    # 初始化
    def __init__(self, fitness, bounds, swarmSize=100, w=0.5, wp=0.5, wg=0.5):
        '''
        v = w*v + wp*(pBest-x) + wg*(gBest-x)
        '''
        self.swarmSize = swarmSize
        self.fitness = fitness
        self.pNum = len(bounds)
        self.bounds = bounds
        self.w = w
        self.wp = wp
        self.wg = wg
        
        # 初始化粒子和速度
        self.particles = np.zeros((self.swarmSize, self.pNum))
        
        self.v = np.zeros((self.swarmSize, self.pNum))
        for i, b in enumerate(self.bounds):
            self.particles[:,i] = np.random.uniform(b[0], b[1], self.swarmSize)
            self.v[:,i] = np.random.uniform(-b[1]+b[0], b[1]-b[0], self.swarmSize)
 
        # 初始化 fitness
        self.pBest = np.zeros((self.swarmSize, self.pNum))
        self.pBestFitness = np.ones(self.swarmSize) * np.inf
        self.updateFitness()
        
    
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
        
        
    def run(self, threshold=0.01, updateThreshold=1e-4, maxiter=20):
        n = 0
        while self.gBestFitness > threshold and n < maxiter:
            # 更新粒子速度
            rp = np.random.rand()
            rg = np.random.rand()
            self.v = self.w*self.v + self.wp*rp*(self.pBest-self.particles) + self.wg*rg*(self.gBest-self.particles)
            
            # 更新粒子
            self.particles = self.particles + self.v
            for i, b in enumerate(self.bounds):
                self.particles[:,i] = np.clip(self.particles[:,i], b[0], b[1])
            
            # 計算 fitness
            old = self.gBestFitness
            self.updateFitness()
            
            # 若更新小於 0.001，持續 maxiter 次，則中止
            if old - self.gBestFitness < 0.001:
                n += 1
            else:
                n = 0
            if n > maxiter:
                break
            
        return self.gBest, self.gBestFitness
        
if __name__ == "__main__":
    def fitness(x):
        return (x[0]-5)**2 + (x[1]-10)**2 + (x[2]+10)**2
 
    xopt, fopt = PSO(fitness, [(-1e10,1e10), (-1e10,1e10), (-1e10,1e10)]).run(threshold=1e-6)
    print("自製：{} {}".format(fopt, xopt))
    
    xopt, fopt = pso(func=fitness, lb=(-1e10,-1e10,-1e10), ub=(1e10,1e10,1e10))
    print("套件：{} {}".format(fopt, xopt))