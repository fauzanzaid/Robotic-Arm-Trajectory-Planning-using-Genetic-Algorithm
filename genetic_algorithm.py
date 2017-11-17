import numpy as np
np.random.seed(1)



class GeneticAlgorithm:
    
    def __init__(self, link_lengths, points_obs, fitness, population_size=120, mutation_percent=0.05, generations=500):
        self.L1 = link_lengths[0]
        self.L2 = link_lengths[1]
        self.points_obs = points_obs
        self.fitness = fitness # fitenss function, takes population as input
        
        self.L = 12
        self.x_min = 0                   
        self.x_max = pow(2,self.L)-1          
        self.y_min = 0                   
        self.y_max = pow(2,self.L)-1          
        
        self.R1 = sum(link_lengths)
        self.R2 = self.L1-sum(link_lengths[1:])
        if self.R2 < 0: self.R2 = 0

        self.population_size = population_size
        self.mutation_percent = mutation_percent
        self.generations = generations
        self.k = self.n_obstacles_interior() + 1

        self.fitness_stats = []


    def n_obstacles_interior(self):
        points_obs = np.array(self.points_obs)
        x_interior = points_obs[:,0]
        y_interior = points_obs[:,1]
        distance = np.sqrt((x_interior-2047.5)*(x_interior-2047.5)+(y_interior-2047.5)*(y_interior-2047.5)) #distance of interior point from centre
        #taking only valid interior points (i.e. points between R1 and R2)
        distance = (distance>self.R2)
        x_interior = x_interior*distance
        x_points = x_interior[x_interior>0]
        return len(x_points)


    def chromosome_init(self):
        chromosome = np.zeros((self.population_size,2*self.k))
        # print(chromosome)

        centre_cood = [2**(self.L-1)-1, 2**(self.L-1)-1]
        distance_max = (self.x_max+1)/2
        distance_min = self.R2/self.R1*distance_max
        
        for i,chrom in enumerate(chromosome):
            chrom_valid = False
            
            while chrom_valid == False:
                random_chrom = np.random.randint(2**self.L,size=[self.k,2])
                distance = np.sqrt((random_chrom[:,0]-centre_cood[0])**2+(random_chrom[:,1]-centre_cood[1])**2)

                if np.all(distance_min < distance) and np.all(distance_max > distance):
                    chrom_valid = True
                    chromosome[i] = np.ravel(random_chrom)

        return chromosome
  

    def run(self):
        chromosome = self.chromosome_init()    #getting initial random chromosome

        fitness_row = self.fitness(chromosome)    #return a matrix which has fitness of respective input chromosomes
        # fitness_row = np.random.rand(self.population_size)  #remove it later on

        # s = 0
        # while(s<self.generations):
        for genr in range(self.generations):

            roulette_wheel_cdf = np.cumsum(fitness_row/np.sum(fitness_row))    #cdf 
            crossover_point = np.random.randint(2*self.k-1)                      #random crossover point 
            index = np.zeros((2))
            new_chromosome = np.zeros((self.population_size,2*self.k))

            for i in range(int(self.population_size/4)):                  #crossover
                a = np.random.rand(2)
                index = np.searchsorted(roulette_wheel_cdf, a)  
                new_chromosome[4*i] = chromosome[index[0]]
                new_chromosome[4*i+1] = chromosome[index[1]]

                new_chromosome[4*i+2,0:crossover_point+1] = chromosome[index[0],0:crossover_point+1]
                new_chromosome[4*i+2,crossover_point+1:2*self.k] = chromosome[index[1],crossover_point+1:2*self.k]
                new_chromosome[4*i+3,0:crossover_point+1] = chromosome[index[1],0:crossover_point+1]
                new_chromosome[4*i+3,crossover_point+1:2*self.k] = chromosome[index[0],crossover_point+1:2*self.k]

            for i in range(self.population_size):                                 #mutation
                if (np.random.rand() < self.mutation_percent):
                    p = np.random.randint(12*2*self.k)
                    q = int(np.floor(p/12))
                    p = int(p - 12*q)

                    binary = list(np.binary_repr(int(new_chromosome[i,q]),12))
                    #flipping the pth binary place
                    if (binary[p] == '0'):
                        binary[p] = '1'
                    elif (binary[p] == '1'):
                        binary[p] = '0'
                    binary_string = "".join(binary)            
                    new_chromosome[i,q] = int(binary_string,2)

            chromosome = new_chromosome
            # s = s+1               #incrementing generation

            fitness_row = self.fitness(chromosome)    #return a matrix which has fitness of respective input chromosomes
            # fitness_row = np.random.rand(self.population_size)  #remove it later on
            self.fitness_stats.append(max(fitness_row))
        

        fitness_row = self.fitness(chromosome)
        max_idx = np.argmax(fitness_row)
        return chromosome[max_idx]
    