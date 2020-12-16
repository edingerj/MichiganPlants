import sqlite3
import webbrowser
import plotly.graph_objs as go
import numpy as np


def coefficients_of_conservatism():
	''' Constructs and executes SQL query to select every coefficient of conservatism
	To limit this to species taught in Woody Plants, I Joined Plants (Michigan Flora data) on WoodyPlants (created from my own CSV) 
	using the GenusSpecies key
	
	Parameters
	----------
	None
	
	Returns
	-------
	list
		a list of every coefficient of conservatism for all 116 plants
	'''
	connection = sqlite3.connect("michiganplants.sqlite")
	cursor = connection.cursor()
	query = '''
	SELECT ConservatismCoef
	FROM Plants
	JOIN WoodyPlants
	ON Plants.GenusSpecies = WoodyPlants.GenusSpecies
	'''
	result = cursor.execute(query).fetchall()
	every_coef = []
	for species in result:
		every_coef.append(species[0])
	connection.close()
	return every_coef

def order_by_conservatism():
	''' Constructs and executes SQL query to select species names and coefficients of conservatism, using the same join as the previous function.
	It eliminates species with a coefficient of "*" because those are non-native species which are a low conservation prio. 
	The top 20 species are printed in descending order by coefficient.

	Parameters
	----------
	None
	
	Returns
	-------
	None
	'''
	connection = sqlite3.connect("michiganplants.sqlite")
	cursor = connection.cursor()
	query = '''
	SELECT Plants.GenusSpecies, CommonName, ConservatismCoef
	FROM Plants
	JOIN WoodyPlants
	ON Plants.GenusSpecies = WoodyPlants.GenusSpecies
	WHERE ConservatismCoef <> '*'
	ORDER BY ConservatismCoef DESC
	'''
	result = cursor.execute(query).fetchall()
	i = 0
	for species in result[:20]:
		i += 1
		print(str(i) + '. ' + species[0] + ' (' + species[1] + ') ' + str(species[2]))
	connection.close()


def coefficient_of_conservatism():
	''' Defines coefficient of conservatism, opens a window using Plotly to graph a histogram of coefficients of conservatism for native species.
	Calls coefficients_of_conservatism() to form the list of coefficients and order_by_conservatism() to print the formatted list.

	Parameters
	----------
	None
	
	Returns
	-------
	None
	'''
	print('Coefficient of conservatism is a value used to determine the relative condition, or "ecological quality" of a specific site or plant community. Values range from 0-10 and represent the probability that plant is likely to occur in a habitat that is relatively unaltered from what is believed to be a pre-settlement condition. Low values mean the plant can be found almost anywhere, while values closer to 10 mean that plant is only found in high quality, specialized habitat. All non-native species have a value of 0.')
	print('Here is a histogram showing the distribution of coefficients of conservatism of all woody plants native to Michigan.')
	print('Launching Plotly...')
	conserv = coefficients_of_conservatism()
	conserv = [c if c != '*' else 0 for c in conserv] # non-native species are given a coefficient of 0 for graphing purposes

	x1 = np.array(conserv)
	data = [go.Histogram(x = x1)]
	layout = go.Layout(title="Histogram of Coefficients of Conservatism for Woody Plants", xaxis_title="Coefficient of Conservatism", yaxis_title="Number of Species", plot_bgcolor="lightgoldenrodyellow")
	fig1 = go.Figure(data=data, layout=layout)
	fig1.show()

	option = input('Enter 1 to learn more or 2 to return to search options: ')
	if option == '1':
		print('-' * 50)
		print('Here is a list of the top 20 species with highest conservation priority, followed by their coefficient of conservatism.')
		print('-' * 50)
		order_by_conservatism()


def unique_families(): 
	''' Constructs and executes SQL query to select unique family names
	Like in the coefficients_of_conservatism() function, I Joined Plants on WoodyPlants using the GenusSpecies key
	There are 176 unique families in Michigan, and 41 of them are taught in Woody Plants
	
	Parameters
	----------
	None
	
	Returns
	-------
	list
		a list of 41 unique plant families
	'''
	connection = sqlite3.connect("michiganplants.sqlite")
	cursor = connection.cursor()
	query = '''
	SELECT DISTINCT Family
	FROM Plants
	JOIN WoodyPlants
	ON Plants.GenusSpecies = WoodyPlants.GenusSpecies
	'''
	result = cursor.execute(query).fetchall()
	every_family = []
	i = 0
	for fam in result:
		i += 1
		print(str(i) + '. ' + fam[0])
		every_family.append(fam[0])
	connection.close()
	return every_family


def unique_species():
	''' Constructs and executes SQL query to select Genus & Species names
	Like in the above functions, I Joined Plants on WoodyPlants using the GenusSpecies key
	There are 2906 plant species in Michigan, and 116 of them are taught in Woody Plants
	
	Parameters
	----------
	None
	
	Returns
	-------
	list
		a list of 116 unique plant species
	'''
	connection = sqlite3.connect("michiganplants.sqlite")
	cursor = connection.cursor()
	query = '''
	SELECT Plants.GenusSpecies
	FROM Plants
	JOIN WoodyPlants
	ON Plants.GenusSpecies = WoodyPlants.GenusSpecies
	'''
	result = cursor.execute(query).fetchall()
	every_species = []
	for species in result:
		every_species.append(species[0])
	connection.close()
	return every_species

def list_plants_in_family(fam):
	''' Constructs and executes SQL query to select Genus & Species names
	Selects only species found in the family specified by the user (fam)
	
	Parameters
	----------
	fam: str
		This is the family name entered by the user
	
	Returns
	-------
	None
	'''
	connection = sqlite3.connect("michiganplants.sqlite")
	cursor = connection.cursor()

	sql = '''
	SELECT Plants.GenusSpecies, CommonName
	FROM Plants
	JOIN WoodyPlants
	ON Plants.GenusSpecies = WoodyPlants.GenusSpecies
	WHERE Family = '{0}'
	'''
	query = sql.format(fam)
	result = cursor.execute(query).fetchall()
	print('-' * 60)
	print('List of plants in the ' + fam + ' family:')
	print('-' * 60)
	i = 0
	for item in result:
		i += 1
		print(str(i) + '. ' + item[0] + ' (' + item[1] + ')')
	connection.close()


def provide_species_info(species):
	''' Constructs and executes SQL query to select some attributes of the species selected by the user
	There are two joins in this process:
		1) Join Plants (Michigan Flora data) on WoodyPlants (created from my own CSV) based on GenusSpecies key
		2) Join on LabSites (created from my own CSV) using the LabId number as the key
	
	Parameters
	----------
	species: str
		This is the species selected by the user
	
	Returns
	-------
	None
	'''
	connection = sqlite3.connect("michiganplants.sqlite")
	cursor = connection.cursor()

	sql = '''
	SELECT Family, Physiognomy, ConservatismCoef, YoutubeVideo, SiteName, Latitude, Longitude, CommonName
	FROM (Plants
	JOIN WoodyPlants
	ON Plants.GenusSpecies = WoodyPlants.GenusSpecies)
	JOIN LabSites ON WoodyPlants.LabId=LabSites.LabId
	WHERE Plants.GenusSpecies = '{0}'
	'''
	query = sql.format(species)
	result = cursor.execute(query).fetchall()
	plant = result[0] # result is a list of 1 tuple representing the selected plant
	common_name = plant[7]
	print('-' * 60)
	print('Here are some interesting facts about ' + species + ' (' + common_name + ')')
	print('-' * 60)
	try:
		family, cons_coef, video, site, latitude, longitude = plant[0], plant[2], plant[3], plant[4], plant[5], plant[6]
		physio = plant[1].split()[1].lower()
		if plant[1].split()[0] == 'Nt':
			native = 'native '
		else:
			native = 'non-native '
		print(species + ' (' + common_name + ') is a ' + native + physio + ' in the ' + family + ' family.')
		
		if native == 'native ': # Coefficient of conservatism doesn't apply to non-native species
			if cons_coef > 7:
				priority = 'high'
			elif cons_coef < 3:
				priority = 'low'
			else:
				priority = 'moderate'
			print('It has a coefficient of conservatism of ' + str(cons_coef) + ', indicating that it has ' + priority + ' priority for conservation.') 
		
		option = input('Select from the following options: \n 1) Watch a video \n 2) Locate on Google Maps \n 3) Go back to search options \n')
		if option == '1':
			print('Launching YouTube...')
			webbrowser.open(video)
		if option == '2':
			map_url = 'https://www.google.com/maps/search/?api=1&query=' + str(latitude) + ',' + str(longitude)
			print('You can find ' + species + ' (' + common_name + ') at ' + site + '! You can find that site on this map.')
			print('Launching Google Maps...')
			webbrowser.open(map_url)
	except:
		print("Sorry, I don't have any information on that plant!")
	connection.close()



print('Welcome to Woody Plants!')

while True:
	option = input('Select from the following options. Enter 1, 2, or 3: \n 1) Search for a plant by family \n 2) Learn about coefficient of conservatism \n 3) Exit \n')
	if option == '3':
		break
	if option == '2':
		coefficient_of_conservatism()
	if option == '1':
		print('Here is a list of families taught in this class: ')
		every_family = unique_families()
		while True:
			family = input('Select a family (e.g. "Rosaceae"), or enter "back" for more options. \n')
			if family == 'back':
				break
			if family not in every_family:
				print('Oops! You must have spelled it wrong. Try entering the family name again. \n')
			else:
				list_plants_in_family(family)
				while True:
					species = input('Enter the Genus & species of a plant to learn more (e.g. "Morus alba"), or enter "back" to search by family: \n')
					if species == 'back':
						unique_families()
						break
					if species not in unique_species():
						print('Oops! You must have spelled it wrong. Try entering the name again. ')
					else:
						provide_species_info(species)

print('Goodbye!')


