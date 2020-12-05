from bs4 import BeautifulSoup
import json
import requests
import sqlite3

CACHE_FILENAME = "trefle_cache.json"
CACHE_DICT = {}

trefle_token = 'kbmEL0Dn4kHt-vypERGA2X_ZrTSmFyL_asoClCM_ISM'

def open_cache():
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict


def save_cache(cache_dict):
    dumped_json_cache = json.dumps(cache_dict, sort_keys=True, indent=4)
    fw = open(CACHE_FILENAME,"w")
    fw.write(dumped_json_cache)
    fw.close() 

def make_url_request_using_cache(url, params=None):
    '''
    '''
    CACHE_DICT = load_cache()
    if (url in CACHE_DICT.keys()): # the url is our unique key
        print("Using cache")
        return CACHE_DICT[url]
    else:
        print("Fetching")
        #time.sleep(0.2)
        response = requests.get(url, params)
        CACHE_DICT[url] = response.text
        save_cache(CACHE_DICT)
        return CACHE_DICT[url]

def construct_unique_key(baseurl, params):
    ''' 
    '''
    param_strings = []
    connector = '_'
    for k in params.keys():
        param_strings.append(f'{k}_{params[k]}')
    param_strings.sort()
    unique_key = baseurl + connector + connector.join(param_strings)
    return unique_key

def make_request(baseurl, params):
    '''Make a request to the Web API using the baseurl and params
    '''
    response = requests.get(baseurl, params=params)
    return response.json()

def load_cache():
    '''
    '''
    try:
        cache_file = open(CACHE_FILE_NAME, 'r')
        cache_file_contents = cache_file.read()
        cache_dict = json.loads(cache_file_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict

def make_request_with_cache(baseurl, params=None):
    '''
    '''
    try:
        with open(CACHE_FILENAME) as my_data:
            CACHE_DICT = json.load(my_data)
        my_data.close()
    except:
        CACHE_DICT = {}

    #params = {'id': family}

    request_key = construct_unique_key(baseurl, params)
    if request_key in CACHE_DICT.keys():
        print("fetching cached data")
        return CACHE_DICT[request_key]
    else:
        print("making new request")
        CACHE_DICT[request_key] = make_request(baseurl, params)
        with open(CACHE_FILENAME, 'w') as outfile:
            outfile.write(json.dumps(CACHE_DICT, indent=2))
        outfile.close()
        #save_cache(CACHE_DICT)
        return CACHE_DICT[request_key]


#r = requests.get('https://trefle.io/api/v1/plants?filter_not%5Bmaximum_height_cm%5D=null&filter%5Bligneous_type%5D=tree&order%5Bmaximum_height_cm%5D=desc&token=YOUR_TREFLE_TOKEN')
#r.json()

def make_list_of_families():
    '''
    This function looks through each page of the Trefle API for plant families and returns a list of all the families in alphabetical order.
    '''
    complete_list = []
    for i in range(1, 35): # last page is 35, so there are (34*20)+(1*5) or 665 total families!
        params = {'page': i}
        families_data = make_request_with_cache(trefle_baseurl, params)
        families_list = families_data['data']
        for fam in families_list:
            complete_list.append(fam['name'])
    print(len(complete_list))
    return complete_list

class Plant:
    '''
    '''
    def __init__(self, family, genus, species, common_name, physiognomy, conservatism, wetness):
        self.family = family
        self.genus = genus
        self.species = species
        self.common_name = common_name
        self.physiognomy = physiognomy
        self.conservatism = conservatism
        self.wetness = wetness

    def info(self):
        return self.genus + ' ' + self.species + ' is in the ' + self.family + ' family.'

    def plant_facts(self): #returns a list of everything to be added to database
        return [self.family, self.genus, self.species, self.common_name, self.physiognomy, self.conservatism, self.wetness]

def build_family_url_dict(family):
    ''' Make a dictionary that maps family name to family page url from "https://www.michiganflora.net"
        e.g. {'Adoxaceae':'https://michiganflora.net/family.aspx?id=Adoxaceae', ...}
        #e.g. {'acer negundo':'https://michiganflora.net/species.aspx?id=2649', ...}
    '''
    #family_baseurl = 'https://michiganflora.net/browse.aspx'
    family_url = 'https://michiganflora.net/family.aspx?id=' + family
    species_baseurl = 'https://michiganflora.net/'
    response = make_url_request_using_cache(family_url)
    soup = BeautifulSoup(response, 'html.parser')

    family_parent = soup.find('div', class_='taxaList')
    family_divs = family_parent.find_all('div', recursive=False)
    families_dict = {}
    for div in family_divs:
        rows = div.find_all('tr')
        for row in rows:
            fam_link_tag = row.find('a')
            fam_path = fam_link_tag['href']
            #fam_url = family_url + fam_path
            fam_url = species_baseurl + fam_path
            fam_name = fam_link_tag.text.strip()
            families_dict[fam_name] = fam_url
    return families_dict

def get_plant_instance(species_url):
    '''Make an instance from a species URL.
    '''
    response = make_url_request_using_cache(species_url)
    soup = BeautifulSoup(response, 'html.parser')

    family_code = soup.find_all('span', {'id':'ctl00_Content_Formview2_FAMILYLabel'})
    family = family_code[0].text

    scientific_code = soup.find_all('span', {'id':'ctl00_Content_speciesHeaderFormview_SCIENTIFIC_NAMELabel'})
    scientific_name = scientific_code[0].text.split()
    genus = scientific_name[0]
    species = scientific_name[1]

    common_name_code = soup.find_all('span', {'id':'ctl00_Content_FormviewDetails_common_nameLabel'})
    common_name = common_name_code[0].text.lower()

    phys_code = soup.find_all('span', {'id':'ctl00_Content_FloraRepeater_ctl00_PHYSLabel'})
    physiognomy = phys_code[0].text

    conservatism_code = soup.find_all('span', {'id':'ctl00_Content_FloraRepeater_ctl00_CLabel'})
    conservatism = conservatism_code[0].text

    wetness_code = soup.find_all('span', {'id':'ctl00_Content_FloraRepeater_ctl00_WLabel'})
    wetness = wetness_code[0].text

    plant_instance = Plant(family, genus, species, common_name, physiognomy, conservatism, wetness)
    return plant_instance

def list_plant_instances(plant_dict):
    # for every plant in plant_dict, make it an instance of the Plant class and return a list of those instances
    urls = list(plant_dict.values())
    every_plant = []
    for url in urls:
        plant = get_plant_instance(url)
        #print(plant)
        every_plant.append(plant.plant_facts())
    return every_plant

################################################################################

conn = sqlite3.connect("michiganplants.sqlite")
cur = conn.cursor()

drop_plants = '''
    DROP TABLE IF EXISTS "Plants";
'''

create_plants = '''
    CREATE TABLE IF NOT EXISTS "Plants" (
        "Id"        INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
        "Family" TEXT NOT NULL,
        "Genus" TEXT NOT NULL,
        "Species" TEXT NOT NULL,
        "CommonName" TEXT NOT NULL,
        "Physiognomy" TEXT NOT NULL, 
        "ConservatismCoef" INTEGER NOT NULL,
        "WetnessCoef" INTEGER NOT NULL
    );
'''

pinaceae_dict = build_family_url_dict('Pinaceae')
pinaceae_instances = list_plant_instances(pinaceae_dict)
#print(pinaceae_instances)

add_tree = '''
    INSERT INTO Plants ("Id", "Family", "Genus", "Species", "CommonName", "Physiognomy", "ConservatismCoef", "WetnessCoef")
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
'''

#first_pine = pinaceae_instances[0]
#first_pine = ['0'] + first_pine
#print(first_pine)


cur.execute(drop_plants)
cur.execute(create_plants)

i = 0
for pine in pinaceae_instances:
    i += 1
    index = str(i)
    corrected_pine = [index] + pine
    cur.execute(add_tree, corrected_pine)

conn.commit()


################################################################################

if __name__ == "__main__":
    CACHE_DICT = open_cache()


    #baseurl = "https://trefle.io/api/v1/plants?token=" + trefle_token
    trefle_baseurl = "https://trefle.io/api/v1/families?token=" + trefle_token

    print(make_list_of_families()) #this uses Trefle API

    #pinaceae_dict = build_family_url_dict('Pinaceae')
    #adoxaceae_dict = build_family_url_dict('Adoxaceae')

    #adoxaceae_instances = list_plant_instances(adoxaceae_dict)
    #print(adoxaceae_instances)
    #pinaceae_instances = list_plant_instances(pinaceae_dict)
    #print(pinaceae_instances)
    #print(list_plants_in_family('Sapindaceae')
    #build_plant_url_dict()

    #common_elder = get_plant_instance('https://michiganflora.net/species.aspx?id=11')
    #print(common_elder.info())

