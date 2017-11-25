#! /usr/bin/python3



import os

import numpy as np
import matplotlib.pyplot as plt

from plotter import Plotter
from genetic_algorithm import GeneticAlgorithm
import trajectory_generation as tg
from invkin import Arm
from three_link import Arm3Link



class ProblemParams:
	"""A struct like class to store problem parameters"""
	def __init__(self, description=None, link_lengths=None, start_cood=None, end_cood=None, obs_coods=None):
		self.description = description
		self.link_lengths = link_lengths
		self.start_cood = start_cood
		self.end_cood = end_cood
		self.obs_coods = obs_coods


preset_params = [
	ProblemParams("Two links, two obstacles", [4,4], [6.5,2.8], [-3.3,5.1], [[-0,5.3],[5.4,3.2]]),
	ProblemParams("Two links, three obstacles", [4,4], [7,2.6], [-5,2.8], [[5,3.8],[1.7,5.8],[-2.5,5.8]]),
	ProblemParams("Three links, two obstacles", [4,4,3], [8.1,4.9], [-7,5.8], [[5.5,7.7],[2.8,8.5]]),
	ProblemParams("Three links, three obstacles", [4,4,3], [8.1,4.9], [-7,5.8], [[5.5,7.7],[2,9],[-2.8,8.5]]),
]


def select_param_method():
	# Clear terminal on win, linux
	os.system('cls' if os.name == 'nt' else 'clear')
	print("Robotic arm trajectory using Genetic Algorithm\n")
	print("Select problem parameters:")
	print("  1: Choose from presets")
	# print("  2: Custom")
	print("\n  q: Quit")

	choice = None
	while choice == None:
		choice = input("Choice: ")
		if choice == 'q':
			return 'q'
		elif choice.isdigit() and 1 <= int(choice) <= 2:
			choice = int(choice)
		else:
			print("Invalid input!")
			choice = None
	return choice


def select_preset_param(preset_params):
	# Clear terminal on win, linux
	os.system('cls' if os.name == 'nt' else 'clear')
	print("Robotic arm trajectory using Genetic Algorithm\n")
	print("Select a preset problem:")
	for i,param in enumerate(preset_params):
		print("  {0}: {1}".format(i+1, param.description))
	print("\n  q: Quit")
	
	choice = None
	while choice == None:
		choice = input("Choice: ")
		if choice == 'q':
			return 'q'
		elif choice.isdigit() and 1 <= int(choice) <= len(preset_params):
			choice = int(choice)
		else:
			print("Invalid input!")
			choice = None
	return choice-1


def select_link_lengths():
	# Clear terminal on win, linux
	os.system('cls' if os.name == 'nt' else 'clear')
	print("Robotic arm trajectory using Genetic Algorithm\n")
	
	links_num = None
	link_lengths = None
	
	while links_num == None:
		links_num = input("Number of links:  ")
		if links_num == 'q':
			return 'q'
		elif links_num.isdigit():
			links_num = int(links_num)
			if links_num < 2 or links_num > 3:
				print("Invalid input! Enter two or three")
				links_num = None
		else:
			print("Invalid input!")
			links_num = None

	link_lengths = []
	for i in range(links_num):
		link_length = None

		while link_length == None:
			link_length = input("Length of link {0}: ".format(i+1))
			if link_length == 'q':
				return 'q'
			elif link_length.isdigit():
				link_length = int(link_length)
				link_lengths.append(link_length)
			else:
				print("Invalid input!")
				link_length = None

	return link_lengths



while True:

	
	plotter = Plotter()

	link_lengths = None
	start_cood = None
	end_cood = None
	obs_coods = None

	ga_genr_2 = 300
	ga_genr_3 = 20
	ga_genr = 10
	ga_pop_sz = 40
	ga_mut_ratio = 0.05
	ga_xov_ratio = 0.30
	ga_mu_2 = [0.5,0.5]
	ga_mu_3 = [0.4,0.3,0.3]
	ga_mu = None
	ga_eps = 0.1

	param_method = select_param_method()

	if param_method == 'q':
		break

	elif param_method == 1:
		param_idx = select_preset_param(preset_params)
		
		if param_idx == 'q':
			break

		else:
			link_lengths = preset_params[param_idx].link_lengths
			start_cood = preset_params[param_idx].start_cood
			end_cood = preset_params[param_idx].end_cood
			obs_coods = preset_params[param_idx].obs_coods

			plotter.link_lengths = link_lengths
			plotter.start_cood = start_cood
			plotter.end_cood = end_cood
			plotter.obs_coods = obs_coods

			plotter.static_show()


	elif param_method == 2:
		link_lengths = select_link_lengths()

		if link_lengths == 'q':
			break

		plotter.link_lengths = link_lengths
		
		plotter.picker_show()
		
		start_cood = plotter.start_cood
		end_cood = plotter.end_cood
		obs_coods = plotter.obs_coods

		if len(obs_coods) < 2:
			print("Select atleast two obstacles!")
			continue


	os.system('cls' if os.name == 'nt' else 'clear')
	print("Robotic arm trajectory using Genetic Algorithm\n")
	print("Running genetic algorithm... ")

	ga_mu = ga_mu_2 if len(link_lengths) == 2 else ga_mu_3
	ga_genr = ga_genr_2 if len(link_lengths) == 2 else ga_genr_3

	ga = GeneticAlgorithm(link_lengths, start_cood, end_cood, obs_coods, tg.fitness_population, ga_mu, ga_eps, ga_pop_sz, ga_mut_ratio, ga_xov_ratio, ga_genr)
	output_chr = ga.run()
	print("Done")

	output_path = tg.chrome_traj(output_chr, start_cood, end_cood)

	arm = Arm(link_lengths) if len(link_lengths) == 2 else Arm3Link(np.array(link_lengths))
	link_angles_series = np.degrees(arm.time_series(output_path))

	# plt.plot(ga.fitness_stats)
	# plt.show()
	
	plotter.transition_show(link_angles_series)

	usr_input = input("\nTry again? [y/n] ")
	if usr_input == 'y':
		continue
	else:
		break
