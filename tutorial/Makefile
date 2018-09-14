all: tutorial.ipynb solution.ipynb

tutorial.ipynb: querybuilder/template.ipynb
	python make_notebook.py -t $@ $<

solution.ipynb: querybuilder/template.ipynb
	python make_notebook.py -s $@ $<

.PHONY: all clean

clean: 
	rm -f tutorial.ipynb solution.ipynb *~