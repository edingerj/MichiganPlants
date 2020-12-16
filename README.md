# MichiganPlants

Link to YouTube video: https://www.youtube.com/watch?v=BxUwoK4eUJQ

SI 507 Final Project
by Jackie Edinger

Required packages: BeautifulSoup, json, requests, sqlite3, csv, webbrowser, plotly, numpy

This code is organized into 3 .py files:
1) MichiganFlora.py
2) WoodyPlants.py
3) FinalCode.py

Part 1) MichiganFlora.py
I accessed data by crawling and scraping multiple pages of the Michigan Flora website (https://michiganflora.net/)
Michigan Flora is an encyclopedia-like website that has a webpage for every plant species found in the state of Michigan. 
See the docstrings for detailed information on each function, including caching, building dictionaries for each family of
plants, and creating lists of each field scraped for each species. This code also creates a table in the michiganplants sql
database called "Plants", entering each species as a row containing all the fields scraped from Michigan Flora. 
I added an index (i) at the bottom of the code for each species so that it would have a unique identifier in the table. 
However, I used GenusSpecies as the key for all joins because each plant has a unique Genus and species combination. 

Part 2) WoodyPlants.py
This code reads the CSV files I made as a GSI for ENV 436 (Woody Plants) and creates two separate tables for a species list
and a list of all lab sites visited over the course of a semester. The commented-out code at the bottom shows examples of how
joins can be made on the three tables. 

Part 3) FinalCode.py
This is the interactive part of the code. See the docstrings for full descriptions of what each function does. Most functions
construct and execute a SQL query, selecting only the columns necessary for that function. For example, unique_families() selects
only the Family column. The user has two main options to interact with the code: A) Search for a plant by family or B) Learn about
coefficient of conservation. 
A) Search for a plant by family: the user is prompted to enter the name of a family (not the number it is listed under). For example, 
"Magnoliaceae" would be an appropriate response. The program checks that the input matches a family in the list returned by 
unique_families(); if it does not match, it was probably spelled wrong. The user then has the option to select a species within 
that family by entering the name of a species listed, for example "Liriodendron tulipifera". Again, the program checks that it was
spelled correctly. If a valid name is provided, it calls the function provide_species_info(). This executes a SQL query to select the
Family, Physiognomy, ConservatismCoef, YoutubeVideo, SiteName, Latitude, and Longitude of that plant in the joined table. A sentence
describing that plant is printed. For example, "Liriodendron tulipifera is a native tree in the Magnoliaceae family.
It has a coefficient of conservatism of 9, indicating that it has moderate priority for conservation." The user then has the option
to watch a video or open a map. If the video option is selected, a browser window will open with a Youtube video of that plant. These
videos were created by me and two other GSIs for the course and are available to the public. If the map option is selected, a browser
window will open with Google Maps showing the location of the lab where we taught that plant. For example, Liriodendron tulipifera
was taught at Haven Hill Recreational Area, and the program will show where that is located on Google Maps using the latitude and
longitude from the LabSites CSV to find the location. 
B) Learn about coefficient of conservation: the program will print a definition of this term. It will then use Plotly to display
a histogram showing the distribution of coefficients (from 0-10) of all 116 plants. Non-native plants have "*" as their coefficient
on Michigan Flora, so this was changed to a value 0 for graphing purposes because those plants have low conservation priority. If the 
user wants to learn more about coefficient of conservation, the program will print a list of the top 20 plants in order of 
conservation priority. 
The user also has the option to go "back" to the main options or exit at any time. 

