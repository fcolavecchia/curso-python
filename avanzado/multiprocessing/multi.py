import random
import multiprocessing
import time 

NUM_PROC = 2


def append_to_list(lst, num_items):
	"""
	Appends num_items integers within the range [0-20000000) to the input lst
	"""
	for n in random.sample(range(20000000), num_items):
		lst.append(n)


if __name__ == "__main__":

    jobs = []
    # start_time = time.time()
    
    for i in range(NUM_PROC):
        process = multiprocessing.Process(
        target=append_to_list, 
            args=([], 1000000)
        )
        jobs.append(process)

    for j in jobs:
        j.start()

    for j in jobs:
        j.join()
        
    # end_time = time.time()
    # print(f"It took {end_time-start_time:.2f} seconds to compute")        