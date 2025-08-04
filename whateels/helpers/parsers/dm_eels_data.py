
import numpy as np
from typing import List
from ...helpers.dm_file_reader.abstract_classes import IDM_EELS_DataHandler
from ..logging import Logger
from ...errors import *

_logger = Logger.get_logger("dm_eels_data.log", __name__)

class DM_EELS_data(IDM_EELS_DataHandler):
    """
    The idea of this class is to extract relevant EELS data from the
    parsed dictionary. It acts as a handler, as it can retrieve the
    relevant information for its later usage
    """

    # Supported types to be read using numpy from file.
    _supported_dtypes = {
        1: "int16",
        2: "float32",
        6: "uint8",
        7: "int32",
        9: "int8",
        10: "uint16",
        11: "uint32",
        12: "float64",
        23: "float32"
    }

    def get_file_data(self, file, infoDict=None):
        """
        Store all image metadata from the parsed info dictionary.
        Collects all images into self.image_dict for later access.
        """
        self.f = file  # An opened file, handled from the factory later on.
        if not infoDict:
            message = f"Expected an informaction dictionary from parser. None provided : {infoDict =}"
            _logger.exception(message)
            raise DMEmptyInfoDictionary(message)
        try:
            # Only keep entries that have both 'ImageData' and 'ImageTags' keys, and pass all real-image filters
            print(infoDict)
            all_blocks = infoDict["ImageList"]
            
            self.spectrum_images = {
                k: v for k, v in all_blocks.items()
                if (
                    isinstance(v, dict)
                    and 'ImageData' in v
                    and 'ImageTags' in v
                    and isinstance(v['ImageTags'], dict)
                    and len(v['ImageTags']) > 0
                    and not (len(v['ImageTags']) == 1 and 'GMS Version' in v['ImageTags'])
                )
            }
        except Exception:
            message = f"The dictionary provided after parsing the file does not contain spectral information.\n{infoDict.keys()}"
            _logger.exception(message)
            raise DMNonEelsError(message)
        # For backward compatibility, set the first image as spectralInfo
        imageKeys = list(self.spectrum_images.keys())
        self.spectralInfo = self.spectrum_images[imageKeys[0]] if imageKeys else None

    def get_all_images(self):
        """
        Returns a dict of all images parsed from the file, each with its metadata.
        """
        return self.spectrum_images

    def _recursively_add_key(self, infoD, keylist):
        """Method used to expand the dictionary recursevely, if a keyError is raised during
        the info reading. This is useful to create the dictionary structure expected for the
        E0, alpha and beta values later on. So, if a _setter function is called for these
        parameters, the correct route is in place to modify them
        """
        for el in keylist:
            if el not in infoD:
                infoD[el] = dict()
            infoD = infoD[el]

    @property
    def beam_energy(self):
        """Beam energy read from file (informationDictionary). In reality, a voltage is read.
        Returns
        --------------
        E0 : float = Value in keV"""
        try:
            E0 = self.spectralInfo["ImageTags"]["Microscope Info"]["Voltage"] / 1000
        except KeyError as e:
            msg = "Expected a value for the beam energy. No such value in the parsed dictionary found"
            _logger.warning(msg)
            _logger.warning(e)
            self._recursively_add_key(
                self.spectralInfo, ["ImageTags", "Microscope Info"]
            )
            _logger.info(
                "Added Route to the dictionary -> [ImageTags][Microscope Info]"
            )
            E0 = 0
            self.spectralInfo["ImageTags"]["Microscope Info"]["Voltage"] = E0
            _logger.info(f"Acceleration voltage V0 value updated to {E0*1000} V")
        return E0

    def _set_beam_energy(self, value, kV=True):
        """Method that changes the beam energy from a given value. The value is most ofen given in kV"""
        if kV:
            value *= 1000
        self.spectralInfo["ImageTags"]["Microscope Info"]["Voltage"] = value
        _logger.info(f"Acceleration Voltage V value updated to {value} V")

    @property
    def convergence_angle(self):
        """Convergence semi angle property, read from dictionary if available.
        Returns
        --------------
        alpha : float = Value in mrad
        """
        try:
            alpha = self.spectralInfo["ImageTags"]["EELS"]["Experimental Conditions"][
                "Convergence semi-angle (mrad)"
            ]
        except KeyError as e:
            msg = "Expected a value for the convergence angle. No such value in the parsed dictionary found"
            _logger.warning(msg)
            _logger.warning(e)
            self._recursively_add_key(
                self.spectralInfo, ["ImageTags", "EELS", "Experimental Conditions"]
            )
            _logger.info(
                "Added Route to the dictionary -> [ImageTags][EELS][Experimental Conditions]"
            )
            alpha = 0
            self.spectralInfo["ImageTags"]["EELS"]["Experimental Conditions"][
                "Convergence semi-angle (mrad)"
            ] = alpha
            _logger.info(f"Convergence angle alpha value updated to {alpha} mrad")
        return alpha

    def _set_convergence_angle(self, value, rad=False):
        """Method that changes the conovergence semi angle from a given value. The value is most ofen given in mrad"""
        if rad:
            value *= 1000
        self.spectralInfo["ImageTags"]["EELS"]["Experimental Conditions"][
            "Convergence semi-angle (mrad)"
        ] = value
        _logger.info(f"Convergence angle alpha value updated to {value} mrad")

    @property
    def collection_angle(self):
        """Collection semi angle property, read from dictionary if available.
        Returns
        --------------
        beta : float = Value in mrad"""
        try:
            beta = self.spectralInfo["ImageTags"]["EELS"]["Experimental Conditions"][
                "Collection semi-angle (mrad)"
            ]
        except KeyError as e:
            msg = "Expected a value for the convergence angle. No such value in the parsed dictionary found"
            _logger.warning(msg)
            _logger.warning(e)
            self._recursively_add_key(
                self.spectralInfo, ["ImageTags", "EELS", "Experimental Conditions"]
            )
            _logger.info(
                "Added Route to the dictionary -> [ImageTags][EELS][Experimental Conditions]"
            )
            beta = 0
            self.spectralInfo["ImageTags"]["EELS"]["Experimental Conditions"][
                "Collection semi-angle (mrad)"
            ] = beta
            _logger.info(f"Collection angle beta value updated to {beta} mrad")
        return beta

    def _set_collection_angle(self, value, rad=False):
        """Method that changes the collection semi angle from a given value. The value is most ofen given in mrad"""
        if rad:
            value *= 1000
        self.spectralInfo["ImageTags"]["EELS"]["Experimental Conditions"][
            "Collection semi-angle (mrad)"
        ] = value
        _logger.info(f"Collection angle beta value updated to {value} mrad")

    def _set_energy_scale(self, scale_val):
        """Method that sets a new value for the energy scale
        Raises ValueError whenever we face an spectrum dataset with ill-defined units
        """
        scale_items = [
            k
            for k, el in self.spectralInfo["ImageData"]["Calibrations"][
                "Dimension"
            ].items()
            if el["Units"] == "eV"
        ]
        if len(scale_items) != 1:
            raise ValueError
        self.spectralInfo["ImageData"]["Calibrations"]["Dimension"][scale_items[0]][
            "Scale"
        ] = scale_val

    def _set_lateral_scale(self, scale_val):
        """Method that sets a new scale for the lateral units, if they exists
        It assumes that the lateral units are the same for spectrum images (square pixels)
        """
        scale_items = [
            k
            for k, el in self.spectralInfo["ImageData"]["Calibrations"][
                "Dimension"
            ].items()
            if el["Units"] != "eV"
        ]

        for el in scale_items:
            self.spectralInfo["ImageData"]["Calibrations"]["Dimension"][el][
                "Scale"
            ] = scale_val

    def _set_energy_origin(self, offset_val):
        """Method that changes the offset value of the energy axis"""
        scale_items = [
            k
            for k, el in self.spectralInfo["ImageData"]["Calibrations"][
                "Dimension"
            ].items()
            if el["Units"] == "eV"
        ]
        if len(scale_items) != 1:
            raise ValueError
        self.spectralInfo["ImageData"]["Calibrations"]["Dimension"][scale_items[0]][
            "Origin"
        ] = offset_val

    # Now, a complex method that adjusts the energy origin automatically given the E-axis origin

    def calibrate_single_channel(self, eValue: float, pixID: int = 0) -> None:
        """Given a single energy loss channel and a value for the Energy Loss value
        expected, modifies the origins property, so the channel lies in the actual expected
        energy value.
        If no index is given, it is assumed to be the origin of the energy axis ...
        """
        eAxis_offset = -(
            eValue / self.scales[0] - pixID
        )  # Expected offset value for the energy axis
        self._set_energy_origin(eAxis_offset)

    # Now, a complex method that adjusts the energy origin automatically given two positions (indices)
    # in the E-axis and their expected values

    def calibrate_dual_channels(
        self, eValues: List[float], pixIDs: List[int] = [0, -1]
    ) -> None:
        """Given two indices in the energy axis and two expected energy loss values, the scale
        is calibrated, as well as the origin position, so the provided indices for the new
        energy loss axis correspond to the given energy loss values.
        If no index are provided, they are assumed to be the origin and last index of the energy axis
        """
        # TODO program exceptions to enforce good energy values lists and pixel ids (i.e., avoid deltaE < 0)
        deltaE = eValues[1] - eValues[0]
        numChannels = pixIDs[1] - pixIDs[0]
        new_scale = deltaE / numChannels
        self._set_energy_scale(new_scale)
        # And now, we calibrate the origin to have the correct possitions
        eAxis_offset = -(
            eValues[0] / self.scales[0] - pixIDs[0]
        )  # Expected offset value for the energy axis
        self._set_energy_origin(eAxis_offset)

    @property
    def shape(self):
        """Shape property for the EELS dataset read from the
        information dictionary parsed. DM stores EELS spectral data
        as - SImages (Eloss,Y,X) - SLines(Eloss,X) - SingleSpectrum (Eloss,)
        """
        dims = tuple(
            [el[1] for el in self.spectralInfo["ImageData"]["Dimensions"].items()]
        )
        return dims[::-1]

    # ['Origin']['Scale']['Dimension']

    @property
    def scales(self):
        """scale properties for all the dimensions involved"""
        # TODO safeguard for the cases where the dimensions cannot be read from file
        scale = [
            el["Scale"]
            for k, el in self.spectralInfo["ImageData"]["Calibrations"][
                "Dimension"
            ].items()
        ]
        return np.array(scale)[::-1]

    @property
    def origins(self):
        """origins for the dimensions involved"""
        # TODO safeguard for the cases where the dimensions cannot be read from file
        orig = [
            el["Origin"]
            for k, el in self.spectralInfo["ImageData"]["Calibrations"][
                "Dimension"
            ].items()
        ]
        return np.array(orig)[::-1]

    @property
    def unit_origins(self):
        """Origins for the dimensions involved that include the scaling factors"""
        return -1 * self.origins * self.scales

    @property
    def units(self):
        """Units for the scales involved, one per each dimension"""
        # TODO safeguard for the cases where the dimensions cannot be read from file
        units = []
        for k, el in self.spectralInfo["ImageData"]["Calibrations"][
            "Dimension"
        ].items():
            if not el["Units"]:
                # self.spectralInfo['ImageData']['Calibrations']['Dimension'][k]['Units'] = 'a.u.'
                el["Units"] = "a.u."
            units.append(el["Units"])
        return tuple(units[::-1])

    @property
    def energy_axis(self):
        """Energy axis for the spectral dataset.
        This is one of the more confusing properties to extract
        from DM. By some unknown reason, it is stored"""
        if len(self.shape) == 3:
            return np.arange(self.shape[0]) * self.scales[0] + self.unit_origins[0]
        # For Slines and single spectra, this works ...
        return np.arange(self.shape[-1]) * self.scales[-1] + self.unit_origins[-1]

    def get_eels_data(self):
        """This method will attempt to extract the actual EELS data,
        to be handled to the factory later on.
        It does several things.
        """
        idx = self.spectralInfo["ImageData"]["DataType"]
        try:
            dtype = self._supported_dtypes[idx]
        except KeyError as e:
            message = (
                f"Data Type index ({idx}) read from file ({self.f.name}) not supported."
            )
            _logger.exception(message)
            raise DMNonSupportedDataType(message)

        bSize = self.spectralInfo["ImageData"]["Data"]["bytes_size"]
        offset = self.spectralInfo["ImageData"]["Data"]["offset"]
        nItems = self.spectralInfo["ImageData"]["Data"]["size"]
        # Checking that the info is readable
        if bSize / nItems != np.dtype(dtype).itemsize:
            message = f"Size_in_bytes / Number_of_items = {bSize / nItems}\
                != from NumPy expected size for {dtype} = {np.dtype(dtype).itemsize}"
            _logger.error(message)
            raise DMConflictingDataTypeRead(message)

        self.f.seek(0)
        data = np.fromfile(self.f, count=nItems, offset=offset, dtype=dtype)
        return data.reshape(self.shape)

    def handle_EELS_data(self):
        """
        This method will basically read from file, using numpy, the EELS data.
        After that, it returns itself, the instance of this class created, so the properties
        of the object can be accessed from the exterior (energy_axis, shape, collection_angle, etc)
        """
        self.data = self.get_eels_data()
        return self

