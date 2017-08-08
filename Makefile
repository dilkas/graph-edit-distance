# Needed to prevent Make from parsing these symbols as part of Make syntax (even inside a string). Used inside functions and function calls.
COMMA := ,
DOLLAR_SIGN := $

REPEAT = 1 # How many times to repeat each run

# ========== Parameters for problems involving generating new graphs ==========

NUMBER_OF_VERTICES1 = 10
NUMBER_OF_VERTICES2 = 10
EDGE_PROBABILITY = 0.5
EDGE_PROBABILITY_RANGE = 0 0.5 1 # First, increment, last
LABEL_PROBABILITY = 0.3
LABEL_PROBABILITY_RANGE = 0 0.5 1 # First, increment, last
#SIZE_OF_CLIQUE = 5

# ========== Parameters for graph edit distance ==========

DATABASE = Protein
INFO_FILE = graphs/db/$(DATABASE)-GED/$(DATABASE)-low-level-info/$(DATABASE)20-lowlevelinfo.csv
TIME_LIMIT = 5 # in seconds
#INT_VERSION = 1

# Just leave these as they are
MWC_FILE = mwc.csv
MODELS = cp vertex-edge-weights vertex-weights
MODEL_FILES = models/GraphEditDistance2.mzn models/MinimumWeightClique.mzn models/MinimumWeightClique2.mzn

# ========== Helper functions ==========

define write_headers
	for file in $(CSV_FILES) ; do \
		echo $(if $(1),$(1))answer,runtime,solvetime,solutions,variables,propagators,propagations,nodes,failures,restarts,peak depth > "$${file}" ; \
	done
endef

# The meaning of each regular expression is as follows:
# 1. Mark unsatisfiable instances as having an answer of -1
# 2. If there is a distance variable, that is the answer we want to extract. (Output statements sometimes make the model produce a wrong answer)
# 3. If there is still an equal sign, the answer is 'satisfiable', so set answer to 1
# 4. Remove the lines between answers and statistics
# 5. Replace %% with commas
# 6. For runtime and solvetime statistics. Extracts the number in parentheses (miliseconds)
# 7. For all the other statistics. Extracts the number
define convert_results_to_csv
	for file in $(CSV_FILES) ; do \
		sed -i 's/=====UNSATISFIABLE=====/-1/g' "$(DOLLAR_SIGN)$(DOLLAR_SIGN){file}" ; \
		sed -i 's/\(^[^,]*,[^,]*,\).*distance\s=\s\([0-9]*\.[0-9]*\);/\1\2/g' "$(DOLLAR_SIGN)$(DOLLAR_SIGN){file}" ; \
		sed -i 's/[a-zA-Z]*\s=\s.*;/1/g' "$(DOLLAR_SIGN)$(DOLLAR_SIGN){file}" ; \
		sed -i 's/\s----------\(\s==========\)\?//g' "$(DOLLAR_SIGN)$(DOLLAR_SIGN){file}" ; \
		sed -i 's/\s%%/,/g' "$(DOLLAR_SIGN)$(DOLLAR_SIGN){file}" ; \
		sed -i 's/[a-z]*:\s[0-9]*\.[0-9]*\s(\([0-9]*\.[0-9]*\)\sms)/\1/g' "$(DOLLAR_SIGN)$(DOLLAR_SIGN){file}" ; \
		sed -i 's/[a-z]\+\(\s[a-z]*\)\?:\s\([0-9]*\)/\2/g' "$(DOLLAR_SIGN)$(DOLLAR_SIGN){file}" ; \
	done
endef

define run
	for edge_probability in $(shell seq $(EDGE_PROBABILITY_RANGE)) ; do \
		models=($^) ; \
		filenames=($(CSV_FILES)) ; \
		data_files=($(CSV_FILES:.csv=.dzn)) ; \
		r=1 ; while [[ r -le $(REPEAT) ]] ; do \
			python generator.py $@ $(NUMBER_OF_VERTICES1) $(1) ; \
			for i in "$${!models[@]}" ; do \
				echo "$${edge_probability}, $(if $(2),$(2)$(COMMA))" `mzn-gecode -s $${models[$$i]} $${data_files[$$i]}` \
					>> "$${filenames[$$i]}" ; \
			done ; \
			((r = r + 1)) ; \
		done ; \
	done
endef

# ======== Targets for problems involving generating new graphs ==========

# Can be used for the decision problem by setting the SIZE_OF_CLIQUE variable and changing the model file
clique: models/Clique.mzn
	$(eval CSV_FILES = clique.csv)
	$(call write_headers,edge probability$(COMMA))
	$(call run,"$${edge_probability}"$(if $(SIZE_OF_CLIQUE), $(SIZE_OF_CLIQUE)))
	$(call convert_results_to_csv)

# Pattern graph has a fixed edge probability, target graph has a range of probabilities
subgraph: models/Subgraph.mzn
	$(eval CSV_FILES = subgraph.csv)
	$(call write_headers,edge probability$(COMMA))
	$(call run,$(EDGE_PROBABILITY) $(NUMBER_OF_VERTICES2) "$${edge_probability}")
	$(call convert_results_to_csv)

subgraphClique: models/CommonInducedSubgraph.mzn models/Clique.mzn
	$(eval CSV_FILES = subgraph.csv clique.csv)
	$(call write_headers,edge probability$(COMMA))
	$(call run,$(EDGE_PROBABILITY) $(NUMBER_OF_VERTICES2) "$${edge_probability}")
	$(call convert_results_to_csv)

labelledSubgraph: models/LabelledCommonInducedSubgraph.mzn models/Clique.mzn
	$(eval CSV_FILES = subgraph.csv clique.csv)
	$(call write_headers,edge probability$(COMMA)label probability$(COMMA))
	for label_probability in $(shell seq $(LABEL_PROBABILITY_RANGE)) ; do \
		$(call run,$(EDGE_PROBABILITY) $(LABEL_PROBABILITY) $(NUMBER_OF_VERTICES2) "$${edge_probability}" \
			"$${label_probability}",$(label_probability)) ; \
	done
	$(call convert_results_to_csv)

# ========== Targets for graph edit distance ==========

# Generates data files used by other rules
convert-%: $(INFO_FILE)
	$(eval model = $(subst convert-,,$@))
ifeq ($(MAKECMDGOALS), convert-mwc)
	$(eval mwc = 1)
	$(eval model = vertex-weights)
endif
	{ \
		read ; \
		while IFS=";" read name1 name2 nodes1 nodes2 edges1 edges2 method param distance optimal class1 class2 matching ; do \
			format=$(if $(mwc),dimacs,dzn) ; \
			prefix="graphs/db/$(DATABASE)-GED/$(DATABASE)/" ; \
			filename="graphs/$${format}/$(model)/$(DATABASE)/$${name1%.*}-$${name2%.*}.$(if $(mwc),txt,dzn)" ; \
			if [ ! -z "$${name1}" ] && [ ! -f "$${filename}" ] ; then \
				python convert.py $(model) "$${format}" "$${prefix}$${name1}" "$${prefix}$${name2}"$(if $(INT_VERSION), int) ; \
			fi ; \
		done ; \
	} < $<

# ===== Minimum weight clique (the C program) =====

# As we want to allow concurrency, we have to add graph names as two additional columns. The regexp leaves the first
# two columns, skips everything until the last four numbers and keeps them. This is the main target.
mwc: $(addsuffix .target,$(wildcard graphs/dimacs/vertex-weights/$(DATABASE)/*))
	sed -i 's/^\([^,]*,[^,]*,\).*\s\([0-9]\+\)\s\([0-9]\+\(\.[0-9]\+\)\?\)\s\([0-9]\+\)\s\([0-9]\+\)/\1\2,\3,\5,\6/g' $(MWC_FILE)

# A target for each data file
graphs/dimacs/vertex-weights/$(DATABASE)/%.target: graphs/dimacs/vertex-weights/$(DATABASE)/% mwc_header
	r=1; while [[ r -le $(REPEAT) ]] ; do \
		filename=$(<F) ; \
		second_part="$${filename##*-}" ; \
		echo "$${filename%%-*}.gxl,$${second_part%.txt}.gxl,"`./max-weight-clique/colour_order$(if $(TIME_LIMIT), -l $(TIME_LIMIT),) $<` >> $(MWC_FILE) ; \
		((r = r + 1)) ; \
	done

# Header-writing functionality has to be a separate target so that it's executed only once at the start
mwc_header:
	echo "graph1,graph2,size,answer,runtime,node count" > $(MWC_FILE)

# ===== MiniZinc models for GED =====

define model_rule
$(1): $(addsuffix .target,$(wildcard graphs/dzn/$(1)/$(DATABASE)/*))
	$(eval CSV_FILES = $(MAKECMDGOALS).csv)
	$(call convert_results_to_csv)
endef

# This defines a rule for each model
$(foreach model,$(MODELS),$(eval $(call model_rule,$(model))))

define dzn_rule
graphs/dzn/$(1)/$(DATABASE)/%.target: graphs/dzn/$(1)/$(DATABASE)/% minizinc_header
	r=1; while [[ r -le $(REPEAT) ]] ; do \
		filename=$$(<F) ; \
		second_part="$(DOLLAR_SIGN)$(DOLLAR_SIGN){filename##*-}" ; \
		echo "$(DOLLAR_SIGN)$(DOLLAR_SIGN){filename%%-*}.gxl,$(DOLLAR_SIGN)$(DOLLAR_SIGN){second_part%.dzn}.gxl,"`mzn-gecode -s $(2) $$<` >> $(1).csv ; \
		((r = r + 1)) ; \
	done
endef

# A rule for each data file, just like with MWC
$(foreach i,$(shell seq 1 $(words $(MODELS))),$(eval $(call dzn_rule,$(word $(i),$(MODELS)),$(word $(i),$(MODEL_FILES)))))

minizinc_header:
	$(eval CSV_FILES = $(MAKECMDGOALS).csv)
	$(call write_headers,graph1$(COMMA)graph2$(COMMA))

# ========== Miscellaneous ==========

# Remove all data files, all csv files, and all DIMACS and dzn files converted from the database
clean:
	rm -f *.dzn
	rm -f *.csv
	for format in dimacs dzn ; do \
		for model in cp vertex-edge-weights vertex-weights ; do \
			for database in CMU GREC Mutagenicity Protein ; do \
				rm -f graphs/$${format}/$${model}/$${database}/* ; \
			done ; \
		done ; \
	done
