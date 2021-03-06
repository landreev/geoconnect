from django.conf.urls import url
from gc_apps.gis_tabular import views, views_create_layer, views_delete

urlpatterns = [

    url(r'^test/latest/$', views.view_tabular_file_latest, name="view_tabular_file_latest"),

    #url(r'^test1/(?P<tabular_id>\d{1,10})/$', 'view_tabular_file', name="view_tabular_file"),

    url(r'^view-tab-examine/(?P<tab_md5>\w{32})/$', views.view_tabular_file, name="view_tabular_file"),

    url(r'^view-existing-map/$', views.view_existing_map, name="view_existing_map"),

    # Join targets returned in list of tuples (id, name)
    #
    url(r'^ajax-join-targets/(?P<selected_geo_type>[\w|-]{1,255})/$', views.ajax_get_join_targets,\
        name='ajax_get_join_targets'),

    url(r'^ajax-join-targets/$', views.ajax_get_all_join_targets,\
        name='ajax_get_all_join_targets'),

    # Join targets returned in JSON format with id, name, and description
    #
    url(r'^ajax-join-targets-with-descriptions/$', views.ajax_get_all_join_targets_with_descriptions,\
        name='ajax_get_all_join_targets_with_descriptions'),

    url(r'^ajax-join-targets-with-descriptions/(?P<selected_geo_type>[\w|-]{1,255})$', views.ajax_join_targets_with_descriptions,\
        name='ajax_join_targets_with_descriptions'),

    url(r'^view-unmatched-join-rows-json/(?P<tab_md5>\w{32})$', views.view_unmatched_join_rows_json,\
        name='view_unmatched_join_rows'),

    url(r'^view-unmatched-lat-lng-rows-json/(?P<tab_md5>\w{32})$', views.view_unmatched_lat_lng_rows_json,\
        name='view_unmatched_lat_lng_rows'),

    url(r'^download-unmatched-lat-lng-rows/(?P<tab_md5>\w{32})$', views.download_unmatched_lat_lng_rows,\
        name='download_unmatched_lat_lng_rows'),

    url(r'^download-unmatched-join-rows/(?P<tab_md5>\w{32})$', views.download_unmatched_join_rows,\
        name='download_unmatched_join_rows'),

    url(r'^process-lat-long-form/$', views_create_layer.view_process_lat_lng_form,\
        name='view_process_lat_lng_form'),

    url(r'^process-tabular-form/$', views_create_layer.view_map_tabular_file_form,\
        name='view_map_tabular_file_form'),

    url(r'^delete-map/$', views_delete.view_delete_tabular_map, name="view_delete_tabular_map"),

]
