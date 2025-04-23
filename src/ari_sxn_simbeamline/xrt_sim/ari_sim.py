from custom_devices import (ID29Source, ID29OE, ID29Aperture, ID29Screen,
                            TestM1, beam_to_xarray)
import matplotlib
from matplotlib import pyplot as plt
import numpy as np
from sim_model import BeamlineModel
import xrt.backends.raycing.materials as xrt_material

matplotlib.use('qtagg')

# Define a test object to use in place of the caproto IOC for testing
mirror1 = TestM1({'Ry_coarse': -2, 'Ry_fine': 0, 'Rz': 0,
                  'x': 0, 'y': 0})


# Define optics coating material instances.
nickel = xrt_material.Material('Ni', rho=8.908,
                               table='Chantler Total',
                               kind='mirror', name='Ni')

gold = xrt_material.Material('Au', rho=19.3, table='Chantler Total',
                             kind='mirror', name='Au')

genericGR = xrt_material.Material('Ni', rho=8.908,
                                  table='Chantler total',
                                  kind='grating', name='generic grating',
                                  efficiency=[(1, 1), (-1, 1)])  # efficiency=1

# beamline definition file, move to ari_sim.py once fully functional.
definition_dict = \
    {'source': {
        'type': ID29Source,
        'kwargs': {'center': (0., 0., 0.),  # location (global XRT)
                   'pitch': 0, 'roll': 0, 'yaw': 0,
                   'nrays': 10000,
                   'distx': 'normal', 'dx': 0.30,  # linear profile
                   'disty': None, 'dy': 0,
                   'distz': 'normal', 'dz': 0.30,
                   'distxprime': 'normal', 'dxprime': 3E-5,  # angular profile
                   'distzprime': 'normal', 'dzprime': 3E-5,
                   # source energy profile below
                   'distE': 'normal',
                   'energies': (850, 5),  # (energy, bandwidth)
                   'polarization': 'horizontal',
                   'filamentBeam': False,
                   'uniformRayDensity': False,
                   'parameter_map': {'center': {'x': 0, 'y': 0, 'z': 0},
                                     'angles': {'pitch': 0, 'roll': 0,
                                                'yaw': 0}},
                   'origin': np.array([0, 0, 0, 0, 0, 0]),
                   'deflection': None}},
     'm1_screen': {
        'type': ID29Screen,
        'kwargs': {'center': (0., 26591., 0.),  # location (global XRT)
                   'x': np.array([1, 0, 0]),
                   'z': np.array([0, 0, 1]),
                   'upstream_optic': 'source',
                   'parameter_map': {},
                   'origin': np.array([0, 0, 26591, 0, 0, 0]),
                   'deflection': None}},
     'm1': {
        'type': ID29OE,
         'kwargs': {'center': (0., 26591.243, 0.),  # location (global XRT)
                    'yaw': 0, 'roll': +np.pi/2, 'pitch': np.radians(2),
                    'material': gold,
                    'limPhysX': [-60/2-10, 60/2+10],
                    'limOptX': [-15/2, 15/2],
                    'limPhysY': [-400/2, 400/2], 'limOptY': [-240/2, 240/2],
                    'shape': 'rect',
                    'upstream_optic': 'source',
                    'parameter_map': {'center': {'x': (mirror1, 'x'),
                                                 'y': (mirror1, 'y'),
                                                 'z': 0},
                                      'angles': {'Rx': 0,
                                                 'Ry': (mirror1, 'Ry'),
                                                 'Rz': (mirror1, 'Rz')}},
                    'origin': np.array([0, 0, 26591.24, 0, 0, 0]),
                    'deflection': 'inboard'}},
     'm1_baffles': {
         'type': ID29Aperture,
         'kwargs': {'center': (195.22, 29383.04, 0),
                    'x': 'auto', 'z': 'auto',
                    'kind': ['left', 'right', 'bottom', 'top'],
                    'opening': [50.0, -50.0, -50.0, 50.0],
                    'upstream_optic': 'm1',
                    'parameter_map': {
                        'opening': {'left': (mirror1.baffles, 'left'),
                                    'right': (mirror1.baffles, 'right'),
                                    'bottom': (mirror1.baffles, 'bottom'),
                                    'top': (mirror1.baffles, 'top')}},
                    'origin': np.array([-195.22, 0, 29383.0, 0, -4, 0]),
                    'deflection': None}},
     'm1_diag': {
         'type': ID29Screen,
         'kwargs': {'center': (121.426, 29629.078, 0),  # location (global XRT)
                    'x': np.array([1, 0, 0]),
                    'z': np.array([0, 0, 1]),
                    'upstream_optic': 'm1',
                    'parameter_map': {},
                    'origin': np.array([-121.43, 0, 29629.08, 0, 4, 0]),
                    'deflection': None}},
     'm1_diag_slit': {
         'type': ID29Aperture,
         'kwargs': {'center': (121.426, 29629.2, 0),  # 0.1mm offset to diag
                    'x': 'auto', 'z': 'auto',
                    'kind': ['left', 'right', 'bottom', 'top'],
                    'opening': [-50.0, 50.0, -50.0, 50.0],
                    'upstream_optic': 'm1',
                    'parameter_map': {
                        'opening': {'left': -50, 'right': 50, 'bottom': -50,
                                    'top': (mirror1.diagnostic, 'multi_trans')}
                                     },
                    'origin': np.array([-121.43, 0, 29629.1, 0, -4, 0]),
                    'deflection': None}}
     }

model = BeamlineModel(definition_dict)
