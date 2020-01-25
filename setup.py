import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="slack-webclient-logger",
    version="1.0.0",
    author="Gerard Weatherby",
    author_email="gweatherby@uchc.edu",
    description="Python logging handler which post to slack",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/NMRbox/slacklogger",
    packages=setuptools.find_packages(exclude='test.cfg'),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['slackclient>=2.50'],
    python_requires='>=3.6',
    keywords='slack logger'
)
