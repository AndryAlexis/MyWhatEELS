
import numpy as np
from whateels.helpers.logging import Logger
from whateels.errors import *

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
        self._spectral_info = None
        self._file = None
        self.data = None

    # ==================== PUBLIC INTERFACE ====================
    
    def get_file_data(self, file, infoDict=None):
        """
        Store metadata and filter spectrum images from parsed info dictionary.
        
        This method combines metadata storage and spectrum filtering for backward compatibility.
        """

        self._file = file
        
        if not infoDict:
            message = f"Expected an information dictionary from parser. None provided : {infoDict =}"
            _logger.exception(message)
            raise DMEmptyInfoDictionary(message)

        self.spectrum_images = self._filter_spectrum_images(infoDict)

        # For backward compatibility, set the first image as spectralInfo
        imageKeys = list(self.spectrum_images.keys())
        # TODO - Here is where the code is choosing the first image as spectralInfo
        self._spectral_info = self.spectrum_images[imageKeys[0]] if imageKeys else None
        self._all_spectral_info = self.spectrum_images

    # TODO - DELETE IT
    def handle_EELS_data(self):
        """
        This method will basically read from file, using numpy, the EELS data.
        After that, it returns itself, the instance of this class created, so the properties
        of the object can be accessed from the exterior (energy_axis, shape, collection_angle, etc)
        """
        self.data = self._get_eels_data()
        return self
    
    def handle_all_EELS_data(self):
        self.all_data = self._get_all_eels_data()
        return self

    # ==================== PUBLIC PROPERTIES ====================
    
    # TODO - DELETE IT
    @property
    def spectral_info(self):
        """Spectral information read from file (informationDictionary)."""
        return self._spectral_info

    @property
    def beam_energy(self):
        """Beam energy read from file (informationDictionary). In reality, a voltage is read.
        Returns
        --------------
        E0 : float = Value in keV"""
        try:
            E0 = self._spectral_info["ImageTags"]["Microscope Info"]["Voltage"] / 1000
        except KeyError as e:
            msg = "Expected a value for the beam energy. No such value in the parsed dictionary found"
            _logger.warning(msg)
            _logger.warning(e)
            self._recursively_add_key(
                self._spectral_info, ["ImageTags", "Microscope Info"]
            )
            _logger.info(
                "Added Route to the dictionary -> [ImageTags][Microscope Info]"
            )
            E0 = 0
            self._spectral_info["ImageTags"]["Microscope Info"]["Voltage"] = E0
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
            alpha = self._spectral_info["ImageTags"]["EELS"]["Experimental Conditions"][
                "Convergence semi-angle (mrad)"
            ]
        except KeyError as e:
            msg = "Expected a value for the convergence angle. No such value in the parsed dictionary found"
            _logger.warning(msg)
            _logger.warning(e)
            self._recursively_add_key(
                self._spectral_info, ["ImageTags", "EELS", "Experimental Conditions"]
            )
            _logger.info(
                "Added Route to the dictionary -> [ImageTags][EELS][Experimental Conditions]"
            )
            alpha = 0
            self._spectral_info["ImageTags"]["EELS"]["Experimental Conditions"][
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
            beta = self._spectral_info["ImageTags"]["EELS"]["Experimental Conditions"][
                "Collection semi-angle (mrad)"
            ]
        except KeyError as e:
            msg = "Expected a value for the convergence angle. No such value in the parsed dictionary found"
            _logger.warning(msg)
            _logger.warning(e)
            self._recursively_add_key(
                self._spectral_info, ["ImageTags", "EELS", "Experimental Conditions"]
            )
            _logger.info(
                "Added Route to the dictionary -> [ImageTags][EELS][Experimental Conditions]"
            )
            beta = 0
            self._spectral_info["ImageTags"]["EELS"]["Experimental Conditions"][
                "Collection semi-angle (mrad)"
            ] = beta
            _logger.info(f"Collection angle beta value updated to {beta} mrad")
        return beta

    # TODO - DELETE IT
    @property
    def shape(self):
        """Shape property for the EELS dataset read from the
        information dictionary parsed. DM stores EELS spectral data
        as - SImages (Eloss,Y,X) - SLines(Eloss,X) - SingleSpectrum (Eloss,)
        """
        dims = tuple(
            [el[1] for el in self._spectral_info["ImageData"]["Dimensions"].items()]
        )
        return dims[::-1]

    def _get_image_shape(self, image_dict):
        """
        Get the shape of a spectrum image from its metadata dictionary.
        Returns
        -------
        tuple
            Shape of the image, reversed as in the current property.
        """
        dims = tuple(
            [el[1] for el in image_dict["ImageData"]["Dimensions"].items()]
        )
        return dims[::-1]

    # TODO - DELETE IT
    @property
    def energy_axis(self):
        """Energy axis for the spectral dataset.
        This is one of the more confusing properties to extract
        from DM. By some unknown reason, it is stored"""        
        if len(self.shape) == 3:
            return np.arange(self.shape[0]) * self._get_scales()[0] + self._get_unit_origins()[0]
        # For Slines and single spectra, this works ...
        return np.arange(self.shape[-1]) * self._get_scales()[-1] + self._get_unit_origins()[-1]
    
    @property
    def all_energy_axes(self) -> list[np.ndarray]:
        """
        Get the energy axes for all spectrum images.

        Returns
        -------
        list[np.ndarray] or np.ndarray
            If there are multiple images, returns a list of energy axis arrays (one per image).
            If there is a single 3D image, returns a single energy axis array for that image.
        """
        
        EELS_IMAGE_NUM_AXES = 3
        
        energy_axes = []
        
        for image_dict in self._all_spectral_info.values():
            shape = self._get_image_shape(image_dict)
            
            scale = self._get_scales_of_one_image(image_dict)
            origin = self._get_unit_origins_of_one_image(image_dict)

            if len(shape) == EELS_IMAGE_NUM_AXES:
                # For 3D images, return energy axis based on the first dimension
                energy_axes.append(np.arange(shape[0]) * scale[0] + origin[0])
                continue

            # For Slines and single spectra, this works ...
            energy_axes.append(np.arange(shape[-1]) * scale[-1] + origin[-1])

        return energy_axes

    # ==================== PRIVATE METHODS ====================

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

    # TODO - DELETE IT
    def _get_eels_data(self) -> np.ndarray:
        """
        This method will attempt to extract the actual EELS data,
        to be handled to the factory later on.
        It does several things.

        Returns
        -------
        np.ndarray
            The EELS data for the selected spectrum image, reshaped according to its dimensions.
        """
        idx = self._spectral_info["ImageData"]["DataType"]
        try:
            dtype = self._supported_dtypes[idx]
        except KeyError as e:
            message = (
                f"Data Type index ({idx}) read from file ({self._file.name}) not supported."
            )
            _logger.exception(message)
            raise DMNonSupportedDataType(message)

        bSize = self._spectral_info["ImageData"]["Data"]["bytes_size"]
        offset = self._spectral_info["ImageData"]["Data"]["offset"]
        nItems = self._spectral_info["ImageData"]["Data"]["size"]
        # Checking that the info is readable
        if bSize / nItems != np.dtype(dtype).itemsize:
            message = f"Size_in_bytes / Number_of_items = {bSize / nItems}\
                != from NumPy expected size for {dtype} = {np.dtype(dtype).itemsize}"
            _logger.error(message)
            raise DMConflictingDataTypeRead(message)

        self._file.seek(0)
        data = np.fromfile(self._file, count=nItems, offset=offset, dtype=dtype)
        return data.reshape(self.shape)

    def _get_all_eels_data(self) -> list[np.ndarray]:
        """This method will extract all EELS data from the spectrum images."""
        
        IMAGE_DATA = 'ImageData'
        DATA_TYPE = 'DataType'
        DATA = 'Data'
        BYTES_SIZE = 'bytes_size'
        OFFSET = 'offset'
        SIZE = 'size'
        KEY_ERROR_MESSAGE = "Data Type index ({idx}) read from file ({filename}) not supported."
        READABLE_ERROR_MESSAGE = "Size_in_bytes / Number_of_items = {bSize} != from NumPy expected size for {nItems} = {dtype}"

        all_eels_data = []

        for _, image_data in self.spectrum_images.items():
            idx = image_data[IMAGE_DATA][DATA_TYPE]
            try:
                dtype = self._supported_dtypes[idx]
            except KeyError:
                message = KEY_ERROR_MESSAGE.format(idx=idx, filename=self._file.name)
                _logger.exception(message)
                raise DMNonSupportedDataType(message)

            bSize = image_data[IMAGE_DATA][DATA][BYTES_SIZE]
            offset = image_data[IMAGE_DATA][DATA][OFFSET]
            nItems = image_data[IMAGE_DATA][DATA][SIZE]

            # Checking that the info is readable
            if bSize / nItems != np.dtype(dtype).itemsize:
                message = READABLE_ERROR_MESSAGE.format(bSize=bSize, nItems=nItems, dtype=dtype)
                _logger.error(message)
                raise DMConflictingDataTypeRead(message)

            self._file.seek(0)
            shape = self._get_image_shape(image_data)
            all_eels_data.append(np.fromfile(self._file, count=nItems, offset=offset, dtype=dtype).reshape(shape))

        return all_eels_data

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

    # TODO - DELETE IT
    def _get_scales(self):
        """scale properties for all the dimensions involved"""
        # TODO safeguard for the cases where the dimensions cannot be read from file
        scale = [
            el["Scale"]
            for k, el in self._spectral_info["ImageData"]["Calibrations"]["Dimension"].items()
        ]
        return np.array(scale)[::-1]

    def _get_scales_of_one_image(self, image_dict):
        """Get scale properties for a single image."""
        # TODO safeguard for the cases where the dimensions cannot be read from file
        scale = [
            el["Scale"]
            for k, el in image_dict["ImageData"]["Calibrations"]["Dimension"].items()
        ]
        return np.array(scale)[::-1]

    # TODO - DELETE IT
    def _get_origins(self):
        """origins for the dimensions involved"""
        # TODO safeguard for the cases where the dimensions cannot be read from file
        orig = [
            el["Origin"]
            for k, el in self._spectral_info["ImageData"]["Calibrations"][
                "Dimension"
            ].items()
        ]
        return np.array(orig)[::-1]
    
    def _get_origins_of_one_image(self, image_dict):
        """Get origins for the dimensions of a single image."""
        # TODO safeguard for the cases where the dimensions cannot be read from file
        orig = [
            el["Origin"]
            for k, el in image_dict["ImageData"]["Calibrations"]["Dimension"].items()
        ]
        return np.array(orig)[::-1]

    # TODO - DELETE IT
    def _get_unit_origins(self):
        """Origins for the dimensions involved that include the scaling factors"""
        return -1 * self._get_origins() * self._get_scales()

    def _get_unit_origins_of_one_image(self, image_dict):
        """Origins for the dimensions of a single image that include the scaling factors"""
        return -1 * self._get_origins_of_one_image(image_dict) * self._get_scales_of_one_image(image_dict)

    def _get_units(self):
        """Units for the scales involved, one per each dimension"""
        # TODO safeguard for the cases where the dimensions cannot be read from file
        units = []
        for k, el in self._spectral_info["ImageData"]["Calibrations"][
            "Dimension"
        ].items():
            if not el["Units"]:
                # self.spectralInfo['ImageData']['Calibrations']['Dimension'][k]['Units'] = 'a.u.'
                el["Units"] = "a.u."
            units.append(el["Units"])
        return tuple(units[::-1])

    # TODO - CHECK IF WE NEED THIS BECAUSE IT'S NOT USED ANYWHERE
    # IF WE DO, UNCOMMENT AND UPDATE DUE TO THIS FUNCTIONS WAS DESIGN FOR A SINGLE IMAGE AND CODE WAS REMAKE TO HANDLE MULTIPLE IMAGES.
    # SO UPDATE "self._spectral_info"
    # def _set_energy_scale(self, scale_val):
    #     """Method that sets a new value for the energy scale
    #     Raises ValueError whenever we face an spectrum dataset with ill-defined units
    #     """
    #     scale_items = [
    #         k
    #         for k, el in self._spectral_info["ImageData"]["Calibrations"][
    #             "Dimension"
    #         ].items()
    #         if el["Units"] == "eV"
    #     ]
    #     if len(scale_items) != 1:
    #         raise ValueError
    #     self._spectral_info["ImageData"]["Calibrations"]["Dimension"][scale_items[0]][
    #         "Scale"
    #     ] = scale_val

    # TODO - CHECK IF WE NEED THIS BECAUSE IT'S NOT USED ANYWHERE
    # IF WE DO, UNCOMMENT AND UPDATE DUE TO THIS FUNCTIONS WAS DESIGN FOR A SINGLE IMAGE AND CODE WAS REMAKE TO HANDLE MULTIPLE IMAGES.
    # SO UPDATE "self._spectral_info"
    # def _set_energy_origin(self, offset_val):
    #     """Method that changes the offset value of the energy axis"""
    #     scale_items = [
    #         k
    #         for k, el in self._spectral_info["ImageData"]["Calibrations"][
    #             "Dimension"
    #         ].items()
    #         if el["Units"] == "eV"
    #     ]
    #     if len(scale_items) != 1:
    #         raise ValueError
    #     self._spectral_info["ImageData"]["Calibrations"]["Dimension"][scale_items[0]][
    #         "Origin"
    #     ] = offset_val

