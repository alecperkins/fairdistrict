from base import db, printCount




def findMaxPopCounty():
    print 'finding county max population'
    # Find the total population of each county (for distributing the votes proportionally)
    for county in db.counties.find():
        pop_list = [int(g.get('population',0)) for g in db.groups.find({
            "county_fips": county.get('fips')
        })]
        county['population'] = sum(pop_list)
        db.counties.save(county)
        print county.get('name')


def distributeVotesToGroupsAndBlocks():
    # Distribute the votes amongst the block groups, by share of county population
    for county in db.counties.find():
        c_groups = db.groups.find({
            "county_fips": county['fips']
        })
        print c_groups.count(), 'block groups in county', county.get('name'), ', population:', county.get('population')

        c_total_pop = county.get('population')

        count = 0
        for group in c_groups:
            count += 1
            ratio = group['population'] / county.get('population')
            group['votes'] = {
                'president': {},
                'senate': {},
                'house': {}
            }

            for office in group['votes']:
                for party, votes in county.get('votes')[office].items():
                    group['votes'][office][party] = votes * ratio
            db.groups.save(group)

            group_blocks = db.blocks.find({
                'state_fips': group.get('state_fips'),
                'county_fips': group.get('county_fips'),
                'tract': group.get('tract'),
                'group': group.get('group'),
            })
            num_blocks = group_blocks.count()
            # print num_blocks
            for block in group_blocks:
                block['group_lat'] = group.get('lat')
                block['group_lon'] = group.get('lon')
                block['votes'] = {
                    'president': {},
                    'senate': {},
                    'house': {}
                }
                for office in group['votes']:
                    for party, votes in county.get('votes')[office].items():
                        block['votes'][office][party] = votes * ratio / num_blocks
                db.blocks.save(block)

        print count, 'groups updated'


def assignDistrictsToGroups():
    total_groups = db.groups.count()
    count = 0
    has_multi = []
    for group in db.groups.find():
        count += 1
        districts = {}
        for b in db.blocks.find({
            'state_fips': group.get('state_fips'),
            'county_fips': group.get('county_fips'),
            'tract': group.get('tract'),
            'group': group.get('group'),
        }):
            if not b.get('district') in districts:
                districts[b.get('district')] = 0
            districts[b.get('district')] += 1
        print total_groups - count, districts
        if len(districts) > 1:
            has_multi.append(group)

    print len(has_multi)

findMaxPopCounty()
distributeVotesToGroupsAndBlocks()
assignDistrictsToGroups()


