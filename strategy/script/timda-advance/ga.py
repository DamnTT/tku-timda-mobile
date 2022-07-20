# 2. GA優化算法
class GA(object):
    # 2.1 初始化
    def __init__(self, population_size, chromosome_num, chromosome_length, max_value, iter_num, pc, pm):
        '''初始化參數
        input:population_size(int):種羣數
              chromosome_num(int):染色體數，對應需要尋優的參數個數
              chromosome_length(int):染色體的基因長度
              max_value(float):作用於二進制基因轉化爲染色體十進制數值
              iter_num(int):迭代次數
              pc(float):交叉概率閾值(0<pc<1)
              pm(float):變異概率閾值(0<pm<1)
        '''
        self.population_size = population_size
        self.choromosome_length = chromosome_length
        self.chromosome_num = chromosome_num
        self.iter_num = iter_num
        self.max_value = max_value
        self.pc = pc  # 一般取值0.4~0.99
        self.pm = pm  # 一般取值0.0001~0.1

    def species_origin(self):
        '''初始化種羣、染色體、基因
        input:self(object):定義的類參數
        output:population(list):種羣
        '''
        population = []
        # 分別初始化兩個染色體
        for i in range(self.chromosome_num):
            tmp1 = []  # 暫存器1，用於暫存一個染色體的全部可能二進制基因取值
            for j in range(self.population_size):
                tmp2 = []  # 暫存器2，用於暫存一個染色體的基因的每一位二進制取值
                for l in range(self.choromosome_length):
                    tmp2.append(random.randint(0, 1))
                tmp1.append(tmp2)
            population.append(tmp1)
        return population
# 2.2 計算適應度函數值

    def translation(self, population):
        '''將染色體的二進制基因轉換爲十進制取值
        input:self(object):定義的類參數
              population(list):種羣
        output:population_decimalism(list):種羣每個染色體取值的十進制數
        '''
        population_decimalism = []
        for i in range(len(population)):
            tmp = []  # 暫存器，用於暫存一個染色體的全部可能十進制取值
            for j in range(len(population[0])):
                total = 0.0
                for l in range(len(population[0][0])):
                    total += population[i][j][l] * (math.pow(2, l))
                tmp.append(total)
            population_decimalism.append(tmp)
        return population_decimalism

    def fitness(self, population):
        '''計算每一組染色體對應的適應度函數值
        input:self(object):定義的類參數
              population(list):種羣
        output:fitness_value(list):每一組染色體對應的適應度函數值
        '''
        fitness = []
        population_decimalism = self.translation(population)
        for i in range(len(population[0])):
            tmp = []  # 暫存器，用於暫存每組染色體十進制數值
            for j in range(len(population)):
                value = population_decimalism[j][i] * self.max_value / \
                    (math.pow(2, self.choromosome_length) - 10)
                tmp.append(value)
            # rbf_SVM 的3-flod交叉驗證平均值爲適應度函數值
            # 防止參數值爲0
            if tmp[0] == 0.0:
                tmp[0] = 0.5
            if tmp[1] == 0.0:
                tmp[1] = 0.5
            rbf_svm = svm.SVC(kernel='rbf', C=abs(tmp[0]), gamma=abs(tmp[1]))
            cv_scores = cross_validation.cross_val_score(
                rbf_svm, trainX, trainY, cv=3, scoring='accuracy')
            fitness.append(cv_scores.mean())

        # 將適應度函數值中爲負數的數值排除
        fitness_value = []
        num = len(fitness)
        for l in range(num):
            if (fitness[l] > 0):
                tmp1 = fitness[l]
            else:
                tmp1 = 0.0
            fitness_value.append(tmp1)
        return fitness_value

# 2.3 選擇操作
    def sum_value(self, fitness_value):
        '''適應度求和
        input:self(object):定義的類參數
              fitness_value(list):每組染色體對應的適應度函數值
        output:total(float):適應度函數值之和
        '''
        total = 0.0
        for i in range(len(fitness_value)):
            total += fitness_value[i]
        return total

    def cumsum(self, fitness1):
        '''計算適應度函數值累加列表
        input:self(object):定義的類參數
              fitness1(list):適應度函數值列表
        output:適應度函數值累加列表
        '''
        # 計算適應度函數值累加列表
        # range(start,stop,[step]) # 倒計數
        for i in range(len(fitness1)-1, -1, -1):
            total = 0.0
            j = 0
            while(j <= i):
                total += fitness1[j]
                j += 1
            fitness1[i] = total

    def selection(self, population, fitness_value):
        '''選擇操作
        input:self(object):定義的類參數
              population(list):當前種羣
              fitness_value(list):每一組染色體對應的適應度函數值
        '''
        new_fitness = []  # 用於存儲適應度函歸一化數值
        total_fitness = self.sum_value(fitness_value)  # 適應度函數值之和
        for i in range(len(fitness_value)):
            new_fitness.append(fitness_value[i] / total_fitness)

        self.cumsum(new_fitness)

        ms = []  # 用於存檔隨機數
        pop_len = len(population[0])  # 種羣數

        for i in range(pop_len):
            ms.append(random.randint(0, 1))
        ms.sort()  # 隨機數從小到大排列

        # 存儲每個染色體的取值指針
        fitin = 0
        newin = 0

        new_population = population

        # 輪盤賭方式選擇染色體
        while newin < pop_len & fitin < pop_len:
            if(ms[newin] < new_fitness[fitin]):
                for j in range(len(population)):
                    new_population[j][newin] = population[j][fitin]
                newin += 1
            else:
                fitin += 1

        population = new_population

# 2.4 交叉操作
    def crossover(self, population):
        '''交叉操作
        input:self(object):定義的類參數
              population(list):當前種羣
        '''
        pop_len = len(population[0])

        for i in range(len(population)):
            for j in range(pop_len - 1):
                if (random.random() < self.pc):
                    cpoint = random.randint(
                        0, len(population[i][j]))  # 隨機選擇基因中的交叉點
                    # 實現相鄰的染色體基因取值的交叉
                    tmp1 = []
                    tmp2 = []
                    # 將tmp1作爲暫存器，暫時存放第i個染色體第j個取值中的前0到cpoint個基因，
                    # 然後再把第i個染色體第j+1個取值中的後面的基因，補充到tem1後面
                    tmp1.extend(population[i][j][0:cpoint])
                    tmp1.extend(population[i][j+1]
                                [cpoint:len(population[i][j])])
                    # 將tmp2作爲暫存器，暫時存放第i個染色體第j+1個取值中的前0到cpoint個基因，
                    # 然後再把第i個染色體第j個取值中的後面的基因，補充到tem2後面
                    tmp2.extend(population[i][j+1][0:cpoint])
                    tmp2.extend(population[i][j][cpoint:len(population[i][j])])
                    # 將交叉後的染色體取值放入新的種羣中
                    population[i][j] = tmp1
                    population[i][j+1] = tmp2
# 2.5 變異操作

    def mutation(self, population):
        '''變異操作
        input:self(object):定義的類參數
              population(list):當前種羣
        '''
        pop_len = len(population[0])  # 種羣數
        Gene_len = len(population[0][0])  # 基因長度
        for i in range(len(population)):
            for j in range(pop_len):
                if (random.random() < self.pm):
                    mpoint = random.randint(0, Gene_len - 1)  # 基因變異位點
                    # 將第mpoint個基因點隨機變異，變爲0或者1
                    if (population[i][j][mpoint] == 1):
                        population[i][j][mpoint] = 0
                    else:
                        population[i][j][mpoint] = 1

# 2.6 找出當前種羣中最好的適應度和對應的參數值
    def best(self, population_decimalism, fitness_value):
        '''找出最好的適應度和對應的參數值
        input:self(object):定義的類參數
              population(list):當前種羣
              fitness_value:當前適應度函數值列表
        output:[bestparameters,bestfitness]:最優參數和最優適應度函數值
        '''
        pop_len = len(population_decimalism[0])
        bestparameters = []  # 用於存儲當前種羣最優適應度函數值對應的參數
        bestfitness = 0.0  # 用於存儲當前種羣最優適應度函數值

        for i in range(0, pop_len):
            tmp = []
            if (fitness_value[i] > bestfitness):
                bestfitness = fitness_value[i]
                for j in range(len(population_decimalism)):
                    tmp.append(abs(
                        population_decimalism[j][i] * self.max_value / (math.pow(2, self.choromosome_length) - 10)))
                    bestparameters = tmp

        return bestparameters, bestfitness

# 2.7 畫出適應度函數值變化圖
    def plot(self, results):
        '''畫圖
        '''
        X = []
        Y = []
        for i in range(self.iter_num):
            X.append(i + 1)
            Y.append(results[i])
        plt.plot(X, Y)
        plt.xlabel('Number of iteration', size=15)
        plt.ylabel('Value of CV', size=15)
        plt.title('GA_RBF_SVM parameter optimization')
        plt.show()

# 2.8 主函數
    def main(self):
        results = []
        parameters = []
        best_fitness = 0.0
        best_parameters = []
        # 初始化種羣
        population = self.species_origin()
        # 迭代參數尋優
        for i in range(self.iter_num):
            # 計算適應函數數值列表
            fitness_value = self.fitness(population)
            # 計算當前種羣每個染色體的10進製取值
            population_decimalism = self.translation(population)
            # 尋找當前種羣最好的參數值和最優適應度函數值
            current_parameters, current_fitness = self.best(
                population_decimalism, fitness_value)
            # 與之前的最優適應度函數值比較，如果更優秀則替換最優適應度函數值和對應的參數
            if current_fitness > best_fitness:
                best_fitness = current_fitness
                best_parameters = current_parameters
            print('iteration is :', i, ';Best parameters:',
                  best_parameters, ';Best fitness', best_fitness)
            results.append(best_fitness)
            parameters.append(best_parameters)

            # 種羣更新
            # 選擇
            self.selection(population, fitness_value)
            # 交叉
            self.crossover(population)
            # 變異
            self.mutation(population)
        results.sort()
        self.plot(results)
        print('Final parameters are :', parameters[-1])
