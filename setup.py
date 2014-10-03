from setuptools import setup

setup(name='mcache',
    version='0.9',
    description='Convinience Wrapper for joblib Memory cache',
    url='',
    author='Mathias Hauser',
    author_email='mathias.hauser@env.ethz.ch',
    license='MIT',
    packages=['mcache'],
    install_requires=[
        'sys',
		'errno',
		'os',
		'inspect',
		'warnings'
		],
    zip_safe=False)







