import os
import configparser
import math
import fiona
from shapely.ops import transform
from shapely.geometry import Point, mapping, shape, Polygon, LineString
from functools import partial
from rtree import index
import pyproj
import numpy as np
from itertools import tee

from collections import OrderedDict, defaultdict

from pytal.terrain_module import terrain_module
from pytal.run_itmlogic import run_itmlogic

# #set up file paths
CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__),'..','..','scripts', 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA_RAW = os.path.join(BASE_PATH, 'raw')
DATA_INTERMEDIATE = os.path.join(BASE_PATH, 'intermediate')


class NetworkManager(object):
    """
    Meta-object for managing all transmitters and receivers in wireless system.
    Parameters
    ----------
    area : geojson
        Polygon of the simulation area boundary
    sites : list of dicts
        Contains a dict for each cellular transmitter site in a list format.
    receivers : list of dicts
        Contains a dict for each user equipment receiver in a list format.
    simulation_parameters : dict
        A dict containing all simulation parameters necessary.
    """
    def __init__(self, transmitter, interfering_transmitters,
        receivers, cell_area, simulation_parameters):

        self.transmitter = Transmitter(transmitter[0], simulation_parameters)
        self.cell_area = CellArea(cell_area[0])
        self.receivers = {}
        self.interfering_transmitters = {}

        for receiver in receivers:
            receiver_id = receiver['properties']["ue_id"]
            receiver = Receiver(receiver, simulation_parameters)
            self.receivers[receiver_id] = receiver

        for interfering_transmitter in interfering_transmitters:
            site_id = interfering_transmitter['properties']["site_id"]
            site_object = InterferingTransmitter(
                interfering_transmitter, simulation_parameters
                )
            self.interfering_transmitters[site_id] = site_object

    def estimate_link_budget(self, propagation_parameters,
        modulation_and_coding_lut, simulation_parameters,
        dem_folder, old_crs, new_crs):
        """
        Takes propagation parameters and calculates link budget capacity.
        Parameters
        ----------
        frequency : float
            The carrier frequency for the chosen spectrum band (GHz).
        bandwidth : float
            The width of the spectrum around the carrier frequency (MHz).
        environment : string
            Either urban, suburban or rural.
        modulation_and_coding_lut : list of tuples
            A lookup table containing modulation and coding rates,
            spectral efficiencies and SINR estimates.
        Returns
        -------
        sinr : float
            The signal to noise plut interference ratio (GHz).
        capacity_mbps : float
            The estimated link budget capacity.
        """
        results = []

        for receiver in self.receivers.values():

            path_loss_dict = self.calculate_path_loss(
                self.transmitter, receiver, dem_folder,
                old_crs, new_crs, propagation_parameters,
                simulation_parameters
            )

            received_power_dict = self.calc_received_power(
                self.transmitter, receiver, path_loss_dict
            )

            interference_dict = self.calculate_interference(
                self.interfering_transmitters, receiver,
                dem_folder, old_crs, new_crs, propagation_parameters,
                simulation_parameters)

            bandwidth = 10
            noise = self.calculate_noise(
                bandwidth
            )

            sinr_dict, summed_interference_dict = self.calculate_sinr(
                received_power_dict, interference_dict, noise, simulation_parameters
            )

            generation = '4G'
            spectral_efficiency_dict = self.modulation_scheme_and_coding_rate(
                sinr_dict, generation, modulation_and_coding_lut
            )

            estimated_capacity_dict = self.estimated_capacity(
                bandwidth, spectral_efficiency_dict
            )

            for key in estimated_capacity_dict.keys():
                data = {
                    'receiver_x': receiver.coordinates[0],
                    'receiver_y': receiver.coordinates[1],
                    'path_loss': path_loss_dict[key],
                    'received_power': received_power_dict[key],
                    'interference': summed_interference_dict[key],
                    'noise': noise,
                    'sinr': sinr_dict[key],
                    'spectral_efficiency': spectral_efficiency_dict[key],
                    'estimated_capacity': estimated_capacity_dict[key],
                    'frequency': key,
                    'bandwidth': 10,
                    }

                results.append(data)

            # print('received_power is {}'.format(received_power))
            # print('interference is {}'.format(interference))
            # print('noise is {}'.format(noise))
            # print('sinr is {}'.format(sinr))
            # print('spectral_efficiency is {}'.format(spectral_efficiency))
            # print('estimated_capacity is {}'.format(estimated_capacity))
            # print('path_loss is {}'.format(path_loss))
            # print('-----------------------------')

        return results


    def calculate_path_loss(self, transmitter, receiver, dem_folder,
        old_crs, new_crs, propagation_parameters, simulation_parameters):

        line = {
            'type': 'Feature',
            'geometry': {
                'type': 'LineString',
                'coordinates': [
                    (receiver.coordinates[0], receiver.coordinates[1]),
                    (transmitter.coordinates[0], transmitter.coordinates[1])
                ]},
            'properties': {
                'id': 'line1'
                }
            }

        measured_terrain_profile = terrain_module(dem_folder, line, old_crs, new_crs)
        # print(measured_terrain_profile)
        # print(LineString(line['geometry']['coordinates']).length)
        distance = LineString(line['geometry']['coordinates']).length / 1e3
        # print(distance)
        # output = run_itmlogic(
        #     measured_terrain_profile,
        #     distance
        #     )
        # if distance > 0.5:
        #error if the distance is under ~1km
        #(not that this would be a worthy ITM problem anyway)
        output = run_itmlogic(
            measured_terrain_profile,
            distance,
            propagation_parameters,
            simulation_parameters['antenna_heights'],
            )

        path_loss_dict = {}
        for frequency in propagation_parameters:
            # print(frequency)
            for frequency_results in output.values():
                # print(frequency_results)
                for reliability_level in frequency_results:
                    # print(reliability_level)
                    #get 90% reliability level
                    if reliability_level[0] == 90:
                        confidence_90_percent = reliability_level[2]
                        path_loss_dict[frequency] = confidence_90_percent
        # print(path_loss_dict)
        # else:
        #     confidence_90_percent = 0
        # confidence_90_percent = 0
        return path_loss_dict


    def calc_received_power(self, site, receiver, path_loss_dict):
        """
        Calculate received power based on site and receiver
        characteristcs, and path loss.
        Equivalent Isotropically Radiated Power (EIRP) = Power + Gain - Losses
        """
        #calculate Equivalent Isotropically Radiated Power (EIRP)
        eirp = float(site.power) + \
            float(site.gain) - \
            float(site.losses)

        received_power_dict = {}
        for key, value in path_loss_dict.items():
            received_power = eirp - \
                value - \
                receiver.misc_losses + \
                receiver.gain - \
                receiver.losses
            received_power_dict[key] = received_power

        return received_power_dict


    def calculate_interference(
        self, interfering_sites, receiver, dem_folder, old_crs,
        new_crs, propagation_parameters, simulation_parameters):
        """
        Calculate interference from other cells.
        closest_sites contains all sites, ranked based
        on distance, meaning we need to select cells 1-3 (as cell 0
        is the actual cell in use)
        """
        interference = defaultdict(list)

        # for frequency in propagation_parameters.keys():
        for interference_site in interfering_sites.values():

            line = {
                'type': 'Feature',
                'geometry': {
                    'type': 'LineString',
                    'coordinates': [
                        (receiver.coordinates[0], receiver.coordinates[1]),
                        (interference_site.coordinates[0], interference_site.coordinates[1])
                    ]},
                'properties': {
                    'id': 'line1'
                    }
                }

            measured_terrain_profile = terrain_module(dem_folder, line, old_crs, new_crs)
            distance = LineString(line['geometry']['coordinates']).length / 1e3
            if distance > 0:
                # print('distance is {}'.format(distance))
                output = run_itmlogic(
                    measured_terrain_profile,
                    distance,
                    propagation_parameters,
                    simulation_parameters['antenna_heights'],
                    )

            path_loss_dict = {}
            for frequency in propagation_parameters.keys():
                for frequency_results in output.values():
                    for reliability_level in frequency_results:
                        #get 90% reliability level
                        if reliability_level[0] == 90:
                            confidence_90_percent = reliability_level[2]
                            path_loss_dict[frequency] = confidence_90_percent

            #calc interference from other cells
            received_interference_dict = self.calc_received_power(
                interference_site,
                receiver,
                path_loss_dict
                )

            for frequency in propagation_parameters.keys():
                if interference.get(frequency) != None:
                    interference[frequency].append(received_interference_dict[frequency])
                else:
                    interference[frequency] = [received_interference_dict[frequency]]

        return interference


    def calculate_noise(self, bandwidth):
        #TODO
        """
        Terminal noise can be calculated as:
        “K (Boltzmann constant) x T (290K) x bandwidth”.
        The bandwidth depends on bit rate, which defines the number of resource blocks.
        We assume 50 resource blocks, equal 9 MHz, transmission for 1 Mbps downlink.
        Required SNR (dB)
        Detection bandwidth (BW) (Hz)
        k = Boltzmann constant
        T = Temperature (kelvins) (290 kelvin = ~16 celcius)
        NF = Receiver noise figure
        NoiseFloor (dBm) = 10log10(k*T*1000)+NF+10log10BW
        NoiseFloor (dBm) = 10log10(1.38x10e-23*290*1x10e3)+1.5+10log10(10x10e6)
        """
        k = 1.38e-23
        t = 290
        BW = bandwidth*1000000

        noise = 10*np.log10(k*t*1000)+1.5+10*np.log10(BW)

        return noise


    def calculate_sinr(self, received_power_dict, interference_dict,
        noise, simulation_parameters):
        """
        Calculate the Signal-to-Interference-plus-Noise-Ration (SINR).
        """
        sinr_dict = {}
        summed_interference_dict = {}
        for rp_key, rp_value in received_power_dict.items():
            for i_key, i_value in interference_dict.items():
                if rp_key == i_key:
                    raw_received_power = 10**rp_value

                    interference_values = []
                    for value in i_value[:3]:
                        output_value = 10**value
                        interference_values.append(output_value)

                    network_load = simulation_parameters['network_load']

                    raw_sum_of_interference = sum(interference_values) * (1+(network_load/100))

                    raw_noise = 10**noise

                    sinr_dict[rp_key] = np.log10(
                        raw_received_power / (raw_sum_of_interference + raw_noise)
                        )
                    summed_interference_dict[rp_key] = np.log10(raw_sum_of_interference)

        return sinr_dict, summed_interference_dict


    def modulation_scheme_and_coding_rate(self, sinr_dict,
        generation, modulation_and_coding_lut):
        """
        Uses the SINR to allocate a modulation scheme and affliated
        coding rate.
        """
        spectral_efficiency_dict = {}
        for key, value in sinr_dict.items():
            for lower, upper in pairwise(modulation_and_coding_lut):
                if lower[0] and upper[0] == generation:

                    lower_sinr = lower[5]
                    upper_sinr = upper[5]

                    if value >= lower_sinr and value < upper_sinr:
                        spectral_efficiency_dict[key] = lower[4]
                        continue

                    if value >= modulation_and_coding_lut[-1][5]:
                        spectral_efficiency_dict[key] = modulation_and_coding_lut[-1][4]
                        continue

        return spectral_efficiency_dict


    def estimated_capacity(self, bandwidth, spectral_efficiency_dict):
        """
        Estimate wireless link capacity (Mbps) based on bandwidth and
        receiver signal.
        capacity (Mbps) = bandwidth (MHz) + log2*(1+SINR[dB])
        """
        estimated_capacity_dict = {}
        for key, value in spectral_efficiency_dict.items():
            #estimated_capacity = round(bandwidth*np.log2(1+sinr), 2)
            bandwidth_in_hertz = bandwidth*1000000

            estimated_capacity = bandwidth_in_hertz * value
            estimated_capacity_mbps = estimated_capacity / 1e6

            #link_budget_capacity_mbps_km2
            estimated_capacity_dict[key] = estimated_capacity_mbps / (self.cell_area.area / 1e6)

        return estimated_capacity_dict


class Transmitter(object):
    """
    A site object is specific site.
    """
    def __init__(self, data, simulation_parameters):

        self.id = data['properties']['site_id']
        self.coordinates = data['geometry']['coordinates']
        self.geometry = data['geometry']

        self.ant_height = simulation_parameters['tx_baseline_height']
        self.power = simulation_parameters['tx_power']
        self.gain = simulation_parameters['tx_gain']
        self.losses = simulation_parameters['tx_losses']


class CellArea(object):
    """
    The geographic area which holds all sites and receivers.
    """
    def __init__(self, data):
        self.id = data['properties']['cell_area_id']
        self.geometry = data['geometry']
        self.coordinates = data['geometry']['coordinates']
        self.area = self._calculate_area(data)

    def _calculate_area(self, data):
        polygon = shape(data['geometry'])
        area = polygon.area
        return area


    def __repr__(self):
        return "<Transmitter id:{}>".format(self.id)


class Receiver(object):
    """
    A receiver object is a piece of user equipment which can
    connect to a site.
    """
    def __init__(self, data, simulation_parameters):
        self.id = data['properties']['ue_id']
        self.coordinates = data['geometry']["coordinates"]

        self.misc_losses = data['properties']['misc_losses']
        self.gain = data['properties']['gain']
        self.losses = data['properties']['losses']
        self.ue_height = data['properties']['ue_height']
        # self.indoor = data['properties']['indoor']

    def __repr__(self):
        return "<Receiver id:{}>".format(self.id)


class InterferingTransmitter(object):
    """
    A site object is specific site.
    """
    def __init__(self, data, simulation_parameters):

        self.id = data['properties']['site_id']
        self.coordinates = data['geometry']['coordinates']
        self.geometry = data['geometry']

        self.ant_height = simulation_parameters['tx_baseline_height']
        self.power = simulation_parameters['tx_power']
        self.gain = simulation_parameters['tx_gain']
        self.losses = simulation_parameters['tx_losses']


def transform_coordinates(old_proj, new_proj, x, y):
    new_x, new_y = transform(old_proj, new_proj, x, y)
    return new_x, new_y


def pairwise(iterable):
    """
    Return iterable of 2-tuples in a sliding window
    Parameters
    ----------
    iterable: list
        Sliding window
    Returns
    -------
    list of tuple
        Iterable of 2-tuples
    Example
    -------
        >>> list(pairwise([1,2,3,4]))
            [(1,2),(2,3),(3,4)]
    """
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)
