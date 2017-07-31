GECODE_PREFIX = "mzn-gecode -p 9 -s"
REPEAT = 1 # How many times to repeat each run
INT_VERSION = false
NUMBER_OF_VERTICES = 10
SIZE_OF_CLIQUE = ""
EDGE_PROBABILITY_RANGE = 0 0.5 1 # First, increment, last
FILENAME = "results.csv"

clique: models/Clique.mzn
	echo "edge probability,runtime,solvetime,solutions,variables,propagators,propagations,nodes,failures,restarts,peak depth" > $(FILENAME)
	for edge_probability in $(shell seq $(EDGE_PROBABILITY_RANGE)) ; do \
		r=1 ; while [[ $$r -le $(REPEAT) ]] ; do \
			python generator.py $@ "${NUMBER_OF_VERTICES}" "$${edge_probability}" ; \
			echo "$$edge_probability," `mzn-gecode -p 9 -s $< clique.dzn` >> $(FILENAME) ; \
			((r = r + 1)) ; \
		done ; \
	done
	sed -i s/----------//g $(FILENAME)
	sed -i s/==========//g $(FILENAME)
	sed -i 's/[a-z]*:\s[0-9]*\.[0-9]*\s\([0-9]*\.[0-9]*\sms\)/\1/g' $(FILENAME) # TODO: fix this line
	sed -i s/%%/,/g $(FILENAME)
