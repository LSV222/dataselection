from setuptools import setup

setup(name='dataselection',
	version='0.0.1',
	description='Includes modules with utility for data analysis, particulary oriented to select groups with certain conditions , where the groups have statistical significance as a sample',
	author='lucianodata',
	author_email='luciano.spinelli.x@gmail.com,
	packages=['dataselection'],
	install_requires=[
			os,
			pandas,
			operator,
			itertools,
			scipy
			]
	)	