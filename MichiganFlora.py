from bs4 import BeautifulSoup
import json
import requests
import sqlite3

CACHE_FILENAME = "plants_cache.json"


def open_cache():
    ''' Opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    if the cache file doesn't exist, creates a new cache dictionary
    
    Parameters
    ----------
    None
    
    Returns
    -------
    The opened cache: dict
    '''
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict

def save_cache(cache_dict):
    ''' Saves the current state of the cache to disk
    
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save
    
    Returns
    -------
    None
    '''
    dumped_json_cache = json.dumps(cache_dict, sort_keys=True, indent=4)
    fw = open(CACHE_FILENAME,"w")
    fw.write(dumped_json_cache)
    fw.close() 

def make_url_request_using_cache(url, params=None): # Michigan Flora
    '''Check the cache for a saved result. If the result is found, return it. Otherwise send a new 
    request, save it, then return it.
    
    Parameters
    ----------
    url: string
        The URL for the API endpoint
    params: dictionary
        A dictionary of param:value pairs
    
    Returns
    -------
    dict
        the results of the query as a dictionary loaded from cache
        JSON
    '''
    CACHE_DICT = open_cache()
    if (url in CACHE_DICT.keys()): # the url is our unique key
        print("Using cache")
        return CACHE_DICT[url]
    else:
        print("Fetching")
        response = requests.get(url, params)
        CACHE_DICT[url] = response.text
        save_cache(CACHE_DICT)
        return CACHE_DICT[url]


class Plant:
    '''a plant species found in the state of Michigan

    Instance Attributes
    -------------------
    family: string
        the family of a plant species (e.g. 'Magnoliaceae')
    
    genus_species: string
        the genus and species of a plant (e.g. 'Liriodendron tulipifera')

    common_name: string
        the common name of a plant (e.g. 'tulip tree')

    physiognomy: string
        defines whether a plant is native (Nt) or non-native (Ad) and the structure of the plant (shrub, tree, vine, etc.) 
        (e.g. 'Nt tree', 'Ad shrub')

    conservatism: string
        Coefficient of conservatism is a value used to determine the relative condition, or "ecological quality" of a specific site or 
        plant community. Values range from 0-10 and represent the probability that plant is likely to occur in a habitat that is relatively 
        unaltered from what is believed to be a pre-settlement condition. Low values mean the plant can be found almost anywhere, while 
        values closer to 10 mean that plant is only found in high quality, specialized habitat. All non-native species have a value of 0.
        (e.g. '9')

    wetness: string
        Coefficient of wetness is a value that represents the probability that a species occurs in wetlands. Positive values indicate a 
        species is likely to be found in a wetland, while negative values indicate a species almost never occurs in wetlands.
        Values range from -5 to 5.
        (e.g. '-3', '5')
    '''
    def __init__(self, family, genus_species, common_name, physiognomy, conservatism, wetness):
        self.family = family
        self.genus_species = genus_species
        self.common_name = common_name
        self.physiognomy = physiognomy
        self.conservatism = conservatism
        self.wetness = wetness

    def info(self):
        return self.genus_species + ' is in the ' + self.family + ' family.'

    def plant_facts(self): # returns a list of everything to be added to database
        return [self.family, self.genus_species, self.common_name, self.physiognomy, self.conservatism, self.wetness]


def build_family_url_dict(family):
    ''' Make a dictionary that maps genus_species of every plant in that family to species url from "https://www.michiganflora.net"

    Parameters
    ----------
    family: string
        the family of a plant species (e.g. 'Adoxaceae')

    Returns
    -------
    dict
        key is the genus_species of a species and value is the url
        e.g. {'Sambucus canadensis':'https://michiganflora.net/species.aspx?id=11', ...}
    '''
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
            fam_url = species_baseurl + fam_path
            fam_name = fam_link_tag.text.strip()
            families_dict[fam_name] = fam_url
    return families_dict

def browse_families():
    '''Creates a list of every plant family found in Michigan

    Parameters
    ----------
    None

    Returns
    -------
    list
        michigan_families is a list of all plant families found in Michigan in alphabetical order
        e.g. ['Acanthaceae', 'Acoraceae', 'Adoxaceae', ...]
    '''
    browse_url = 'https://michiganflora.net/browse.aspx'
    response = make_url_request_using_cache(browse_url)
    soup = BeautifulSoup(response, 'html.parser')

    parent = soup.find('div', class_='browse-links')
    families = parent.find_all('a', class_='browse')
    michigan_families = []
    for fam in families:
        fam_name = fam.text.strip()
        michigan_families.append(fam_name)
    return michigan_families


def get_plant_instance(species_url):
    '''Make an instance from a species URL.

    Parameters
    ----------
    species_url: string
        The URL for a plant species (e.g. 'https://michiganflora.net/species.aspx?id=11')
    
    Returns
    -------
    instance
        a Plant instance
    '''
    response = make_url_request_using_cache(species_url)
    soup = BeautifulSoup(response, 'html.parser')

    family_code = soup.find_all('span', {'id':'ctl00_Content_Formview2_FAMILYLabel'})
    family = family_code[0].text

    scientific_code = soup.find_all('span', {'id':'ctl00_Content_speciesHeaderFormview_SCIENTIFIC_NAMELabel'})
    scientific_name = scientific_code[0].text.split()
    genus_species = scientific_name[0] + ' ' + scientific_name[1]

    common_name_code = soup.find_all('span', {'id':'ctl00_Content_FormviewDetails_common_nameLabel'})
    common_name = common_name_code[0].text.lower()

    phys_code = soup.find_all('span', {'id':'ctl00_Content_FloraRepeater_ctl00_PHYSLabel'})
    physiognomy = phys_code[0].text

    conservatism_code = soup.find_all('span', {'id':'ctl00_Content_FloraRepeater_ctl00_CLabel'})
    conservatism = conservatism_code[0].text

    wetness_code = soup.find_all('span', {'id':'ctl00_Content_FloraRepeater_ctl00_WLabel'})
    wetness = wetness_code[0].text

    plant_instance = Plant(family, genus_species, common_name, physiognomy, conservatism, wetness)
    return plant_instance

def list_plant_instances(plant_dict):
    # for every plant in plant_dict, make it an instance of the Plant class and return a list of those instances
    '''Make an instance from a species URL.

    Parameters
    ----------
    plant_dict: dict
        A dictionary that maps genus_species to that species' URL
        e.g. {'Sambucus canadensis':'https://michiganflora.net/species.aspx?id=11', ...}
    
    Returns
    -------
    every_plant is a list of lists. Each family has its own list of each species' instance and associated attributes
        e.g. List of all plant instances in the 'Aquifoliaceae' family:
        [['Aquifoliaceae', 'Ilex mucronata', 'mountain holly', 'Nt Shrub', '7', '-5'], 
        ['Aquifoliaceae', 'Ilex opaca', 'american holly', 'Ad Shrub', '0', '3'], ...]
    '''
    urls = list(plant_dict.values())
    every_plant = []
    for url in urls:
        plant = get_plant_instance(url)
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
        "GenusSpecies" TEXT NOT NULL,
        "CommonName" TEXT NOT NULL,
        "Physiognomy" TEXT NOT NULL, 
        "ConservatismCoef" INTEGER NOT NULL,
        "WetnessCoef" INTEGER NOT NULL
    );
'''

add_tree = '''
    INSERT INTO Plants ("Id", "Family", "GenusSpecies", "CommonName", "Physiognomy", "ConservatismCoef", "WetnessCoef")
        VALUES (?, ?, ?, ?, ?, ?, ?)
'''

################################################################################

if __name__ == "__main__":
    CACHE_DICT = open_cache()

    cur.execute(drop_plants)
    cur.execute(create_plants)

    michigan_families = browse_families()

    every_family = []
    for fam in michigan_families:
        fam_dict = build_family_url_dict(fam)
        fam_instances = list_plant_instances(fam_dict)
        every_family.append(fam_instances)

    i = 0
    for family in every_family:
        for species in family:
            i += 1
            index = str(i)
            indexed_species = [index] + species  # This addes a unique ID to each plant before adding it to database
            cur.execute(add_tree, indexed_species)

    conn.commit()


