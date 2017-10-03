ogr2ogr -overwrite --config OSM_CONFIG_FILE ogrconfig.ini -f "ESRI Shapefile" amenities_all_points.shp helvetiaplatz.osm -progress -sql 'select osm_id,name,amenity,other_tags from points where amenity is not null'

ogr2ogr -overwrite --config OSM_CONFIG_FILE ogrconfig.ini -f "ESRI Shapefile" amenities_all_polygons.shp helvetiaplatz.osm -progress -sql "select osm_id,name,amenity,highway from multipolygons where highway='pedestrian' or area='yes'"

# Todo: import lines (ways)
