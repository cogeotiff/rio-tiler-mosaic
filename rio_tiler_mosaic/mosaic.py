"""rio_tiler_mosaic.mosaic: create tile from multiple assets."""

import os
import multiprocessing
from functools import partial
from concurrent import futures

import numpy

from rio_tiler.utils import _chunks


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
    pixel_selection="first",
    chunk_size=5,
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
    pixel_selection : str, optional
        Best pixel selection method (default: "first").
    kwargs: dict, optional
        Rio-tiler tiler module specific options.

    Returns
    -------
    tile, mask : tuple of ndarray
        Return tile and mask data.

    """
    if pixel_selection == "last":
        assets = list(reversed(assets))
        pixel_selection = "first"

    tile = None
    mask = None

    _tiler = partial(tiler, tile_x=tile_x, tile_y=tile_y, tile_z=tile_z, **kwargs)
    max_threads = int(os.environ.get("MAX_THREADS", multiprocessing.cpu_count() * 5))

    for chunks in _chunks(assets, max_threads):
        with futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
            future_tasks = [executor.submit(_tiler, asset) for asset in chunks]

        for t, m in _filter_futures(future_tasks):
            t = numpy.ma.array(t)
            t.mask = m == 0

            if tile is None:
                tile = t

            if pixel_selection == "darkest":
                pidex = numpy.bitwise_and(t.data < tile.data, ~t.mask) | tile.mask

            elif pixel_selection == "brightest":
                pidex = numpy.bitwise_and(t.data > tile.data, ~t.mask) | tile.mask

            elif pixel_selection == "first":
                pidex = tile.mask & ~t.mask

            else:
                pidex = tile.mask & ~t.mask

            mask = numpy.where(pidex, t.mask, tile.mask)
            tile = numpy.ma.where(pidex, t, tile)
            tile.mask = mask

            if not numpy.ma.is_masked(tile) and pixel_selection == "first":
                return tile.data, ~tile.mask[0] * 255

    if tile is not None:
        return tile.data, ~tile.mask[0] * 255

    return tile, mask
