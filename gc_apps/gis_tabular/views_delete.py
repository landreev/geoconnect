"""
View to delete Map created from a tabular file.
    - Delete the WorldMap layer
    - Delete the Dataverse metadata
"""
import logging

from django.shortcuts import render
from django.http import HttpResponse, Http404

from django.conf import settings

from gc_apps.geo_utils.msg_util import msg
from gc_apps.geo_utils.view_util import get_common_lookup
from gc_apps.geo_utils.geoconnect_step_names import PANEL_TITLE_DELETE_MAP,\
    PANEL_TITLE_REMAP
from gc_apps.gis_tabular.forms_delete import DeleteMapForm
from gc_apps.dv_notify.metadata_updater import MetadataUpdater
from gc_apps.worldmap_connect.dataverse_layer_services import delete_map_layer

logger = logging.getLogger(__name__)

def view_delete_tabular_map(request):
    """
    Attempt to delete a dataverse-created WorldMap layer
    """
    if not request.POST:
        raise Http404('Delete Not Found.')

    d = get_common_lookup(request)
    d['WORLDMAP_SERVER_URL'] = settings.WORLDMAP_SERVER_URL
    d['DATAVERSE_SERVER_URL'] = settings.DATAVERSE_SERVER_URL

    d['page_title'] = PANEL_TITLE_DELETE_MAP
    d['IS_DELETE_PAGE'] = True
    # Check the delete request
    f = DeleteMapForm(request.POST)

    if not f.is_valid():
        d['ERROR_FOUND'] = True
        d['FAILED_TO_VALIDATE'] = True
        return render(request, 'worldmap_layers/view_delete_layer.html', d)

    # Form params look good
    worldmap_layer_info = f.get_worldmap_layer_info()
    if not worldmap_layer_info:
        raise Http404('WorldMap Layer info no longer available')

    # depending on the type: tabular_info, shapefile_info, etc
    #
    if worldmap_layer_info.is_shapefile_layer():
        d['is_shapefile_layer'] = True
    else:
        d['is_tabular_layer'] = True

    gis_data_info = worldmap_layer_info.get_gis_data_info()

    d['gis_data_info'] = gis_data_info

    # -----------------------------------
    # Delete map from WorldMap
    # -----------------------------------
    flag_delete_local_worldmap_info = False

    (success, err_msg_or_None) = delete_map_layer(gis_data_info, worldmap_layer_info)
    if success is False:
        logger.error("Failed to delete WORLDMAP layer: %s", err_msg_or_None)

        if err_msg_or_None and err_msg_or_None.find('"Existing layer not found."') > -1:
            pass
        else:
            d['ERROR_FOUND'] = True
            d['WORLDMAP_DATA_DELETE_FAILURE'] = True
            d['ERR_MSG'] = err_msg_or_None
            return render(request, 'worldmap_layers/view_delete_layer.html', d)
    else:
        # At this point, the layer no longer exists on WorldMap,
        # set a flag to delete it from geoconnect, even if the Dataverse
        # delete fails
        flag_delete_local_worldmap_info = True

    # -----------------------------------
    # Delete metadata from dataverse
    # -----------------------------------

    (success2, err_msg_or_None2) = MetadataUpdater.delete_dataverse_map_metadata(worldmap_layer_info)

    # Delete the Geoconnect WorldMap info -- regardless of
    # whether the data was removed from Dataverse
    if flag_delete_local_worldmap_info:
        worldmap_layer_info.delete()

    if success2 is False:
        logger.error("Failed to delete Map Metadata from Dataverse: %s", err_msg_or_None)

        d['ERROR_FOUND'] = True
        d['DATAVERSE_DATA_DELETE_FAILURE'] = True
        d['ERR_MSG'] = err_msg_or_None2

        return render(request, 'worldmap_layers/view_delete_layer.html', d)

    d['DELETE_SUCCESS'] = True
    d['page_title'] = PANEL_TITLE_REMAP

    return render(request, 'worldmap_layers/view_delete_layer.html', d)
