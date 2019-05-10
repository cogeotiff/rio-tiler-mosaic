"""tests ard_tiler.mosaic."""

import os

import numpy

from rio_tiler_mosaic import mosaic
from rio_tiler.main import tile as cogTiler


asset1 = os.path.join(os.path.dirname(__file__), "fixtures", "cog1.tif")
asset2 = os.path.join(os.path.dirname(__file__), "fixtures", "cog2.tif")
assets = [asset1, asset2]
assets_order = [asset2, asset1]

# Full covered tile
x = 150
y = 182
z = 9

# Partially covered tile
xp = 150
yp = 180
zp = 9


def test_mosaic_tiler():
    """Test mosaic tiler."""
    # test with default and full covered tile and default options
    t, m = mosaic.mosaic_tiler(assets, x, y, z, cogTiler)
    assert t.shape == (3, 256, 256)
    assert m.shape == (256, 256)
    assert m.all()
    assert t[0][-1][-1] == 8000

    # Test last pixel selection
    t, m = mosaic.mosaic_tiler(assets, x, y, z, cogTiler, pixel_selection="last")
    assert t.shape == (3, 256, 256)
    assert m.shape == (256, 256)
    assert m.all()
    assert t[0][-1][-1] == 7645

    t, m = mosaic.mosaic_tiler(assets, x, y, z, cogTiler, indexes=1)
    assert t.shape == (1, 256, 256)
    assert m.shape == (256, 256)
    assert t.all()
    assert m.all()
    assert t[0][-1][-1] == 8000

    # Test darkest pixel selection
    t, m = mosaic.mosaic_tiler(assets, x, y, z, cogTiler, pixel_selection="darkest")
    assert m.all()
    assert t[0][-1][-1] == 7645

    to, mo = mosaic.mosaic_tiler(
        assets_order, x, y, z, cogTiler, pixel_selection="darkest"
    )
    numpy.testing.assert_array_equal(t[0, m], to[0, mo])

    # Test brightest pixel selection
    t, m = mosaic.mosaic_tiler(assets, x, y, z, cogTiler, pixel_selection="brightest")
    assert m.all()
    assert t[0][-1][-1] == 8000

    to, mo = mosaic.mosaic_tiler(
        assets_order, x, y, z, cogTiler, pixel_selection="brightest"
    )
    numpy.testing.assert_array_equal(to, t)
    numpy.testing.assert_array_equal(mo, m)

    # Test fallback case (first)
    t, m = mosaic.mosaic_tiler(assets, x, y, z, cogTiler, pixel_selection="yo")
    assert m.all()

    # test with default and partially covered tile
    t, m = mosaic.mosaic_tiler(
        assets, xp, yp, zp, cogTiler, pixel_selection="brightest"
    )
    assert t.any()
    assert not m.all()

    # test when tiler raise errors (outside bounds)
    t, m = mosaic.mosaic_tiler(assets, 150, 300, 9, cogTiler)
    assert not t
    assert not m
