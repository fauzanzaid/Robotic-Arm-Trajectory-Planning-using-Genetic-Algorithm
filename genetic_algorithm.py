import numpy as np
np.random.seed(1)



class GeneticAlgorithm:
    
    def __init__(self, link_lengths, points_obs, population_size=120, mutation_percent=0.05, generations=500):
        self.L1 = link_lengths[0]
        self.L2 = link_lengths[1]
        self.points_obs = points_obs
        
        self.population_size = population_size
        self.mutation_percent = mutation_percent
        self.generations = generations
        self.k = self.n_obstacles_interior() + 1
        self.L = 12
        
        self.x_min = 0                   
        self.x_max = pow(2,L)-1          
        self.y_min = 0                   
        self.y_max = pow(2,L)-1          
        self.R1 = self.L1+self.L2           
        self.R2 = self.L1-self.L2



    def n_obstacles_interior(self):
        points_obs = np.array(self.points_obs)
        x_interior = self.points_obs[:,0]
        y_interior = self.points_obs[:,1]
        distance = np.sqrt((x_interior-2047.5)*(x_interior-2047.5)+(y_interior-2047.5)*(y_interior-2047.5)) #distance of interior point from centre
        #taking only valid interior points (i.e. points between R1 and R2)
        distance = (distance>R2)
        x_interior = x_interior*distance
        x_points = x_interior[x_interior>0]
        return len(x_points)


    def chromosome_init(self,x_points,y_points):
        chromosome = np.zeros((self.population_size,2*k))
        a = np.random.randint(len(x_points),size=(self.population_size,k))
        for i in range(k):
            chromosome[:,2*i] = x_points[a[:,i]]
            chromosome[:,2*i+1] = y_points[a[:,i]]
        return chromosome
  

    def run(self):
        Bx, By = np.meshgrid(np.array(range(pow(2,self.L))),np.array(range(pow(2,self.L))))  #input
        x_interior = self.x_min + Bx*((self.x_max-self.x_min)/(pow(2,self.L)-1))
        y_interior = self.y_min + By*((self.y_max-self.y_min)/(pow(2,self.L)-1))

        distance = np.sqrt((x_interior-2047.5)*(x_interior-2047.5)+(y_interior-2047.5)*(y_interior-2047.5)) #distance of interior point from centre
        #taking only valid interior points (i.e. points between R1 and R2)
        distance = ((distance<self.R1)&(distance>self.R2))
        x_interior = x_interior*distance
        x_points = x_interior[x_interior>0]
        y_interior = y_interior*distance
        y_points = y_interior[y_interior>0]

        points = self.k*self.population_size

        chromosome = chromosome_init(x_points,y_points)    #getting initial random chromosome

        #fitness_row = fitness(chromosome)    #return a matrix which has fitness of respective input chromosomes
        fitness_row = np.random.rand(120)  #remove it later on

        s = 0
        while(s<self.generation):

            roulette_wheel_cdf = np.cumsum(fitness_row/np.sum(fitness_row))    #cdf 
            crossover_point = np.random.randint(2*k-1)                      #random crossover point 
            index = np.zeros((2))
            new_chromosome = np.zeros((population_size,2*k))

            for i in range(int(population_size/4)):                  #crossover
                a = np.random.rand(2)
                index = np.searchsorted(roulette_wheel_cdf, a)  
                new_chromosome[4*i] = chromosome[index[0]]
                new_chromosome[4*i+1] = chromosome[index[1]]

                new_chromosome[4*i+2,0:crossover_point+1] = chromosome[index[0],0:crossover_point+1]
                new_chromosome[4*i+2,crossover_point+1:2*k] = chromosome[index[1],crossover_point+1:2*k]
                new_chromosome[4*i+3,0:crossover_point+1] = chromosome[index[1],0:crossover_point+1]
                new_chromosome[4*i+3,crossover_point+1:2*k] = chromosome[index[0],crossover_point+1:2*k]

            for i in range(population_size):                                 #mutation
                if (np.random.rand() < mutation_percent):
                    p = np.random.randint(12*2*k)
                    q = np.floor(p/12)
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
            s = s+1               #incrementing generation

            #fitness_row = fitness(chromosome)    #return a matrix which has fitness of respective input chromosomes
            fitness_row = np.random.rand(120)  #remove it later on
    
            return chromosome
    
