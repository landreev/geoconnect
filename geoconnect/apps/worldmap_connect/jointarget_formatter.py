"""
Helper class to format JSON in the JoinTargetInformation model's "target_info" field

- In terms of UI, this data is used for:
    1. Creating a list of Geospatial Identifiers
        - e.g. Census Tract, Zip code
    2. Creating a list of Names/Years based on the chosen Geospatial Identifiers
        - e.g. If Cenus Tract is chosen, list might be:
            "US Census 2010", "US Census 2000", "US Census 1990", etc.
    3. Based on the chosen JoinTarget, prep data for WorldMap datatables API
        - The Upload and Join API
        - Parms: name of target layer, name of target layer column
"""

class JoinTargetFormatter(object):
    """
    Helper class to format JSON in the JoinTargetInformation model's "target_info" field
        Sample target info data:
        {
          "data": [
            {
              "layer": "geonode:massachusetts_census_nhu",
              "geocode_type": "US Census Tract",
              "attribute": {
                "attribute": "TRACTCE",
                "type": "xsd:string"
              },
              "year": 2010,
              "type": null,
              "id": 3
            }
          ],
          "success": true
        }
    """
    def __init__(self, target_info):
        self.target_info = target_info

        self.err_found = False
        self.err_message = None

        self.initial_check()

    def is_valid(self):
        return self.err_found

    def add_error(self, msg):
        """
        Error detected, store a messsage in the class
        """
        self.err_found = True
        self.err_message = msg

    def initial_check(self):
        """
        Make sure that 'target_info' has the expected data
        """
        if self.target_info is None:
            self.add_error("target_info should not be None")
            return False

        # Is this a dict?  (e.g. not a list or blank, etc)
        print 'target_info', self.target_info
        if not hasattr(self.target_info, 'has_key'):
            self.add_error("target_info is not a dict")
            return False

        # Is there a 'success' attribute?
        if not 'success' in self.target_info:
            self.add_error("target_info does not have a 'success' attribute")
            return False

        # Is success True?
        if not self.target_info['success'] is True:
            self.add_error("target_info does not have a 'success' marked as True")
            return False

        # Is there a data attribute?
        if not 'data' in self.target_info:
            self.add_error("target_info does not have a 'data' attribute")
            return False

        # Does the data attribute contain any elements?
        if len(self.target_info['data']) == 0:
            self.add_error("There are no JoinTargets available.")
            return False

        return True


    @staticmethod
    def get_formatted_name(geocode_type, year=None):
        if year is None:
            return "{0}".format(geocode_type)

        return "{0} ({1})".format(geocode_type, year)


    def get_geocode_types(self):
        """
        Create a list of available Geospatial Identifiers
                - e.g. ["Census Tract", "Zip code", ...]
        """
        if self.err_found:
            return None

        gtypes = []
        for info in self.target_info['data']:
            if not 'geocode_type' in info:
                continue
            if not info['geocode_type'] in gtypes:
                info_line = JoinTargetFormatter.get_formatted_name(\
                            info['geocode_type'],)
                gtypes.append(info_line)
        return gtypes


    def get_join_targets_by_type(self, chosen_geocode_type=None):
        """
        Creating a list of tuples of Names/Years based on the chosen Geospatial Identifier
            - Format:
                join_target_name = name (year)
                join_target_id = JoinTarget id on the WorldMap system
                    - Used in the Geoconnect form
                [(join target name, join_target_id), ]
            - e.g. If Cenus Tract is chosen, list might be:
                [("US Census 2010", 7), ("US Census 2000", 3), etc.]

        Note: if chosen_geocode_type is None, all identifiers will be retrieved
        """
        if self.err_found:
            return None

        join_targets = []
        for info in self.target_info['data']:

            gtype = info['geocode_type']
            if chosen_geocode_type == gtype or\
                chosen_geocode_type is None:
                info_line = JoinTargetFormatter.get_formatted_name(\
                            info['geocode_type'],\
                            info['year'])
                join_targets.append((info_line, info['id']))
        return join_targets

"""
python manage.py shell
from apps.worldmap_connect.utils import get_latest_jointarget_information
from apps.worldmap_connect.jointarget_formatter import JoinTargetFormatter

jt = get_latest_jointarget_information()
formatter = JoinTargetFormatter(jt.target_info)
gtypes = formatter.get_geocode_types()
print gtypes
print '-- targets for each type --'
cnt = 0
for g in gtypes:
    cnt +=1
    print '({0}) {1}'.format(cnt, formatter.get_join_targets_by_type(g))

cnt = 0
print '\n-- all targets --'
for item in formatter.get_join_targets_by_type(g):
    cnt +=1
    print '({0}) {1}'.format(cnt, item)

"""
