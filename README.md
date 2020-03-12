pytal
====

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


Download necessary data
=======================

You will need numerous input data sets.

First, download the WorldPop global settlement data from:

- https://www.worldpop.org/geodata/summary?id=24777.

and place the data in `data/raw/settlement_layer`.

Then download the Global Administrative Database (GADM), following the link below and making
sure you download the "six separate layers.":

- https://gadm.org/download_world.html

Placing the data into `data/raw/gadm36_levels_shp`.



Using the model
===============

First run the following initial preprocessing script to extract the necessary files:

    python scripts/preprocess.py

Then


    python scripts/core.py
    python scripts/preprocess.py




Thanks for the support
======================

**pyTAL** was written and developed at the `Environmental Change Institute, University of Oxford <http://www.eci.ox.ac.uk>`_ within the EPSRC-sponsored MISTRAL programme, as part of the `Infrastructure Transition Research Consortium <http://www.itrc.org.uk/>`_.
