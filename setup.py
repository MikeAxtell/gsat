import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gsat", 
    version="0.1a2",
    author="Michael J. Axtell",
    author_email="mja18@psu.edu",
    description="General Small RNA-seq Analysis Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MikeAxtell/gsat",
    scripts=['bin/gsat'],
    package_dir={'': 'src'},
    packages=setuptools.find_packages(where='src'),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>3.5, <4',
    install_requires=['biopython','python-Levenshtein'],
)
