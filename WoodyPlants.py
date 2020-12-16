import csv
import sqlite3
import requests
import pandas

def create_db():
    conn = sqlite3.connect('michiganplants.sqlite')
    cur = conn.cursor()

    drop_woody_plants_sql = 'DROP TABLE IF EXISTS "WoodyPlants"'
    drop_lab_sites_sql = 'DROP TABLE IF EXISTS "LabSites"'
    
    create_woody_plants_sql = '''
        CREATE TABLE IF NOT EXISTS "WoodyPlants" (
            "GenusSpecies" TEXT NOT NULL,
            "LabId" INTEGER NOT NULL, 
            "YoutubeVideo" TEXT NOT NULL
        );
    '''

    create_lab_sites_sql = '''
        CREATE TABLE IF NOT EXISTS "LabSites" (
            "LabId" INTEGER NOT NULL, 
            "SiteName" TEXT NOT NULL,
            "SpeciesCount" INTEGER NOT NULL,
            "Latitude" REAL NOT NULL,
            "Longitude" REAL NOT NULL,
            "DistanceFromCampus(mi)" INTEGER NOT NULL
        );
    '''

    cur.execute(drop_woody_plants_sql)
    cur.execute(drop_lab_sites_sql)
    cur.execute(create_woody_plants_sql)
    cur.execute(create_lab_sites_sql)
    conn.commit()
    conn.close()

def load_woody_plants():
    file_contents = open('SpeciesList.csv', 'r')
    csv_reader = csv.reader(file_contents)
    next(csv_reader)
    insert_plant_sql = '''
        INSERT INTO WoodyPlants
            VALUES (?, ?, ?)
    '''
    conn = sqlite3.connect('michiganplants.sqlite')
    cur = conn.cursor()
    for row in csv_reader:
        cur.execute(insert_plant_sql, [row[0], row[1], row[2]])
    
    conn.commit()
    conn.close()

def load_lab_sites():
    file_contents = open('LabSites.csv', 'r')
    csv_reader = csv.reader(file_contents)
    next(csv_reader)
    insert_lab_sql = '''
        INSERT INTO LabSites
            VALUES (?, ?, ?, ?, ?, ?)
    '''
    conn = sqlite3.connect('michiganplants.sqlite')
    cur = conn.cursor()
    for row in csv_reader:
        cur.execute(insert_lab_sql, [row[0], row[1], row[2], row[3],row[4],row[5]])
    
    conn.commit()
    conn.close()

create_db()
load_woody_plants()
load_lab_sites()


# how to join Woody Plants and Lab Sites using LabId
'''
SELECT *
    FROM WoodyPlants
    JOIN LabSites
    ON WoodyPlants.LabId = LabSites.LabId

#how to join full Michigan species list with Woody Plants list using GenusSpecies
SELECT *
    FROM Plants
    JOIN WoodyPlants
    ON Plants.GenusSpecies = WoodyPlants.GenusSpecies

#how to do double join
SELECT *
    FROM (Plants
    JOIN WoodyPlants
    ON Plants.GenusSpecies = WoodyPlants.GenusSpecies)
    JOIN LabSites ON WoodyPlants.LabId=LabSites.LabId
    
'''
