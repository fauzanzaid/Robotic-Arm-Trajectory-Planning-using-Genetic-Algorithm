import numpy as np
import scipy.optimize


class Arm3Link:

    def __init__(self,Len=None):

        """Set up the basic parameters of the arm.
        order [link1(lowest link), link2, link3].
        input
            L : np.array
                the arm segment lengths
        """
        # initial joint angles set randomly, they will be updated later
        self.angles = [.3, .3, 0] 
        # A default arm position(set randomly, any angles would work)
        self.default = np.array([np.pi/4, np.pi/4, np.pi/4]) 
        # arm lengths
        self.Len = np.array([1, 1, 1]) if Len is None else Len

    def inv_kin(self, xy):
        """
        Given an (x,y) coords of the hand, return a set of joint angles (q)
        using the scipy.optimize package
        input
            xy : tuple
                the desired xy position of the arm
        returns : list
            the optimal [link 1-shoulder, link 2- elbow, link 3-wrist] angle configuration
        """

        def distance_to_default(q, *args):
            """Objective function to minimize
            Calculates the euclidean distance of arms.The weights allow us to penalise 
            an arm for moving too far from the default position
            input
                q : array
                    the list of current joint angles
            returns : 
                euclidean distance to the default arm position
            """
            weight = [1, 1, 1.3]
            return np.sqrt(np.sum([(qi - q0i)**2 * wi for qi, q0i, wi in zip(q, self.default, weight)]))
            

        def x_constraint(q, xy):
            """Function required as a parameter in the scipy fucntion
            Input
                q : array
                    the list of current joint angles
                xy : array
                    current xy position (not used)
            returns : array
                the difference between current and desired x position
            """
            x = (self.Len[0]*np.cos(q[0]) + self.Len[1]*np.cos(q[0]+q[1]) +self.Len[2]*np.cos(np.sum(q))) - xy[0]
            return x

        def y_constraint(q, xy):

            """Function required as a parameter in the scipy fucntion
            Input
                q : array
                    the list of current joint angles
                xy : array
                    current xy position (not used)
            returns : array
                the difference between current and desired x position
            """
            y = (self.Len[0]*np.sin(q[0]) + self.Len[1]*np.sin(q[0]+q[1]) +self.Len[2]*np.sin(np.sum(q))) - xy[1]
            return y


        return scipy.optimize.fmin_slsqp(func=distance_to_default,x0=self.angles,eqcons=[x_constraint,y_constraint],args=(xy,),iprint=0) 

    def time_series(self,coordinate_series):
        """
        Given a series of coordinates in the form [[x0,y0],
                                                   [x1,y1],
                                                   ...
                                                   [xn,yn]]
        we get the series of link angles [theta1,theta2,theta3]
        input
            coordinate_series: array
        returns : array
            the series of angles for every coordinate provided
        """
        angle_series=[]
        self.angles = self.inv_kin(coordinate_series[0])

        for i in range(len(coordinate_series)):
            angle_series.append(self.inv_kin(coordinate_series[i]))
            self.angles = self.inv_kin(coordinate_series[i])

        return angle_series

def test():

    arm = Arm3Link()
    
    x = [-.75,.5]
    y= [.25,.40]

    coordinate_series = list(zip(x,y))
    arm.time_series(coordinate_series)
    print(arm.time_series(coordinate_series))
    

#test()





