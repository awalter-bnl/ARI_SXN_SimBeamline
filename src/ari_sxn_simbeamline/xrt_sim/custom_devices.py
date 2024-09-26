import numpy as np
import xrt.backends.raycing.sources as xrt_source
import xrt.backends.raycing.apertures as xrt_aperture
import xrt.backends.raycing.screens as xrt_screen
import xrt.backends.raycing.oes as xrt_oes


# Transformation of coordinates between XRT and NSLS-II.
_coordinate_NSLS2XRT = {'inboard': np.array([[0, -1.0, 0], [0, 0, 1.0],
                                             [-1.0, 0, 0]]),
                        'outboard': np.array([[0, 1.0, 0], [0, 0, 1.0],
                                              [1.0, 0, 0]]),
                        'downward': np.array([[1.0, 0, 0], [0, 0, 1.0],
                                              [0, -1.0, 0]]),
                        'upward': np.array([[-1.0, 0, 0], [0, 0, 1.0],
                                            [0, 1.0, 0]])}


class ID29Source(xrt_source.GeometricSource):
    """
    A Geometric Source inherited from XRT.

    Update the xrt.backends.raycing.sources.GeometricSource with an activate
    method, and add the Beam Object (beamOut) generated from the shine() method.

    Parameters
    ----------
    *args : arguments
        The arguments passed to the parent
        'xrt.backends.raycing.sources.GeometricSource' class.

    **kwargs : keyword arguments
        The keyword arguments passed to the parent
        'xrt.backends.raycing.sources.GeometricSource' class.

    Attributes
    ----------
    *attrs : many
        The attributes of the parent
        `xrt.backends.raycing.sources.GeometricSource` class.

    beamOut :  xrt.backends.raycing.sources_beams.Beam
        Output of most recent activate method in global coordinate!

    pv2xrt : dict
        Mapping the PV names and the terminology of XRT.

    Methods
    -------
    *methods : many
        The methods of the parent `xrt.backends.raycing.sources.GeometricSource`
        class.

    activate(update=None, updated=False) :
        A method generating the beamOut attribute and updating the attribute if
        any parameters in update had been changed.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.beamOut = None  # Output in global coordinate!

        # This dict needs to be modified later on!
        _source_pv2xrt = {'ARI_pgm:energy': 'energies'}

        self.pv2xrt = {'ARI_pgm': _source_pv2xrt}

    def activate(self, update=None, updated=False):
        """
        A method adding or modifying the beamOut attribute.

        This method modifies the Object of beamline source if any parameters had
        been changed and then updates the beamOut accordingly.

        Parameters
        ----------
        update: dict
            Wrap up the PV names and values, update = {'ARI_pgm:energy':850}.

        updated: a boolean, i.e., False (by default) or True.
            The boolean indicates the beamOut needs to be updated as the source
            has been modified. Potentially modified and returned.

        Returns
        -------
        updated : Boolean
            Potentially modified the input parameter updated if the update
            indicates a re-activation required.
        """

        if update is not None:
            for pv_name, pv_val in update.items():
                if pv_name.split(':')[1] in ['x', 'y', 'z']:
                    center_list = getattr(self, 'center').copy()

                    # Find out the position of changed element based on the
                    # coordination transformation between NSLS2 and XRT
                    unit_vector_trans_NSLS2 = np.array([0, 0, 0])
                    for i, p in enumerate(['x', 'y', 'z']):
                        if pv_name.split(':')[1] == p:
                            unit_vector_trans_NSLS2[i] = 1.0
                    unit_vector_trans_XRT = np.dot(
                        _coordinate_NSLS2XRT['upward'], unit_vector_trans_NSLS2)

                    center_list[int(np.where(unit_vector_trans_XRT != 0
                                             )[0][0])] = \
                        (pv_val * unit_vector_trans_XRT[int(np.where(
                            unit_vector_trans_XRT != 0)[0][0])])
                    if getattr(self, 'center') != center_list:
                        setattr(self, 'center', center_list)
                        updated = True

                elif pv_name.split(':')[1][:2] in ['Rx', 'Ry', 'Rz']:
                    angle_XRT = np.array(['pitch', 'roll', 'yaw'])

                    unit_vector_angle_NSLS2 = np.array([0, 0, 0])
                    for i, p in enumerate(['Rx', 'Ry', 'Rz']):
                        if pv_name.split(':')[1][:2] == p:
                            unit_vector_angle_NSLS2[i] = 1.0
                    unit_vector_angle_XRT = np.dot(
                        _coordinate_NSLS2XRT['upward'], unit_vector_angle_NSLS2)

                    angle_set_v = pv_val * unit_vector_angle_XRT[
                        int(np.where(unit_vector_angle_XRT != 0)[0][0])]
                    if (getattr(self, str(angle_XRT[int(
                            np.where(unit_vector_angle_XRT != 0)[0][0])])) !=
                            angle_set_v):
                        setattr(self, str(angle_XRT[int(
                            np.where(unit_vector_angle_XRT != 0)[0][0])]),
                                angle_set_v)
                        updated = True
                else:
                    if getattr(self, self.pv2xrt[pv_name.split(':')[0]][
                            pv_name]) != pv_val:
                        setattr(self, self.pv2xrt[
                            pv_name.split(':')[0]][pv_name], pv_val)
                        updated = True
        if updated:
            self.beamOut = self.shine()

        return updated


class ID29OE(xrt_oes.OE):
    """
    A modified OE class including the beamIn and beamOut attributes.

    Updates the xrt.backends.raycing.oes.OE with an update method, and adds the
    Beam Object (beamIn/beamOut) generated from the reflect() method.

    Parameters
    ----------
    upstream : arguments, such as m1, pgm ...
        The argument takes the beamline component that has Beam Object.

    *args : arguments
        The arguments passed to the parent 'xrt.backends.raycing.oes.OE' class.

    **kwargs : keyword arguments
        The keyword arguments passed to the parent 'xrt.backends.raycing.oes.OE'
        class.

    Attributes
    ----------
    *attrs : many
        The attributes of the parent `xrt.backends.raycing.oes.OE` class.

    beamIn :
        Input of Beam Object in global coordinate!

    beamOut :
        Output of Beam Object in global coordinate!

    beamOutloc :
        Output of Beam Object in local coordinate!

    pv2xrt : dict
        Mapping the PV names and the terminology of XRT.

    _upstream : argument
        upstream.

    Methods
    -------
    *methods : many
        The methods of the parent `xrt.backends.raycing.oes.OE` class.

    activate(update=None, updated=False) :
        A method generating the beamOut attribute and updating the attribute if
        any parameters in update had been changed.
    """
    def __init__(self, deflection='inboard', upstream=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.beamIn = None  # Input in global coordinate!
        self.beamOut = None  # Output in global coordinate!
        self.beamOutloc = None  # Output in local coordinate!
        self._upstream = upstream  # Object from modified XRT
        self.deflection = deflection

        # Note: the sign needs to be carefully checked between NSLS-II and XRT!
        _M1_pv2xrt = {'ARI_M1:Ry_fine': 'pitch', 'ARI_M1:Rz': 'roll',
                      'ARI_M1:x': 'center', 'ARI_M1:y': 'center'}

        _M2_pv2xrt = {'ARI_M2:Ry_fine': 'pitch', 'ARI_M2:Rz': 'roll',
                      'ARI_M2:x': 'center', 'ARI_M2:y': 'center',
                      'ARI_M2:z': 'center'}

        self.pv2xrt = {'ARI_M1': _M1_pv2xrt, 'ARI_M2': _M2_pv2xrt}

    def activate(self, update=None, updated=False):
        """
        A method adding or modifying the beamOut attribute.

        This method modifies the Object of beamline optics if any parameters had
        been changed and then updates the outcome of Beam Object accordingly.

        Parameters
        ----------
        update: a dict wrapping up the PV names and values,
                update = {'ARI_M2:x': 0.2, 'ARI_M1:Ry_fine': 3.1}.

        updated: a boolean, i.e., False (by default) or True.
        The Ture means the outcome of Beam Object needs to be updated
        as the beamline optics has been modified.

        Returns
        -------
        updated : Boolean
            Potentially modified the input parameter updated if the update
            indicates a re-activation required.
        """

        if update is not None:
            for pv_name, pv_val in update.items():
                if pv_name.split(':')[1] in ['x', 'y', 'z']:
                    center_list = getattr(self, 'center').copy()

                    # Find out the position of changed element based on the
                    # coordination transformation between NSLS2 and XRT
                    unit_vector_trans_NSLS2 = np.array([0, 0, 0])
                    for i, p in enumerate(['x', 'y', 'z']):
                        if pv_name.split(':')[1] == p:
                            unit_vector_trans_NSLS2[i] = 1.0
                    unit_vector_trans_XRT = np.dot(
                        _coordinate_NSLS2XRT[self.deflection],
                        unit_vector_trans_NSLS2)

                    center_list[int(np.where(
                        unit_vector_trans_XRT != 0)[0][0])] = (
                            pv_val * unit_vector_trans_XRT[int(
                                np.where(unit_vector_trans_XRT != 0)[0][0])])
                    if getattr(self, 'center') != center_list:
                        setattr(self, 'center', center_list)
                        updated = True
                elif pv_name.split(':')[1][:2] in ['Rx', 'Ry', 'Rz']:
                    angle_XRT = np.array(['pitch', 'roll', 'yaw'])

                    unit_vector_angle_NSLS2 = np.array([0, 0, 0])
                    for i, p in enumerate(['Rx', 'Ry', 'Rz']):
                        if pv_name.split(':')[1][:2] == p:
                            unit_vector_angle_NSLS2[i] = 1.0
                    unit_vector_angle_XRT = np.dot(
                        _coordinate_NSLS2XRT[self.deflection],
                        unit_vector_angle_NSLS2)

                    angle_set_v = pv_val * unit_vector_angle_XRT[int(
                        np.where(unit_vector_angle_XRT != 0)[0][0])]
                    if (getattr(self, str(angle_XRT[int(
                            np.where(unit_vector_angle_XRT != 0)[0][0])])) !=
                            angle_set_v):
                        setattr(self, str(angle_XRT[int(np.where(
                            unit_vector_angle_XRT != 0)[0][0])]), angle_set_v)
                        updated = True

                else:
                    if getattr(self, self.pv2xrt[
                            pv_name.split(':')[0]][pv_name]) != pv_val:
                        setattr(self, self.pv2xrt[
                            pv_name.split(':')[0]][pv_name], pv_val)
                        updated = True

        if updated:
            self.beamIn = getattr(self._upstream, 'beamOut')
            self.beamOut, self.beamOutloc = self.reflect(self.beamIn)

        return updated


class ID29Aperture(xrt_aperture.RectangularAperture):
    """
    A modified Aperture class including the beamIn and beamOut attributes.

    Updates the xrt.backends.raycing.apertures.RectangularAperture with an
    activate method, and adds the Beam Object (beamIn/beamOut) generated from
    the propagate() method.

    Parameters
    ----------
    upstream : arguments, such as m1, pgm ...
        The argument takes the beamline component that has Beam Object.

    *args : arguments
        The arguments passed to the parent
        'xrt.backends.raycing.apertures.RectangularAperture' class.

    **kwargs : keyword arguments
        The keyword arguments passed to the parent
        'xrt.backends.raycing.apertures.RectangularAperture' class.

    Attributes
    ----------
    *attrs : many
        The attributes of the parent
        `xrt.backends.raycing.apertures.RectangularAperture` class.

    beamIn :
        Input of Beam Object in global coordinate!

    beamOut :
        Output of Beam Object in global coordinate!

    pv2xrt : dict
        Mapping the PV names and the terminology of XRT.

    _upstream : argument
        upstream.

    Methods
    -------
    *methods : many
        The methods of the parent `xrt.backends.raycing.apertures
        `RectangularAperture` class.

    activate(update=None, updated=False) :
        A method generating the beamOut attribute and updating the attribute if
        any parameters in update had been changed.

    """
    def __init__(self, upstream=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.beamIn = None  # Input in global coordinate!
        self.beamOut = None  # Output in global coordinate!
        self._upstream = upstream  # Object from modified XRT

        _m1_baff_pv2xrt = {'ARI_M1:baffle:top': 'opening',  # opening[3]
                           'ARI_M1:baffle:bottom': 'opening',  # opening[2]
                           'ARI_M1:baffle:inboard': 'opening',  # opening[1]
                           'ARI_M1:baffle:outboard': 'opening'}  # opening[0]
        _m1_diag_pv2xrt = {'ARI_M1:multi_trans': 'opening',  # top
                           'ARI_M1:yag_trans': 'opening'}  # bottom

        _m2_baff_pv2xrt = {'ARI_M2:baffle:top': 'opening',  # opening[3]
                           'ARI_M2:baffle:bottom': 'opening',  # opening[2]
                           'ARI_M2:baffle:inboard': 'opening',  # opening[1]
                           'ARI_M2:baffle:outboard': 'opening'}  # opening[0]
        self.pv2xrt = {'ARI_M1:baffle': _m1_baff_pv2xrt,
                       'ARI_M1:diag': _m1_diag_pv2xrt,
                       'ARI_M2:baffle': _m2_baff_pv2xrt}

    def activate(self, update=None, updated=False):
        """
        A method adding or modifying the beamOut attribute.

        This method modifies the Object of beamline aperture if any parameters
        had been changed and then updates the outcome of Beam Object
        accordingly.


        Parameters
        ----------
        update: a dict wrapping up the PV names and values,
                update = {'ARI_M2:Ry_fine':0.2}.

        updated: a boolean, i.e., False (by default) or True.
        The Ture means the outcome of Beam Object needs to be updated
        as the beamline aperture has been modified.

        Returns
        -------
        updated : Boolean
            Potentially modified the input parameter updated if the update
            indicates a re-activation required.

        """

        if update is not None:
            for pv_name, pv_val in update.items():
                if pv_name.split(':')[-1] in ['x', 'y', 'z']:
                    center_list = getattr(self, 'center').copy()

                    # Find out the position of changed element based on the
                    # coordination transformation between NSLS2 and XRT
                    unit_vector_trans_NSLS2 = np.array([0, 0, 0])
                    for i, p in enumerate(['x', 'y', 'z']):
                        if pv_name.split(':')[-1] == p:
                            unit_vector_trans_NSLS2[i] = 1.0
                    unit_vector_trans_XRT = np.dot(
                        _coordinate_NSLS2XRT['upward'], unit_vector_trans_NSLS2)

                    center_list[int(np.where(
                        unit_vector_trans_XRT != 0)[0][0])] = (
                            pv_val * unit_vector_trans_XRT[int(
                                np.where(unit_vector_trans_XRT != 0)[0][0])])
                    if getattr(self, 'center') != center_list:
                        setattr(self, 'center', center_list)
                        updated = True

                elif pv_name.split(':')[-1] in ['top', 'bottom', 'inboard',
                                                'outboard']:
                    opening_list = getattr(self, 'opening').copy()

                    # Note: convert the coordination from XRT to NSLS-II
                    if pv_name.split(':')[-1] == 'top':
                        opening_list[3] = pv_val
                    elif pv_name.split(':')[-1] == 'bottom':
                        opening_list[2] = pv_val
                    elif pv_name.split(':')[-1] == 'inboard':
                        opening_list[1] = -pv_val
                    elif pv_name.split(':')[-1] == 'outboard':
                        opening_list[0] = -pv_val

                    if getattr(self, 'opening') != opening_list:
                        setattr(self, 'opening', opening_list)
                        updated = True
                else:
                    if getattr(self, self.pv2xrt[pv_name.split(':')[0]][
                            pv_name]) != pv_val:
                        setattr(self, self.pv2xrt[pv_name.split(':')[0]][
                            pv_name], pv_val)
                        updated = True

        if updated:
            self.beamIn = getattr(self._upstream, 'beamOut')
            self.beamOut = self.propagate(self.beamIn)

        return updated


class ID29Screen(xrt_screen.Screen):
    """
    A modified Screen class including the beamIn and beamOut attributes.

    Updates the xrt.backends.raycing.screens.Screen with an update method,
    and adds the Beam Object (beamIn/beamOut) generated from the expose()
    method.

    Parameters
    ----------
    upstream : arguments, such as m1, pgm ...
        The argument takes the beamline component that has Beam Object.

    *args : arguments
        The arguments passed to the parent
        'xrt.backends.raycing.screens.Screen' class.

    **kwargs : keyword arguments
        The keyword arguments passed to the parent
        'xrt.backends.raycing.screens.Screen' class.

    Attributes
    ----------
    *attrs : many
        The attributes of the `xrt.backends.raycing.screens.Screen` class.

    beamIn :
        Input of Beam Object in global coordinate!

    beamOut :
        Output of Beam Object in global coordinate!

    pv2xrt : dict
        Mapping the PV names and the terminology of XRT.

    _upstream : argument
        upstream.

    Methods
    -------
    *methods : many
        The methods of the parent `xrt.backends.raycing.screens.Screen` class.

    activate(update=None, updated=False) :
        A method generating the beamOut attribute and updating the attribute if
        any parameters in update had been changed.

    """
    def __init__(self, upstream=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.beamIn = None  # Input in global coordinate!
        self.beamOut = None  # Output in global coordinate!
        self._upstream = upstream  # Object from modified XRT

        _m1_screen_pv2xrt = {'ARI_M1:Screen:x': 'center',
                             'ARI_M1:Screen:y': 'center'}

        self.pv2xrt = {'ARI_M1:Screen': _m1_screen_pv2xrt}

    def activate(self, update=None, updated=False):
        """

        A method adding or modifying the beamOut attribute.

        This method modifies the Object of beamline screen if any parameters
        had been changed and then updates the outcome of Beam Object
        accordingly.


        Parameters
        ----------
        update: a dict wrapping up the PV names and values,
                update = {'ARI_M2:Ry_fine':0.2}.

        updated: a boolean, i.e., False (by default) or True.
        The Ture means the outcome of Beam Object needs to be updated
        as the beamline aperture has been modified.

        Returns
        -------
        updated : Boolean
            Potentially modified the input parameter updated if the update
            indicates a re-activation required.

        """

        if update is not None:
            for pv_name, pv_val in update.items():
                if pv_name.split(':')[-1] in ['x', 'y', 'z']:
                    center_list = getattr(self, 'center').copy()

                    # Find out the position of changed element based on the
                    # coordination transformation between NSLS2 and XRT
                    unit_vector_trans_NSLS2 = np.array([0, 0, 0])
                    for i, p in enumerate(['x', 'y', 'z']):
                        if pv_name.split(':')[-1] == p:
                            unit_vector_trans_NSLS2[i] = 1.0
                    unit_vector_trans_XRT = np.dot(
                        _coordinate_NSLS2XRT['upward'], unit_vector_trans_NSLS2)

                    center_list[int(np.where(
                        unit_vector_trans_XRT != 0)[0][0])] = (
                            pv_val * unit_vector_trans_XRT[int(np.where(
                                unit_vector_trans_XRT != 0)[0][0])])
                    if getattr(self, 'center') != center_list:
                        setattr(self, 'center', center_list)
                        updated = True
                else:
                    if getattr(self, self.pv2xrt[pv_name.split(':')[0]][
                            pv_name]) != pv_val:
                        setattr(self, self.pv2xrt[pv_name.split(':')[0]][
                            pv_name], pv_val)
                        updated = True

        if updated:
            self.beamIn = getattr(self._upstream, 'beamOut')
            self.beamOut = self.expose(self.beamIn)

        return updated