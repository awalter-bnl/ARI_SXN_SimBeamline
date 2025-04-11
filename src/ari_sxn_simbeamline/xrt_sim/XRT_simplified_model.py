import xrt.backends.raycing as xrt_raycing
import xrt.backends.raycing.materials as xrt_material
from xrt.backends.raycing.sources import GeometricSource as Xrt_source
from xrt.backends.raycing.apertures import RectangularAperture as Xrt_aperture
from xrt.backends.raycing.screens import Screen as Xrt_screen
from xrt.backends.raycing.oes import OE as Xrt_oes
import numpy as np


gold = xrt_material.Material('Au', rho=19.3, table='Chantler Total',
                             kind='mirror', name='Au')

# Initialize the beamline object
bl = xrt_raycing.BeamLine(azimuth=0.0, height=0.0, alignE=0)
energy_value = 850.0  # default energy in eV.
energy_bandwidth = 5.0  # default energy width in eV.

# Add the source to beamline object bl
# TODO: Consider a toroidal (donut) source profile.
source = Xrt_source(bl=bl,
                    name='source',
                    center=(0., 0., 0.),  # location (global XRT coords)
                    nrays=10000,
                    distx='normal', dx=0.30,  # source linear profile
                    disty=None, dy=0,
                    distz='normal', dz=0.30,
                    distxprime='normal', dxprime=0.03,  # angular profile
                    distzprime='normal', dzprime=0.03,
                    # source energy profile below
                    distE='normal',
                    energies=(energy_value, energy_bandwidth),
                    polarization='horizontal',
                    filamentBeam=False,
                    uniformRayDensity=False)

# Add the M1 to beamline object bl
# TODO: This should be an elliptical mirror that focuses the beam.
m1 = Xrt_oes(bl=bl,
             name='m1',
             center=(0, 27850, 0),  # location (global XRT coords)
             yaw=0, roll=0, pitch=np.radians(2),
             material=gold,
             limPhysX=[-60/2+10, 60/2+10], limOptX=[-15/2, 15/2],
             limPhysY=[-400/2, 400/2], limOptY=[-240/2, 240/2],
             shape='rect')

# Add the M1 Baffle slit to beamline object bl
baffles = Xrt_aperture(bl=bl,
                       name='m1_baffles',
                       center=(314.13, 32342.3, 0),  # location (XRT coords)
                       x='auto', z='auto',
                       kind=['left', 'right', 'bottom', 'top'],
                       opening=[-20 / 2, 20 / 2,
                                -20 / 2, 20 / 2])

# Add one screen at M1 diagnostic to monitor the beam
# NOTE: the IOC needs to select the right region based on diag position
# and potentially energy filter based on if a multilayer is inserted.
diagnostic = Xrt_screen(bl=bl,
                        name='m1_diag',
                        center=(331.3, 32587.8, 0),  # location (global XRT coords)
                        x=np.array([1, 0, 0]),
                        z=np.array([0, 0, 1]))

# Add slit at M1 diagnostic to block beam when diagnostic unit is in
diagnostic_slit = Xrt_aperture(bl=bl,
                               name='m1_diag_slit',
                               center=(331.3, 32587.8, 0),  # 0.1mm offset to diag
                               x='auto', z='auto',
                               kind=['left', 'right', 'bottom', 'top'],
                               opening=[-50, 50, -50, 50])


def update_model():
    """
    Function to update the model parameters.
    This function is called when the model needs to be updated.
    """

    source_beam = source.shine()
    M1_beam, M1_beam_local = m1.reflect(source_beam)
    baffles_beam = baffles.propagate(M1_beam)
    diagnostic_beam = diagnostic.expose(baffles_beam)
    diagnostic_slit_beam = diagnostic_slit.propagate(diagnostic_beam)

    beams = {'source': source_beam, 'M1': M1_beam, 'baffles': baffles_beam,
             'diagnostic': diagnostic_beam, 'diag_slit': diagnostic_slit_beam}

    return beams


def check_output(beams):
    """
    Function to check the output of the model.
    This function is called when the model needs to be checked.
    """

    # Check the output of the model
    for name, beam in beams.items():
        print(f"{name} output:")
        for axis in ['x', 'z']:
            print(f'{axis} range: {getattr(beam, axis).min()} to '
                  f'{getattr(beam, axis).max()}')
