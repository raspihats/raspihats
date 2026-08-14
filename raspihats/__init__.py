"""Python package for controlling the boards at raspihats.com.

:mod:`raspihats.i2c_hats` carries the board classes - the scripting API.
:mod:`raspihats.protocol` carries the wire format, and is public and
semver-stable so that other transports can build on it.
"""
try:
    from importlib.metadata import PackageNotFoundError, version as _version
except ImportError:  # Python < 3.8
    try:
        from importlib_metadata import PackageNotFoundError, version as _version
    except ImportError:
        _version = None

if _version is None:
    __version__ = 'unknown'
else:
    try:
        # read from the installed distribution rather than repeating the
        # number here, so the two can never disagree
        __version__ = _version('raspihats')
    except PackageNotFoundError:
        __version__ = 'unknown'
