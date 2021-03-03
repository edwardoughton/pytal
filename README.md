Python Telecommunications Assessment Library (pytal)
===================================================

[![Build Status](https://travis-ci.com/edwardoughton/pytal.svg?branch=master)](https://travis-ci.com/edwardoughton/pytal)
[![Coverage Status](https://coveralls.io/repos/github/edwardoughton/pytal/badge.svg?branch=master)](https://coveralls.io/github/edwardoughton/pytal?branch=master)

**pytal** provides open-source assessment tools to help quantify the effectiveness of different
digital infrastructure strategies, particularly for 4G and 5G deployment.

**pytal** enables researchers to examine trade-offs in infrastructure decisions relating to
technologies, infrastructure sharing, regulation and taxation, with the ultimate aim of
helping to connect more people to a faster Internet.

Citation
---------

- Oughton, E.J., Comini, N., Foster, V., and Hall, J.W. (2021) Policy choices can help keep 4G
  and 5G universal broadband affordable. [World Bank Policy Research Working Paper](https://documents.worldbank.org/en/publication/documents-reports/documentdetail/658521614715617195/policy-choices-can-help-keep-4g-and-5g-universal-broadband-affordable).



The **pytal** approach
======================
The aim is to be able to assess representative countries using a spatially-explicit modeling
codebase, and then use these estimates to scale the results globally. Firstly, using metrics
which affect 4G and 5G infrastructure deployment, a k-means clustering method groups low- and
middle-income countries into similar clusters based on GDP per capita, population density and
existing 4G deployment.

## Global country clustering

<p align="center">
  <img src="/figures/cluster_panel.png" />
</p>

Modeling representative countries
=================================
In Oughton et al. (2021) the analysis includes eight representative countries across the six
clusters, including Malawi, Uganda, Kenya, Senegal, Pakistan, Albania, Peru and Mexico. For
different types of cellular technologies the cost composition can be obtained.

## Example of 5G costs for representative countries
<p align="center">
  <img src="/figures/percentage_of_total_private_cost.png" />
</p>

The aim of achieving universal broadband is highly important for economic development,
therefore `pytal` helps to quantify the social cost for this target given different user
capacities (for example, up to 25, 200 or 400 Mbps per user as the peak speed). The social
cost to society (the private cost + government cost) represents the cost of achieving universal
broadband. This includes any net required government subsidy, after spectrum and taxation
income is accounted for.

## Example technology costs for representative countries
<p align="center">
  <img src="/figures/baseline_tech_country_costs.png" />
</p>

Global estimates for 4G and 5G deployment
=======================================
Once different strategies have been modeled for representative countries, the results can be
scaled within each country cluster to provide global cost estimates. This allows researchers
to understand the required investment for each country, or by each country income group. The
results are reported for the required percentage of annual GDP which would need to be invested
over the next decade.

## Global costs by income group
<p align="center">
  <img src="/figures/costs_by_income_group.png" />
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

**pytal** was jointly developed at the University of Oxford and George Mason University, with
funding support from UKRI (EPSRC) and the World Bank 5G Flagship.
