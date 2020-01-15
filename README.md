pytal
=====

Python Telecommunications Assessment Library

**pyTAL** enables the assessment of telecommunication infrastructure, with the ultimate aim of helping to connect more people to the internet.

Using conda
==========

The recommended installation method is to use conda, which handles packages and virtual environments, along with the conda-forge channel which has a host of pre-built libraries and packages.

Create a conda environment called pytal:

    conda create --name cdcam python=3.7 gdal

Activate it (run this each time you switch projects):

    conda activate pytal

First, install optional packages:

    conda install fiona shapely rtree pyproj

Then install pytal:

    python setup.py install

Alternatively, for development purposes, clone this repo and run:

    python setup.py develop

Thanks for the support
======================

**pyTAL** was written and developed at the [Environmental Change Institute, University of Oxford](http://www.eci.ox.ac.uk) within the EPSRC-sponsored MISTRAL programme, as part of the [Infrastructure Transition Research Consortium](http://www.itrc.org.uk/).
