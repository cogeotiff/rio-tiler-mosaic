"""rio_tiler_mosaic.mosaic: create tile from multiple assets."""

import os
import multiprocessing
from functools import partial
from concurrent import futures

import numpy

from rio_tiler.utils import _chunks

from rio_tiler_mosaic.methods.base import MosaicMethodBase
from rio_tiler_mosaic.methods.defaults import FirstMethod


def _filter_futures(tasks):
    """
    Filter future task to remove Exceptions.

    Attributes
    ----------
    tasks : list
        List of 'concurrent.futures._base.Future'

    Yields
    ------
    Successful task's result

    """
    for future in tasks:
        try:
            yield future.result()
        except Exception:
            pass


def mosaic_tiler(
    assets,
    tile_x,
    tile_y,
    tile_z,
    tiler,
    pixel_selection=None,
    chunk_size=None,
    **kwargs
):
    """
    Create mercator tile from multiple observations.

    Attributes
    ----------
    assets : list, tuple
        List of rio-tiler compatible sceneid or url
    tile_x : int
        Mercator tile X index.
    tile_y : int
        Mercator tile Y index.
    tile_z : int
        Mercator tile ZOOM level.
    tiler: function
        Rio-tiler's tiler function (e.g rio_tiler.landsat8.tile)
    pixel_selection: MosaicMethod, optional
        Instance of MosaicMethodBase class.
        default: "rio_tiler_mosaic.methods.defaults.FirstMethod".
    chunk_size: int, optional
        Control the number of asset to process per loop (default = MAX_THREADS).
    kwargs: dict, optional
        Rio-tiler tiler module specific options.

    Returns
    -------
    tile, mask : tuple of ndarray
        Return tile and mask data.

    """
    if pixel_selection is None:
        pixel_selection = FirstMethod()

    if not isinstance(pixel_selection, MosaicMethodBase):
        raise Exception(
            "Mosaic filling algorithm should be an instance of"
            "'rio_tiler_mosaic.methods.base.MosaicMethodBase'"
        )

    _tiler = partial(tiler, tile_x=tile_x, tile_y=tile_y, tile_z=tile_z, **kwargs)
    max_threads = int(os.environ.get("MAX_THREADS", multiprocessing.cpu_count() * 5))
    if not chunk_size:
        chunk_size = max_threads

    for chunks in _chunks(assets, chunk_size):
        with futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
            future_tasks = [executor.submit(_tiler, asset) for asset in chunks]

        for t, m in _filter_futures(future_tasks):
            t = numpy.ma.array(t)
            t.mask = m == 0

            pixel_selection.feed(t)
            if pixel_selection.is_done:
                return pixel_selection.data

    return pixel_selection.data
