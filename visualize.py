import Image

from base import db, printCount


WIDTH = 1400
HEIGHT = 800

GROUPS_IMAGE                    = 'images/groups.png'
BLOCKS_IMAGE                    = 'images/blocks.png'
CURRENT_DISTRICT_VOTES_IMAGE    = 'images/current_district_votes.png'
DISTRICT_VOTES_IMAGE            = 'images/%s_votes.png'
BLOCKS_PRES_HOUSE_DIFF_IMAGE    = 'images/PA_2012_county_pres-house_diff.png'
BLOCK_VOTES_IMAGE               = 'images/blocks_%s_votes.png'

def getGroupXY(group):
    x = int( ( 81 + group.get('lon') ) * 200 )
    y = int( ( group.get('lat') - 39 ) * 200 )
    # flip vertically since image is 0 top
    y = HEIGHT - y
    return (x, y)

from random import random
def jitter():
    if random() > 5:
        sign = -1
    else:
        sign = 1
    return sign * random() * 3

def getBlockXY(block):
    x = int( ( 81 + block.get('group_lon') ) * 200 + jitter() )
    y = int( ( block.get('group_lat') - 39 ) * 200 + jitter() )
    # flip vertically since image is 0 top
    y = HEIGHT - y
    return (x, y)

def newImage():
    img = Image.new( 'RGB', (WIDTH,HEIGHT), "black") # create a new black image
    pixels = img.load() # create the pixel map
    return img, pixels

def writeImage(img, name):
    img.save(name, 'PNG')
    img.show()

def blockGroupID(block):
    return "{state_fips}{county_fips}{tract}{group}".format(**block)




def drawGroups():
    img, pixels = newImage()

    for group in db.groups.find():
        x, y = getGroupXY(group)
        pixels[x,y] = (255,255,255)

    writeImage(img, GROUPS_IMAGE)


def drawBlocks():
    img, pixels = newImage()

    for block in db.blocks.find():
        x, y = getBlockXY(block)
        pixels[x,y] = (
            pixels[x,y][0] + 10,
            pixels[x,y][1] + 10,
            pixels[x,y][2] + 10
        )

    writeImage(img, BLOCKS_IMAGE)



def drawCurrentVotes(flat=True, key='house'):
    img, pixels = newImage()

    count = 0

    # if not flat:
    #     max_votes = []
    #     max_delta = []
    #     for block in db.blocks.find():
    #         max_votes.append(block['votes'][key]['rep'])
    #         max_votes.append(block['votes'][key]['dem'])
    #         max_delta.append(abs(block['votes'][key]['rep'] - block['votes']['house']['dem']))
    #     max_votes = max(max_votes)
    #     max_delta = max(max_delta)

    #     print max_votes, max_delta

    for block in db.blocks.find():
        count += 1
        printCount(count)
        x, y = getBlockXY(block)
        votes = block['votes'][key]
        if flat:
            if votes.get('rep',0) > votes.get('dem',0):
                pixels[x, y] = (255,0,0)
            else:
                pixels[x, y] = (0,0,255)
        else:
            max_votes = votes.get('rep',0) + votes.get('dem', 0)
            # r_ratio = votes.get('rep',0) / max_rep
            # b_ratio = votes.get('dem',0) / max_dem
            # r = int( r_ratio * 100  + (155 * (1 - b_ratio)) )
            # b = int( b_ratio * 100  + (155 * (1 - r_ratio)) )
            print max_votes

            if max_votes:
                shift_r = 128 * votes.get('rep',0) / max_votes
                shift_b = 128 * votes.get('dem',0) / max_votes        
                r = int( 128 + shift_r - shift_b )
                b = int( 128 + shift_b - shift_r )
            else:
                r = 0
                b = 0

            # r = int( 255 * votes.get('rep',0) / max_votes )
            # b = int( 255 * votes.get('dem',0) / max_votes )
            # 0      255
            # 255      0
            pixels[x, y] = (pixels[x,y][0] + r,0,pixels[x,y][2] + b)


    writeImage(img, BLOCK_VOTES_IMAGE % (key,))




def drawDistricts(district_key='district'):
    img, pixels = newImage()

    dem_districts = []
    rep_districts = []

    total_votes_dem = []
    total_votes_rep = []

    for district in db.districts.find():
        print district
        vote_dem = []
        vote_rep = []
        for block in db.blocks.find({
            district_key: district.get('_id')
        }):
            vote_rep.append(block['votes']['house']['rep'])
            vote_dem.append(block['votes']['house']['dem'])

        vote_dem = sum(vote_dem)
        vote_rep = sum(vote_rep)
        total_votes_dem.append(vote_dem)
        total_votes_rep.append(vote_rep)
        if vote_rep > vote_dem:
            color = (255,0,0)
            rep_districts.append(district)
        else:
            color = (0,0,255)
            dem_districts.append(district)

        for block in db.blocks.find({
            district_key: district.get('_id')
        }):
            x, y = getBlockXY(block)
            pixels[x, y] = color

    print 'R:', len(rep_districts), sum(total_votes_rep)
    print 'D:', len(dem_districts), sum(total_votes_dem)


    total_votes_dem = []
    total_votes_rep = []
    for block in db.blocks.find():
        total_votes_rep.append(block['votes']['house']['rep'])
        total_votes_dem.append(block['votes']['house']['dem'])
    print 'R:', sum(total_votes_rep)
    print 'D:', sum(total_votes_dem)


    writeImage(img, DISTRICT_VOTES_IMAGE % district_key)




def drawBlockHousePresidentDelta():

    img, pixels = newImage()

    count = 0
    for block in db.blocks.find():
        count += 1
        printCount(count)
        x, y = getBlockXY(block)

        pres_votes = block['votes']['president']
        house_votes = block['votes']['house']

        pres_rep = pres_votes.get('rep',0) > pres_votes.get('dem',0)
        house_rep = house_votes.get('rep',0) > house_votes.get('dem',0)

        pixels[x,y] = (40,40,40)
        if pres_rep != house_rep:
            
            pres_total = 0
            house_total = 0
            for party, votes in pres_votes.items():
                pres_total += votes
            for party, votes in house_votes.items():
                house_total += votes

            def deltaFor(house_party, pres_party):
                
                house_percent = house_votes.get(house_party,0) / house_total
                pres_percent = pres_votes.get(pres_party,0) / pres_total
                print pres_total, pres_percent, house_total, house_percent
                return abs(house_percent - pres_percent)

            if house_rep:
                delta = deltaFor('rep', 'dem')
                color = (255,0,0)
            else:
                delta = deltaFor('dem', 'rep')
                color = (0,0,255)
            pixels[x,y] = (
                pixels[x,y][0] + int(color[0] * delta),
                pixels[x,y][1],
                pixels[x,y][2] + int(color[2] * delta),
            )

    writeImage(img, BLOCKS_PRES_HOUSE_DIFF_IMAGE)


drawGroups()
drawBlocks()
drawDistricts()
drawDistricts(district_key='b_district')
drawBlockHousePresidentDelta()

drawCurrentVotes(False, key='house')
drawCurrentVotes(True, key='president')
drawCurrentVotes(True, key='senate')

