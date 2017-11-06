#! /usr/bin/python3

import matplotlib.pyplot as plt

class Plotter():
	"""docstring for Plotter"""

	"""
	x_range: A tuple or a list (x_min, x_max) to set graph limits
	y_range: Similar to x_range, for y axis
	link_lengths: A list containing lengths of each link, starting
		from the base.
	link_angles_init: Initial link angles. Length of list must be
		equal to link_lengths
	start_cood: A tuple or list with initial end effector coordinates
	end_cood: A tuple or list with desired end effector coordinates
		The above two coordinates are for plotting points only. No
		caculation of link angles takes place in this class
	"""
	def __init__(self, link_lengths, link_angles_init, start_cood, end_cood):
		self.link_lengths = link_lengths
		self.link_angles = link_angles_init
		self.start_cood = start_cood
		self.end_cood = end_cood
		self.obs_coods = []

		self.axis_limit = sum(link_lengths)


	def add_obstacle_cood(self, cood):
		self.obs_coods.append(cood)


	def plot_env(self):
		fig,ax = plt.subplots()

		plt.axis('scaled')
		plt.xlim(-1.2*self.axis_limit, 1.2*self.axis_limit)
		plt.ylim(-1.2*self.axis_limit, 1.2*self.axis_limit)

		plt.axhline(c="0.8")
		plt.axvline(c="0.8")

		circle1 = plt.Circle((0,0), self.link_lengths[0], color='0.8', fill=False)
		circle2 = plt.Circle((0,0), self.link_lengths[0]+self.link_lengths[1], color='0.8', fill=False)
		ax.add_artist(circle1)
		ax.add_artist(circle2)

		plt.plot(*self.start_cood, 'bo')
		plt.annotate("Ps", xy=self.start_cood, xytext=(-15,-15), textcoords='offset points')
		
		plt.plot(*self.end_cood, 'go')
		plt.annotate("Pt", xy=self.end_cood, xytext=(-15,-15), textcoords='offset points')
		
		for i,cood in enumerate(self.obs_coods):
			plt.plot(*cood, 'r^')
			plt.annotate("P"+str(i), xy=cood, xytext=(-15,-15), textcoords='offset points')


	def plot(self):
		self.plot_env()
		plt.show()


	"""
	link_angles_series: A time series 2d numpy array. Each element
		is a link_angles aray, indexed by time
	"""
	def plot_path(self, link_angles_series):
		pass
