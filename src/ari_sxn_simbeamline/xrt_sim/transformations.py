import numpy as np


def _rotation_matrix(angles):
    """
    A function that calculates the rotation matrix for a given set of angles.

    Parameters
    ----------
    angles : np.array, list or tuple
        A 3 element array, list or tuple that defines the angles (Rx, Ry, Rz),
        in degrees around the x, y and z axes respectively.

    Returns
    -------
    rot_matrix : np.array
        A 3x3 numpy array that is the rotation matrix.
    """
    Rx, Ry, Rz = angles

    # Rotation matrices around x, y, z axes
    Rx_matrix = np.array([[1, 0, 0],
                          [0, np.cos(Rx), -np.sin(Rx)],
                          [0, np.sin(Rx), np.cos(Rx)]])

    Ry_matrix = np.array([[np.cos(Ry), 0, np.sin(Ry)],
                          [0, 1, 0],
                          [-np.sin(Ry), 0, np.cos(Ry)]])

    Rz_matrix = np.array([[np.cos(Rz), -np.sin(Rz), 0],
                          [np.sin(Rz), np.cos(Rz), 0],
                          [0, 0, 1]])

    rot_matrix = np.dot(Rz_matrix, np.dot(Ry_matrix, Rx_matrix))

    return rot_matrix


def _nsls2_local_to_nsls2global(nsls2_local, origin):
    """
    A method that converts the coordinates from NSLS-II local to NSLS-II
    global coordinates.

    In this method the NSLSII local coordinates are in the form:

     $(x_{l}, y_{l}, z_{l}, Rx_{l}, Ry_{l}, Rz_{l})$

     where: $x_{l}, y_{l}, z_{l}$ are the coordinates in local NSLSII
        coordinates and $Rx_{l}, Ry_{l}, Rz_{l}$ are the angles around each
        axis defining the outgoing beam direction in local NSLSII
        coordinates.

    In this method the NSLSII global coordinates are in the form:

     $(x_{g}, y_{g}, z_{g}, Rx_{g}, Ry_{g}, Rz_{g})$

     where: $x_{g}, y_{g}, z_{g}$ are the coordinates in local NSLSII
        coordinates and $Rx_{g}, Ry_{g}, Rz_{g}$ are the angles around each
        axis defining incoming beam direction in global NSLSII
        coordinates.

    This function uses a rotation matrix to first rotate the local coordinates
    to be parallel to the global coordinates and them translates them via the
    origin coordinates. This works because the local NSLS-II coordinates are
    always defined with the z axis along the incoming beam direction and the y
    axis nominally vertical.

    Parameters
    ----------
    nsls2_local : np.array, list or tuple.
        A 1x6 array that is the coordinates in NSLS-II local
        coordinates, see doc-string for coordinate description.
    origin : np.array
        A 1x6 array that is the origin of the component in NSLS-II
        global coordinates, see doc-string for coordinate description.

    Returns
    -------
    nsls2_global : np.array
        A 1x6 numpy array that is the coordinates in NSLS-II global
        coordinates.
    """
    # Convert the local and origin to 1x3 numpy arrays
    local_coords = np.array(nsls2_local[:3])
    local_angles = np.array(nsls2_local[3:])
    origin_coords = np.array(origin[:3])
    origin_angles = np.array(origin[3:])

    # rotate and translate the local coordinates into global coordinates
    rotation_matrix = _rotation_matrix(origin_angles)
    global_coords = origin_coords + np.dot(rotation_matrix, local_coords)

    # translate the local angles into global angles
    global_angles = origin_angles + local_angles

    # combine the global coordinates and angles into a single array
    nsls2_global = np.concatenate((global_coords, global_angles))

    return nsls2_global


def _nsls2_global_to_nsls2_local(nsls2_global, origin):
    """
    A method that converts the coordinates from NSLS-II global to NSLS-II
    local coordinates.

    In this method the NSLSII local coordinates are in the form:

     $(x_{l}, y_{l}, z_{l}, Rx_{l}, Ry_{l}, Rz_{l})$

     where: $x_{l}, y_{l}, z_{l}$ are the coordinates in local NSLSII
        coordinates and $Rx_{l}, Ry_{l}, Rz_{l}$ are the angles around each
        axis defining the outgoing beam direction in local NSLSII
        coordinates.

    In this method the NSLSII global coordinates are in the form:

     $(x_{g}, y_{g}, z_{g}, Rx_{g}, Ry_{g}, Rz_{g})$

     where: $x_{g}, y_{g}, z_{g}$ are the coordinates in local NSLSII
        coordinates and $Rx_{g}, Ry_{g}, Rz_{g}$ are the angles around each
        axis defining incoming beam direction in global NSLSII
        coordinates.

    This function uses a rotation matrix to first rotate the local coordinates
    to be parallel to the global coordinates and them translates them via the
    origin coordinates. This works because the local NSLS-II coordinates are
    always defined with the z axis along the incoming beam direction and the y
    axis nominally vertical.

    Parameters
    ----------
    nsls2_global : np.array, list or tuple.
        A 1x6 array that is the coordinates in NSLS-II global
        coordinates, see doc-string for coordinate description.
    origin : np.array
        A 1x6 array that is the origin of the component in NSLS-II
        global coordinates, see doc-string for coordinate description.

    Returns
    -------
    nsls2_local : np.array
        A 1x6 numpy array that is the coordinates in NSLS-II local
        coordinates.
    """
    # Convert the local and origin to 1x3 numpy arrays
    global_coords = np.array(nsls2_global[:3])
    global_angles = np.array(nsls2_global[3:])
    origin_coords = np.array(origin[:3])
    origin_angles = np.array(origin[3:])

    # rotate and translate the local coordinates into global coordinates
    rotation_matrix = _rotation_matrix(origin_angles)
    local_coords = np.dot(rotation_matrix.T, global_coords-origin_coords)

    # translate the global angles into local angles
    local_angles = global_angles - origin_angles

    # combine the global coordinates and angles into a single array
    nsls2_local = np.concatenate((local_coords, local_angles))

    return nsls2_local


def _nsls2_global_to_xrt_global(nsls2_global):
    """
    A method that converts the coordinates from NSLS-II global to XRT global
    coordinates.

    In this method the NSLSII global coordinates are in the form:

     $(x_{g}, y_{g}, z_{g}, Rx_{g}, Ry_{g}, Rz_{g})$

     where: $x_{g}, y_{g}, z_{g}$ are the coordinates in local NSLSII
        coordinates and $Rx_{g}, Ry_{g}, Rz_{g}$ are the angles around each
        axis defining the outgoing beam direction in global NSLSII
        coordinates.

    In this method the XRT global coordinates are in the form:
    $$
    (x_{g}^{xrt}, y_{g}^{xrt}, z_{g}^{xrt},
     Rx_{g}^{xrt}, Ry_{g}^{xrt}, Rz_{g}^{xrt})
    $$

     where: $x_{g}^{xrt}, y_{g}^{xrt}, z_{g}^{xrt}$ are the coordinates in
        global NSLSII coordinates and $Rx_{g}^{xrt}, Ry_{g}^{xrt}, Rz_{g}^{xrt}$
        are the angles around each axis defining incoming beam direction in
        global XRT coordinates.

    This function uses a rotation matrix, defined as swapping the z and y axes,
    to rotate the NSLSII global coordinates into XRT global coordinates.

    Parameters
    ----------
    nsls2_global : np.array, list or tuple.
        A 1x6 array that is the coordinates in NSLS-II global
        coordinates, see doc-string for coordinate description.

    Returns
    -------
    xrt_global : np.array
        A 1x6 numpy array that is the coordinates in XRT global coordinates.
    """
    # Convert the local and origin to 1x3 numpy arrays
    nsls2_coords = np.array(nsls2_global[:3])
    nsls2_angles = np.array(nsls2_global[3:])

    # rotation matrix which is swapping the z axis for the y axis
    rotation_matrix = np.array([[0, -1.0, 0], [0, 0, 1.0], [-1.0, 0, 0]])

    # rotate the NSLS-II coordinates and angles into XRT coordinates and angles
    xrt_coords = np.dot(rotation_matrix, nsls2_coords)
    xrt_angles = np.dot(rotation_matrix, nsls2_angles)

    # combine the global coordinates and angles into a single array
    xrt_global = np.concatenate((xrt_coords, xrt_angles))

    return xrt_global


def _xrt_global_to_nsls2_global(xrt_global):
    """
    A method that converts the coordinates from XRT global to NSLSII global
    coordinates.

    In this method the NSLSII global coordinates are in the form:

     $(x_{g}, y_{g}, z_{g}, Rx_{g}, Ry_{g}, Rz_{g})$

     where: $x_{g}, y_{g}, z_{g}$ are the coordinates in local NSLSII
        coordinates and $Rx_{g}, Ry_{g}, Rz_{g}$ are the angles around each
        axis defining the outgoing beam direction in global NSLSII
        coordinates.

    In this method the XRT global coordinates are in the form:
    $$
    (x_{g}^{xrt}, y_{g}^{xrt}, z_{g}^{xrt},
     Rx_{g}^{xrt}, Ry_{g}^{xrt}, Rz_{g}^{xrt})
    $$

     where: $x_{g}^{xrt}, y_{g}^{xrt}, z_{g}^{xrt}$ are the coordinates in
        global NSLSII coordinates and $Rx_{g}^{xrt}, Ry_{g}^{xrt}, Rz_{g}^{xrt}$
        are the angles around each axis defining incoming beam direction in
        global XRT coordinates.

    This function uses a rotation matrix, defined as swapping the y and z
    axes, to rotate the NSLSII global coordinates into XRT global
    coordinates.

    Parameters
    ----------
    xrt_global : np.array, list or tuple.
        A 1x6 array that is the coordinates in NSLS-II global
        coordinates, see doc-string for coordinate description.

    Returns
    -------
    nsls2_global : np.array
        A 1x6 numpy array that is the coordinates in XRT global coordinates.
    """
    # Convert the local and origin to 1x3 numpy arrays
    xrt_coords = np.array(xrt_global[:3])
    xrt_angles = np.array(xrt_global[3:])

    # rotation matrix which is swapping the z axis for the y axis
    rotation_matrix = np.array([[0, -1.0, 0], [0, 0, 1.0], [-1.0, 0, 0]])

    # rotate the NSLS-II coordinates and angles into XRT coordinates and angles
    nsls2_coords = np.dot(rotation_matrix, xrt_coords)
    nsls2_angles = np.dot(rotation_matrix, xrt_angles)

    # combine the global coordinates and angles into a single array
    nsls2_global = np.concatenate((nsls2_coords, nsls2_angles))

    return nsls2_global


class _Nsls2_local:
    """
    A class that contains the NSLS-II local coordinates transformations.

    This class contains the methods to transform between NSLS-II local
    coordinates and  NSLS-II global, XRT local and XRT global coordinates. The
    transformations are done using rotation matrices and translations.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """

    def __init__(self):
        pass

    def to_nsls2_global(self, nsls2_local, origin):
        """
        Convert NSLS-II local coordinates to NSLS-II global coordinates.

        Parameters
        ----------
        nsls2_local : np.array, list or tuple.
            A 1x6 array that is the coordinates in NSLS-II local
            coordinates, see doc-string for coordinate description.
        origin : np.array
            A 1x6 array that is the origin of the component in NSLS-II
            global coordinates, see doc-string for coordinate description.

        Returns
        -------
        nsls2_global : np.array
            A 1x6 numpy array that is the coordinates in NSLS-II global
            coordinates.
        """
        return _nsls2_local_to_nsls2global(nsls2_local, origin)

    def to_xrt_global(self, nsls2_local, origin):
        """
        Convert NSLS-II local coordinates to XRT global coordinates.

        Parameters
        ----------
        nsls2_local : np.array, list or tuple.
            A 1x6 array that is the coordinates in NSLS-II local
            coordinates, see doc-string for coordinate description.
        origin : np.array
            A 1x6 array that is the origin of the component in NSLS-II
            global coordinates, see doc-string for coordinate description.

        Returns
        -------
        xrt_global : np.array
            A 1x6 numpy array that is the coordinates in XRT global
            coordinates.
        """
        nsls2_global = _nsls2_local_to_nsls2global(nsls2_local, origin)
        return _nsls2_global_to_xrt_global(nsls2_global)

    def to_xrt_local(self, nsls2_local, origin):
        """
        Convert NSLS-II local coordinates to XRT local coordinates.

        Parameters
        ----------
        nsls2_local : np.array, list or tuple.
            A 1x6 array that is the coordinates in NSLS-II local
            coordinates, see doc-string for coordinate description.
        origin : np.array
            A 1x6 array that is the origin of the component in NSLS-II
            global coordinates, see doc-string for coordinate description.

        Returns
        -------
        xrt_local : np.array
            A 1x6 numpy array that is the coordinates in XRT local
            coordinates.
        """
        xrt_global = self.to_xrt_global(nsls2_local, origin)
        xrt_origin = _nsls2_global_to_xrt_global(origin)
        xrt_local = xrt_global - xrt_origin

        return xrt_local


class _Nsls2_global:
    """
    A class that contains the NSLS-II global coordinates transformations.

    This class contains the methods to transform between NSLS-II global
    coordinates and  NSLS-II local, XRT local and XRT global coordinates. The
    transformations are done using rotation matrices and translations.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """

    def __init__(self):
        pass

    def to_nsls2_local(self, nsls2_global, origin):
        """
        Convert NSLS-II local coordinates to NSLS-II global coordinates.

        Parameters
        ----------
        nsls2_global : np.array, list or tuple.
            A 1x6 array that is the coordinates in NSLS-II global
            coordinates, see doc-string for coordinate description.
        origin : np.array
            A 1x6 array that is the origin of the component in NSLS-II
            global coordinates, see doc-string for coordinate description.

        Returns
        -------
        nsls2_local : np.array
            A 1x6 numpy array that is the coordinates in NSLS-II global
            coordinates.
        """
        return _nsls2_global_to_nsls2_local(nsls2_global, origin)

    def to_xrt_global(self, nsls2_global):
        """
        Convert NSLS-II local coordinates to XRT global coordinates.

        Parameters
        ----------
        nsls2_global : np.array, list or tuple.
            A 1x6 array that is the coordinates in NSLS-II global
            coordinates, see doc-string for coordinate description.

        Returns
        -------
        xrt_global : np.array
            A 1x6 numpy array that is the coordinates in XRT global
            coordinates.
        """

        return _nsls2_global_to_xrt_global(nsls2_global)

    def to_xrt_local(self, nsls2_global, origin):
        """
        Convert NSLS-II global coordinates to XRT local coordinates.

        Parameters
        ----------
        nsls2_global : np.array, list or tuple.
            A 1x6 array that is the coordinates in NSLS-II global
            coordinates, see doc-string for coordinate description.
        origin : np.array
            A 1x6 array that is the origin of the component in NSLS-II
            global coordinates, see doc-string for coordinate description.

        Returns
        -------
        xrt_local : np.array
            A 1x6 numpy array that is the coordinates in XRT local
            coordinates.
        """
        xrt_global = self.to_xrt_global(nsls2_global)
        xrt_origin = _nsls2_global_to_xrt_global(origin)
        xrt_local = xrt_global - xrt_origin

        return xrt_local


class Transform:
    """
    A class that contains the transformation methods between NSLS-II and XRT
    coordinates.

    This class contains the methods to transform between NSLS-II local,
    NSLS-II global, XRT local and XRT global coordinates. The transformations
    are done using rotation matrices and translations.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """

    def __init__(self):
        pass

    nsls2_local = _Nsls2_local()
    nsls2_global = _Nsls2_global()
