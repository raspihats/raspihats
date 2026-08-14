"""
This module contains the I2C Frame class and related classes.

.. deprecated::
    The frame format lives in :mod:`raspihats.protocol`, which is public and
    covered by a stability commitment. This module is a compatibility
    re-export and will not gain anything new; import from
    ``raspihats.protocol`` instead.
"""
from ..protocol import Command, DecodeException, Frame

__all__ = ['Command', 'DecodeException', 'Frame']
