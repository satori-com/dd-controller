# vim: ts=4 sts=4 sw=4 noexpandtab syntax=make

all: pylint check

pylint:
	pylint --disable="\
		missing-docstring, \
		invalid-name, \
		locally-disabled, \
		star-args, \
		unidiomatic-typecheck, \
		too-few-public-methods", \
		*.py lib/*.py tests/*.py

check:
	nosetests -v

install-deps:
	sudo pip install -r requirements.txt

clean:
	find . -name *.pyc | xargs rm -f
