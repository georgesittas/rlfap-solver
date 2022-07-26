from os    import listdir
from time  import time
from rlfap import *


# ------------------------------------ Usage ------------------------------------
#
# Solve an RLFAP instance by calling the solve method in one of the following ways:
#
# • solve() to test FC + DOM/WDEG + LCV combo
#
# • solve(infer=RLFAP.mac) to test MAC(AC3) + DOM/WDEG + LCV combo
#
# • solve(search='cbj') to test FC-CBJ + DOM/WDEG + LCV combo
#
# • solve(search='min_conflicts') to test Min-Conflicts with maxsteps=1000
#
# In each of these calls, an optional timeout can be set as solve(..., timeout=X).
# This will force the search to stop after X seconds. Additionally, the backtracking
# search routine supports the heuristics that can be found in csp.py. For example,
# one could also call the solve method as follows:
#
# solve(select_var=RLFAP.mrv, select_val=RLFAP.unordered_domain_values)

def main():

	instances = [ x[3:-4] for x in listdir('./rlfap/') if x[:3] == 'var' ]

	for instance in instances:
		start = time()
		solution, nassigns, nctrchecks, violvars = RLFAP(instance).solve(infer=RLFAP.mac)
		end = time()

		msg = 'Instance ' + instance + ': '
		res = 'UNSAT'       if solution is  None     \
		 else 'UNDECIDABLE' if solution is 'Timeout' \
		 else 'SAT'

		print('\n')
		print(msg + res)
		print('# of assignments: '       + str(nassigns))
		print('# of constraint checks: ' + str(nctrchecks))

		if violvars is not None:
			print('# of violating variables: ' + violvars)

		print('Elapsed time: ' + str((end-start)/60)[:6] + ' min')

	print('\n')


if __name__ == "__main__":
	main()
