import os

from django.shortcuts import render
from django.shortcuts import render_to_response

from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.core.urlresolvers import reverse

from gis_shapefiles.forms import ShapefileSetForm
from gis_shapefiles.models import ShapefileSet, SingleFileInfo
from gis_shapefiles.shp_services import update_shapefileset_with_metadata
from geoconnect.settings import MEDIA_ROOT 
from gis_shapefiles.shapefile_zip_check import ShapefileZipCheck
from gis_shapefiles.models import SHAPEFILE_MANDATORY_EXTENSIONS, WORLDMAP_MANDATORY_IMPORT_EXTENSIONS 

import json
from django.http import Http404

import logging
logger = logging.getLogger(__name__)

# Temp while figuring out steps
shapefile_steps = { 10 : ('Examine Dataset', )\
                   #, 20 : ('Choose Shapefile', )\
                   , 30 : ('Inspect Shapefile', )\
                   , 40 : ('Choose Column\Style Info', )\
                    }
def get_shapefile_step_title(k):
    t = shapefile_steps.get(k, None)
    if t:
        return t[0]
    return None
    
# Create your views here.
def view_examine_dataset(request):
    #return HttpResponse('view_google_map')
    d = { 'page_title' : get_shapefile_step_title(10)\
        , 'existing_shapefiles' : ShapefileSet.objects.all()
        }
    
    if request.method=='POST':        
        shp_form = ShapefileSetForm(request.POST, request.FILES)
        if shp_form.is_valid():
            shapefile_set = shp_form.save()
            return HttpResponseRedirect(reverse('view_shapefile'\
                                        , kwargs={ 'shp_md5' : shapefile_set.md5 })\
                                    )
            return HttpResponse('saved')            
        else:
            d['Form_Err_Found'] = True
            print shp_form.errors
            #return HttpResponse('blah - not valid')
    else:
        shp_form = ShapefileSetForm

    d['shp_form'] = shp_form 

    return render_to_response('view_01_examine_zip.html', d\
                            , context_instance=RequestContext(request))

def view_shapefile(request, shp_md5):
    
    d = {}
    
    try:
        shapefile_set = ShapefileSet.objects.get(md5=shp_md5)
        d['shapefile_set'] = shapefile_set        
        
    except ShapefileSet.DoesNotExist:
        logger.error('Shapefile not found for hash: %s' % shp_md5)
        raise Http404('Shapefile not found.')
    
    
    """
    Early pass: Move this logic out of view
    """
    if not shapefile_set.zipfile_checked:
        #zip_checker = ShapefileZipCheck(shapefile_set.dv_file, **{'is_django_file_field': True})
        zip_checker = ShapefileZipCheck(os.path.join(MEDIA_ROOT, shapefile_set.dv_file.name))
        zip_checker.validate()
        list_of_shapefile_set_names = zip_checker.get_shapefile_setnames()

        if list_of_shapefile_set_names is None:
            shapefile_set.has_shapefile = False
            shapefile_set.zipfile_checked = True
            shapefile_set.save()
            d['Err_Found'] = True
            d['Err_No_Shapefiles_Found'] = True
            d['zip_name_list'] = zip_checker.get_zipfile_names()
            d['WORLDMAP_MANDATORY_IMPORT_EXTENSIONS'] = WORLDMAP_MANDATORY_IMPORT_EXTENSIONS
            zip_checker.close_zip()        
            return render_to_response('view_02_single_shapefile.html', d\
                                    , context_instance=RequestContext(request))

        elif len(list_of_shapefile_set_names) > 1:      # more than one shapefile is in this zip
            shapefile_set.has_shapefile = False
            shapefile_set.zipfile_checked = True
            shapefile_set.save()
            d['Err_Found'] = True
            d['Err_Multiple_Shapefiles_Found'] = True
            d['list_of_shapefile_set_names'] = list_of_shapefile_set_names
            d['zip_name_list'] = zip_checker.get_zipfile_names()
            #d['WORLDMAP_MANDATORY_IMPORT_EXTENSIONS'] = WORLDMAP_MANDATORY_IMPORT_EXTENSIONS
            zip_checker.close_zip()        
            return render_to_response('view_02_single_shapefile.html', d\
                                    , context_instance=RequestContext(request))

        elif len(list_of_shapefile_set_names) == 1:
            shapefile_set.has_shapefile = True
            shapefile_set.zipfile_checked = True
            shapefile_set.save()
            #shapefile_set.name = os.path.basename(list_of_shapefile_set_names[0])
            (success, err_msg_or_none) = zip_checker.load_shapefile_from_open_zip(list_of_shapefile_set_names[0], shapefile_set)
            print 'here'
            if not success:
                print 'here - err'
                d['Err_Found'] = True
                d['Err_Msg'] = err_msg_or_none
                logger.error('Shapefile not loaded. (%s)' % shp_md5)
                return render_to_response('view_02_single_shapefile.html', d\
                                        , context_instance=RequestContext(request))

            zip_checker.close_zip()        
            return render_to_response('view_02_single_shapefile.html', d\
                                    , context_instance=RequestContext(request))
            
        
        
    if not shapefile_set.has_shapefile:
        d['Err_Found'] = True
        d['Err_No_Shapefiles_Found'] = True
        #d['zip_name_list'] = zip_checker.get_zipfile_names()
        d['WORLDMAP_MANDATORY_IMPORT_EXTENSIONS'] = WORLDMAP_MANDATORY_IMPORT_EXTENSIONS
        return render_to_response('view_02_single_shapefile.html', d\
                                , context_instance=RequestContext(request))
        
    #return HttpResponse('yes')
    return render_to_response('view_02_single_shapefile.html', d\
                            , context_instance=RequestContext(request))
                            
    #return HttpResponse(list_of_shapefile_set_names)

    #return HttpResponse('zip checked')
  
                        
def view_03_choose_shapefile_set(request, shp_md5, shapefile_base_name):
    return view_03_single_shapefile_set(request, shp_md5, shapefile_base_name, shp_group_obj=None, zip_checker=None)

def view_03_single_shapefile_set(request, shp_md5, shapefile_base_name, shp_group_obj=None, zip_checker=None):
    """Given a ShapefileGroup and a shapefile name:
        - Open the shapefile 
        - Save basic metadata
    Note: If the ShapefileGroup or ShapefileZipCheck are already loaded, send them over
    
    """
    print 'view_03_single_shapefile_set', shapefile_base_name
    if not shp_md5:
        logger.error('shp_md5 not found: %s' % shp_md5)
        raise Http404('shp_md5 set not found')

    if not shapefile_base_name:
        logger.error('shapefile_base_name not found')
        raise Http404('shapefile_base_name not found')
    
    d = { 'page_title' : get_shapefile_step_title(30) + ': ' + shapefile_base_name }
    
    if shp_group_obj is None:     
        print 'shp_group_obj is None'
        try:
            logger.info('retrieve ShapefileGroup')
            shp_group_obj = ShapefileGroup.objects.select_related('shapefile_group').get(md5=shp_md5)
            d['shp_group_obj'] = shp_group_obj
        except ShapefileGroup.DoesNotExist:
            d['Err_Found'] = True
            d['Err_ShapefileGroup_Not_Found'] = True
            logger.error('ShapefileGroup not found for md5: %s' % shp_md5)
            return render_to_response('view_03_single_shapefile_set.html', d\
                                    , context_instance=RequestContext(request))
    
    # Does the single shapefile set already exist?
    try:
        single_shapefile_set = ShapefileSet.objects.get(\
                                      shapefile_group=shp_group_obj\
                                    , name=shapefile_base_name)
        d['single_shapefile_set'] = single_shapefile_set
        print 'md5: ', single_shapefile_set.md5
        
        return render_to_response('view_03_single_shapefile_set.html', d\
                                , context_instance=RequestContext(request))
    except:
        pass
        
        
    if zip_checker is None:
        zip_checker = ShapefileZipCheck(shp_group_obj.shp_file, **{'is_django_file_field': True})
        zip_checker.validate()
    
    (success, err_msg_or_single_shapefile_set) = zip_checker.load_shapefile(shp_group_obj, shapefile_base_name)
    print 'here'
    if not success:
        print 'here - err'
        d['Err_Found'] = True
        d['Err_Msg'] = err_msg_or_single_shapefile_set
        logger.error('ShapefileGroup not found for md5: %s' % shp_md5)
        return render_to_response('view_03_single_shapefile_set.html', d\
                                , context_instance=RequestContext(request))
                                
    d['single_shapefile_set'] = err_msg_or_single_shapefile_set
    print 'md5: ', err_msg_or_single_shapefile_set.md5
    print 'not bad'
    return render_to_response('view_03_single_shapefile_set.html', d\
                            , context_instance=RequestContext(request))

def xview_03_single_shapefile_set(request, shapefileset_md5, shapefile_name):
    if shapefileset_md5 is None:
        raise Http404('shapefile set not found')
    
    d = {}

    try:
        shapefile_set = ShapefileSet(md5=shapefileset_md5)
        d['shapefile_set']  = shapefile_set
    except ShapefileSet.DoesNotExist:
         d['Err_Found'] = True
         d['Err_ShapefileSet_Not_Found'] = True
         return render_to_response('view_03_single_shapefile_set.html', d\
                                 , context_instance=RequestContext(request))

    
    
    
    
    
