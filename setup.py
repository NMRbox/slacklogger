from setuptools import setup,find_packages

with open("README.rst", "r") as fh:
    readme_long_description = fh.read()

setup(
    name="slack-webclient-logger",
    version="2.2",
    author="Gerard Weatherby",
    author_email="gweatherby@uchc.edu",
    description="Python logging handler which posts to slack",
    long_description=readme_long_description,
    url="https://github.com/NMRbox/slacklogger",
    packages=find_packages(exclude='test.cfg'),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['slackclient>=2.5.0'],
    python_requires='>=3.6',
    keywords='slack logger'
)
