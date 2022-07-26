def parse_input(path, instance_name):
	"""Read and parse rlfap input files

	path -- absolute or relative path used to locate the input directory
	instance_name -- the instance input to be parsed (eg '2-f24')

	Returns: vbls, doms, nbrs, ctrs and wgts. These are:

	vbls -- [ var_id1, var_id2, var_id3, ...]
	doms -- { var_id : [val1, val2, val3, ...] }
	nbrs -- { var_id : [var_id1, var_id2, var_id3, ...] }
	ctrs -- { (var_id1, var_id2) : (op, k) }  (eg (0, 1) : ('=', 238))
	wgts -- { (var_id1, var_id2) : 1 } (auxiliary --used for dom/wdeg)
	"""

	var_file = open(path + 'var' + instance_name + '.txt', 'r')
	dom_file = open(path + 'dom' + instance_name + '.txt', 'r')
	ctr_file = open(path + 'ctr' + instance_name + '.txt', 'r')

	var_lines = var_file.readlines()
	dom_lines = dom_file.readlines()
	ctr_lines = ctr_file.readlines()

	var_file.close()
	dom_file.close()
	ctr_file.close()

	# Assumption: variables are labeled in increasing order, starting from 0
	vbls = [ var_id for var_id in range(int(var_lines[0])) ]

	domains = {} # { <domain_id> : <list of values for this domain> }
	for dom_line in dom_lines[1:]:
		tokens = dom_line.split(' ')
		domains[ int(tokens[0]) ] = [ int(val) for val in tokens[2:] ]

	doms = {}
	for var_line in var_lines[1:]:
		tokens = var_line.split(' ')
		doms[ int(tokens[0]) ] = domains[ int(tokens[1]) ]

	nbrs = {}
	ctrs = {}
	wgts = {}

	# Note that we have an undirected constraint graph for an RLFAP
	for ctr_line in ctr_lines[1:]:
		tokens = ctr_line.split(' ')

		ctrs[ (int(tokens[0]), int(tokens[1])) ] = (tokens[2], int(tokens[3]))
		wgts[ (int(tokens[0]), int(tokens[1])) ] = 1
		ctrs[ (int(tokens[1]), int(tokens[0])) ] = (tokens[2], int(tokens[3]))
		wgts[ (int(tokens[1]), int(tokens[0])) ] = 1

		if int(tokens[0]) not in nbrs:
			nbrs[ int(tokens[0]) ] = []
		if int(tokens[1]) not in nbrs:
			nbrs[ int(tokens[1]) ] = []

		nbrs[ int(tokens[0]) ].append(int(tokens[1]))
		nbrs[ int(tokens[1]) ].append(int(tokens[0]))


	return vbls, doms, nbrs, ctrs, wgts
