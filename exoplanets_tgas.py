#!/usr/bin/python

import gaia_tools.load as gload
from gaia_tools.xmatch import xmatch
from gaia_kepler import data, tgas_match
import pandas as pd
import numpy as np
import os

# Get exoplanets data and cross-match with TGAS
exoplanets = data.ExoplanetCatalog().df
planets_tgas = tgas_match(exoplanets)

# Proper motion is needed to account for the epoch difference
xmatch_kwargs = {"lamost": { "colRA1" : "ra_obs", "colDec1" : "dec_obs",
                             "epoch1" : 2000.0,},
                  "rave": { "colRA1" : "RAdeg", "colDec1" : "DEdeg",
                             "epoch1" : 2000.0,},
                  "tgas": { "colRA2" : "tgas_ra", "colDec2" : "tgas_dec",
                          "epoch2" : 2015.0, "colpmRA2" : "tgas_pmra",
                          "colpmDec2" : "tgas_pmdec"}
}


# Do the cross-match with lamost using gaia_tools
lamost_cat= gload.lamost(cat='star')
# Dictionary unpacking syntax only works on python 3.5
m1, m2, dist = xmatch(lamost_cat, planets_tgas.to_records(),
                      **{**xmatch_kwargs['lamost'], **xmatch_kwargs['tgas']})


# Add lamost columns to planets_tga dataframe
lamost_columns = ['teff', 'teff_err', 'logg', 'logg_err', 'feh', 'feh_err']

for k in lamost_columns:
    planets_tgas["lamost_" + k] = np.nan
    planets_tgas.loc[planets_tgas.iloc[m2].index, "lamost_" + k] = lamost_cat[k][m1]


# Do the cross-match with rave using gaia_tools
rave_columns = ['RAdeg', 'DEdeg', 'Teff_K', 'eTeff_K', 'logg_K', 'elogg_K',
                'Met_K', 'eMet_K']
# Find column numbers to speed up loading of the data
rave_data = os.path.join(os.environ.get("GAIA_TOOLS_DATA"),
                         'rave', 'DR5', 'RAVE_DR5.csv')
data = pd.read_csv(rave_data, nrows=1)
cols = np.where(data.columns.isin(rave_columns))[0]
rave_cat = gload.rave(usecols=cols)
m1, m2, dist = xmatch(rave_cat, planets_tgas.to_records(),
                      **{**xmatch_kwargs['rave'], **xmatch_kwargs['tgas']})

# Add rave columns to planets_tga dataframe
for k in rave_columns:
    planets_tgas["rave_" + k] = np.nan
    planets_tgas.loc[planets_tgas.iloc[m2].index, "rave_" + k] = rave_cat[k][m1]

planets_tgas.to_hdf("exoplanets_tgas.h5", "exoplanets_tgas", format="table")
