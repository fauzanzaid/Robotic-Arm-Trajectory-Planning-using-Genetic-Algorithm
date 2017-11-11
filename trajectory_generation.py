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


def generate_trajectories(population, start, end):
    #Every chromosome's points are seperated and arranged in form of x and y cooridnates. \
    #It is then arranged in the order of x coordinated. Start and End point coordinates are then added to the array.
    #then the trajectories are generated.
    shape = np.shape(population)
    population_trajectories = []
    sorted_points = np.zeros([shape[0], int(shape[1]/2 + 2), 2])
    for i in range(shape[0]):
        chrome = np.reshape(population[i, :], [int(shape[1]/2), 2])
        chrome_internal_sorted = chrome[chrome[:, 0].argsort()].transpose()
        ch_with_start = np.insert(chrome_internal_sorted, 0, start, axis=1)
        chrome_all_pts = np.insert(ch_with_start, (int(shape[1]/2 +1)) ,end, axis=1)
        print(chrome_all_pts)
        population_trajectories.append(sc.PchipInterpolator(chrome_all_pts[0], chrome_all_pts[1]))
        sorted_points[i, :, :] = chrome_all_pts.transpose()
    return sorted_points, population_trajectories


def testing():
    test_mat = np.array([[1.1, 2.2, 1.5, 2, -1, 1.3],
                         [-2, 1.5, 2, 2, 0, 0.75]])
    start_pt = np.array([-3, 1])
    end_pt = np.array([3, 0.5])
    points, trajectories = generate_trajectories(test_mat, start_pt, end_pt)
    t = np.linspace(-3, 3, 100)
    for i in range(len(test_mat)):
        ax = plt.plot(t, trajectories[i](t), lw=1)
        ap = plt.plot(points[i, :, 0], points[i, :, 1], 'ro')
    plt.show()

testing()


def radius_bounds(chrome):
    k = np.linalg.norm(chrome, axis=1)
    print(k)