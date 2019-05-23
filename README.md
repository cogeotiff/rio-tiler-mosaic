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

The goal of this rio-tiler plugin is to create tiles from multiple observations. Because user might want to choose which pixel goes on top of the tile, this plugin comes with 4 differents options:
- **first**: takes the first pixel received
- **last**: takes the last pixel received (works by inverting the order of the assets)
- **brightest**: loop though all the assets and return the highest value 
- **darkest**: loop though all the assets and return the lowest value

### API

`mosaic_tiler(assets, tile_x, tile_y, tile_z, tiler, pixel_selection='scene', chunk_size=5, kwargs)`

Inputs:
- assets : list, tuple of rio-tiler compatible assets (url or sceneid)
- tile_x : Mercator tile X index. 
- tile_y : Mercator tile Y index. 
- tile_z : Mercator tile ZOOM level. 
- tiler: Rio-tiler's tiler function (e.g rio_tiler.landsat8.tile) 
- pixel_selection : optional **pixel selection** method (default: "first"). 
- kwargs: Rio-tiler tiler module specific otions.

Returns:
- tile, mask : tuple of ndarray Return tile and mask data.


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