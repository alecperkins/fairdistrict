from datetime import datetime
import csv, json, pymongo

from base import db, printCount



DISTRICT_DATA_FILE  = 'data/2012_district_votes.csv'
COUNTY_DATA_FILE    = 'data/2012_PA_county_data.json'
BLOCK_DATA_FILE     = 'data/42_PA_CD113.txt'
NEW_DISTRICT_FILE   = 'data/PA_Congress.csv'
GROUP_DATA_FILE     = 'data/CenPop2010_Mean_BG42.txt'



def insertDistricts():
    print 'loading districts'
    count = 0
    with open(DISTRICT_DATA_FILE) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            printCount(count)
            count += 1
            db.districts.save({
                "_id"       : int(row[0]),
                "vote_rep"  : int(row[1]),
                "vote_dem"  : int(row[2]),
            })
    print count, 'districts loaded'


def insertCounties():
    print 'loading counties'
    count = 0
    county_data = json.loads(file(COUNTY_DATA_FILE).read())
    for county in county_data:
        count +=1
        printCount(count)
        county['_id'] = county['id']
        db.counties.save(county)
    print count, 'counties loaded'


def insertBlocksWithCurrentDistricts():
    print 'loading census blocks'
    count = 0
    with open(BLOCK_DATA_FILE) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            try:
                int(row[0])
            except:
                pass
            else:
                count += 1
                printCount(count)
                _id = row[0]
                block_data = {
                    "_id": _id,
                    "district": int(row[1]),
                    "state_fips": _id[0:2],
                    "county_fips": _id[2:5],
                    "tract": _id[5:11],
                    "group": _id[11],
                    "tabulation": _id[11:15],
                }
                db.blocks.save(block_data)
    print count, 'blocks inserted'


def loadNewDistrictAssignments():
    print 'loading new district assignments'
    count = 0
    with open(NEW_DISTRICT_FILE) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            count += 1
            printCount(count)
            db.blocks.update({
                "_id": row[0],
            }, {
                "$set": {"b_district": int(row[1]) + 1} # +1 because they're 0 indexed
            })
    print count, 'blocks updated'


def insertGroups():
    """
    STATEFP,COUNTYFP,TRACTCE,BLKGRPCE,POPULATION,LATITUDE,LONGITUDE
    42,001,030101,1,2580,+40.015805,-077.081172
    """
    print 'loading census block groups'
    count = 0
    with open(GROUP_DATA_FILE) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            try:
                int(row[0])
            except:
                pass
            else:
                # print row
                count += 1
                printCount(count)
                new_group = {
                    "_id"           : "%s%s%s%s" % (row[0],row[1],row[2],row[3]),
                    "state_fips"    : row[0],
                    "county_fips"   : row[1],
                    "tract"         : row[2],
                    "group"         : row[3],
                    "lat"           : float(row[5]),
                    "lon"           : float(row[6]),
                    "population"    : float(row[4]),
                }
                db.groups.save(new_group)

    print count, 'groups loaded'



start = datetime.now()
printCount()

insertDistricts()
insertCounties()
insertBlocksWithCurrentDistricts()
loadNewDistrictAssignments()
insertGroups()

printCount()
print (datetime.now() - start).total_seconds(), 'seconds'


