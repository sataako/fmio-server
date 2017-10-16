# coding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals
__metaclass__ = type

from j24 import running_py3

import numpy as np
if running_py3():
    from urllib.parse import urlencode
else:
    from urllib import urlencode
from rasterio.plot import show
from os import path, environ
from fmio import USER_DIR

keyfilepath = path.join(USER_DIR, 'api.key')

def read_key(keyfilepath=keyfilepath):
    if "FMI_API_KEY" in environ:
        return environ['FMI_API_KEY']
    with open(keyfilepath, 'r') as keyfile:
        return keyfile.readline().splitlines()[0]


def gen_url(key=None, width=3400, height=5380, var='rr'):
    if key is None:
        key = read_key()
    url_base = 'http://wms.fmi.fi/fmi-apikey/{}/geoserver/Radar/ows?'
    params = dict(service='WMS',
                  version='1.3.0',
                  request='GetMap',
                  layers='Radar:suomi_{}_eureffin'.format(var),
                  styles='raster',
                  bbox='-118331.366,6335621.167,875567.732,7907751.537',
                  srs='EPSG:3067',
                  format='image/geotiff',
                  width=width,
                  height=height)
    # old API params
    params_old = dict(service='WMS',
                      request='GetMap',
                      format='image/geotiff',
                      bbox='-118331.366,6335621.167,875567.732,7907751.537',
                      width=1700,
                      height=2500,
                      srs='EPSG:3067',
                      layers='Radar:suomi_dbz_eureffin')
    return url_base.format(key) + urlencode(params)


def plot_radar_map(radar_data, border=None, cities=None, ax=None, tight=True):
    dat = radar_data.read(1)
    mask = dat==65535
    d = dat.copy()*0.01
    d[mask] = 0
    datm = np.ma.MaskedArray(data=d, mask=d==0)
    nummask = np.ma.MaskedArray(data=dat, mask=~mask)
    ax = show(datm, transform=radar_data.transform, ax=ax, zorder=3)
    show(nummask, transform=radar_data.transform, ax=ax, zorder=4, alpha=.1,
         interpolation='bilinear')
    if border is not None:
        border.to_crs(radar_data.read_crs().data).plot(zorder=0, color='gray',
                                                       ax=ax)
    if cities is not None:
        cities.to_crs(radar_data.read_crs().data).plot(zorder=5, color='black',
                                                       ax=ax, markersize=2)
    ax.axis('off')
    if tight:
        ax.set_xlim(left=1e4, right=7.8e5)
        ax.set_ylim(top=7.8e6, bottom=6.45e6)
    else:
        ax.set_xlim(left=-5e4)
        ax.set_ylim(top=7.8e6, bottom=6.42e6)
    return ax

