"""rio_tiler_mosaic.mosaic: create tile from multiple assets."""

import logging
from concurrent import futures
from typing import Callable, Generator, Optional, Sequence, Tuple, Union

import numpy

from rio_tiler.constants import MAX_THREADS
from rio_tiler.utils import _chunks
from rio_tiler_mosaic.methods.base import MosaicMethodBase
from rio_tiler_mosaic.methods.defaults import FirstMethod

logger = logging.getLogger()
logger.setLevel(logging.ERROR)
TaskType = Union[Generator[Callable, None, None], Sequence[futures.Future]]


def _filter_tasks(tasks: TaskType):
    """
    Filter tasks to remove Exceptions.

    Attributes
    ----------
    tasks : list or tuple
        Sequence of 'concurrent.futures._base.Future' or 'partial'

    Yields
    ------
    Successful task's result

    """
    for future in tasks:
        try:
            if isinstance(future, futures.Future):
                yield future.result()
            else:
                yield future
        except Exception as err:
            logging.error(err)
            pass


def mosaic_tiler(
    assets: Sequence[str],
    tile_x: int,
    tile_y: int,
    tile_z: int,
    tiler: Callable,
    pixel_selection: Optional[MosaicMethodBase] = None,
    chunk_size: Optional[int] = None,
    threads: int = MAX_THREADS,
    **kwargs,
) -> Tuple[numpy.ndarray, numpy.ndarray]:
    """
    Create mercator tile from multiple observations.

    Attributes
    ----------
    assets: list or tuple
        List of tiler compatible asset.
    tile_x: int
        Mercator tile X index.
    tile_y: int
        Mercator tile Y index.
    tile_z: int
        Mercator tile ZOOM level.
    tiler: callable
        tiler function. The function MUST take asset, x, y, z, **kwargs as arguments,
        and MUST return a tuple with tile data and mask
        e.g:
        def tiler(asset: str, x: int, y: int, z: int, **kwargs) -> Tuple[numpy.ndarray, numpy.ndarray]:
            with COGReader(asset) as cog:
                return cog.tile(x, y, z, **kwargs)
    pixel_selection: MosaicMethod, optional
        Instance of MosaicMethodBase class.
        default: "rio_tiler_mosaic.methods.defaults.FirstMethod".
    chunk_size: int, optional
        Control the number of asset to process per loop (default = threads).
    threads: int, optional
        Number of threads to use. If <=1, runs single threaded without an event
        loop. By default reads from the MAX_THREADS environment variable, and if
        not found defaults to multiprocessing.cpu_count() * 5.
    kwargs: dict, optional
        tiler specific options.

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

    if not chunk_size:
        chunk_size = threads or len(assets)

    tasks: TaskType

    for chunks in _chunks(assets, chunk_size):
        if threads:
            with futures.ThreadPoolExecutor(max_workers=threads) as executor:
                tasks = [
                    executor.submit(tiler, asset, tile_x, tile_y, tile_z, **kwargs)
                    for asset in chunks
                ]
        else:
            tasks = (tiler(asset, tile_x, tile_y, tile_z, **kwargs) for asset in chunks)

        for t, m in _filter_tasks(tasks):
            t = numpy.ma.array(t)
            t.mask = m == 0

            pixel_selection.feed(t)
            if pixel_selection.is_done:
                return pixel_selection.data

    return pixel_selection.data
