from csp   import *
from math  import inf
from time  import time
from parse import parse_input


def dom_wdeg(assignment, rlfap):
	min_ratio, target_var = inf, None

	for var1 in rlfap.variables:
		if var1 not in assignment:
			unasgn_nbrs = [x for x in rlfap.neighbors[var1] if x not in assignment]
			weight_sum = sum([ rlfap.wgts[ (var1, var2) ] for var2 in unasgn_nbrs])
			curr_ratio = len(rlfap.choices(var1)) / (weight_sum or 1)
			if min_ratio > curr_ratio:
				target_var = var1
				min_ratio = curr_ratio

	return target_var


class RLFAP(CSP):

	def __init__(self, instance, path='./rlfap/'):
		vbls, doms, nbrs, ctrs, wgts = parse_input(path, instance)

		self.ctrs = ctrs # Constraint index
		self.wgts = wgts # Constraint weight index (used for the dom/wdeg heuristic)

		self.nctrchecks = 0
		super().__init__(vbls, doms, nbrs, self.constraint)


	def constraint(self, A, a, B, b):
		"""Check whether A=a, B=b satisfies the constraint between vars A and B."""

		self.nctrchecks += 1
		op, k = self.ctrs[ (A, B) ]
		return abs(a - b) == k if op == '=' else abs(a - b) > k


	def restore_conf_sets(self, var):
		"""Restore conflict sets of future vars, if var is about to be unassigned."""

		for pruned_var in self.prune_history[var]:
			self.conf_set[pruned_var] -= {var}


	def fc(self, var, value, assignment, removals, running_cbj=False):
		"""Prune neighbor values inconsistent with var=value."""

		self.fail = None
		self.support_pruning()

		for B in self.neighbors[var]:
			if B not in assignment:
				for b in self.curr_domains[B][:]:
					if not self.constraints(var, value, B, b):
						self.prune(B, b, removals)

						if running_cbj:
							self.prune_history[var].append(B) # Remember prunes caused by var
							self.conf_set[B].add(var) # var caused a prune in B's domain

				if not self.curr_domains[B]:
					# Update the constraint weights (for dom/wdeg)
					self.wgts[ (var, B) ] += 1
					self.wgts[ (B, var) ] += 1

					self.fail = B
					return False

		return True


	def ac3(self, queue=None, removals=None, arc_heuristic=dom_j_up):
		"""Propagate constraints by enforcing Arc Consistency for the current state."""
		if queue is None:
			queue = { (Xi, Xk) for Xi in self.variables for Xk in self.neighbors[Xi] }

		self.support_pruning()
		queue = arc_heuristic(self, queue)

		while queue:
			(Xi, Xj) = queue.pop()
			revised, _ = revise(self, Xi, Xj, removals)

			if revised:
				if not self.curr_domains[Xi]:
					# Update the constraint weights (for dom/wdeg)
					self.wgts[ (Xi, Xj) ] += 1
					self.wgts[ (Xj, Xi) ] += 1

					return False # RLFAP is inconsistent

				for Xk in self.neighbors[Xi]:
					if Xk != Xj:
						queue.add((Xk, Xi))

		return True # RLFAP is satisfiable


	def mac(self, var, value, assignment, removals, propagate=ac3):
		"""Maintain arc consistency."""
		return propagate(self, { (X, var) for X in self.neighbors[var] }, removals)


	def cbj_search(self, select_var, select_val, infer, timeout=None):
		"""Conflict-directed backjumping search with an optional timeout limit."""

		def backjump(assignment, start_time=None):
			if len(assignment) == len(self.variables):
				return assignment, None
			if start_time is not None and time() - start_time > timeout:
				return 'Timeout', None

			var = select_var(assignment, self)
			for value in select_val(var, assignment, self):
				self.assign(var, value, assignment)
				removals = self.suppose(var, value)

				self.prune_history[var] = [] # Remember vars that are in conflict with var
				if infer(self, var, value, assignment, removals, True):
					result, conf_set = backjump(assignment, start_time)

					if result is not None:
						return result, None # Timeout or a solution's been found

					if var not in conf_set:
						self.restore_conf_sets(var)
						self.restore(removals)
						self.unassign(var, assignment)

						return None, conf_set # Haven't jumped to the target var yet

					# Found target variable (jump point). Merge the conflict sets accordingly
					self.conf_set[var] = self.conf_set[var].union(conf_set) - {var}

				if self.fail:
					# Domain wipeout --> merge conflict sets of current var and failed var
					self.conf_set[var] = self.conf_set[var].union(self.conf_set[self.fail])

				self.restore_conf_sets(var)
				self.restore(removals)
				self.unassign(var, assignment)

			return None, set(self.conf_set[var] - {var}) # Current var failed, jump back

		self.fail = None
		self.prune_history = {}
		self.conf_set = { var : set() for var in self.variables }

		start_time = None if timeout is None else time()
		result, _ = backjump({}, start_time)
		return result


	def bt_search(self, select_var, select_val, infer, timeout=None):
		"""Backtracking search with an optional timeout limit."""

		def backtrack(assignment, start_time=None):
			if len(assignment) == len(self.variables):
				return assignment
			if start_time is not None and time() - start_time > timeout:
				return 'Timeout'

			var = select_var(assignment, self)
			for value in select_val(var, assignment, self):
				if self.nconflicts(var, value, assignment) == 0:
					self.assign(var, value, assignment)
					removals = self.suppose(var, value)

					if infer(self, var, value, assignment, removals):
						result = backtrack(assignment, start_time)
						if result is not None:
							return result

					self.restore(removals)

			self.unassign(var, assignment)
			return None

		start_time = None if timeout is None else time()
		result = backtrack({}, start_time)
		return result

	def min_conflicts(self, max_steps=10000):
		"""Solve a CSP by stochastic Hill Climbing on the number of conflicts."""

		# Generate a complete assignment for all variables (probably with conflicts)
		self.current = current = {}
		for var in self.variables:
			val = min_conflicts_value(self, var, current)
			self.assign(var, val, current)

		# Now repeatedly choose a random conflicted variable and change it
		for i in range(max_steps):
			conflicted = self.conflicted_vars(current)
			if not conflicted:
				return current, 0

			var = random.choice(conflicted)
			val = min_conflicts_value(self, var, current)
			self.assign(var, val, current)

    # Return None as an indication of UNSAT & the number of contraint-violating vars
		return None, len(self.conflicted_vars(current))

	def solve(self, search='bt', select_var=dom_wdeg, select_val=lcv, infer=fc,
		        timeout=1200, max_steps=1000):
		"""Solve the RLFA problem."""

		n_violating_vars = None # Used only for min conflicts (bonus metric)

		if   search == 'bt':
			solution = self.bt_search(select_var, select_val, infer, timeout)
		elif search == 'cbj':
			solution = self.cbj_search(select_var, select_val, infer, timeout)
		elif search == 'min_conflicts':
			solution, n_violating_vars = self.min_conflicts(max_steps)
			n_violating_vars = str(n_violating_vars) + ' out of ' + str(len(self.variables))
		else:
			return None

		return solution, self.nassigns, self.nctrchecks, n_violating_vars
