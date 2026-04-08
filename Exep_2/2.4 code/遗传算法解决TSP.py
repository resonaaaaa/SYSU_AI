import random
import math


class City:
    def __init__(self, index, x, y):
        self.index = index
        self.x = x
        self.y = y

    def distance_to(self, other):
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

class GeneticAlgorithm:
    def __init__(self, pop_size, file_path):
        self.mutation_rate = 0.05
        self.elite_size = int(0.1 * pop_size)
        self.pop_size = pop_size
        self.file_path = file_path
        self.cities = []
        self.read_cities()
        self.population = self.initial_population()

    def read_cities(self):
        with open(self.file_path,'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split()
                if len(parts) < 3:
                    continue
                index = int(parts[0])
                x, y = float(parts[1]), float(parts[2])
                self.cities.append(City(index, x, y))

    # 顺序交叉（OX)
    def crossover(self, parent1, parent2, s, t):
        offspring1 = [None] * len(parent1)
        offspring2 = [None] * len(parent2)
        
        offspring1[s:t] = parent2[s:t]
        offspring2[s:t] = parent1[s:t]
        part1 = [gene for gene in parent1 if gene not in offspring1[s:t]]  #保留父母中不在交叉段的基因
        part2 = [gene for gene in parent2 if gene not in offspring2[s:t]]
        offspring1[:s] = part1[:s]
        offspring1[t:] = part1[s:]
        offspring2[:s] = part2[:s]
        offspring2[t:] = part2[s:]

        return offspring1, offspring2

    #倒置变异
    def mutate(self, s, t, offspring):
        offspring[s:t] = offspring[s:t][::-1]
        return offspring

    def initial_population(self):
        population = []
        #生成一个随机排列作为初始个体
        initial = list(range(len(self.cities)))
        for i in range(self.pop_size):
            indiv = initial[:]
            random.shuffle(indiv) #打乱顺序生成新的个体
            population.append(indiv)
        return population

    def filter(self,fitness_func, threshold):
        for indiv in self.population:
            if fitness_func(indiv) < threshold:
                self.population.remove(indiv)

    def select(self, population, fitness_func):
        total_fitness = sum(fitness_func(indiv) for indiv in population)
        if total_fitness <= 0:
            return random.choice(population)
        pick = random.uniform(0, total_fitness)
        current = 0
        for indiv in population:
            current += fitness_func(indiv)
            if current > pick:  #选择适应度较高的个体
                return indiv
        return population[-1]

    #精英主义，保留优秀个体
    def elitism(self, population, fitness_func):
        sorted_pop = sorted(population, key=fitness_func, reverse=True)
        elite = sorted_pop[: self.elite_size]
        return elite

    def evolve(self, population, fitness_func):
        new_population = self.elitism(population, fitness_func)
        while len(new_population) < len(population):
            parent1 = self.select(population, fitness_func)
            parent2 = self.select(population, fitness_func)
            s, t = sorted(random.sample(range(len(parent1)), 2))  # 随机选择交叉点
            offspring1, offspring2 = self.crossover(parent1, parent2, s, t)
            # 随机变异
            if random.random() < self.mutation_rate:
                offspring1 = self.mutate(s, t, offspring1)
            if random.random() < self.mutation_rate:
                offspring2 = self.mutate(s, t, offspring2)
            new_population.extend([offspring1, offspring2])  # 加入新个体
        selected = new_population[: len(population)]  # 保持种群大小
        return selected

    def fitness(self, individual):
        total_distance = 0
        for i in range(len(individual)):
            city1 = self.cities[individual[i]]
            city2 = self.cities[individual[(i + 1) % len(individual)]]
            total_distance += city1.distance_to(city2)
        return 1 / total_distance if total_distance > 0 else float('inf')  # 距离越小适应度越大

    def route_distance(self, individual):
        total_distance = 0
        for i in range(len(individual)):
            city1 = self.cities[individual[i]]
            city2 = self.cities[individual[(i + 1) % len(individual)]]
            total_distance += city1.distance_to(city2)
        return total_distance

    def best_individual(self, population):
        return max(population, key=self.fitness)

    def get_route(self, individual):
        route = []
        for city in individual:
            route.append(self.cities[city].index)
        return route

    def print_result(self, population, generation=None):
        best = self.best_individual(population)
        best_distance = self.route_distance(best)
        route = self.get_route(best)
        if generation is None:
            print(f"最优路径长度: {best_distance:.4f}")
        else:
            print(f"第 {generation} 代最优路径长度: {best_distance:.4f}")
        print("最优路径:", route)
        return best, best_distance, route

    #主循环，默认迭代300代，默认每50代打印一次结果
    def run(self, generations=300, gap = 50):
        population = self.population
        best = self.best_individual(population)
        best_distance = self.route_distance(best)
        print("初始种群:")
        self.print_result(population, generation=0)

        for generation in range(1, generations + 1):
            population = self.evolve(population, self.fitness)
            current_best = self.best_individual(population)
            current_distance = self.route_distance(current_best)
            if current_distance < best_distance:
                best = current_best
                best_distance = current_distance
            if generation % gap == 0: #每50代打印一次结果
                self.print_result(population, generation=generation)

        self.population = population
        return best, best_distance


def main():
    f_path = "E:\projects\Python\SYSU_AI\Exep_2\\2.4 code\data1.txt"    
    ga = GeneticAlgorithm(pop_size=100, file_path=str(f_path))
    best, best_distance = ga.run(generations=300)
    print("最终结果:")
    print(f"最优路径长度: {best_distance:.4f}")
    print("最优路径:", ga.get_route(best))

if __name__ == "__main__":
    main()
