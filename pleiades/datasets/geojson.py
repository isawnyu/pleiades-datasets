#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create GeoJSON versions of Pleiades gazetteer data
"""

from copy import deepcopy
import geojson
import json
import logging
from pathlib import Path
from pprint import pformat
import sys

logger = logging.getLogger(__name__)

DEFAULT_CONTEXT = Path(__file__).parent.parent / 'data' / 'json'
GEO_KEYS = {
    'type': '',
    'geometry': '',
    'properties': ''
}


class Maker(object):
    """Make GeoJSON from Pleiades idiosyncratic JSON"""

    def __init__(self, context=DEFAULT_CONTEXT):
        logger.debug(context)
        self.context = context

    def make_feature(self, PID=None):
        """Create a GeoJSON feature from Pleiades JSON for PID"""
        if PID is None:
            msg = 'Expected Pleiades ID for PID argument. Got None.'
            raise ValueError(msg)
        if isinstance(self.context, Path):
            with open(
                self.context / '{}.json'.format(PID), encoding='utf-8'
            ) as f:
                j = json.load(f)
            del f
            properties = {}
            geometries = self._make_geometries(j)
            geo_feature = geojson.Feature(
                id=j['id'],
                title=j['title'],
                description=j['description'],
                properties=properties,
                geometry=geometries
            )
            if not geo_feature.is_valid:
                msg = 'Invalid Feature'
                raise RuntimeError(msg)
            return geojson.dumps(geo_feature, sort_keys=True, indent=4)
        else:
            raise NotImplementedError(type(self.context))

    def make_feature_collection(self, PID=None):
        """Create a GeoJSON FeatureCollection from Pleiades JSON for PID"""
        if PID is None:
            msg = 'Expected Pleiades ID for PID argument. Got None.'
            raise ValueError(msg)
        if isinstance(self.context, Path):
            with open(
                self.context / '{}.json'.format(PID), encoding='utf-8'
            ) as f:
                pleiades_json = json.load(f)
            del f
            # title (foreign member)
            # description (foreign member)
            # bbox (optional geojson: must be calculated from locations)
            # hull (foreign member)
            # id (foreign member)
            # features (array of feature objects)
            locations = pleiades_json['locations']
            features = self._make_features(locations)
            fc = geojson.FeatureCollection(
                features=features,
                bbox=self._make_bbox(features),
                centroid=self._make_centroid(features),
                hull=self._make_hull(features),
                id=pleiades_json['id'],
                title=pleiades_json['title'],
                description=pleiades_json['description'])
            if not fc.is_valid:
                msg = 'Invalid FeatureCollection'
                raise RuntimeError(msg)
            return geojson.dumps(
                fc, indent=4, sort_keys=True, ensure_ascii=False)
        else:
            raise NotImplementedError(type(self.context))

    def walk_feature_collection(self):
        raise NotImplementedError(sys._getframe().f_code.co_name)

    def _make_bbox(self, features):
        return None

    def _make_centroid(self, features):
        return None

    def _make_feature(self, location):
        return None

    def _make_features(self, locations):
        return [self._make_feature(l) for l in locations]

    def _make_hull(self, features):
        return None

    def _make_geometries(self, j: dict):
        geo_collection = geojson.GeometryCollection(
            [self._make_geometry(location) for location in j['locations']])
        if not geo_collection.is_valid:
            msg = 'Invalid GeometryCollection'
            raise RuntimeError(msg)
        return geo_collection

    def _make_geometry(self, jloc: dict):
        return getattr(
            geojson, jloc['geometry']['type'])(jloc['geometry']['coordinates'])


