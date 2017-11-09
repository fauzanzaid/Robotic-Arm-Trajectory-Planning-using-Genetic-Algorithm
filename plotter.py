#! /usr/bin/python3



import math

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons



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


	def plot_grids(self, ax):
		# X and Y axis
		ax.axhline(c="0.9")
		ax.axvline(c="0.9")

		# Two circles
		circle1 = plt.Circle((0,0), self.link_lengths[0], color='0.9', fill=False)
		circle2 = plt.Circle((0,0), self.link_lengths[0]+self.link_lengths[1], color='0.9', fill=False)
		ax.add_artist(circle1)
		ax.add_artist(circle2)


	def plot_terminals(self, ax):
		ax.plot(*self.start_cood, 'bo')
		ax.plot(*self.end_cood, 'go')
		
		ax.annotate(r'$P_s$', xy=self.start_cood, xytext=(5,-10), textcoords='offset points')
		ax.annotate(r'$P_t$', xy=self.end_cood, xytext=(5,-10), textcoords='offset points')


	def plot_obstacles(self, ax):
		for i,cood in enumerate(self.obs_coods):
			ax.plot(*cood, 'r^')
			ax.annotate(r'$P_{o'+str(i)+r'}$', xy=cood, xytext=(5,-10), textcoords='offset points')


	def plot_links(self, ax, *args):
		if args:
			coods_x, coods_y = args[0]
		else:
			coods_x, coods_y = self.get_coods_from_link_angles()

		[link_object] = ax.plot(coods_x, coods_y, '-mo')
		return link_object


	def plot_links_by_time(self, ax, coods_series, t):
		steps = len(coods_series[0])
		coods_x = coods_series[0][int(t*(steps-1))]
		coods_y = coods_series[1][int(t*(steps-1))]

		return self.plot_links(ax, [coods_x, coods_y])


	def plot_update_links_by_time(self, link, coods_series, t):
		steps = len(coods_series[0])
		coods_x = coods_series[0][int(t*(steps-1))]
		coods_y = coods_series[1][int(t*(steps-1))]

		link.set_xdata(coods_x)
		link.set_ydata(coods_y)


	def env_set_plot_lims(self, ax):
		ax.axis('scaled')
		ax.set_xlim(-1.2*self.axis_limit, 1.2*self.axis_limit)
		ax.set_ylim(-1.2*self.axis_limit, 1.2*self.axis_limit)


	def env_plot(self, ax):
		self.plot_grids(ax)
		self.plot_terminals(ax)
		self.plot_obstacles(ax)
		self.plot_links(ax)
		self.env_set_plot_lims(ax)


	def env_show(self):
		fig,ax = plt.subplots()
		self.env_plot(ax)
		plt.show()


	def plot_end_path(self, ax, xs, ys):
		ax.plot(xs, ys, '--', c="y")


	def plot_joint_path(self, ax, xs, ys):
		ax.plot(xs, ys, '--', c="0.8")


	def transition_set_plot_lims(self, ax):
		ax.axis('scaled')
		ax.set_xlim(-1.2*self.axis_limit, 1.2*self.axis_limit)
		ax.set_ylim(-1.2*self.axis_limit, 1.2*self.axis_limit)



	"""
	link_angles_series: A time series 2d numpy array. Each element
		is a link_angles aray, indexed by time
	"""
	def transition_plot_static(self, ax, coods_series):
		self.plot_grids(ax)
		self.plot_terminals(ax)
		self.plot_obstacles(ax)
		self.transition_set_plot_lims(ax)

		coods_x_series, coods_y_series = coods_series
		self.plot_end_path(ax, coods_x_series.T[-1], coods_y_series.T[-1])
		for xs, ys in zip(coods_x_series.T[:-1], coods_y_series.T[:-1]):
			self.plot_joint_path(ax, xs, ys)


	def transition_show(self, link_angles_series):		
		fig = plt.figure()

		ax_main = fig.add_axes([0.1,0.2,0.8,0.7])
		ax_slider = fig.add_axes([0.1,0.03,0.8,0.03])

		coods_series = self.get_coods_series_from_link_angles_series(link_angles_series)

		self.transition_plot_static(ax_main, coods_series)
		link = self.plot_links_by_time(ax_main, coods_series, 0)


		slider = Slider(ax_slider, "Time", 0, 1, valinit=0)
		def on_slider_upd(val):
			self.plot_update_links_by_time(link, coods_series, val)
			fig.canvas.draw()
		slider.on_changed(on_slider_upd)

		plt.show()


	def get_coods_from_link_angles(self, *args):
		coods_y = [0]
		coods_x = [0]

		if args:
			link_angles = args[0]
		else:
			link_angles = self.link_angles

		angle = 0
		for l,a in zip(self.link_lengths, link_angles):
			angle += a 
			cood_y = coods_y[-1] + l*math.sin(math.radians(angle))
			cood_x = coods_x[-1] + l*math.cos(math.radians(angle))

			coods_y.append(cood_y)
			coods_x.append(cood_x)

		return coods_x, coods_y


	def get_coods_series_from_link_angles_series(self, link_angles_series):
		coods_y_series = []
		coods_x_series = []
		
		for link_angles in link_angles_series:
			coods_x, coods_y = self.get_coods_from_link_angles(link_angles)
			coods_x_series.append(coods_x)
			coods_y_series.append(coods_y)

		coods_x_series = np.array(coods_x_series)
		coods_y_series = np.array(coods_y_series)
		
		return coods_x_series, coods_y_series


