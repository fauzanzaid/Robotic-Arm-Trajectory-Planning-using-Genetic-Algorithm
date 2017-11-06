#! /usr/bin/python3



import math

import matplotlib.pyplot as plt
import numpy as np



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


	def env_plot_grids(self, ax):
		# X and Y axis
		ax.axhline(c="0.8")
		ax.axvline(c="0.8")

		# Two circles
		circle1 = plt.Circle((0,0), self.link_lengths[0], color='0.8', fill=False)
		circle2 = plt.Circle((0,0), self.link_lengths[0]+self.link_lengths[1], color='0.8', fill=False)
		ax.add_artist(circle1)
		ax.add_artist(circle2)


	def env_plot_terminals(self, ax):
		ax.plot(*self.start_cood, 'bo')
		ax.plot(*self.end_cood, 'go')
		
		ax.annotate(r'$P_s$', xy=self.start_cood, xytext=(5,-10), textcoords='offset points')
		ax.annotate(r'$P_t$', xy=self.end_cood, xytext=(5,-10), textcoords='offset points')


	def env_plot_obstacles(self, ax):
		for i,cood in enumerate(self.obs_coods):
			ax.plot(*cood, 'r^')
			ax.annotate(r'$P_{o'+str(i)+r'}$', xy=cood, xytext=(5,-10), textcoords='offset points')


	def env_plot_links(self, ax):
		coods_x, coods_y = self.get_coods_from_link_angles()
		ax.plot(coods_x, coods_y, '-mo')


	def env_set_plot_lims(self, ax):
		ax.axis('scaled')
		ax.set_xlim(-1.2*self.axis_limit, 1.2*self.axis_limit)
		ax.set_ylim(-1.2*self.axis_limit, 1.2*self.axis_limit)


	def env_plot(self, ax):
		self.env_plot_grids(ax)
		self.env_plot_terminals(ax)
		self.env_plot_obstacles(ax)
		self.env_plot_links(ax)
		self.env_set_plot_lims(ax)


	def env_show(self):
		fig,ax = plt.subplots()
		self.env_plot(ax)
		plt.show()


	"""
	link_angles_series: A time series 2d numpy array. Each element
		is a link_angles aray, indexed by time
	"""
	def plot_path(self, link_angles_series):
		pass


	def get_coods_from_link_angles(self):
		coods_y = [0]
		coods_x = [0]

		angle = 0
		for l,a in zip(self.link_lengths, self.link_angles):
			angle += a 
			cood_y = coods_y[-1] + l*math.sin(math.radians(angle))
			cood_x = coods_x[-1] + l*math.cos(math.radians(angle))

			coods_y.append(cood_y)
			coods_x.append(cood_x)

		return coods_x, coods_y


	def get_coods_series_from_link_angles_series(self, link_angles_series):
		pass
