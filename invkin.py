import math
import numpy as np

def div(a,b):
        return a/b if b is not 0 else math.inf if a>0 else -math.inf

class Arm :
    '''
    Class to define arm parameters
    Input: arm lenghts , initial position of end arm(angles of each arm) , final (x,y) coordinates of end effector
    Output: inv_kin() returns the angles(in radians) for a given (x,y) position , get_position(angles(radians)) returns the (x,y) coordinates
            for a given set of angles
    '''
    def __init__(self,arm_lens,intial_position,final_position):

        self.arm_lens = arm_lens
        self.intial_position = intial_position
        self.final_position = final_position

    def get_position(self,angles):

        x = self.arm_lens[0]*np.cos(angles[0]) + self.arm_lens[1]* np.cos(angles[0]+angles[1])
        y = self.arm_lens[0]*np.sin(angles[0]) + self.arm_lens[1]* np.sin(angles[0]+angles[1])
        return x,y

    def inv_kin(self,final_coords=None):
        if final_coords == None:
            final_coords = self.final_position
        # definition of a division to allow for the case division with 0
        D = div( (final_coords[0]**2 + final_coords[1]**2 - self.arm_lens[0]**2 - self.arm_lens[1]**2), 2*self.arm_lens[0]*self.arm_lens[1] )
        #final angles
        angles = [0,0]
        #use of atan to use the range(-pi,pi) rather than (0,pi/2)
        temp = math.atan2( (1-(D**2))**(1/2),D  )
        angles[1] = temp if temp>=0 else -temp
        angles[0] = math.atan2(final_coords[1],final_coords[0]) - math.atan2( self.arm_lens[1]*np.sin(angles[1]), self.arm_lens[0]+ self.arm_lens[1]*np.cos(angles[1]) )
        return angles

    def time_series(self,coordinate_series):
        angle_series=[]
        for i in range(len(coordinate_series)):
            angle_series.append(self.inv_kin(coordinate_series[i]))
        return angle_series
def test():

    initialangles = [.349 , .349]
    lengths = [4,4]
    initialPos = [0,0]
    Arm1 = Arm(lengths,initialangles,[4,4])

    print(Arm1.inv_kin())
    
    print(Arm1.get_position(Arm1.inv_kin()))
    
    series = [[2,2],[3,3],[4,4]]
    print(Arm1.time_series(series))

test()
