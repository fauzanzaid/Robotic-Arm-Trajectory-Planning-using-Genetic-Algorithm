import numpy as np
import scipy.interpolate as sc
import matplotlib.pyplot as plt

'''
generate_trajectories(population, start, end) : 
    population - matrix of (interlaced x and y coordinates of internal points) of each chromosome of the population. 
                 Each row contains 1 chromosome
    start - x and y coordinates of start point
    end - x and y coordinates of end point
    outputs - list of interpolated functions for each chromosome (list of PchipInterpolator objects)
            - points are also returned.
    
'''


def generate_trajectories(sorted_population, start, end):
    #Every chromosome's points are seperated and arranged in form of x and y cooridnates. \
    #It is then arranged in the order of x coordinated. Start and End point coordinates are then added to the array.
    #then the trajectories are generated.
    shape = np.shape(sorted_population)
    population_trajectories = []
    trajectory_points = np.zeros([shape[0], shape[1]+2, shape[2]])
    for i in range(shape[0]):
        ch_with_start = np.insert(sorted_population[i, :, :], 0, start, axis=0)
        chrome_all_pts = np.insert(ch_with_start, (shape[1] + 1), end, axis=0)
        population_trajectories.append(sc.PchipInterpolator(chrome_all_pts[:, 0], chrome_all_pts[:, 1]))
        trajectory_points[i, :, :] = chrome_all_pts
    return trajectory_points, population_trajectories


def format(population) -> object:
    shape = np.shape(population)
    sorted_population = np.zeros([shape[0], int(shape[1]/2), 2])
    for i in range(shape[0]):
        chrome = np.reshape(population[i, :], [int(shape[1]/2), 2])
        chrome_sorted = chrome[chrome[:, 0].argsort()].transpose()
        sorted_population[i, :, :] = chrome_sorted.transpose()
    return sorted_population


def check_point_validity(sorted_population, link1, link2) -> list:
    shape = np.shape(sorted_population)
    validity = []
    for i in range(shape[0]):
        r = np.linalg.norm(sorted_population[i, :, :], axis=1)
        if np.all(r > link1):
            if np.all(r < (link1+link2)):
                validity.append(True)
            else:
                validity.append(False)
        else:
            validity.append(False)
    return validity


def cleanse_chromosomes(sorted_population, validity):
    size = len(validity)
    print(sorted_population, '\n', validity)
    clean_population = sorted_population
    for i in range(size):
        if validity[size-i-1] == False:
            clean_population = np.delete(clean_population, (size-i-1), axis=0)
    return clean_population


def check_trajectory_validity(trajectories, obstacles):
    n = np.shape(obstacles)
    validity = [True for x in range(len(trajectories))]
    for i in range(n[0]):
        for path in trajectories:
                if path(obstacles[i][0]) > obstacles[i][1]:            #value of path at x is greater than y coord of point
                    validity[path] = False
                else:
                    continue
    print(validity)


def testing():
    test_mat = np.array([[1.1, 2.2, 1.5, 2, -1, 1.3],
                         [-2, 1.5, 2, 2, 0, 0.75],
                         [0.5, 0.5, 1, 0.7, -2, 0.5]])
    start_pt = np.array([-3, 1])
    end_pt = np.array([3, 0.5])
    obst = np.array([2, 4])
    link1 = 1
    link2 = 3
    sorted_mat = format(test_mat)
    v = check_point_validity(sorted_mat, link1, link2)
    clean_population = cleanse_chromosomes(sorted_mat, v)
    points, trajectories = generate_trajectories(clean_population, start_pt, end_pt)
    check_trajectory_validity(trajectories, obst)
    t = np.linspace(-3, 3, 100)
    for i in range(len(trajectories)):
        ax = plt.plot(t, trajectories[i](t), lw=1)
        ap = plt.plot(points[i, :, 0], points[i, :, 1], 'ro')
    plt.show()

testing()




def radius_bounds(chrome):
    k = np.linalg.norm(chrome, axis=1)
    print(k)