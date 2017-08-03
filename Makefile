# Needed to prevent Make from parsing a comma as part of Make syntax (even inside a string)
COMMA := ,
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

DATABASE = GREC
INFO_FILE = graphs/db/GREC-GED/GREC-low-level-info/GREC5-lowlevelinfo.csv
MWC_FILE = mwc.csv
#INT_VERSION = 1
MODELS = cp vertex-edge-weights vertex-weights
MODEL_FILES = models/GraphEditDistance2.mzn models/MinimumWeightClique.mzn models/MinimumWeightClique2.mzn
RUN_MWC = 1

CSV_FILES = $(MODELS:=.csv)

define write_header
	for file in $(CSV_FILES) ; do \
		echo $(if $(1),$(1))answer,runtime,solvetime,solutions,variables,propagators,propagations,nodes,failures,restarts,peak depth > "$${file}" ; \
	done
endef

define convert_results_to_csv
	for file in $(1) ; do \
		sed -i 's/=====UNSATISFIABLE=====/-1/g' $(1) ; \
		sed -i 's/^.*distance\s=\s\([0-9]*\.[0-9]*\);/\1/g' $(1) ; \
		sed -i 's/[a-zA-Z]*\s=\s.*;/1/g' $(1) ; \
		sed -i 's/\s----------\(\s==========\)\?//g' $(1) ; \
		sed -i 's/\s%%/,/g' $(1) ; \
		sed -i 's/[a-z]*:\s[0-9]*\.[0-9]*\s(\([0-9]*\.[0-9]*\)\sms)/\1/g' $(1) ; \
		sed -i 's/[a-z]\+\(\s[a-z]*\)\?:\s\([0-9]*\)/\2/g' $(1) ; \
	done
endef

# Arguments: 1. model (cp, vertex-weights, vertex-edge-weights)
define generate_ged
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

#======== Targets for problems involving generating new graphs ==========

# Can be used for the decision problem by setting the SIZE_OF_CLIQUE variable and changing the model file
clique: models/Clique.mzn
	$(eval CSV_FILES = clique.csv)
	$(call write_header,edge probability$(COMMA))
	$(call run,"$${edge_probability}"$(if $(SIZE_OF_CLIQUE), $(SIZE_OF_CLIQUE)))
	$(call convert_results_to_csv)

# Pattern graph has a fixed edge probability, target graph has a range of probabilities
subgraph: models/Subgraph.mzn
	$(eval CSV_FILES = subgraph.csv)
	$(call write_header,edge probability$(COMMA))
	$(call run,$(EDGE_PROBABILITY) $(NUMBER_OF_VERTICES2) "$${edge_probability}")
	$(call convert_results_to_csv)

subgraphClique: models/CommonInducedSubgraph.mzn models/Clique.mzn
	$(eval CSV_FILES = subgraph.csv clique.csv)
	$(call write_header,edge probability$(COMMA))
	$(call run,$(EDGE_PROBABILITY) $(NUMBER_OF_VERTICES2) "$${edge_probability}")
	$(call convert_results_to_csv)

labelledSubgraph: models/LabelledCommonInducedSubgraph.mzn models/Clique.mzn
	$(eval CSV_FILES = subgraph.csv clique.csv)
	$(call write_header,edge probability$(COMMA)label probability$(COMMA))
	for label_probability in $(shell seq $(LABEL_PROBABILITY_RANGE)) ; do \
		$(call run,$(EDGE_PROBABILITY) $(LABEL_PROBABILITY) $(NUMBER_OF_VERTICES2) "$${edge_probability}" \
			"$${label_probability}",$(label_probability)) ; \
	done
	$(call convert_results_to_csv)

#========== Targets for graph edit distance ==========

# Generates files used by the ged rule
convert-%: $(INFO_FILE)
	$(eval MODEL = $(subst convert-,,$@))
ifeq ($(MAKECMDGOALS), convert-mwc)
	$(eval MWC = 1)
	$(eval MODEL = vertex-weights)
endif
	{ \
		read ; \
		while IFS=";" read name1 name2 nodes1 nodes2 edges1 edges2 method param distance optimal class1 class2 matching ; do \
			format=$(if $(MWC),dimacs,dzn) ; \
			prefix="graphs/db/$(DATABASE)-GED/$(DATABASE)/" ; \
			filename="graphs/$${format}/$(MODEL)/$(DATABASE)/$${name1%.*}-$${name2%.*}.$(if $(MWC),txt,dzn)" ; \
			if [ ! -f "$${filename}" ] ; then \
				python convert.py $(MODEL) "$${format}" "$${prefix}$${name1}" "$${prefix}$${name2}"$(if $(INT_VERSION), int) ; \
			fi ; \
		done ; \
	} < $<

mwc: $(addsuffix .target,$(wildcard graphs/dimacs/vertex-weights/$(DATABASE)/*))
	sed -i 's/^.*\([0-9]\+\)\s\([0-9]\+\(\.[0-9]\+\)\?\)\s\([0-9]\+\)\s\([0-9]\+\)/\1$(COMMA)\2$(COMMA)\4$(COMMA)\5/g' $(MWC_FILE)

define model_rule
$(1): $(addsuffix .target,$(wildcard graphs/dzn/$(1)/$(DATABASE)/*))
	$(call convert_results_to_csv,$(1).csv)
endef

$(foreach model,$(MODELS),$(eval $(call model_rule,$(model))))

header:
	$(call write_header)
	echo "graph1,graph2,size,answer,runtime,node count" > $(MWC_FILE)

define dzn_rule
graphs/dzn/$(1)/$(DATABASE)/%.target: graphs/dzn/$(1)/$(DATABASE)/%
	r=1; while [[ r -le $(REPEAT) ]] ; do \
		echo `mzn-gecode -s $(2) $$<` >> $(1).csv ; \
		((r = r + 1)) ; \
	done
endef

$(foreach i,$(shell seq 1 $(words $(MODELS))),$(eval $(call dzn_rule,$(word $(i),$(MODELS)),$(word $(i),$(MODEL_FILES)))))

graphs/dimacs/vertex-weights/$(DATABASE)/%.target: graphs/dimacs/vertex-weights/$(DATABASE)/% header
	r=1; while [[ r -le $(REPEAT) ]] ; do \
		filename=$< ; \
		echo "$${filename%-.*}.gxl,$${filename##*-}.gxl,"`./max-weight-clique/colour_order $<` >> $(MWC_FILE) ; \
		((r = r + 1)) ; \
	done

clean:
	rm -f *.dzn
	rm -f *.csv
	for format in dimacs dzn ; do \
		for model in cp vertex-edge-weights vertex-weights ; do \
			for database in CMU GREC MUTA Protein ; do \
				rm -f "graphs/$${format}/$${model}/$${database}/*" ; \
			done ; \
		done ; \
	done
