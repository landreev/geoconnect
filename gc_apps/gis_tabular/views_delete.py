"""
View to delete Map created from a tabular file.
    - Delete the WorldMap layer
    - Delete the Dataverse metadata
"""
import logging

from django.shortcuts import render
from django.http import HttpResponse, Http404

from django.conf import settings

from gc_apps.geo_utils.msg_util import msg, msgt
from gc_apps.geo_utils.view_util import get_common_lookup
from gc_apps.geo_utils.geoconnect_step_names import PANEL_TITLE_DELETE_MAP,\
    PANEL_TITLE_REMAP, GEOCONNECT_STEP_KEY, STEP1_EXAMINE
from gc_apps.gis_tabular.forms_delete import DeleteMapForm
from gc_apps.gis_tabular.forms import SELECT_LABEL
from gc_apps.gis_tabular.models import TabularFileInfo
from gc_apps.gis_tabular.tab_services import get_tabular_file_from_dv_api_info, add_worldmap_layerinfo_if_exists
from gc_apps.dv_notify.metadata_updater import MetadataUpdater
from gc_apps.worldmap_connect.dataverse_layer_services import delete_map_layer
from gc_apps.geo_utils.message_helper_json import MessageHelperJSON
from gc_apps.gis_shapefiles.initial_request_helper import InitialRequestHelper

logger = logging.getLogger(__name__)

def view_formatted_error_page(request, error_type, err_msg=None):
    """Show an error page"""

    d = get_common_lookup(request)
    d['page_title'] = 'Examine Shapefile'
    d['WORLDMAP_SERVER_URL'] = settings.WORLDMAP_SERVER_URL
    d[GEOCONNECT_STEP_KEY] = STEP1_EXAMINE

    d['Err_Found'] = True
    if error_type is not None:
        d[error_type] = True
    d['Dataverse_Connect_Err_Msg'] = err_msg
    d['SELECT_LABEL'] = SELECT_LABEL

    return render(request, 'shapefiles/main_outline_shp.html', d)

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
        msgt('Delete worldmap_layer_info: %s' % worldmap_layer_info)
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

def view_delete_tabular_map_no_ui(request, dataverse_token):
    """
    Attempt to delete a dataverse-created WorldMap layer via a direct API call, w/out any UI involved.
    Operates on the same token-callback url principle as other geoconnect methods.
    (1) Check incoming url for a callback key 'cb'
        and use the callback url to retrieve the DataverseInfo via a POST
        (this is copied directly from the workflow of the "map-it" method)
    (2) If the Datafile info looks good, download and process the datafile
        (yes, we do have to actually download the file, even if we are merely deleting a map layer... 
        unless I'm missing something)
    (3) If that worked, look up TabularInfo for this file, using the md5 produced in step (2)
    (4) Look up MapLayerInfo by the TabularInfo produced in step (3)
    (5) If found, try deleting the map layer on the WorldMap side
    (6) And if that worked too, delete it locally, in GeoConnect.
    (7) Return 200 and a success message.
    """

    # Process the incoming url for a callback key 'cb'
    # and use the callback url to retrieve the DataverseInfo via a POST
    # (this is copied directly from the workflow of the "map-it" method)
    request_helper = InitialRequestHelper(request, dataverse_token)
    if request_helper.has_err:
        return HttpResponse(MessageHelperJSON.get_json_fail_msg("Failed to obtain datafile metadata from the Dataverse. Error: " + request_helper.err_msg), status=412)

    # check that it's a tabular file:
    if not request_helper.mapping_type == 'tabular':
        return HttpResponse(MessageHelperJSON.get_json_fail_msg("Precondition failed: Not a tabular file"), status=412)

    # check if the file is actually restricted (this is the use case - we are deleting this layer, because 
    # the user on the Dataverse side has made the file restricted)
    if request_helper.dv_data_dict.pop('datafile_is_restricted', None):
        return HttpResponse(MessageHelperJSON.get_json_fail_msg("Precondition failed: Tabular file is not restricted"), status=412)

    # (2) If the Datafile info looks good, download and process the datafile
    success, response_msg = get_tabular_file_from_dv_api_info(dataverse_token, request_helper.dv_data_dict)

    if not success:
        return HttpResponse(MessageHelperJSON.get_json_fail_msg("Failed to download and process the tabular file from the Dataverse. Error:" + response_msg.err_msg), status=412)

    tab_file_md5 = response_msg

    # (3) retrieve tabular file info, by md5:

    try:
        tabular_info = TabularFileInfo.objects.get(md5=tab_file_md5)
    except TabularFileInfo.DoesNotExist:
        raise Http404('No TabularFileInfo for md5: %s' % tab_file_md5)

    # (4) Is there a WorldMap layer associated with this tabular_info?
    if not add_worldmap_layerinfo_if_exists(tabular_info):
        raise Http404('No WorldMap layer info found for this TabularFileInfo (md5: %s)' % tab_file_md5)

    worldmap_layer_info = tabular_info.get_worldmap_info()
    if not worldmap_layer_info:
        return HttpResponse(MessageHelperJSON.get_json_fail_msg("Failed to retrieve worldmap info for this md5 (" + tab_file_md5+")"), status=412)

    gis_data_info = worldmap_layer_info.get_gis_data_info()

    # (5) ok, let's try and delete it on the worldmap side:
    (success, err_msg) = delete_map_layer(gis_data_info, worldmap_layer_info)
    if success is False:
        logger.error("Failed to delete WORLDMAP layer: %s", err_msg)
        return HttpResponse(MessageHelperJSON.get_json_fail_msg("Failed to delete WorldMap layer: "+err_msg), status=503)

    # (6) and delete it locally (in geoconnect):
    worldmap_layer_info.delete()


    # (7) Success!
    json_msg = MessageHelperJSON.get_json_msg(success=True, msg="Success! Successfully deleted WorldMap layer for the " + request_helper.mapping_type + " file, (md5: " + tab_file_md5 + ")")
    msg('message: %s' % json_msg)
    return HttpResponse(json_msg, content_type="application/json", status=200)
