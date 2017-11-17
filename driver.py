#! /usr/bin/python3



import os

from plotter import Plotter
# from genetic_algorithm import GeneticAlgorithm
# import trajectory_generation as tg
# from invkin import Arm



class ProblemParams:
	"""A struct like class to store problem parameters"""
	def __init__(self, description=None, link_lengths=None, start_cood=None, end_cood=None, obs_coods=None):
		self.description = description
		self.link_lengths = link_lengths
		self.start_cood = start_cood
		self.end_cood = end_cood
		self.obs_coods = obs_coods


preset_params = [
	ProblemParams("No obstacles", [4,3], [4,4], [-5,3], []),
	ProblemParams("Two obstacles", [4,3], [4,4], [-5,3], [[2,5],[-3,4]]),
]


def select_param_method():
	# Clear terminal on win, linux
	os.system('cls' if os.name == 'nt' else 'clear')
	print("Robotic arm trajectory using Genetic Algorithm\n")
	print("Select problem parameters:")
	print("  1: Choose from presets")
	print("  2: Custom")
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


	os.system('cls' if os.name == 'nt' else 'clear')
	print("Robotic arm trajectory using Genetic Algorithm\n")
	print("Running genetic algorithm... ")

	# ga = GeneticAlgorithm(link_lengths, obs_coods, 120, 0.05, 500)
	# ga.fitness = tg.fitness
	# output_chrs = ga.run()
	print("Done")

	# link_angles_series = None
	# plotter.transition_show(link_angles_series)


	usr_input = input("\nTry again? [y/n] ")
	if usr_input == 'y':
		continue
	else:
		break
