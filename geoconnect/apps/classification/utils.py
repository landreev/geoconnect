import logging
from apps.layer_types.static_vals import TYPE_SHAPEFILE_LAYER,\
                TYPE_JOIN_LAYER,\
                TYPE_LAT_LNG_LAYER
from apps.gis_tabular.models import WorldMapJoinLayerInfo, WorldMapLatLngInfo
from apps.worldmap_connect.models import WorldMapLayerInfo

LOGGER = logging.getLogger(__name__)

def get_worldmap_info_object(data_source_type, info_md5):
    """
    Based on the type of data, return the appropriate container
    WorldMap data

    shapfile -> WorldMapLayerInfo
    tabular join -> WorldMapJoinLayerInfo
    tabular lat/lng -> WorldMapLatLngInfo
    """
    if data_source_type == TYPE_SHAPEFILE_LAYER:
        WORLDMAP_INFO_CLASS_TYPE = WorldMapLayerInfo
    elif data_source_type == TYPE_JOIN_LAYER:
        WORLDMAP_INFO_CLASS_TYPE = WorldMapJoinLayerInfo
    elif data_source_type == TYPE_LAT_LNG_LAYER:
        WORLDMAP_INFO_CLASS_TYPE = WorldMapLatLngInfo

    try:
        return WORLDMAP_INFO_CLASS_TYPE.objects.get(md5=info_md5)
    except WORLDMAP_INFO_CLASS_TYPE.DoesNotExist:
        err_note = ('Sorry! The layer data could not be found '
                    'for md5 "%s". '
                    '(%s object not found)' % (info_md5, data_source_type))
        LOGGER.error(err_note)
        return None