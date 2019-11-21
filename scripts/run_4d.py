"""
Four Dimensional Model

Written by Ed Oughton

June 2019

"""
import configparser
import os
import csv
import math
from shapely.ops import transform
from shapely.geometry import shape, mapping, Polygon, LineString, Point
import fiona
from functools import partial
import pyproj
import numpy as np

from collections import OrderedDict

from hex_grid import produce_sites_and_cell_areas
from pytal.network_manager import NetworkManager

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA_RAW = os.path.join(BASE_PATH, 'raw')
DATA_INTERMEDIATE = os.path.join(BASE_PATH, 'intermediate')
DATA_PROCESSED = os.path.join(BASE_PATH, 'processed')


def generate_receivers(transmitter, interfering_transmitters, simulation_parameters):
    """

    Generate receivers on a line between the transmitter and all other transmitters,
    to represent movement over time.

    Parameters
    ----------
    transmitter : point
        Transmitter point.
    interfering_transmitters : dict
        Interfering transmitter points.
    simulation_parameters : dict
        Contains all necessary simulation parameters.

    Output
    ------
    receivers : List of dicts
        Contains the quantity of desired receivers within the area boundary.

    """
    paths = []

    for interfering_transmitter in interfering_transmitters:
        geom = LineString([
            transmitter[0]['geometry']['coordinates'],
            interfering_transmitter['geometry']['coordinates']])
        paths.append(geom)

    receivers = []

    length = int(paths[0].length)
    increment = int(length / 5)

    id_number = 0
    for path in paths:
        for increment_value in range(1, 5):
            point = path.interpolate(increment * increment_value)
            indoor_outdoor_probability = np.random.rand(1,1)[0][0]
            receivers.append({
                'type': "Feature",
                'geometry': mapping(point),
                'properties': {
                    'ue_id': "id_{}".format(id_number),
                    "misc_losses": simulation_parameters['rx_misc_losses'],
                    "gain": simulation_parameters['rx_gain'],
                    "losses": simulation_parameters['rx_losses'],
                    "ue_height": float(simulation_parameters['rx_height']),
                    "indoor": str(True if float(indoor_outdoor_probability) < \
                        float(0.5) else False),
                    "time_increment": id_number,
                }
            })
            id_number += 1

    return receivers


def convert_shape_to_projected_crs(geojson, original_crs, new_crs):
    """
    Existing elevation path needs to be converted from WGS84 to projected
    coordinates.

    """
    # Geometry transform function based on pyproj.transform
    project = partial(
        pyproj.transform,
        pyproj.Proj(init = original_crs),
        pyproj.Proj(init = new_crs)
        )

    # if geojson['geometry']['type'] == 'Point':
    new_geom = transform(project, Point(geojson[0], geojson[1]))

    # if geojson['geometry']['type'] == 'LineString':
    #     new_geom = transform(project, LineString(geojson['geometry']['coordinates']))

    output = {
        'type': 'Feature',
        'geometry': mapping(new_geom),
        'properties': {}#geojson['properties']
        }

    return output


def convert_results_geojson(data):

    output = []

    for datum in data:
        output.append({
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [datum['receiver_x'], datum['receiver_y']]
                },
            'properties': {
                'path_loss': float(datum['path_loss']),
                'received_power': float(datum['received_power']),
                'interference': float(datum['interference']),
                'noise': float(datum['noise']),
                'sinr': float(datum['sinr']),
                'spectral_efficiency': float(datum['spectral_efficiency']),
                'estimated_capacity': float(datum['estimated_capacity']),
                },
            })

    return output


def csv_writer(data, directory, filename):
    """
    Write data to a CSV file path

    """
    if not os.path.exists(directory):
        os.makedirs(directory)

    full_path = os.path.join(directory, filename)

    if not os.path.exists(full_path):
        results_file = open(full_path, 'w', newline='')
        results_writer = csv.writer(results_file)
        results_writer.writerow(
            ('receiver_x', 'receiver_y', 'path_loss',
            'received_power', 'interference', 'noise',
            'sinr', 'spectral_efficiency', 'estimated_capacity'))

    else:
        results_file = open(full_path, 'a', newline='')
        results_writer = csv.writer(results_file)

    for row in data:
        results_writer.writerow((
            row['receiver_x'],
            row['receiver_y'],
            row['path_loss'],
            row['received_power'],
            row['interference'],
            row['noise'],
            row['sinr'],
            row['spectral_efficiency'],
            row['estimated_capacity'],
            ))


def write_shapefile(data, new_crs, filename):

    # Translate props to Fiona sink schema
    prop_schema = []
    for name, value in data[0]['properties'].items():
        fiona_prop_type = next((
            fiona_type for fiona_type, python_type in \
                fiona.FIELD_TYPES_MAP.items() if \
                python_type == type(value)), None
            )

        prop_schema.append((name, fiona_prop_type))

    sink_driver = 'ESRI Shapefile'
    sink_crs = {'init': new_crs}
    sink_schema = {
        'geometry': data[0]['geometry']['type'],
        'properties': OrderedDict(prop_schema)
    }

    # Create path
    directory = os.path.join(DATA_INTERMEDIATE, 'test_simulation')
    if not os.path.exists(directory):
        os.makedirs(directory)

    # print(os.path.join(directory, filename))
    # Write all elements to output file
    with fiona.open(
        os.path.join(directory, filename), 'w',
        driver=sink_driver, crs=sink_crs, schema=sink_schema) as sink:
        for datum in data:
            sink.write(datum)


if __name__ == '__main__':

    MODULATION_AND_CODING_LUT =[
        # CQI Index	Modulation	Coding rate
        # Spectral efficiency (bps/Hz) SINR estimate (dB)
        ('4G', 1, 'QPSK',	0.0762,	0.1523, -6.7),
        ('4G', 2, 'QPSK',	0.1172,	0.2344, -4.7),
        ('4G', 3, 'QPSK',	0.1885,	0.377, -2.3),
        ('4G', 4, 'QPSK',	0.3008,	0.6016, 0.2),
        ('4G', 5, 'QPSK',	0.4385,	0.877, 2.4),
        ('4G', 6, 'QPSK',	0.5879,	1.1758,	4.3),
        ('4G', 7, '16QAM', 0.3691, 1.4766, 5.9),
        ('4G', 8, '16QAM', 0.4785, 1.9141, 8.1),
        ('4G', 9, '16QAM', 0.6016, 2.4063, 10.3),
        ('4G', 10, '64QAM', 0.4551, 2.7305, 11.7),
        ('4G', 11, '64QAM', 0.5537, 3.3223, 14.1),
        ('4G', 12, '64QAM', 0.6504, 3.9023, 16.3),
        ('4G', 13, '64QAM', 0.7539, 4.5234, 18.7),
        ('4G', 14, '64QAM', 0.8525, 5.1152, 21),
        ('4G', 15, '64QAM', 0.9258, 5.5547, 22.7),
    ]

    SIMULATION_PARAMETERS = {
        'iterations': 100,
        'tx_baseline_height': 30,
        'tx_upper_height': 40,
        'tx_power': 40,
        'tx_gain': 16,
        'tx_losses': 1,
        'rx_gain': 4,
        'rx_losses': 4,
        'rx_misc_losses': 4,
        'rx_height': 1.5,
        'network_load': 50,
        'percentile': 90,
        'antenna_heights': [50, 2],
    }

    PROPAGATION_PARAMETERS = {
        700: 10,
        800: 10,
    }

    inter_site_distance = 10000

    old_crs = 'EPSG:4326'
    new_crs = 'EPSG:3857'

    dem_folder = os.path.join(DATA_RAW, 'dem_london')

    with fiona.open(
        os.path.join(DATA_RAW, 'crystal_palace_to_mursley.shp'), 'r') as source:
            unprojected_line = next(iter(source))
            unprojected_point = unprojected_line['geometry']['coordinates'][0]

    point = convert_shape_to_projected_crs(unprojected_point, old_crs, new_crs)

    transmitter, interfering_transmitters, cell_area, interfering_cell_areas = \
        produce_sites_and_cell_areas(point, inter_site_distance, old_crs, new_crs)

    receivers = generate_receivers(
        transmitter, interfering_transmitters, SIMULATION_PARAMETERS
    )

    MANAGER = NetworkManager(
        transmitter, interfering_transmitters, receivers, cell_area, SIMULATION_PARAMETERS
        )

    results = MANAGER.estimate_link_budget(
        # frequency, bandwidth, generation, mast_height,
        # environment,
        PROPAGATION_PARAMETERS,
        MODULATION_AND_CODING_LUT,
        SIMULATION_PARAMETERS,
        dem_folder,
        old_crs,
        new_crs
        )

    csv_writer(results,
        os.path.join(DATA_PROCESSED, 'test_results'),
        'test_capacity_data_{}.csv'.format(inter_site_distance))

    geojson_receivers = convert_results_geojson(results)

    write_shapefile(geojson_receivers, new_crs, 'receivers_{}.shp'.format(inter_site_distance))
    write_shapefile(transmitter, new_crs, 'transmitter_{}.shp'.format(inter_site_distance))
    write_shapefile(cell_area, new_crs, 'cell_area_{}.shp'.format(inter_site_distance))
    write_shapefile(interfering_transmitters, new_crs, 'interfering_transmitters_{}.shp'.format(inter_site_distance))
    write_shapefile(interfering_cell_areas, new_crs, 'interfering_cell_areas_{}.shp'.format(inter_site_distance))

    # average_capacity = []
    # for result in results:
    #     average_capacity.append(result['estimated_capacity'])
    # print('------')
    # print_ave_capacity = round(sum(average_capacity)/len(average_capacity))
    # print('isd: {}, {}'.format(inter_site_distance, print_ave_capacity))

    print('complete')
