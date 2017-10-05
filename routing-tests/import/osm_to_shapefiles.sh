#!/bin/bash
set -e

SHAPETYPE="ESRI Shapefile"
OGRCONFIG=ogrconfig.ini

if [ "$#" -ne 1 ]
then
  echo "Usage: ./osm_to_shapefiles.sh <OSMFILE>"
  exit 1
fi

OSMFILEPATH=$1
OSMFILE=$(basename "$OSMFILEPATH")
OSMFILENAME="${OSMFILE%.*}"
BASECMD="ogr2ogr -overwrite --config OSM_CONFIG_FILE ${OGRCONFIG} -progress"

mkdir -p $OSMFILENAME

# All points that are amenities
$BASECMD -f "${SHAPETYPE}" -sql "select osm_id,name,amenity,other_tags from points where amenity is not null" ${OSMFILENAME}/${OSMFILENAME}_points_amenities.shp $OSMFILEPATH

# all plazas (highway=pedestrian or area=yes)
$BASECMD -f "${SHAPETYPE}" -sql "select osm_id,name,amenity,highway from multipolygons where highway='pedestrian' or area='yes'" ${OSMFILENAME}/${OSMFILENAME}_plazas.shp $OSMFILEPATH

# all buildings
$BASECMD -f "${SHAPETYPE}" -sql "select osm_id,osm_way_id,name,building,amenity,other_tags from multipolygons where building is not null" ${OSMFILENAME}/${OSMFILENAME}_buildings.shp $OSMFILEPATH

# all lines
$BASECMD -f "${SHAPETYPE}" -sql "select osm_id,name,natural,amenity,other_tags from lines" ${OSMFILENAME}/${OSMFILENAME}_lines.shp $OSMFILEPATH
