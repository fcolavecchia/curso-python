
import time
import random


def append_to_list(lst, num_items):
	"""
	Appends num_items integers within the range [0-20000000) to the input lst
	"""
	for n in random.sample(range(20000000), num_items):
		lst.append(n)


if __name__ == "__main__":
    
	# start_time = time.time()

	for i in range(2):
		append_to_list([], 1000000)
	
	# end_time = time.time()
	# print(f"It took {end_time-start_time:.2f} seconds to compute")