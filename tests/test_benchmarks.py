"""Benchmark."""

import os

import pytest
import rasterio

from rio_tiler.io import COGReader
from rio_tiler_mosaic import mosaic

asset1 = os.path.join(os.path.dirname(__file__), "fixtures", "cog1.tif")
asset2 = os.path.join(os.path.dirname(__file__), "fixtures", "cog2.tif")
assets = [asset1, asset2, asset1, asset2, asset1, asset2]


def _tiler(asset, x, y, z):
    with COGReader(asset) as cog:
        return cog.tile(x, y, z)


def read_tile(threads, asset_list):
    """Benchmark rio-tiler.utils._tile_read."""
    with rasterio.Env(
        GDAL_CACHEMAX=0, GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",
    ):
        return mosaic.mosaic_tiler(asset_list, 150, 180, 9, _tiler, threads=threads)


@pytest.mark.parametrize("threads", [0, 1, 2, 3, 4, 5])
@pytest.mark.parametrize("nb_image", [1, 2, 3, 4, 5])
def test_threads(benchmark, nb_image, threads):
    """Test tile read for multiple combination of datatype/mask/tile extent."""
    benchmark.name = f"{nb_image}images-{threads}threads"
    benchmark.group = f"{nb_image}images"

    asset_list = assets[:nb_image]

    tile, _ = benchmark(read_tile, threads, asset_list)
    assert tile.shape == (3, 256, 256)
