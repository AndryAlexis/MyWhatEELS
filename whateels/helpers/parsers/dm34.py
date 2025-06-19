import logging, re
import numpy as np

from ...errors.exception import *
from ...helpers.decorders import decoders as dec
from ...helpers.file_reader.abstract_classes import IDM_Parser, IDM_EELS_DataHandler

from typing import List, Tuple

####################################################
# Setting up the logging system for this module
_log_fname = "dmReader.log"
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)
# These formatter keywords are not fstrings, but they work better
# with the logging module
_formatter = logging.Formatter(
    "%(asctime)s : %(name)s : \
    %(levelname)s : %(funcName)s : %(message)s"
)
_fhandler = logging.FileHandler(_log_fname)
_fhandler.setFormatter(_formatter)
_shandler = logging.StreamHandler()
_shandler.setFormatter(_formatter)
# _logger.addHandler(_shandler)
_logger.addHandler(_fhandler)
#####################################################

# from .decoders import decoders as dec

class DM_InfoParser(IDM_Parser):
    """
    This class contains all the methods required to parse a dm3 or dm4 file.
    After its usage, the user will find that the info acquired is stored in a dictionary,
    which can later be used to read the actual data (e.g., spectrum images) from the file.
    """

    ###
    # Data types read from external plugin
    _simple_data_types = (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)
    # Simple type readers from exteral plugin
    _simple_parsers_dictionary = {
        2: (dec.read_short, 2),
        3: (dec.read_long, 4),
        4: (dec.read_ushort, 2),
        5: (dec.read_ulong, 4),
        6: (dec.read_float, 4),
        7: (dec.read_double, 8),
        8: (dec.read_boolean, 1),
        9: (dec.read_char, 1),
        10: (dec.read_byte, 1),
        11: (dec.read_long_long, 8),
        12: (dec.read_ulong_long, 8),
    }
    # SizeId - Encryption | allowed pairs
    # The pairings are written literaly here ... for more clarity
    """
    _id_pairings = [
        (1, i) for i in range(2, 13)
    ]
    """
    _id_pairings = [
        (1, 2),
        (1, 3),
        (1, 4),
        (1, 5),
        (1, 6),
        (1, 7),
        (1, 8),
        (1, 9),
        (1, 10),
        (1, 11),
        (1, 12),
        (2, 18),
        (3, 20),
    ]
    """
    _id_pairings.append((2, 18))
    _id_pairings.extend([(2, 18), (3, 20)])
    _id_pairings = tuple(_id_pairings)
    """
    _id_pairings = tuple(_id_pairings)
    ###
    # Valid extensions for the file reading
    _valid_extensions = (".dm3$", ".dm4$")
    ####

    def __init__(self):
        """
        Instansciation of the DM_InfoParser class for a file f.
        It calls automatically the file header reader -> so if
        a wrong version of dm file is provided, the instantiation is
        halted.

        Parameters
        --------------
        file : cls:_io.BufferedReader = Opened file. This class is deviced to be
                                        used within a context manager (with statement)
                                        where an actual file f is opened.

        Dependencies
        ---------------
        self.read_file_header() : method to read the file header and decide if it's a valid
                                candidate.
        """
        self.information_dictionary = dict()

    def get_file(self, file):
        self.f = file

    def check_extension_in_fname(self) -> None:
        """Before even starting to parse the file, we check that the
        provided file has a valid extension (dm3 or dm4). Otherwise, raises error.
        This will be once again checked - upon parsing the header of the file -.
        """
        # First thing we do is to check is we have an actual valid file
        fname = (
            self.f.name
        )  # It is an opened file, should have a name instance variable ...
        if not any(
            [
                re.search(ext, fname, flags=re.IGNORECASE)
                for ext in self._valid_extensions
            ]
        ):
            msg = f"The file-name given does not have a valid extension - {fname}.\
                The extension should be one of the following : {self._valid_extensions}."
            _logger.error(msg)
            raise DMVersionError(msg)

    @property
    def _callable_parsers_dictionary(self):
        dictio = {
            "simpleType": (
                self.catch_simpleTypeData_format,
                self.read_simpleTypeData,
                self.skip_simpleTypeData,
            ),
            "structure": (
                self.catch_structure_format,
                self.read_structure,
                self.skip_structure,
            ),
            "string": (self.catch_string_format, self.read_string, self.skip_string),
            "array": (
                self.catch_simpleTypesArray_format,
                self.read_simpleTypesArray,
                self.skip_simpleTypesArray,
            ),
            "complexArray": (
                self.catch_complexTypesArray_format,
                self.read_complexTypesArray,
                self.skip_complexTypesArray,
            ),
        }
        return dictio

    def get_callable_word(self, encryption_type):
        """
        This method is in charge getting the keyword for the type of callables to be read

        Parameters
        ------------
        encryption_type : int = Type of encryption for the data to be read.
        """
        if 2 <= encryption_type <= 12:
            return "simpleType"

        dictionary_words = {18: "string", 15: "structure", 20: "array"}
        return dictionary_words[encryption_type]

    def process_file_header(self) -> None:
        """
        Method that reads the header of the file:
        1-  Gets the dm version -> self.version
        2-  The parser that it will be using in general to get the integer values
            Format - long <4 bytes> or long_long <8 bytes>
        3-  file_size
        4-  Endianness of the info read by the parser -> self.endianness

        Dependencies
        ---------------
        self._version_parsers : class variable. Dictionary of the possible
                                general usage reader methods -> for long or long_long
                                data, according to the file version (dm3 or dm4)
        """
        self.f.seek(0)  # Pointer to the 0 possition
        self.version = dec.read_long(self.f, "big")  # version : <4 bytes> big endian
        if self.version not in [3, 4]:
            # If version != 3 or 4 -> Raises an error -> Unsuported file for DM
            message = f"Expected versions 3 or 4 (.dm3/.dm4). Got {self.version} instead\
            -> from the header of {self.f.name}"
            raise DMVersionError(message)

        # The general parser/reader - reads in chuncks of 4 or 8 bytes returning integer values
        self.parser = dec.read_long if self.version == 3 else dec.read_long_long
        file_size = self.parser(self.f, "big")  # Full size of file <4 or 8 bytes>
        self.endianness = (
            "little" if dec.read_long(self.f, "big") else "big"
        )  # True - little / #False - big

        # logging header read - info level
        msg = f"DM version = {self.version} - File size (Bytes) = {file_size} - {self.endianness} endian"
        _logger.info(msg)

    def read_ParentBlockSize_info(self, read_block_size: bool = False) -> int:
        """
        This method gets the info for the current block of data to be read -

        - Gets the number of named subblocks of info inside the current block
        * As a side effect, if the file is dm4 and read_block_size is True, it
        reads an extra byte-space located before the number of named subblocks
        -> corresponding to the block size ? -> Not always though.
                                Only uppon calling the method with read_block_size

        Parameters
        ----------------------------------------
        read_block_size : bool = Whenever a version 4 (dm4) is given, an extra memory direction is included
                            in front of the actual number of header names. This has to be read to advance
                            the memory pointer to the place we are interested in. It is suposedly related
                            to the size of the current infoGroup.

        Returns
        ----------------------------------------
        number_of_names : int = Number of named tags in the file in the current block

        Block info structure
        ----------------------------------------
        GATAN dm3
        ordered : <1 byte> - opened <1 byte> - number_of_names <4 bytes>
        ---------
        GATAN dm4
        ordered : <1 byte> - opened <1 byte> - ¿block_size <8 bytes>? - number_of_names <8 bytes>
        """
        # Deprecated #############################################
        # These two lines read a single byte position for a boolean info on wheather or not the file :
        # dec.read_byte(self.f,'big')        #is ordered
        # dec.read_byte(self.f,'big')        #is opened
        #########################################################
        self.f.seek(2, 1)  # advances 2 bytes from the current possition

        if self.version == 4 and read_block_size:
            # TODO Lacking the logging capability still
            # Relies on the parser defined by the version
            # (dm4 or dm3 - 8 or 4 byte chuncks of info)
            block_size = self.parser(self.f, "big")

        number_of_names = self.parser(self.f, "big")
        return number_of_names

    def read_ChildrenBlock_header(self):
        """
        Method to extract the header info for the current chuck of the parent block of info.
        The files in dm3/4 are structured in blocks of info - Parent blocks containing children blocks.
        A children block can then become a parent block of another set of children subblocks ... and so on.
        These blocks are usually named, and also contain a numerical code that
        specifies the type of data stored in that possition:
        id == 20 -> This children block contains more subblocks -> Is the parent of a new set of children blocks.
                    (Potentially containing several name spaces.)
        id == 21 -> This children block contains data and info. So this data can later be read or skipped ...

        Returns
        -----------
        (identifier, block_name) : tuple(int,str) =
            identifier : int = id for the type of block -> Data block, or set of new children subblocks
            block_name : str = string for the name of the current block (can be '' empty)

        File structure here:
        ---------------------
        identifier <1 byte> - length <4 bytes> - block_name <'length' bytes>
        """
        identifier = dec.read_byte(self.f, "big")  # a single byte integer used as index
        # Reading the name - a string
        length = dec.read_short(self.f, "big")  # a double byte integer
        block_name = self.read_string(length)
        return identifier, block_name

    def read_DataType_info(self) -> Tuple:
        """
        This method will, in principle, read the size identifier for the current children data
        block been studied, as well as the actual type of data.
        If a value <1 is read, raises an error (as that identifier is not implemented in GATAN DM)

        Returns
        ---------------
        size_Data_id : int = The number identifier that will indicate the type of data read
                            1  - simple type                         <4 or 8 bytes> most likely
                            2  - string                              <length bytes>
                            3  - Array of simple types               <size * element_type bytes>
                            >3 - Structure or Array of complex types <?>
                                The array of complex types can be array of strings,
                                structs or an arrays(simple_types)

        encryption_type : int = Whenever size_Data_id >= 1, this read number will denote the decryption
                                method (reader) required to get the actual data from the current children block
                                -> pointing in the _readers_dictionay to the actual reader method required.

        Dependencies
        ----------------
        self.parser()
        """
        size_Data_id = self.parser(self.f, "big")
        # Checking data size -> If not correct automatically raises and error.
        if size_Data_id < 1:
            # Check this always ... to catch possible corrupted files
            msg = f"Invalid {size_Data_id = } < -1. DM does not support this id\
                (Error parsing the file?)"
            _logger.exception(msg)
            raise IOError(msg)

        encryption_type = self.parser(self.f, "big")

        # Before returning anything, it also checks if the pairings are correct

        return size_Data_id, encryption_type

    def check_sizeID_encryption_pair(
        self, size_Data_id: int, encryption_type: int
    ) -> None:
        """Method in charge of checking size and encryptions read from file.
        In case of containing a wrong pairing of size index and encryption type, raises

        Parameters
        ----------
        size_Data_id    : int = Index indicating the size of the data to be read/skipped.
        encryption_type : int = Index indicating the type of data to be read.
        """
        if size_Data_id > 3:
            if encryption_type not in [15, 20]:
                m0 = f"Expected EncryptionTypes of 15 or 20 for the DataSize {size_Data_id}"
                m1 = f"Got {encryption_type} instead."
                message = "\n".join([m0, m1])
                _logger.exception(message)
                raise IOError(message)
        else:
            if (size_Data_id, encryption_type) not in self._id_pairings:
                m0 = f"The pair (DataSize = {size_Data_id}, EncryptionType {encryption_type}) is not correct."
                m1 = f"The possible (DataSize,EncryptionType) pairings are {self._id_pairings}."
                m2 = "Check for possible parsing error and/or data corruption, and report"
                message = "\n".join([m0, m1, m2])
                _logger.exception(message)
                raise IOError(message)

    def read_delimiter(self) -> None:
        """
        Method that reads the delimiter between blocks names, and the actual data they refer to.
        Raises an error when the delimiter is not what was expected from ta DM3 or DM4 files...
        """
        if self.version == 4:
            # Notice it moves the pointer 8 bytes further down
            # the file from the current position, if dm4.
            self.f.seek(8, 1)
        delimiter = self.read_string(4)
        if delimiter != "%%%%":
            message = f"Error with the delimiter between blocks.\nExpected %%%%\nGot{delimiter}"
            _logger.exception(message)
            raise DMDelimiterCharacterError(message)

    #############################################
    ## Simple data type reading #################
    def backtracking_position_in_file(self, nbytes=None) -> None:
        """Helper method in  charge of backtracking a number of nbytes in the file reader
        Parameters
        ----------
        nbytes : int =  number of bytes to be backtracked in the file (the memory pointer is moved
                        back that number of bytes).
                        If None, the nbytes is assigned a value 4 for dm3
                        and 8 for dm4 format files in DM.
                        Default = None
        """
        if not nbytes:
            if self.version == 3:
                nbytes = 4
            elif self.version == 4:
                nbytes = 8
            else:
                message = (
                    f"Expected DM versions 3 or 4, got version number = {self.version}"
                )
                _logger.exception(message)
                raise DMVersionError(message)
        current_position = self.f.tell()
        self.f.seek(current_position - nbytes, 0)

    # This method does nothing in reality ... it exists to be injected
    def catch_simpleTypeData_format(self):
        """Method that gets the simple element type read from memory,
        and returns a dictionary, to be fed to the reader

        Parameters
        -----------
        element_type : int = Type of element (simple) read from memory
        """

        self.backtracking_position_in_file()
        element_type = self.parser(self.f, "big")
        return {"element_type": element_type}

    def skip_simpleTypeData(self, element_type: int):
        """This method skips the reading of a simple data type.
        In principle, should never be called ... it is included for the completitudeness
        of the behaviour injection scheme used in this class

        Parameters
        ----------
        element_type : int = Type of element (simple) read from memory

        Returns
        ---------
        dictionary_simpleDType : dict = Information for the element type, size, size in bytes ... etc
        """
        sizeB = self._simple_parsers_dictionary[element_type][-1]
        offset = self.f.tell()
        dictionary_simpleDType = {
            "size": 1,
            "bytes_size": sizeB,
            "offset": offset,
            "endian": self.endianness,
        }
        self.f.seek(sizeB, 1)  # Advancing the pointer memory

        return dictionary_simpleDType

    def read_simpleTypeData(self, element_type: int):
        """Method that searches the adequate data reader from the dictionary, and
        returns the data read

        Parameters
        -----------
        element_type : int = numerical identifier for the simpleType data reader

        Returns
        -----------
        data = Data read. The type is dependent on the type of data stored, obviously.

        """
        data = self._simple_parsers_dictionary[element_type][0](self.f, self.endianness)
        return data

    #############################################
    ## String related methods ###################

    def catch_string_format(self):
        """
        Method that will recover the length of the string to be read,
        using the appropriate byte-size depending on the dm version
        dm3 <4 bytes> -- dm4 <8 bytes> -> But always big endian.

        Return
        --------------
        length : int = Length of the chain of characters that will form the string
        """
        length = self.parser(self.f, "big")
        return {"length": length}

    def read_string(self, length: int, methods: List | None = None) -> str:
        """
        This method will read a string from the encoded files
        adressing every single character one by one, and returning
        a fully formed string from the list of joined characters.
        Then, the string is decoded (or at least decoding is tried)

        Parameters
        -------------
        length : int = Determines the number of characters of the string
        methods : list | None = list of methods that the decoder will try
                                to get the string decoded from its byte format
                                Default = None.

        Returns
        -------------
        string : str = The actual string read from the list of characters.
        """
        # Reading files
        list_characters = [
            dec.read_char(self.f, self.endianness) for _ in range(length)
        ]
        string_byte_characters = b"".join(list_characters)
        string = " - "
        # Decoding byte-strings
        if not methods:
            methods = ["utf8", "latin-1"]
        # Loop through the possible decoding methods
        for decoding_method in methods:
            try:
                string = string_byte_characters.decode(decoding_method)
            except UnicodeError as e:
                msg = f"Failed reading with an encoding {decoding_method}"
                _logger.warning(msg)
            else:
                break
        """    
        if not string:
            
            string = " - "
        """
        return string

    def skip_string(self, length: int, data=False):
        """
        This method will skip the reading of a string, by jumping forward in the file
        a number of byte possitions equal to the string length given.

        Parameters
        -------------
        length : int = Determines the number of characters of the string

        Returns
        -------------
        string_info : dict = The dictionary of info to be able to locate and read the string.
                            The usual suspects as keys
                            - size (length of the string)
                            - bytes_size (size in bytes) == size (1 character = 1 byte)
                            - offset (pointer position in the file)
                            - endian (endianness of the string bytes chain) == self.endianness
        """
        offset = self.f.tell()  # Get the current pointer position
        self.f.seek(
            length, 1
        )  # advances the pointer a number of bytes equal to the length
        string_info = {
            "size": length,
            "bytes_size": length,
            "offset": offset,
            "endian": self.endianness,
        }
        return string_info

    #### Check element (structures or arrays) data types

    def check_multipleElementObjects_DataTypes(self, definition) -> None:
        """Simple method to validate that the element data types given to
        the structure and array readers are of simple type.

        Parameters
        --------------
        definition : list | tuple = Iterable that defines the element data types
                                    in an array (list) or structure (tuple).
        """
        if any([el not in self._simple_data_types for el in definition]):
            m1 = "Expected id labels of simple data types."
            m2 = f"Got {definition} instead >> numbers outside the [2,12] range"
            message = "\n".join([m1, m2])
            raise DMStructDataTypeError(message)

    ###############################################
    ## Structure related methods ##################

    def catch_structure_format(self):
        """
        This method will, in principle, the structure or format of the
        struct object stored in the Gatan DM file, returning in a tuple format
        so later the data can be extracted from within the file.

        Returns
        ---------------
        s_format : tuple = Tuple of the format descriptor of the struc object
        """
        self.parser(
            self.f, "big"
        )  # Reads the length of the struct ... not relevant, so not strored
        n_fields = self.parser(self.f, "big")
        # Loop doing exactly the same, n_fields times
        s_format = []
        for _ in range(n_fields):
            self.parser(
                self.f, "big"
            )  # Again - Reads the length of the struct.. not stored
            s_format.append(self.parser(self.f, "big"))
        return {"struct_format": tuple(s_format)}

    def read_structure(self, struct_format):
        """
        This method reads a struct without skipping the actual info reading
        It relies in a variable dictionary that contains the type of readers
        that it can access. Notice that the structs can only be filled with
        simple_types - That is - integers (8,4 bytes - signed or unsigned),
        floats, etc.

        It cannot be a struct of strings, arrays, etc -> Those would be complex_type arrays

        Parameters
        ----------------
        struct_format : tuple = The format tuple that contains the descriptors
                                of the types of data that the struct contains

        Return
        ----------------
        data : tuple = The actual struct data read and decoded.

        Dependencies
        ----------------
        _parsers_dictionary : dict = A dictionary that links the data types from
                            the struct format, to the actual byte reader functions
        """
        # Firts, check that the definition is right -> Otherwise raise
        self.check_multipleElementObjects_DataTypes(struct_format)

        # Now the actual reading of the struct
        values = []
        for num_type in struct_format:
            # Getting and calling the reader
            data = self._simple_parsers_dictionary[num_type][0](self.f, self.endianness)
            values.append(data)

        return tuple(values)

    def skip_structure(self, struct_format):
        """
        This method skips a struct and store its info -> meaning that it bassically returns
        possitional info and size for the struct.

        Parameters
        ----------------
        struct_format : tuple = The format tuple that contains the descriptors
                                of the types of data that the struct contains

        Return
        ----------------
        data : dict = Now, we do not return a tuple for the struct
                        We return a dictionary holding info about the struct
                        possition in the file, size (len of the tuple), size
                        in bytes and endianness ... in case of needing it later.

        Dependencies
        ----------------
        readers_dict : dict = A dictionary that links the data types from
                                the struct format, to the actual byte reader functions
        simple_data_types : tuple = Tuple of integers, descriptor numbers for the simple data types
        """
        # Firts, check that the definition is right -> Otherwise raise
        self.check_multipleElementObjects_DataTypes(struct_format)

        # Now let's skip through the reading and advance the file pointer
        offset = self.f.tell()  # Getting the current pointer position
        struct_Bsize = 0  # Size in bytes
        for num_type in struct_format:
            # Getting the size in bytes to skip
            struct_Bsize += self._simple_parsers_dictionary[num_type][-1]

        # Now we advance the pointer position
        self.f.seek(struct_Bsize, 1)

        # Create the info dictionary
        dictionary_struct_info = {
            "size": len(struct_format),
            "bytes_size": struct_Bsize,
            "offset": offset,
            "endian": self.endianness,
        }

        return dictionary_struct_info

    #############################################
    ## Arrays of simple types ###################

    def catch_simpleTypesArray_format(self):
        """
        This method will, in principle, read the structure or format of the
        array object stored in the Gatan DM file, returning the size (length)
        of the array and the types of elements inside the array (all elements must share
        the type, so is single valued and represented by a single type)

        Returns
        ---------------
        element_encryption : int = Type of encryption for the elements in the array
        size : int = Lentgh of the array to be read

        Dependencies
        ----------------
        Currently, the parser function

        Data structure
        -----------------
        The arrays will be structured as a header + data.
        The header
        """
        # The reading order is relevant
        element_encryption = self.parser(self.f, "big")
        size = self.parser(self.f, "big")
        return {"element_encryption_type": element_encryption, "length": size}

    def read_simpleTypesArray(self, element_encryption_type, length):
        """
        Method to read simple-type arrays - Where every single element of the array
        belongs to the same type and, thus, addresses the same reader type

        Parameters
        -------------
        element_encryption_type : int = The actual type of encryption, key in the dictionary of types
        length : int = The size of the array, read from the file in the pre-processing step for arrays.

        Return
        -------------
        data : list | str = Data read from file, corresponding to an array of data
        """
        # Checking that the data types given are correct -> We create the list on site ...
        self.check_multipleElementObjects_DataTypes(
            [
                element_encryption_type,
            ]
        )

        reader = self._simple_parsers_dictionary[element_encryption_type][0]
        data = [reader(self.f, self.endianness) for _ in range(length)]
        # There's the possibility, apparently, of a simple array to correspond to an actual string
        # So, the list is joined to form the string
        if element_encryption_type == 4 and data:
            try:
                data = "".join(
                    [chr(i) for i in data]
                )  # Not encoded, as the rest of strings
            except Exception as e:
                _logger.warning(
                    f"Skipped the reading of array-like string. Exception - {e}"
                )
                data = self.skip_string(length=length * 2)
        return data

    def skip_simpleTypesArray(self, element_encryption_type, length):
        """
        Method to skip simple-type arrays - Where every single element of the array
        belongs to the same type and, thus, addresses the same reader type -> But returns a dictionary
        with the description of the actual array

        Parameters
        -------------
        element_ecryption_type : int = The actual type of encryption, key in the dictionary of types
        length : int = The size of the array, read from the file in the pre-processing step for arrays.

        Return
        --------------
        data : dict = info for the data read from file, corresponding to an array of data
        """
        # The info about size per element is in the dictionary
        self.check_multipleElementObjects_DataTypes(
            [
                element_encryption_type,
            ]
        )

        size_bytes = (
            self._simple_parsers_dictionary[element_encryption_type][-1] * length
        )
        data = {
            "size": length,  # Size of the array (number of elements)
            "endian": self.endianness,  # endianess of the elements
            "bytes_size": size_bytes,  # Size of the array in bytes
            "offset": self.f.tell(),
        }  # offset position of the array in the memory
        self.f.seek(size_bytes, 1)  # Skipping data -> Not read
        return data

    ###########################
    # Complex arrays #######

    def catch_complexTypesArray_format(self):
        """
        This method will try to catch the format header for complex type arrays
        (i.e., arrays with strings, structures or other arrays as their elements).

        Returns
        -------------
        format_dict : dict() = Dictionary with the necessary keywords to excecute the
                            complex array reader/skipper later on. So, it gets:
                            keyword           : str  = identifier of the array
                                                        element encryption type
                            array_size        : int  = size of the complex array
                                                        to be read/skipped
                            format_definition : dict = format dictionary to be fed
                                                        to the reader/skipper
        """
        element_encryption_type = self.parser(self.f, "big")
        keyword = self.get_callable_word(element_encryption_type)
        format_definition = self._callable_parsers_dictionary[keyword][
            0
        ]()  # Definition of the elements
        array_size = self.parser(self.f, "big")
        return {
            "keyword": keyword,
            "array_size": array_size,
            "format_definition": format_definition,
        }

    def read_complexTypesArray(self, keyword, array_size, format_definition):
        """
        Method to read complex-type arrays - Where every single element of the array
        belongs to the same type and, thus, addresses the same reader type. Furthermore,
        in these arrays that contain multiple-element elements, each one of them is always
        of the same type, and, so, described by the same format_definition. Hence, the
        definition is only read once ...

        Parameters
        -----------
        """
        # Let us read the arrays of length == array_size
        reader = self._callable_parsers_dictionary[keyword][1]
        # And we read all the data inside, according to the type of reader we got ...
        data = [reader(**format_definition) for el in range(array_size)]
        return data

    def skip_complexTypesArray(self, keyword, array_size, format_definition):
        """
        Method to skip the reading of complex-type arrays, returning the memory size and location
        info as data
        """
        skipper = self._callable_parsers_dictionary[keyword][-1]
        # This will advance an element_size length the pointer position in memory,
        # appart from retrieving the offset, size, size in bytes and endiannes in a
        # data dictionary
        element_data = skipper(**format_definition)
        # We advance the pointer the (array_size -1)*element_bytesSize positions
        # still to be moved
        self.f.seek(element_data["bytes_size"] * (array_size - 1), 1)
        # We substitute the size by the actual array size read from header
        element_data["size"] = array_size
        # and the size in bytes by the actual size for the whole array
        element_data["bytes_size"] *= array_size
        return element_data

    ######################
    # General methods ####

    def process_ChildrensDataBlock(self, formatCallable, readerCallable):
        """
        Method to process the block of data according to the size and encrytion
        found in the header.

        Parameters
        --------------
        formatCallable : Callable = Method injected according to the type of encryption
                                    read on the general block header. It will be in charge of
                                    reading the format (extra header info).

        readerCallable : Callable = Method injected according to the type of encryption
                                    read on the general block header. It will be in charge of
                                    reading the actual data contained within the data block.
                                    To function properly, these types of callables are instantiated
                                    with a format_dictionary, provided by executing the formatCallable

        Returns
        ---------------
        data : Unknown type = Data type read or skipped according to the callables provided.
        """
        format_header = formatCallable()
        data = readerCallable(**format_header)
        return data

    def parse_Blocks(self, nnames, info_dictionary, parentBlock_name: str = "root"):
        """
        Method that parses all the information in the file, except the initial file headers.
        Notice that this method will be called recursevely whenever a Children_block becomes a
        Parent_block (i.e., when an specific block contains a series of Children blocks, instead of data)

        Parameters
        -----------
        nnames : int = Number of name spaces inside the current block (with name == parentBlock_name)
        info_dictionary : dict = Dictionary referred to the current parent namespace,
                                where the new info is going to be stored.
        partentBlock_name : str = Name of the current block being read. Its only function is to
                                keep track of where we are currently reading info - to skip
                                the reading if we are in the 'ImageData' parent namespace, and the
                                children read from file is 'Data'. Default = 'root'
        """
        # Local indices for unnamed data/group Blocks
        noNameData = 0
        noNameBlock = 0

        for _ in range(nnames):
            # NameSpace - Header info
            identifier, childrenBlock_name = self.read_ChildrenBlock_header()
            # This is coupled with the dictionary of callers
            callable_id = (
                2
                if (parentBlock_name == "ImageData" and childrenBlock_name == "Data")
                else 1
            )

            if identifier == 21:
                if not childrenBlock_name:
                    childrenBlock_name = f"DataBlock{noNameData}"  # NoNameData
                    noNameData += 1
                self.read_delimiter()  # Checks the delimiter name - data
                (
                    sizeBlock_id,
                    encryption_type,
                ) = self.read_DataType_info()  # Type of data header
                self.check_sizeID_encryption_pair(
                    sizeBlock_id, encryption_type
                )  # Checking types
                # The type pairings are check, so we can use the size to get the correct callables
                if sizeBlock_id > 3 and encryption_type == 20:  # Array of complex types
                    keyword = "complexArray"
                    pass  # Do something -> implement complex type caller
                else:
                    keyword = self.get_callable_word(encryption_type)

                catcher = self._callable_parsers_dictionary[keyword][0]
                caller = self._callable_parsers_dictionary[keyword][callable_id]
                data = self.process_ChildrensDataBlock(catcher, caller)
                # The endgame - creating a dictionary of things ...
                info_dictionary[childrenBlock_name] = data

            elif identifier == 20:  # ChildrenBlock becoming a ParentBlock -> Recursion
                if not childrenBlock_name:
                    childrenBlock_name = f"GroupBlock{noNameBlock}"  # NoNameBlock
                    noNameBlock += 1
                nnames = self.read_ParentBlockSize_info(
                    read_block_size=True
                )  # Number of names inside

                info_dictionary[childrenBlock_name] = dict()
                # Recursion !
                self.parse_Blocks(
                    nnames, info_dictionary[childrenBlock_name], childrenBlock_name
                )

            else:
                raise DMIdentifierError(
                    f"Identifier missread while parsing the file. {identifier =}"
                )

    def parse_file(self):
        self.check_extension_in_fname()
        self.process_file_header()
        nnames = self.read_ParentBlockSize_info()
        self.information_dictionary["root"] = dict()
        self.parse_Blocks(nnames, self.information_dictionary, "root")
        return self.information_dictionary


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
    }

    def get_file_data(self, file, infoDict=None):
        """This method gets the opened file and the parsed info dict,
        so we can actually extract the required information and use it
        to our advantage
        """
        self.f = file  # An opened file, handled from the factory later on.
        if not infoDict:
            message = f"Expected an informaction dictionary from parser.\
                None provided : {infoDict =}"
            _logger.exception(message)
            raise DMEmptyInfoDictionary(message)
        try:
            imageKeys = list(infoDict["ImageList"].keys())
        except:
            message = f"The dictionary provided after parsing the file does not\
                contain spectral information.\n{infoDict.keys()}"
            _logger.exception(message)
            raise DMNonEelsError(message)

        # With this, we avoid the selection of the thumbnail info ...
        imIDx = 1 if len(imageKeys) > 1 else 0  # Image index to be selected
        self.spectralInfo = infoDict["ImageList"][imageKeys[imIDx]]

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
