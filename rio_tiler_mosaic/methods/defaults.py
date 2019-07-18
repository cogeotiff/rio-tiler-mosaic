"""rio_tiler_mosaic.methods.defaults: default mosaic filling methods."""

import numpy

from rio_tiler_mosaic.methods.base import MosaicMethodBase


class FirstMethod(MosaicMethodBase):
    """Feed the mosaic tile with the first pixel available."""

    def __init__(self):
        """Overwrite base and init First method."""
        super(FirstMethod, self).__init__()
        self.exit_when_filled = True

    def feed(self, tile):
        """Add data to tile."""
        if self.tile is None:
            self.tile = tile
        pidex = self.tile.mask & ~tile.mask

        mask = numpy.where(pidex, tile.mask, self.tile.mask)
        self.tile = numpy.ma.where(pidex, tile, self.tile)
        self.tile.mask = mask


class HighestMethod(MosaicMethodBase):
    """Feed the mosaic tile with the highest pixel values."""

    def feed(self, tile):
        """Add data to tile."""
        if self.tile is None:
            self.tile = tile

        pidex = (
            numpy.bitwise_and(tile.data > self.tile.data, ~tile.mask) | self.tile.mask
        )

        mask = numpy.where(pidex, tile.mask, self.tile.mask)
        self.tile = numpy.ma.where(pidex, tile, self.tile)
        self.tile.mask = mask


class LowestMethod(MosaicMethodBase):
    """Feed the mosaic tile with the lowest pixel values."""

    def feed(self, tile):
        """Add data to tile."""
        if self.tile is None:
            self.tile = tile

        pidex = (
            numpy.bitwise_and(tile.data < self.tile.data, ~tile.mask) | self.tile.mask
        )

        mask = numpy.where(pidex, tile.mask, self.tile.mask)
        self.tile = numpy.ma.where(pidex, tile, self.tile)
        self.tile.mask = mask


class MeanMethod(MosaicMethodBase):
    """Feed the mosaic tile with the Mean pixel value."""

    @property
    def data(self):
        """Return data and mask."""
        if self.tile is not None:
            tile = numpy.ma.mean(self.tile, axis=0)
            return tile.data, ~tile.mask[0] * 255
        else:
            return None, None

    def feed(self, tile):
        """Add data to tile."""
        if self.tile is None:
            self.tile = tile
            return

        self.tile = numpy.ma.stack([self.tile, tile], axis=0)


class MedianMethod(MosaicMethodBase):
    """Feed the mosaic tile with the Median pixel value."""

    @property
    def data(self):
        """Return data and mask."""
        if self.tile is not None:
            tile = numpy.ma.median(self.tile, axis=0)
            return tile.data, ~tile.mask[0] * 255
        else:
            return None, None

    def feed(self, tile):
        """Create a stack of tile."""
        if self.tile is None:
            self.tile = tile
            return

        self.tile = numpy.ma.stack([self.tile, tile], axis=0)
