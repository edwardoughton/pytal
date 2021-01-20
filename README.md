Python Telecommunications Assessment Library (pytal)
===================================================

[![Build Status](https://travis-ci.com/edwardoughton/pytal.svg?branch=master)](https://travis-ci.com/edwardoughton/pytal)
[![Documentation Status](https://readthedocs.org/projects/pytal/badge/?version=latest)](https://pytal.readthedocs.io/en/latest/?badge=latest)
[![Coverage Status](https://coveralls.io/repos/github/edwardoughton/pytal/badge.svg?branch=master)](https://coveralls.io/github/edwardoughton/pytal?branch=master)

We still lack open-source assessment tools to help quantify the effectiveness of different
digital infrastructure strategies, particularly for 4G and 5G deployment.

**pyTAL** enables researchers to examine trade-offs in infrastructure decisions relating to
technologies, infrastructure sharing, regulation and taxation, with the ultimate aim of
helping to connect more people to the Internet.

Citation
---------

- Oughton, E. J. et al. (2021) Policy choices can help keep 4G and 5G universal broadband
  affordable, arXiv id: 3565357.

The pytal approach
==================

The aim is to be able to assess representative countries using a spatially-explicit modeling
approach, and then scale the results globally. Using metrics which represent the costs of 4G
and 5G deployment, a k-means clustering method groups low- and middle-income countries.

## Global country clustering

<p align="center">
  <img src="/figures/cluster_panel.png" />
</p>

In Oughton et al. (2021) the analysis includes eight representative countries across the six
clusters chosen, including Malawi, Uganda, Kenya, Senegal, Pakistan, Albania, Peru and Mexico.

Modeling representative countries
=================================

The types of results that can be produced from the code include the cost composition for
deploying different types of cellular technologies.

## Example 5G costs for representative countries
<p align="center">
  <img src="/figures/percentage_of_total_private_cost.png" />
</p>

The aim of achieving universal broadband is highly important for economic development,
therefore `pytal` helps to quantify the social cost for this target using different
technologies for different user capacities (up to 25, 200 or 400 Mbps).

## Example technology costs for representative countries
<p align="center">
  <img src="/figures/baseline_tech_country_costs.png" />
</p>


Global estimates for 4G and 5G roll-out
=======================================

Once different strategies have been modeled for representative countries, the results can be
scaled to provide global estimates. This allows researchers to understand the costs for each
country, or by country income group. In the figure below we repor


## Global costs by income group
<p align="center">
  <img src="/figures/h_costs_by_income_group.png" />
</p>


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
