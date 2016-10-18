#!/usr/bin/python

from gaia_kepler import data, tgas_match
import gaia_tools.load as gload
from gaia_tools import xmatch
import pandas as pd
import os

os.environ["GAIA_TOOLS_DATA"] = "/home/miguel/Gaia/data"

lamost_cat= gload.lamost(cat='star')

exoplanets = data.ExoplanetCatalog().df
planets_tgas = tgas_match(exoplanets)

kwargs = {
    "colRA1" : "ra_obs",
    "colDec1" : "dec_obs",
    "epoch1" : 2000.0,
    "colRA2" : "tgas_ra",
    "colDec2" : "tgas_dec",
    "epoch2" : 2015.0,
    "colpmRA2" : "tgas_pmra",
    "colpmDec2" : "tgas_pmdec",
}

# Do the cross-match using gaia_tools
m1, m2, dist = xmatch.xmatch(lamost_cat, planets_tgas.to_records(), **kwargs)

# Build a pandas DataFrame out of the match and save the TGAS columns
matched = pd.DataFrame(planets_tgas.iloc[m2])
lamost_matched = lamost_cat[m1]

for k in lamost_matched.dtype.names:
    # Ugliness to deal with byte ordering
    matched["lamost_" + k] = lamost_matched[k].byteswap().newbyteorder()

print(matched.columns)
