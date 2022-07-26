# RLFAP Solver

For this project, I've implemented a solver for the [Radio Link Frequency Assignment Problem](https://miat.inrae.fr/schiex/rlfap.shtml) in Python, with
the help of [AIMA's CSP code](https://github.com/aimacode/aima-python). This is an NP-hard optimization problem, where we aim to provide communication 
channels from limited spectral resources whilst keeping to a minimum the interference suffered by those whishing to communicate in a given radio
communication network.

## CSP Modelling

The variables of this problem are the radio links, their domains are frequency ranges and the associated (binary) constraints are of the form
|x - y| > k, where x and y are variables and k is a positive integer (interference threshold). The goal is to find an assignment such that all
of the constraints are satisfied for a given instance of the problem.

## Implementation

The solver exposes various options to the user: which search algorithm to use, what variable reodering and selection heuristics to apply, which
constraint propagation method to utilize and what timeout limit to impose on the search. The algorithms of interest for this project are:

- Forward Checking ([FC](https://ktiml.mff.cuni.cz/~bartak/constraints/propagation.html#FC))
- Maintaining Arc Consistency ([MAC](https://ktiml.mff.cuni.cz/~bartak/constraints/propagation.html#LA))
- FC + Conflict-Based Backjumping ([CBJ](https://en.wikipedia.org/wiki/Backjumping#Conflict-based_backjumping_(aka_conflict-directed_backjumping_(cbj)))).
- Local Search ([Min-Conflicts](https://en.wikipedia.org/wiki/Min-conflicts_algorithm)), with an optional iteration threshold (max steps). 

Also provided is an implementation of a dynamic weight-based variable reordering heuristic,  called dom-wdeg, which is based on the corresponding papers 
found [here](https://github.com/GeorgeSittas/RLFAP-Solver/tree/main/readings).

## Usage

To run the solver, execute the command `python solve.py`, after configuring it as needed. Instructions are provided inside this script in the form of a
comment. The problem instances that were tested can be found inside the directory `rlfap`. Each instance is described by three text files, prefixed by
`var`, `dom` and `ctr`, respectively, and followed by the id of the instance. Their format is described below:

- Variable (var-prefixed) file: `<num_vars> (<var_id> <dom_id>)+`
- Domain (dom-prefixed) file: `<num_doms> (<dom_id> <dom_size> <dom_values>*)+`
- Constraint (ctr-prefixed) file: `<num_constraints> (<var_id> <var_id> ">" <number>)+`

## Results

The heuristics dom-wdeg and [lcv](https://stanford.edu/~shervine/teaching/cs-221/cheatsheet-variables-models#dynamic-ordering) have been used in all
trials. The per-instance results can be viewed in table form (.png) [here](https://github.com/GeorgeSittas/RLFAP-Solver/tree/main/results). I used
various metrics to analyze the effectiveness of the algorithms, such as:

- Number of visited nodes in the search tree, which is basically the number of variable assignments that were tested. If this value is small, it
means that the program made a small number of re-assignments (backtracks), so it means that the search went well.

- Number of constraint checks during the search. Again, the smaller this value is, the better (the reasoning is similar). This metric gives us a
hint about the quality of the constraint-propagation method that is used, because fewer constraint checks means that the constraints are being
propagated more efficiently, thus leading the program to the solution faster.

- Elapsed CPU time.

- Number of violating variables found after executing the Min-Conflicts algorithm. Since this algorithm might be slow, we're interested in placing
a threshold on the number of the executed iterations, and thus we might end up at a sub-optimal solution after it's terminated. Hence, this metric
gives us a hint about the effectiveness of said algorithm for a given instance.

By examining the resulting tables, one can notice that Min-Conflicts is a bad algorithm choice in our case, which may happen because
the solutions are simply sparsely distributed in the search space. Also, note that only the MAC algorithm was able to find a solution for every
instance of the problem, as well as it seems to be the fastest among the possible choices. The FC-CBJ algorithm combination is an interesting one,
as it provides better results (visited nodes, constraint checks) for some of the instances, compared to MAC, and is generally better than FC.

Finally, the satisfiability of each instance is shown below.

<img src="https://github.com/GeorgeSittas/RLFAP-Solver/blob/main/results/satisfiability.png" width=350>



