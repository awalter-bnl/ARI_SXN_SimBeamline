from custom_devices import (ID29Source, ID29OE, ID29Aperture, ID29Screen,
                            TestM1, beam_to_xarray)
import matplotlib
from matplotlib import pyplot as plt
import numpy as np
import xrt.backends.raycing as xrt_raycing
import xrt.backends.raycing.materials as xrt_material

matplotlib.use('qtagg')

# Define a test object to use in place of the caproto IOC for testing
mirror1 = TestM1({'Ry_coarse': np.radians(2), 'Ry_fine': 0, 'Rz': 0,
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


# define each beamline components 'origin' in global NSLSII coordinates,
# in the format (x, y, z, Rx, Ry, Rz) where x,y,z are the coordinates of the
# center of the component (in mm) and Rx, Ry, Rz are the angles (in deg) of
# rotation around the x, y, z axes respectively that define the direction of the
# incoming beam.
ari_model_origins = {'source': np.array([0, 0, 0, 0, 0, 0]),
                     'm1': np.array([0, 27850, 0, 0, 0, 0]),
                     'm1_baffles': np.array([314.13, 32342.3, 0, 0, 4, 0]),
                     'm1_diag': np.array([331.3, 32587.8, 0, 0, 4, 0]),
                     'm1_diag_slit': np.array([331.3, 32587.8, 0, 0, 4, 0])}


# noinspection PyUnresolvedReference
class AriModel:
    """
    The ARI beamline simulation based on XRT.

    This class simulates the beam propagation along the ARI beamline and gives
    the beam properties at each beamline component.

    Attributes
    ----------
    *attrs : many

    Methods
    -------
    *methods : many

    """

    def __init__(self):
        # An ordered list of beamline components
        self.components = ['source', 'm1', 'm1_baffles', 'm1_diag',
                           'm1_diag_slit']
        self.activate(updated=True)  # Initialize the beamline components

    def activate(self, updated=False):
        """
        Activate the beamline components.

        This method activates the required beamline components in order, as
        specified by the updated attribute. It returns 'updated' as it may be
        modified by the calls to the component activate methods. This is done
        purely so that AriModel could potentially be used as a component in a
        higher level beamline object.

        Parameters
        updated: a boolean, i.e., False (by default) or True.
            True means the outcome of all components needs to be updated
            otherwise it will only update items (and those downstream) for which
            some of the parameters have been changed.
        """

        for item in self.components:
            updated = getattr(self, item).activate(updated=updated)

        return updated

    # Initialize the beamline object
    bl = xrt_raycing.BeamLine(azimuth=0.0, height=0.0, alignE=0)
    energy_value = 850.0  # default energy in eV.
    energy_bandwidth = 5.0  # default energy width in eV.

    # Add the source to beamline object bl
    # TODO: Consider a toroidal (donut) source profile.
    source = ID29Source(bl=bl,
                        name='source',
                        center=(0, 0, 0),  # location (global XRT coords)
                        nrays=10000,
                        distx='normal', dx=0.30,  # source linear profile
                        disty=None, dy=0,
                        distz='normal', dz=0.001,
                        distxprime='normal', dxprime=0.1,  # angular profile
                        distzprime='normal', dzprime=0.1,
                        # source energy profile below
                        distE='normal',
                        energies=(energy_value, energy_bandwidth),
                        polarization='horizontal',
                        filamentBeam=False,
                        uniformRayDensity=False,
                        parameter_map={'center': {'x': 0, 'y': 0, 'z': 0},
                                       'angles': {'pitch': 0, 'roll': 0,
                                                  'yaw': 0}},
                        origin=ari_model_origins['source'])

    # Add the M1 to beamline object bl
    # TODO: This should be an elliptical mirror that focuses the beam.
    m1 = ID29OE(bl=bl,
                name='m1',
                center=(0, 27850, 0),  # location (global XRT coords)
                yaw=0, roll=0, pitch=np.radians(2),
                material=gold,
                limPhysX=[-60/2+10, 60/2+10], limOptX=[-15/2, 15/2],
                limPhysY=[-400/2, 400/2], limOptY=[-240/2, 240/2],
                shape='rect', upstream=source,
                parameter_map={'center': {'x': (mirror1, 'x'),
                                          'y': (mirror1, 'y'),
                                          'z': 0},
                               'angles': {'Rx': 0,
                                          'Ry': (mirror1, 'Ry'),
                                          'Rz': (mirror1, 'Rz')}},
                origin=ari_model_origins['m1'],
                deflection='inboard')

    # Add the M1 Baffle slit to beamline object bl
    m1_baffles = ID29Aperture(bl=bl,
                              name='m1_baffles',
                              center=(0, 31094.5, 0),  # location (XRT coords)
                              x='auto', z='auto',
                              kind=['left', 'right', 'bottom', 'top'],
                              opening=[-20 / 2, 20 / 2,
                                       -20 / 2, 20 / 2],
                              upstream=m1,
                              parameter_map={
                                  'opening': {'left': (mirror1.baffles,
                                                       'outboard'),
                                              'right': (mirror1.baffles,
                                                        'inboard'),
                                              'bottom': (mirror1.baffles,
                                                         'bottom'),
                                              'top': (mirror1.baffles, 'top')}},
                              origin=ari_model_origins['m1_baffles'])

    # Add one screen at M1 diagnostic to monitor the beam
    # NOTE: the IOC needs to select the right region based on diag position
    # and potentially energy filter based on if a multilayer is inserted.
    m1_diag = ID29Screen(bl=bl,
                         name='m1_diag',
                         center=(0, 31340.6, 0),  # location (global XRT coords)
                         x=np.array([1, 0, 0]),
                         z=np.array([0, 0, 1]),
                         upstream=m1_baffles,
                         parameter_map={},
                         origin=ari_model_origins['m1_diag'],
                         deflection='None')

    # Add slit at M1 diagnostic to block beam when diagnostic unit is in
    m1_diag_slit = ID29Aperture(bl=bl,
                                name='m1_diag_slit',
                                center=(0, 31340.7, 0),  # 0.1mm offset to diag
                                x='auto', z='auto',
                                kind=['left', 'right', 'bottom', 'top'],
                                opening=[-50, 50, -50, 50],
                                upstream=m1_baffles,
                                parameter_map={
                                    'opening': {'left': -50, 'right': 50,
                                                'bottom': -50,
                                                'top': (mirror1.diagnostic,
                                                        'multi_trans')}},
                                origin=ari_model_origins['m1_diag_slit'])
