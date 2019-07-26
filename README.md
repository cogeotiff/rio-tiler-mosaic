# rio-tiler-mosaic

[![Packaging status](https://badge.fury.io/py/rio-tiler-mosaic.svg)](https://badge.fury.io/py/rio-tiler-mosaic)
[![CircleCI](https://circleci.com/gh/cogeotiff/rio-tiler-mosaic.svg?style=svg)](https://circleci.com/gh/cogeotiff/rio-tiler-mosaic)
[![codecov](https://codecov.io/gh/cogeotiff/rio-tiler-mosaic/branch/master/graph/badge.svg)](https://codecov.io/gh/cogeotiff/rio-tiler-mosaic)

A rio-tiler plugin for creating tiles from multiple observations.

![](https://user-images.githubusercontent.com/10407788/57466726-304f5880-724f-11e9-9969-bec4ce940e07.png)


## Install

```bash
$ pip install rio-tiler-mosaic
```
Or 
```bash
$ git clone http://github.com/cogeotiff/rio-tiler-mosaic
$ cd rio-tiler-mosaic
$ pip install -e .
```

## Rio-tiler + Mosaic

![](https://user-images.githubusercontent.com/10407788/57467798-30505800-7251-11e9-9bde-6f50801dc851.png)

The goal of this rio-tiler plugin is to create tiles from multiple observations. 

Because user might want to choose which pixel goes on top of the tile, this plugin comes with 5 differents `pixel selection` algorithms:
- **First**: takes the first pixel received
- **Highest**: loop though all the assets and return the highest value 
- **Lowest**: loop though all the assets and return the lowest value
- **Mean**: compute the mean value of the whole stack
- **Median**: compute the median value of the whole stack

### API

`mosaic_tiler(assets, tile_x, tile_y, tile_z, tiler, pixel_selection=None, chunk_size=5, kwargs)`

Inputs:
- assets : list, tuple of rio-tiler compatible assets (url or sceneid)
- tile_x : Mercator tile X index. 
- tile_y : Mercator tile Y index. 
- tile_z : Mercator tile ZOOM level. 
- tiler: Rio-tiler's tiler function (e.g rio_tiler.landsat8.tile) 
- pixel_selection : optional **pixel selection** algorithm (default: "first"). 
- chunk_size: optional, control the number of asset to process per loop.
- kwargs: Rio-tiler tiler module specific otions.

Returns:
- tile, mask : tuple of ndarray Return tile and mask data.

#### Examples

```python
from rio_tiler.main import tile as cogTiler
from rio_tiler_mosaic.mosaic import mosaic_tiler
from rio_tiler_mosaic.methods import defaults

assets = ["mytif1.tif", "mytif2.tif", "mytif3.tif"]
tile = (1000, 1000, 9)
x, y, z = tile

# Use Default First value method
mosaic_tiler(assets, x, y, z, cogTiler)

# Use Highest value: defaults.HighestMethod()
mosaic_tiler(
    assets,
    x,
    y,
    z,
    cogTiler,
    pixel_selection=defaults.HighestMethod()
)

# Use Lowest value: defaults.LowestMethod()
mosaic_tiler(
    assets,
    x,
    y,
    z,
    cogTiler,
    pixel_selection=defaults.LowestMethod()
)
```

### The `MosaicMethod` interface

the `rio-tiler-mosaic.methods.base.MosaicMethodBase` class defines an abstract 
interface for all `pixel selection` methods allowed by `rio-tiler-mosaic`. its methods and properties are:

- `is_done`: property, returns a boolean indicating if the process is done filling the tile
- `data`: property, returns the output **tile** and **mask** numpy arrays
- `feed(tile: numpy.ma.ndarray)`: method, update the tile

The MosaicMethodBase class is not intended to be used directly but as an abstract base class, a template for concrete implementations.

#### Writing your own Pixel Selection method

The rules for writing your own `pixel selection algorithm` class are as follows:

- Must inherit from MosaicMethodBase
- Must provide concrete implementations of all the above methods.

See [rio_tiler_mosaic.methods.defaults](/rio_tiler_mosaic/defaults.py) classes for examples.

#### Smart Multi-Threading 

When dealing with an important number of image, you might not want to process the whole stack, especially if the pixel selection method stops when the tile is filled. To allow better optimization, `rio-tiler-mosaic` is fetching the tiles in parallel (threads) but to limit the number of files we also embeded the fetching in a loop (creating 2 level of processing): 

```python
assets = ["1.tif", "2.tif", "3.tif", "4.tif", "5.tif", "6.tif"]

# 1st level loop - Creates chuncks of assets
for chunks in _chunks(assets, chunk_size):
    # 2nd level loop - Uses threads for process each `chunck`
    with futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
        future_tasks = [executor.submit(_tiler, asset) for asset in chunks]
```

By default the chunck_size is equal to max_threads ([default](https://github.com/cogeotiff/rio-tiler-mosaic/blob/4a4d188a9b0fefbf244af3cf52cf2695db7e0cf1/rio_tiler_mosaic/mosaic.py#L77))

## Example

See [/example](/example)

## Contribution & Development

Issues and pull requests are more than welcome.

**dev install**

```bash
$ git clone https://github.com/cogeotiff/rio-tiler-mosaic.git
$ cd rio-tiler-mosaic
$ pip install -e .[dev]
```

**Python3.6 only**

This repo is set to use `pre-commit` to run *flake8*, *pydocstring* and *black* ("uncompromising Python code formatter") when commiting new code.

```bash
$ pre-commit install
```


## Implementation
[cogeo-mosaic](http://github.com/developmentseed/cogeo-mosaic.git)