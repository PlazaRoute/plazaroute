#!/bin/bash
set -e

SHAPETYPE="GPKG"
OGRCONFIG=ogrconfig.ini

if [ "$#" -ne 1 ]
then
  echo "Usage: ./osm_to_gpkg.sh <OSMFILE>"
  exit 1
fi

OSMFILEPATH=$1
OSMFILE=$(basename "$OSMFILEPATH")
OSMFILENAME="${OSMFILE%.*}"
BASECMD="ogr2ogr -overwrite --config OSM_CONFIG_FILE ${OGRCONFIG} -progress -append ${OSMFILENAME}.gpkg"

# All points that are amenities
$BASECMD -f "${SHAPETYPE}" -sql "select * from points where amenity is not null" $OSMFILEPATH

# all plazas (highway=pedestrian or area=yes)
$BASECMD -f "${SHAPETYPE}" -sql "select * from multipolygons as plazas where highway='pedestrian' or area='yes'" $OSMFILEPATH

# all buildings
$BASECMD -f "${SHAPETYPE}" -sql "select * from multipolygons as buildings where building is not null" $OSMFILEPATH

# all lines
$BASECMD -f "${SHAPETYPE}" -sql "select * from lines" $OSMFILEPATH
