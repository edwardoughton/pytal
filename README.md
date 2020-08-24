pytal
====

[![Build Status](https://travis-ci.com/edwardoughton/pytal.svg?branch=master)](https://travis-ci.com/edwardoughton/pytal)
[![Documentation Status](https://readthedocs.org/projects/pytal/badge/?version=latest)](https://pytal.readthedocs.io/en/latest/?badge=latest)
[![Coverage Status](https://coveralls.io/repos/github/edwardoughton/pytal/badge.svg?branch=master)](https://coveralls.io/github/edwardoughton/pytal?branch=master)

Python Telecommunications Assessment Library

**pyTAL** enables the assessment of telecommunication infrastructure, with the ultimate aim of
helping to connect more people to the internet.

Using conda
==========

The recommended installation method is to use conda, which handles packages and virtual
environments, along with the conda-forge channel which has a host of pre-built libraries and
packages.

Create a conda environment called pytal:

    conda create --name pytal python=3.7 gdal

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

First, download the Global Administrative Database (GADM), following the link below and making
sure you download the "six separate layers.":

- https://gadm.org/download_world.html

Place the data into the following path `data/raw/gadm36_levels_shp`.

Then download the WorldPop global settlement data from:

- https://www.worldpop.org/geodata/summary?id=24777.

Place the data in `data/raw/settlement_layer`.

Next, download the nightlight data here:

https://ngdc.noaa.gov/eog/data/web_data/v4composites/F182013.v4.tar

Place the unzipped data in `data/raw/nightlights/2013`.

Obtain the Mobile Coverage Explorer data from Collins Bartholomew:

https://www.collinsbartholomew.com/mobile-coverage-maps/mobile-coverage-explorer/

Place the data into `data/raw/Mobile Coverage Explorer`.

Once complete, run the following to preprocess all data:

    python scripts/preprocess.py


Using the model
===============

First run the following initial preprocessing script to extract the necessary files:

    python scripts/preprocess.py

Then

    python scripts/core.py


Thanks for the support
======================

**pyTAL** was written and developed at the `Environmental Change Institute, University of Oxford <http://www.eci.ox.ac.uk>`_ within the EPSRC-sponsored MISTRAL programme, as part of the `Infrastructure Transition Research Consortium <http://www.itrc.org.uk/>`_.
