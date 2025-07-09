"""
WhatEELS Error Handling Module

Custom exceptions for the WhatEELS application, organized by category:
- base: Foundation exception classes
- parsing: DM file format parsing exceptions  
- data: EELS data processing exceptions
"""

from .base import *
from .parsing import *
from .data import *
