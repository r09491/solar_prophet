from setuptools import setup

with open("README.md", 'r') as f:
    long_description = f.read()
    
setup(name='solar_prophet',
      version='0.0.2',
      description='Estimates the power output of solar panels',
      url='https://github.com/r09491/solar_prophet',
      author='r09491',
      author_email='r09491@gmail.com',
      license='MIT',
      long_description=long_description,
      scripts=[
          './solar_prophet.py',
      ],
      packages=[
      ],
      install_requires=[
          'pysolar',
          'pandas',
          'matplotlib',
      ],
      zip_safe=False)
