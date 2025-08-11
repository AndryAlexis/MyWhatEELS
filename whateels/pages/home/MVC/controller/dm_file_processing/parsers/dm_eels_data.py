
import numpy as np
import json
from typing import List
from whateels.helpers.logging import Logger
from whateels.errors import *
from whateels.shared_state import AppState

_logger = Logger.get_logger("dm_eels_data.log", __name__)

class DM_EELS_data:
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

    def __init__(self):
        """Initialize instance attributes."""
        self.spectrum_images = {}
        self.spectralInfo = None
        self.f = None
        self.data = None

    # ==================== PUBLIC INTERFACE ====================
    
    def get_file_data(self, file, infoDict=None):
        """
        Store metadata and filter spectrum images from parsed info dictionary.
        
        This method combines metadata storage and spectrum filtering for backward compatibility.
        For new code, consider using _store_metadata() and _filter_spectrum_images() separately.
        """
        stored_metadata = self._store_metadata(file, infoDict)
        self.spectrum_images = self._filter_spectrum_images(stored_metadata)
        
        # For backward compatibility, set the first image as spectralInfo
        imageKeys = list(self.spectrum_images.keys())
        self.spectralInfo = self.spectrum_images[imageKeys[0]] if imageKeys else None

    def handle_EELS_data(self):
        """
        This method will basically read from file, using numpy, the EELS data.
        After that, it returns itself, the instance of this class created, so the properties
        of the object can be accessed from the exterior (energy_axis, shape, collection_angle, etc)
        """
        self.data = self._get_eels_data()
        return self

    # ==================== PUBLIC PROPERTIES ====================

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

    @property
    def energy_axis(self):
        """Energy axis for the spectral dataset.
        This is one of the more confusing properties to extract
        from DM. By some unknown reason, it is stored"""
        if len(self.shape) == 3:
            return np.arange(self.shape[0]) * self._get_scales()[0] + self._get_unit_origins()[0]
        # For Slines and single spectra, this works ...
        return np.arange(self.shape[-1]) * self._get_scales()[-1] + self._get_unit_origins()[-1]

    # ==================== PRIVATE METHODS ====================

    def _store_metadata(self, file, infoDict=None):
        """
        Store file handle and metadata from parsed info dictionary.
        
        Parameters
        ----------
        file : file object
            Opened binary file handle
        infoDict : dict
            Parsed metadata dictionary from DM file
            
        Raises
        ------
        DMEmptyInfoDictionary
            If infoDict is None or empty
        DMNonEelsError
            If dictionary doesn't contain expected structure
        """
        self.f = file
        if not infoDict:
            message = f"Expected an information dictionary from parser. None provided : {infoDict =}"
            _logger.exception(message)
            raise DMEmptyInfoDictionary(message)
        
        try:
            # Store metadata in AppState for application-wide access
            AppState().metadata = infoDict
            _logger.info("Metadata stored in AppState")
            return infoDict
        except Exception:
            message = f"Failed to store metadata in AppState.\n{infoDict.keys() if infoDict else 'None'}"
            _logger.exception(message)
            raise DMNonEelsError(message)

    def _filter_spectrum_images(self, infoDict):
        """
        Filter and extract spectrum images from metadata dictionary.
        
        Parameters
        ----------
        infoDict : dict
            Metadata dictionary containing ImageList
            
        Returns
        -------
        dict
            Filtered spectrum images with valid EELS data
            
        Raises
        ------
        DMNonEelsError
            If no valid spectrum images found
        """
        try:
            all_blocks = infoDict["ImageList"]
            
            spectrum_images = {
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
            
            if not spectrum_images:
                raise ValueError("No valid spectrum images found")
                
            return spectrum_images
            
        except Exception:
            message = f"The dictionary provided after parsing the file does not contain spectral information.\n{infoDict.keys()}"
            _logger.exception(message)
            raise DMNonEelsError(message)

    def _get_eels_data(self):
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

    def _get_scales(self):
        """scale properties for all the dimensions involved"""
        # TODO safeguard for the cases where the dimensions cannot be read from file
        scale = [
            el["Scale"]
            for k, el in self.spectralInfo["ImageData"]["Calibrations"][
                "Dimension"
            ].items()
        ]
        return np.array(scale)[::-1]

    def _get_origins(self):
        """origins for the dimensions involved"""
        # TODO safeguard for the cases where the dimensions cannot be read from file
        orig = [
            el["Origin"]
            for k, el in self.spectralInfo["ImageData"]["Calibrations"][
                "Dimension"
            ].items()
        ]
        return np.array(orig)[::-1]

    def _get_unit_origins(self):
        """Origins for the dimensions involved that include the scaling factors"""
        return -1 * self._get_origins() * self._get_scales()

    def _get_units(self):
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

