import matplotlib
import numpy as np
from transformations import Transform
import xrt.backends.raycing as xrt_raycing

matplotlib.use('qtagg')


_transform = Transform()


class BeamlineModel:
    """
    The XRT beamline simulation class for use with ARI_SXN_SimBeamline.

    This class simulates the beam propagation along the beamline defined with
    definition_dict and gives the beam properties at each beamline component.


    Parameters
    ----------
    definitions : dict
        A dictionary that defines the beamline components and their
        initialization parameters. It has the form:
                {'1st_component_name': {
                    'type': <component_class>,
                        'kwargs': {
                            'param1': value1,
                            'param2': value2,
                            ...
                                  }
                                    },
                    ...
                'last_component_name': {
                    'type': <component_class>,
                        'kwargs': {
                            'param1': value1,
                            'param2': value2,
                            ...
                                  }
                                    },
                }

        Where each component type is an xrt_sim.custom_devices component class
        (e.g., ID29Source, ID29OE, etc.), the kwargs are the parameters used to
        initialize the component, and the component name is a string that will
        become the components attr name in the model.bl object.

    Attributes
    ----------
    definition_dict : dict
        An updatable copy of the input definition_dict.
    beamline : xrt_raycing.Beamline
        The XRT beamline object that contains the beamline components.

    Methods
    -------
    initialize_beamline(self)
        Initializes the beamline object and adds the components defined in
        definition_dict to the model.

    """

    def __init__(self, definitions):
        """
        Initialize the beamline model.

        Parameters
        ----------
        definitions : xrt_raycing.Beamline
            A dictionary of the form described in the class definition.
        """
        # parse any values in definition_dict that need it.
        for component_name, initial_dict in definitions.items():
            # parse the parameter_map values
            if initial_dict['kwargs']['parameter_map']:
                initial_dict['kwargs']['parameter_map'] = \
                    self._parse_parameter_map(initial_dict['kwargs']
                                              ['parameter_map'])
            # take care of using the default deflection if deflection is None
            if initial_dict['kwargs']['deflection'] is None:
                initial_dict['kwargs']['deflection'] = 'upward'

        self.definition_dict = definitions
        self.initialize_beamline(updated=True)

    def initialize_beamline(self, updated=False):
        """
        Initialize the beamline object.

        This method (re)creates the XRT beamline object, if updated = True or if
        any of the values from parameter_map in self.definition_dict do not
        match those in the rest of definition_dict. If it (re)creates the
        beamline object it also (re)creates the model component attributes
        defined in the definition_dict.

        Parameters
        ----------
        updated: a boolean, i.e., False (by default) or True.
            Boolean that indicates if any of the parameters where updated,
            Potentially modified and returned.

        Returns
        -------
        updated : Boolean
            Potentially modified the input parameter updated if the update
            indicates a re-activation required.

        """
        # update the parameters in the model based on the links in parameter_map
        updated = self._update_parameters(updated=updated)

        if updated:  # Initialize the beamline object
            setattr(self, 'beamline',
                    xrt_raycing.BeamLine(azimuth=0.0, height=0.0, alignE=0))
            # reference the beamline object
            beamline = self.beamline

            # Generate the beamline components
            for component_name, initial_dict in self.definition_dict.items():
                # Initialize the component and add it to the beamline
                component = initial_dict['type'](bl=beamline,
                                                 name=component_name,
                                                 **initial_dict['kwargs'])
                setattr(self, component_name, component)
                # Add the right upstream reference to the component
                upstream = getattr(self, component_name)._upstream
                if upstream is not None:
                    getattr(self, component_name)._upstream = getattr(self,
                                                                      upstream)

            # activate the beamline components
            self.activate()

        return updated

    def _parse_parameter_map(self, default_map):
        """
        A method that parses the default parameter map into a parameter map.

        Parameters
        ----------
        default_map : dict
            The default parameter map to parse
        """
        out = {}
        for key, value in default_map.items():
            if type(value) is dict:  # value is a dictionary
                temp_out = []
                for axis, val in value.items():
                    if type(val) is float or type(val) is int:
                        temp_out.append(val)
                    elif type(val) in [list, tuple] and len(val) == 2:
                        temp_out.append(getattr(val[0], val[1]))
                    else:
                        raise ValueError(f'Invalid value for {key} in '
                                         f'{default_map}')
                out[key] = tuple(temp_out)
            elif type(value) is float or type(value) is int:
                out[key] = value
            elif type(value) in [list, tuple] and len(value) == 2:
                out[key] = getattr(value[0], value[1])
            else:
                raise ValueError(f'Invalid value for {key} in '
                                 f'{default_map}')

        return out

    def _update_parameters(self, updated=False):
        """
        A generic method that updates the XRT model parameters.

        Used to update the parameters in the model based on the links in the
        objects parameter_map dictionary.

        Parameters
        ----------
        updated: a boolean, i.e., False (by default) or True.
            Boolean that indicates if any of the parameters where updated,
            Potentially modified and returned.

        Returns
        -------
        updated : Boolean
            Potentially modified the input parameter updated if the update
            indicates a re-activation required.

        """

        # A dictionary that provides the conversion from xt local Rx, Ry, Rz
        # to yaw, pitch, roll.
        conversion = {'upward': np.array([0, 0, 0]),
                      'downward': np.array([0, 180, 0]),
                      'inboard': np.array([0, 90, 0]),
                      'outboard': np.array([0, -90, 0])}

        for component_name, initial_dict in self.definition_dict.items():
            # step through the components and update the parameters
            kwargs = initial_dict['kwargs']
            for parameter, root in kwargs['parameter_map'].items():
                if parameter == 'center':
                    # convert to XRT global coordinates
                    nsls2_local = np.concatenate((np.array(root),
                                                  np.array([0, 0, 0])))
                    xrt_global = _transform.nsls2_local.to_xrt_global(
                        nsls2_local, kwargs['origin'])
                    xrt_root = tuple(xrt_global[:3])
                    # get current xrt model version
                    current = kwargs['center']
                    if xrt_root != current:
                        updated = True
                        kwargs['center'] = xrt_root

                elif parameter == 'angles':
                    # convert to XRT local coordinates
                    nsls2_local = np.concatenate((np.array(root),
                                                  np.array([0, 0, 0])))
                    xrt_local = _transform.nsls2_local.to_xrt_local(
                        nsls2_local, kwargs['origin'],
                        kwargs['deflection'])

                    # convert from xrt local to 'pitch', 'roll', 'yaw'
                    xrt_local = (xrt_local[:3] +
                                 conversion[kwargs['deflection']])
                    # convert to radians from degrees
                    xrt_root = tuple(np.deg2rad(xrt_local))

                    # get current xrt model version
                    current = tuple([kwargs[angle]
                                     for angle in ['pitch', 'roll', 'yaw']])

                    if xrt_root != current:
                        updated = True
                        for i, angle in enumerate(['pitch', 'roll', 'yaw']):
                            kwargs[angle] = xrt_root[i]

                else:
                    if kwargs[parameter] != root:
                        updated = True
                        kwargs[parameter] = root

        return updated

    def activate(self):
        """
        Activate the beamline components.

        This method activates the required beamline components in order.
        """

        # Loop through the components and activate them
        for item in self.definition_dict.keys():
            getattr(self, item).activate()

        return
