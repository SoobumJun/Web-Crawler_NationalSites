import requests
import json
import plotly.plotly as py
from bs4 import BeautifulSoup
from secrets import google_places_key as KEY



## you can, and should add to and modify this class any way you see fit
## you can add attributes and modify the __init__ parameters,
##   as long as tests still pass
##
## the starter code is here just to make the tests run (and fail)

class NationalSite():
    def __init__(self, type, name, desc, url=None):
        self.type = type
        self.name = name
        self.description = desc
        self.url = url
        self.address_street = ''
        self.address_city = ''
        self.address_state = ''
        self.address_zip = ''
        self.lat = None
        self.lng = None


        # needs to be changed, obvi.

        if url != None :
            try:
                page = request_using_cache(self.url, isstate = False)
                soup = BeautifulSoup(page, 'html.parser')
                self.address_street = soup.find(itemprop='streetAddress').text[1:-1]
                self.address_city = soup.find(itemprop='addressLocality').text
                self.address_state = soup.find(itemprop='addressRegion').text
                self.address_zip = soup.find(itemprop='postalCode').text[:5]
            except:
                None
    def __str__(self):
        return "{} ({}): {}, {}, {} {}".format(self.name, self.type, self.address_street, self.address_city, self.address_state,self.address_zip)

HOME_URL = 'https://www.nps.gov'
CACHE_FNAME = "nps_cache.json"
NEARBY_URL = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?'
PLACE_URL = 'https://maps.googleapis.com/maps/api/place/textsearch/json?'
CACHE_FNAME_GP = "gp_cache.json"

try:
    f = open(CACHE_FNAME, "r")
    fileread = f.read()
    CACHE_DICT = json.loads(fileread)
    f.close()
except:
    CACHE_DICT = {}

try:
    f2 = open(CACHE_FNAME_GP, "r")
    fileread2 = f2.read()
    CACHE_DICT_GP = json.loads(fileread2)
    f2.close()
except:
    CACHE_DICT_GP = {}


def params_unique_combination(baseurl, params_d, isstate, isnps = True):
    sorted_keys = sorted(params_d.keys())
    res = []
    for k in sorted_keys:
        if isnps:
            res.append("{}".format(params_d[k]))
        else:
            res.append("{}={}".format(k, params_d[k]))
    if isnps:
        if isstate:
            return baseurl + "/state/" + "".join(res) + "".join('/index.htm')
        else:
            return baseurl + "".join(res) + "".join('index.htm')
    else:
        return baseurl + "&".join(res)


def check_cache(query, dictionary, cache_filename):
    if query not in dictionary:
        resp = requests.get(query)
        page = resp.text
        dictionary[query] = page
        cache_dump = json.dumps(dictionary)
        cachefile = open(cache_filename, "w")
        cachefile.write(cache_dump)
        cachefile.close()

def request_using_cache(url, isstate = True, isnps = True, parkname = None, parktype = None):
    if isnps:
        params = {}
        params["url"] = url
        query = params_unique_combination(HOME_URL, params, isstate, isnps)
        # print(query)

        check_cache(query, CACHE_DICT, CACHE_FNAME)
        return CACHE_DICT[query]
    else:
        params = {}
        try:
            params["query"] = parkname + " " + parktype
        except:
            pass
        params["key"] = KEY
        query = params_unique_combination(PLACE_URL, params, False, False)


        check_cache(query, CACHE_DICT_GP, CACHE_FNAME_GP)

        # CACHE_DICT_GP[query] = json.loads(CACHE_DICT_GP[query])
        # try:
        # 	x_coord = CACHE_DICT_GP[query]["results"][0]["geometry"]["location"]["lat"]
        # 	y_coord = CACHE_DICT_GP[query]["results"][0]["geometry"]["location"]["lng"]
        # except:
        # 	CACHE_DICT_GP[query] = json.loads(CACHE_DICT_GP[query])
        try:
            cd = json.loads(CACHE_DICT_GP[query])
        except:
            cd = CACHE_DICT_GP[query]
        # print(type(cd))
        x_coord = None
        y_coord = None
        for r in cd['results']:
            if 'geometry' in r:
                x_coord = r['geometry']['location']['lat']
                y_coord = r['geometry']['location']['lng']

        if x_coord != None and y_coord != None:
            coordinate = str(x_coord) + "," + str(y_coord)
            n_params = {}
            n_params["location"] = coordinate
            n_params["radius"] = 10000
            n_params["key"] = KEY
            n_query = params_unique_combination(NEARBY_URL, n_params, False, False)
            check_cache(n_query, CACHE_DICT_GP, CACHE_FNAME_GP)
            # print(CACHE_DICT_GP.keys())

            return CACHE_DICT_GP[n_query]
        else:
            return CACHE_DICT_GP[query]

# request_using_cache(PLACE_URL, False, False, "Yellowstone", "National Park")



## you can, and should add to and modify this class any way you see fit
## you can add attributes and modify the __init__ parameters,
##   as long as tests still pass
##
## the starter code is here just to make the tests run (and fail)
class NearbyPlace():
    def __init__(self, name, lat, lng):
        self.name = name
        self.lat = lat
        self.lng = lng
    def __str__(self):
        return self.name + " (" + self.lat + "," + self.lng + ")"
    def __repr__(self):
        return self.name

## Must return the list of NationalSites for the specified state
## param: the 2-letter state abbreviation, lowercase
##        (OK to make it work for uppercase too)
## returns: all of the NationalSites
##        (e.g., National Parks, National Heritage Sites, etc.) that are listed
##        for the state at nps.gov
def get_sites_for_state(state_abbr):
    html = request_using_cache(state_abbr)
    soup = BeautifulSoup(html, 'html.parser')
    all_parks = {}
    NationalSites_list = []
    park_list_ul = soup.find(id='list_parks')
    # park_list_names = park_list_ul.find_all('h3')
    # for name in park_list_names:
    # 	all_parks[name] = name
    park_list_items = park_list_ul.find_all('li', {'class': 'clearfix'})
    for item in park_list_items:
        park_name = item.find('h3').text
        park_type = item.find('h2').text
        park_desc = item.find('p').text
        try:
            park_url = item.find('a')['href']
        except:
            park_url = None

        NationalSites_list.append(NationalSite(park_type,park_name,park_desc,park_url))
    # print(NationalSites_list[0])
    return NationalSites_list


## Must return the list of NearbyPlaces for the specifite NationalSite
## param: a NationalSite object
## returns: a list of NearbyPlaces within 10km of the given site
##          if the site is not found by a Google Places search, this should
##          return an empty list
def get_nearby_places_for_site(national_site):
    raw_page = request_using_cache(PLACE_URL, False, False, national_site.name, national_site.type)
    json_page = json.loads(raw_page)
    nearby_list = []
    for r in json_page["results"]:

        nearby_list.append(NearbyPlace(r["name"],str(r["geometry"]["location"]["lat"]),str(r["geometry"]["location"]["lng"])))

    # print(nearby_list)
    return nearby_list

# site2 = NationalSite('National Park',
# 	'Yellowstone', 'There is a big geyser there.')

# get_nearby_places_for_site(site2)

def find_lat_lng(site):
    params = {}
    params["query"] = site.name + " " + site.type
    params["key"] = KEY
    q = params_unique_combination(PLACE_URL, params, False, False)
    # print(q)
    check_cache(q, CACHE_DICT_GP, CACHE_FNAME_GP)

    try:
        cd = json.loads(CACHE_DICT_GP[q])
    except:
        cd = CACHE_DICT_GP[q]
    # print(type(cd))
    for r in cd['results']:
        if 'geometry' in r:
            site.lat = r['geometry']['location']['lat']
            site.lng = r['geometry']['location']['lng']

## Must plot all of the NationalSites listed for the state on nps.gov
## Note that some NationalSites might actually be located outside the state.
## If any NationalSites are not found by the Google Places API they should
##  be ignored.
## param: the 2-letter state abbreviation
## returns: nothing
## side effects: launches a plotly page in the web browser
def plot_sites_for_state(state_abbr):
    lat_vals = []
    lon_vals = []
    text_vals = []

    state_sites = get_sites_for_state(state_abbr)
    for site in state_sites:
        find_lat_lng(site)
        lat_vals.append(site.lat)
        lon_vals.append(site.lng)
        text_vals.append(site.name)



    min_lat = 10000
    max_lat = -10000
    min_lon = 10000
    max_lon = -10000

    for str_v in lat_vals:
        try:
            v = float(str_v)
        except:
            pass
        if v < min_lat:
            min_lat = v
        if v > max_lat:
            max_lat = v
    for str_v in lon_vals:
        try:
            v = float(str_v)
        except:
            pass
        if v < min_lon:
            min_lon = v
        if v > max_lon:
            max_lon = v

    center_lat = (max_lat+min_lat) / 2
    center_lon = (max_lon+min_lon) / 2

    max_range = max(abs(max_lat - min_lat), abs(max_lon - min_lon))
    padding = max_range * .10
    lat_axis = [min_lat - padding, max_lat + padding]
    lon_axis = [min_lon - padding, max_lon + padding]


    data = [ dict(
            type = 'scattergeo',
            locationmode = 'USA-states',
            lon = lon_vals,
            lat = lat_vals,
            text = text_vals,
            mode = 'markers',
            marker = dict(
                size = 20,
                symbol = 'star',
                color = 'rgb(12, 114, 29)'
            ))]

    layout = dict(
            title = 'National Sites in ' + state_abbr.upper(),
            geo = dict(
                        scope='usa',
                        projection=dict( type='albers usa' ),
                        showland = True,
                        showlakes = True,
                        showrivers = True,
                        landcolor = "rgb(255, 241, 226)",
                        subunitcolor = "rgb(100, 148, 217)",
                        lakecolor = "rgb(219, 238, 255)",
                        countrycolor = "rgb(217, 100, 217)",
                        lataxis = {'range': lat_axis},
                        lonaxis = {'range': lon_axis},
                        center= {'lat': center_lat, 'lon': center_lon },
                        countrywidth = 3,
                        subunitwidth = 3

            ),
        )
    fig = dict(data=data, layout=layout)
    py.plot(fig)

# plot_sites_for_state('mi')
# plot_sites_for_state('az')

## Must plot up to 20 of the NearbyPlaces found using the Google Places API
## param: the NationalSite around which to search
## returns: nothing
## side effects: launches a plotly page in the web browser
def plot_nearby_for_site(site_object):
    lat_vals = []
    lon_vals = []
    text_vals = []

    lat_vals1 =[]
    lon_vals1 = []
    text_vals1 = []

    nearby_places = get_nearby_places_for_site(site_object)
    if site_object.lat == None or site_object.lng == None:
        find_lat_lng(site_object)
    lat_vals1.append(site_object.lat)
    lon_vals1.append(site_object.lng)
    text_vals1.append(site_object.name)

    for place in nearby_places:
        if place.name not in text_vals:
            lat_vals.append(place.lat)
            lon_vals.append(place.lng)
            text_vals.append(place.name)



    min_lat = 10000
    max_lat = -10000
    min_lon = 10000
    max_lon = -10000

    for str_v in lat_vals:
        try:
            v = float(str_v)
        except:
            pass
        if v < min_lat:
            min_lat = v
        if v > max_lat:
            max_lat = v
    for str_v in lon_vals:
        try:
            v = float(str_v)
        except:
            pass
        if v < min_lon:
            min_lon = v
        if v > max_lon:
            max_lon = v

    center_lat = (max_lat+min_lat) / 2
    center_lon = (max_lon+min_lon) / 2

    max_range = max(abs(max_lat - min_lat), abs(max_lon - min_lon))
    padding = max_range * .10
    lat_axis = [min_lat - padding, max_lat + padding]
    lon_axis = [min_lon - padding, max_lon + padding]


    trace1 = dict(
            type = 'scattergeo',
            locationmode = 'USA-states',
            lon = lon_vals1,
            lat = lat_vals1,
            text = text_vals1,
            mode = 'markers',
            name = 'National Site',
            marker = dict(
                size = 20,
                symbol = 'star',
                color = 'rgb(12, 114, 29)'
            ))
    trace2 = dict(
            type = 'scattergeo',
            locationmode = 'USA-states',
            lon = lon_vals,
            lat = lat_vals,
            text = text_vals,
            mode = 'markers',
            name = 'Point of Interest',
            marker = dict(
                size = 10,
                symbol = 'circle',
                color = 'rgb(89, 183, 173)'
            ))

    layout = dict(
            title = 'Places near ' + site_object.name,
            geo = dict(
                        scope='usa',
                        projection=dict( type='albers usa' ),
                        showland = True,
                        showlakes = True,
                        showrivers = True,
                        landcolor = "rgb(255, 241, 226)",
                        subunitcolor = "rgb(100, 148, 217)",
                        lakecolor = "rgb(219, 238, 255)",
                        countrycolor = "rgb(217, 100, 217)",
                        lataxis = {'range': lat_axis},
                        lonaxis = {'range': lon_axis},
                        center= {'lat': center_lat, 'lon': center_lon },
                        countrywidth = 3,
                        subunitwidth = 3

            ),
        )
    data = [trace1, trace2]
    fig = dict(data=data, layout=layout)
    py.plot(fig, validate=False)


# plot_nearby_for_site(NationalSite('National Lakeshore', 'Sleeping Bear Dunes', desc=""))

# Interactive
if __name__ == '__main__':
    menu = "list <stateabbr> \n\tavailable anytime \n\tlists all National Sites in a state\n\tvalid inputs: a two-letter state abbreviation\nnearby <result_number>\n\tavailable only if there is an active result set \n\tLists all Places nearby a given result\n\tvalid inputs: an integer 1-len(result_set_size)\nmap\n\tavailable only if there is an active result set\n\tdisplays the current results on a map\nexit\n\texits the program\nhelp\n\tlists available commands (these instructions)"

    print(menu)
    prompt = input("\nPlease enter a command: ")
    is_list_active = False
    is_nearby_active = False
    is_map_active = False
    while(prompt != 'exit'):
        if prompt[:4] == "list":
            numcount = 1
            abbr = prompt[5:7]
            national_sites = get_sites_for_state(abbr)
            for site in national_sites:
                print(numcount, site)
                numcount += 1
            numcount = 1
            is_list_active = True
            is_map_active = True
        if prompt[:6] == "nearby":
            if not is_list_active:
                print("\nInactive result set.")
            elif len(prompt) > 9:
                print("\nInvalid result number.")
            elif int(prompt[7:]) > len(national_sites) + 1:
                print("\nResult number out of index.")
            else:
                current_site = national_sites[int(prompt[7:])-1]
                nearby_places = get_nearby_places_for_site(current_site)
                print("\nShowing places near", current_site.name)
                for place in nearby_places:
                    print(numcount, place)
                    numcount += 1
                numcount = 1
                is_list_active = False
                is_nearby_active = True
                is_map_active = True
                if len(nearby_places) == 0:
                    print("\nLocation info unavailable.")
                    is_map_active = False
                    is_list_active = False
                    is_nearby_active = False
        if prompt == 'map':
            if is_list_active and is_map_active:
                plot_sites_for_state(abbr)
                print('map has been created.')
            elif is_nearby_active and is_map_active:
                plot_nearby_for_site(current_site)
                print('map has been created.')
            else:
                print('Map cannot be made.')
            is_list_active = False
            is_nearby_active = False
            is_map_active = False
        if prompt == 'help':
            print(menu)
        prompt = input('Enter command (or "help" for options): ')
