import pymongo

connection  = pymongo.Connection()
db          = connection.redistrict

def printCount(*args):
    if len(args) > 0:
        if args[0] % 1000 == 0:
            print args[0]
    else:
        print
        print db.districts.count(), 'districts'
        print db.blocks.count(), 'blocks'
        print db.groups.count(), 'block groups'
        print db.counties.count(), 'counties'
        print


def ensureBlockIndex():
    db.eval('db.blocks.ensureIndex({ state_fips: 1, county_fips: 1, tract: 1, group: 1})')

if __name__ == '__main__':
    ensureBlockIndex()