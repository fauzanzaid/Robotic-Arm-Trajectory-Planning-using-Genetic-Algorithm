import numpy as np
import scipy.interpolate as sc
import matplotlib.pyplot as plt
import three_link
import timeit

'''
generate_trajectories(sorted_population, start, end) : 
    population - matrix of (interlaced x and y coordinates of internal points) of each chromosome of the population. 
                 Each row contains 1 chromosome
    start - x and y coordinates of start point
    end - x and y coordinates of end point
    outputs - list of interpolated functions for each chromosome (list of PchipInterpolator objects)
            - points are also returned.
format(population):
    takes a population matrix andconverts into a 3D matrix for better use for generate_trajectories function.

check_point_validity(sorted_population, link1, link2)    
'''


def generate_trajectories(sorted_population, start, end, fitness_calculated):
    # Every chromosome's points are seperated and arranged in form of x and y cooridnates. \
    # It is then arranged in the order of x coordinated. Start and End point coordinates are then added to the array.
    # then the trajectories are generated.
    shape = np.shape(sorted_population)
    left_end, right_end = start, start
    if start[0] < end[0]:
        right_end = end
    else:
        left_end = end
    population_trajectories = []
    trajectory_points = np.zeros([shape[0], shape[1] + 2, shape[2]])
    for i in range(shape[0]):
        if fitness_calculated == True:
            continue
        ch_with_start = np.insert(sorted_population[i, :, :], 0, left_end, axis=0)
        chrome_all_pts = np.insert(ch_with_start, (shape[1] + 1), right_end, axis=0)

        population_trajectories.append(sc.PchipInterpolator(chrome_all_pts[:, 0], chrome_all_pts[:, 1]))
        trajectory_points[i, :, :] = chrome_all_pts
    return trajectory_points, population_trajectories


def format(population) -> object:
    '''
    :param population: complete population in 2D matrix (P x 2k)
    :return: sorted_population: 3D array (P x k x 2)
    '''
    shape = np.shape(population)
    formatted_population = np.zeros([shape[0], int(shape[1] / 2), 2])
    for i in range(shape[0]):
        chrome = np.reshape(population[i, :], [int(shape[1] / 2), 2])
        chrome_sorted = chrome[chrome[:, 0].argsort()].transpose()
        formatted_population[i, :, :] = chrome_sorted.transpose()
    return formatted_population


def check_point_validity(formatted_population, link_len) -> list:
    '''
    :param sorted_population: 3D array of sorted population matrix
    :param link1: length of link 1
    :param link2: length of link 2
    :return: validity: list of indexed validity values. could be used for setting fitness to zero.
    '''
    shape = np.shape(formatted_population)
    validity = []
    for i in range(shape[0]):
        r = np.linalg.norm(formatted_population[i, :, :], axis=1)
        if np.all(r > link_len[0]):
            if np.all(r < (sum(link_len))):
                validity.append(True)
            else:
                validity.append(False)
        else:
            validity.append(False)

    return validity


def check_trajectory_validity(trajectory, obstacles):
    '''
    :param trajectory:
    :param obstacles: (x, y) coordinates in the form of :   [x1, x2, ... xn]  (2 x N matrix)
                                                            [y1, y2, ... yn]
    :return: single boolean value of 'validity'
    '''

    if np.any(trajectory(obstacles[0]) > obstacles[1]):  # value of path at x is greater than y coord of point
        validity = False
    else:
        validity = True
    return validity


def path_points(y, epsilon, start, end):
    """
    :param y: PchipInterpolator object for chromosome
    :param epsilon: parameter for distance between points
    :param start: (x, y) coordinates of start point
    :param end: (x, y) coordinates of end point
    epsilon usage: increasing it will improve resolution at the cost of more points to work on.
                   decreasing it will improve computation time at the cost of resolution

    :return: (2 x N) array of (X, Y) coordinates of points, where N = no. of points
    (N is variable to accomodate for equal disatnce between consecutive points)
    """
    # temporary lists to store x and y coordinates
    pt_x = [start[0]]
    pt_y = [start[1]]
    der = y.derivative()

    # iterator point
    x = start[0]

    if start[0] < end[0]:
        while x < end[0]:
            del_x = epsilon / np.sqrt(der(x) ** 2 + 1)
            if (x + del_x) < end[0]:
                pt_x.append(x + del_x)
                pt_y.append(y(x + del_x))
                x += del_x
            else:
                pt_x.append(end[0])
                pt_y.append(end[1])
                break
    else:  # end point on left side
        while x > end[0]:
            del_x = epsilon / np.sqrt(der(x) ** 2 + 1)
            if (x - del_x) > end[0]:
                pt_x.append(x - del_x)
                pt_y.append(y(x - del_x))
                x += del_x
            else:
                pt_x.append(end[0])
                pt_y.append(end[1])
                break

    points = np.zeros([2, len(pt_x)])
    points[0, :] = np.array(pt_x)
    points[1, :] = np.array(pt_y)

    return points.transpose()


def fitness_population(population, link_len, start_pt, end_pt, obstacles, epsilon, mu):
    """
    Envelope function for complete fitness calculation
    Order of operations:
    1. point checking       (set fitness to zero for invalid)
    2. path interpolation
    3. path discretization
    4. reverse kinematics on path
    5. Path checking        (check order here)
    5. fitness calculation
    """
    arm1 = three_link.Arm3Link(link_len)

    pop_size = np.shape(population)[0]

    cost_pop = [np.inf for i in range(pop_size)]  # stores fitness values
    fitness_calculated = [False for i in range(pop_size)]  # stores fitness calculation validity

    formatted_pop = format(population)
    pt_validity = check_point_validity(formatted_pop, link_len)
    for i in range(len(fitness_calculated)):
        if pt_validity[i] == False:
            cost_pop[i] = np.inf
            fitness_calculated[i] = True

    points, trajectories = generate_trajectories(formatted_pop, start_pt, end_pt, fitness_calculated)

    for i in range(pop_size):
        traj_points = path_points(trajectories[i], epsilon, start_pt, end_pt)

        theta = np.array(arm1.time_series(traj_points))

        validity = check_trajectory_validity(trajectories[i], obstacles)
        if validity == False:
            cost_pop[i] = np.inf
            fitness_calculated[i] = True
        else:
            cost_pop[i] = fitness_chrome(theta, mu)
            fitness_calculated[i] = True

    fitness_pop = 1/np.array(cost_pop)
        
    return np.array(fitness_pop)


def fitness_chrome(theta, mu):
    # check for mu dependency on links
    '''
    :param theta: 2 x N matrix of link angles at discrete points
    :param mu: fitness parameters' list. see initial note for setting mu
    :return: fitness value of the chromosome
    theta in format of
    [ th11 th12 th13 th14 ... th1n]     link 1 angles
    [ th21 th22 th23 th24 ... th2n]     link 2 angles
    theta1 and theta 2 are at discrete points on the path.
    internal variables:
    div = no. of theta divisions, 1 dimension of theta matrix
    '''
    # check this while changing code for different input format

    theta = theta.T
    div = np.shape(theta)[1]
    theta_i = theta[:, 0:div - 2]
    theta_j = theta[:, 1:div - 1]
    del_theta = abs(theta_j - theta_i)
    fitness = 0
    for i in range(div - 2):
        for j in len(mu):
            fitness += mu[j] * theta[j, i]
    return fitness


def testing_fitness():
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


def testing_fitness2():

    pop = np.array([[-2, 2, -1.8, 2, 1, 1]])
    print(fitness_population(pop, [2, 2], [-4, 0], [4, 0], [0, 5], .1, .5))

print(timeit.timeit(testing_fitness2(), 'import numpy as np import scipy.interpolate as sc import matplotlib.pyplot as plt', 10))
