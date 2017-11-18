import numpy as np
import scipy.interpolate as sc
import matplotlib.pyplot as plt
import three_link
import invkin
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


def generate_trajectories(formatted_population, start, end, fitness_calculated):
    '''
    :param sorted_population: (P x K x 2) array of formatted population
    :param start: (x, y) cords of start point
    :param end: (x, y) coords of end point
    :param fitness_calculated: boolean list stating whether a chromosome's fitness has been calculated.
                               only those chromosome's values are calculated, whose points are not valid.
    :return: trajectory_points: a (P x (N+2) x 2) array of all internal and end points
             population_trajectories: list of all population trajectories. Invalid chromosomes have 'False' in their index
    '''
    # Every chromosome's points are seperated and arranged in form of x and y coordinates.
    # It is then arranged in the order of x coordinated. Start and End point coordinates are then added to the array.
    # then the trajectories are generated.
    shape = np.shape(formatted_population)
    left_end, right_end = start, start
    if start[0] < end[0]:
        right_end = end
    else:
        left_end = end

    population_trajectories = [False for g in range(shape[0])]
    trajectory_points = np.zeros([shape[0], shape[1] + 2, shape[2]])
    for i in range(shape[0]):
        if fitness_calculated[i]:
            continue
        ch_with_start = np.insert(formatted_population[i, :, :], 0, left_end, axis=0)
        chrome_all_pts = np.insert(ch_with_start, (shape[1] + 1), right_end, axis=0)
        population_trajectories[i] = sc.PchipInterpolator(chrome_all_pts[:, 0], chrome_all_pts[:, 1])
        trajectory_points[i, :, :] = chrome_all_pts
    return trajectory_points, population_trajectories


def chrome_traj(chrome, start, end):
    sorted_chrome = format(chrome)
    sh = np.shape(sorted_chrome)
    left_end, right_end = start, start
    if start[0] < end[0]:
        right_end = end
    else:
        left_end = end
    K = sh[1]
    ch_with_start = np.insert(sorted_chrome, 0, left_end, axis=1)
    chrome_all_pts = np.insert(ch_with_start, (K + 1), right_end, axis=1)
    ch_x, ch_y = chrome_all_pts[:, :, 0][0], chrome_all_pts[:, :, 1][0]
    trajectory = sc.PchipInterpolator(ch_x, ch_y)
    traj_points = path_points(trajectory, 0.1, start, end)
    return traj_points


def format(population) -> object:
    '''
    :param population: complete population in 2D matrix (P x 2k)
    :return: sorted_population: 3D array (P x k x 2)
    '''
    shape = np.shape(population)
    if len(shape) == 1:
        P = 1
        K = int(shape[0]/2)
    elif len(shape) == 2:
        P = shape[0]
        K = int(shape[1]/2)
    formatted_population = np.zeros([P, K, 2])
    for i in range(P):
        if P == 1:
            chrome = np.reshape(population, [K, 2])
        else:
            chrome = np.reshape(population[i, :], [K, 2])
        chrome_sorted = chrome[chrome[:, 0].argsort()].transpose()
        formatted_population[i, :, :] = chrome_sorted.transpose()
    return formatted_population


def check_point_validity(formatted_population, link_len, start, end) -> list:
    '''
    :param sorted_population: 3D array of sorted population matrix
    :param link1: length of link 1
    :param link2: length of link 2
    :return: validity: list of indexed validity values. could be used for setting fitness to zero.
    '''
    shape = np.shape(formatted_population)
    left_end, right_end = start, start
    if start[0] < end[0]:
        right_end = end
    else:
        left_end = end
    validity = []
    for i in range(shape[0]):
        r = np.linalg.norm(formatted_population[i, :, :], axis=1)
        if np.any(formatted_population[i, :, 0] < left_end[0]):
            validity.append(False)
        elif np.any(formatted_population[i, :, 0] > right_end[0]):
            validity.append(False)
        elif np.all(r > link_len[0]):
            if np.all(r < (sum(link_len))):
                if np.all(formatted_population[i,:,1] > 0):
                    validity.append(True)
                else:
                    validity.append(False)
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
    obstacles = np.array(obstacles)
    # print(trajectory(obstacles[:,0]), obstacles[:,1])

    if np.any(trajectory(obstacles[:,0]) > obstacles[:,1]):  # value of path at x is greater than y coord of point
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

    :return: (N x 2) array of (X, Y) coordinates of points, where N = no. of points
    (N is variable to accomodate for equal disatnce between consecutive points)
    the points are the path points as the arm travels from the start point to the end point.
    """
    # temporary lists to store x and y coordinates
    pt_x = [start[0]]
    pt_y = [start[1]]
    der = y.derivative()

    # iterator point
    x = start[0]

    if start[0] < end[0]:  # start point is on left side
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
                x -= del_x
            else:
                pt_x.append(end[0])
                pt_y.append(end[1])
                break

    points = np.zeros([2, len(pt_x)])
    points[0, :] = np.array(pt_x)
    points[1, :] = np.array(pt_y)

    return points.transpose()


def fitness_population(population, link_len, start_pt, end_pt, obstacles, epsilon, mu, Single=False):
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
    if len(link_len) == 3:
        arm1 = three_link.Arm3Link(link_len)
    elif len(link_len) == 2:
        arm1 = invkin.Arm(link_len)

    if Single == True:
        pop_size = 1
    else:
        pop_size = np.shape(population)[0]

    cost_pop = [np.inf for i in range(pop_size)]  # stores fitness values
    fitness_calculated = [False for i in range(pop_size)]  # stores fitness calculation validity

    formatted_pop = format(population)
    pt_validity = check_point_validity(formatted_pop, link_len, start_pt, end_pt)
    for i in range(pop_size):
        if pt_validity[i] == False:
            cost_pop[i] = np.inf
            fitness_calculated[i] = True

    points, trajectories = generate_trajectories(formatted_pop, start_pt, end_pt, fitness_calculated)
    #print(trajectories)
    traj_points = None
    for i in range(pop_size):
        if fitness_calculated[i] == False:
            traj_points = path_points(trajectories[i], epsilon, start_pt, end_pt)
            # plt.plot(traj_points[:, 0], traj_points[:, 1])
            # t = np.linspace(-4, 4, 100)
            # plt.plot(t, np.sqrt(4 - t**2))
            # plt.plot(t, np.sqrt(16 - t ** 2))
            # plt.show()
            theta = np.array(arm1.time_series(traj_points))
            validity = check_trajectory_validity(trajectories[i], obstacles)
            if validity == False:
                cost_pop[i] = np.inf
            else:
                cost_pop[i] = fitness_chrome(theta, mu)
            fitness_calculated[i] = True

    fitness_pop = 1/np.array(cost_pop)
    #fitness_pop = np.array(cost_pop)

    return np.array(fitness_pop), traj_points


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
        for j in range(len(mu)):
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
    points, trajectories = generate_trajectories(clean_population, start_pt, end_pt)
    check_trajectory_validity(trajectories, obst)
    t = np.linspace(-3, 3, 100)
    for i in range(len(trajectories)):
        ax = plt.plot(t, trajectories[i](t), lw=1)
        ap = plt.plot(points[i, :, 0], points[i, :, 1], 'ro')
    plt.show()


def testing_fitness2():
    #pop_x = np.random.rand(3, 3)*8-4*np.ones(3)
    #pop_y = np.random.rand(3, 3)*4-4*np.ones(3)
    #pop = np.append(pop_x, pop_y)
    #print(pop)
    #pop = np.array([[-2, 2, -1.8, 2, 2, 2], [-1.5, 2.5, -0.5, 3, 2.5, 1]])
    pop = np.array([-1.5, 2.5, -0.5, 3, 2.5, 1])
    link_len = [2,2]
    start = [-4, 0]
    end = [4, 0]
    obst = [0, 5]
    mu = [0.5]
    mat = chrome_traj(pop, start, end)
    fit, traj = fitness_population(pop, link_len, start, end, obst, .1, mu, Single=True)
    #print(traj)

#testing_fitness2()

def test_time():
    #print(timeit.timeit(testing_fitness2(),
     #                   'import numpy as np import scipy.interpolate as sc import matplotlib.pyplot as plt', 10))
    #a = np.ones([1, 4, 3])
    #sh = a.shape
    #print(len(sh), sh,  a)
    testing_fitness2()

#test_time()