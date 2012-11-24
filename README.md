# Un-gerrymander

This set of scripts recalculates the 2012 Pennsylvania election for House of Representatives using alternative districts. Using the algorithmically derived districts from [B-Districting](http://bdistricting.com/2010/) that are purely population-based, it calculates an outcome of 9 Republican representatives and 9 Democratic representatives. The actual outcome was 13 Rep. and 5 Dem., even though the Democratic candidates received *over 70,000 more votes* as a whole.

The 2012 election looked like this:

![Image of the 2012 House election in Pennsylvania from NYTimes.com](https://raw.github.com/alecperkins/un-gerrymander/master/images/PA_2012_house_nytimes.png)

When an election using the population-based districting looked like this:

![Image of votes by census block, according to BDistricting districts](https://raw.github.com/alecperkins/un-gerrymander/master/images/PA_2012_House-bdistricting2010.png)



## Usage

(This script requires some familiarity with Python and MongoDB.)

First, install the requirements and prepare the database:

1. `pip install -r requirements.txt`
2. Start an instance of [MongoDB](http://www.mongodb.org/), which stores the processed data

Then, load and process the data:

1. Unzip `data.zip`, unpacking the `/data` directory
2. Run `python load.py` to load the data from `/data` into the database
3. Run `python compute.py` to execute various manipulations of the data, including distributing the votes to the blocks

Next, generate some visualizations with `python visualize.py`. This will create images of votes, like the one above. It also will calculate and display the results of an election using the alternate districts.



## About

### Why

In the 2012 general election for House of Representatives, voters in Pennsylvania cast 2,722,560 votes for Democratic party candidates, and 2,651,901  for Republican party candidates. However, the end result in representation was 13 Republican representatives to 5 Democratic representatives. The [national picture](http://www.ballot-access.org/2012/11/12/only-four-u-s-house-elections-in-the-last-hundred-years-gave-one-party-a-house-majority-even-though-the-other-major-party-polled-more-votes-for-u-s-house/) wasn't much different.

Pennsylvania, like [many states](http://rangevoting.org/GerryGal.html), has some funny looking districts. The cause is generally [gerrymandering](http://en.wikipedia.org/wiki/Gerrymandering), the practice of manipulating district shapes to achieve an electoral outcome. The question is, how much does this manipulation impact the representation? The disconnect between overall party votes and elected representative parties suggests quite a bit.

There are several projects that attempt redistricting using algorithmic, automated approaches that are purely population based, instead of the manual, corruptable approaches currently used.

* [B-Districting](http://bdistricting.com/2010/)
* [RangeVoting Splitline districts](http://rangevoting.org/SplitLR.html)

There are also some neat tools for exploring redistricting, like  [District Builder](http://www.districtbuilder.org/).

Because voting tends to be regional, the factor that makes gerrymandering possible, the way to measure the effect of gerrymandering, and redistricting in different ways, is proportion of elected parties to votes. The goal isn't proportional representation, but rather reducing the bias toward a particular political party based on deliberately manipulated district shapes.

### How

Take votes to each party by county, distribute those votes to the census blocks that make up the county by their share of the population, then recalculate the elections using districts calculated by [bdistricting.com](http://bdistricting.com).

The assumption is that people in one block would vote for the same party if the block is moved to a new district (and new contest with different candidates). There are definitely cases where people vote for the candidate against the party. Scraping the vote data from the state website pulled votes for all contests, and a few counties did vote differently for president versus house, in terms of party. However, this difference was minimal.

### Flaws

As mentioned before, this method ignores the realities of the candidates, and treats votes as for parties, not candidates. It also is not completely accurate, as the most precise vote information used is county-level. Recalculating the election using current districts gets two close contests wrong (but just barely). Block-level would be ideal, but is impossible to get. Precinct-level, which is then distributed to blocks, is the next best thing, but compiling and structuring all that data is a daunting challenge. County websites are miserable, and the precinct data, if at all available, is not provided in a standard format.



## TODOs

### Accuracy

Short of getting precinct-level data, one possible method to explore alleviating the accuracy problem would be to distribute the votes by original district as well, and use the difference between the district-level votes and the county-level votes to adjust the votes in each block. The Department of State will have the more precise data available as early as January (by CD for 10$ — how quaint).

Another source of inaccuracy is turnout. Voter turnout in districts safe for one party may be lower. The precinct data has turnout information, so adjusting for turnout in each area may yield different results.

[**Sample precinct data for Allegheny County**](http://www.alleghenycounty.us/elect/201211gen/el30.htm)

Experimenting with some of this data:

[![Image of the 2012 House election in Allegheny County by precinct](https://raw.github.com/alecperkins/un-gerrymander/master/images/PA_Allegheny_county_precincts.png)](https://tiles.mapbox.com/alecperkins/map/blocks)




### Alternate districts

It would be neat to try this with different districts, such as the RangeVoting Splitline districts. This will require mapping the districts onto the census blocks. This shouldn't be too difficult, since the block groups have coordinate information, and MongoDB supports geospatial queries.

### Country-wide

It would be even more interesting to see this recalculation on a national level, since Pennsylvania is hardly alone in gerrymandered districts. This requires getting vote data on a county level.

### Improved visualization

The images don't show the district borders. Adding in that sort of information about the districts would be helpful (and goes hand-in-hand with alternate districts that are not census block-based).

[TileMill](http://mapbox.com/tilemill/) is really helpful for this sort of thing.


## Census Blocks

[Blocks](http://en.wikipedia.org/wiki/Census_block) are identified using a 15-digit number, looking something like `420010301011000`.

Format: `AABBBCCCCCCDDDD`

* AA - state [FIPS](http://en.wikipedia.org/wiki/Federal_Information_Processing_Standard_state_code)
* BBB - county [FIPS](http://en.wikipedia.org/wiki/FIPS_county_code)
* CCCCCC - [tract](http://en.wikipedia.org/wiki/Census_tract)
* DDDD - tabulation number

The first digit of the tabulation number is the block's [group number](http://en.wikipedia.org/wiki/Census_block_group). The block with ID `42001030101100` has a group number `1` and is in block group `42001030101`.



## Data Files

A set of files that describing each block, its location, and its district information. Most are downloaded from [census.gov](http://www.census.gov).

### `42_PA_CD113.txt`

Assigns census blocks to Congressional districts for the 113th Congress.

    BLOCKID,CD113
    420010301011000,04
    420010301011001,04
    …


### `CenPop2012_Mean_BG42.txt`

Lists the census block groups, their populations, and centers in latitude and longitude. Groups are identified using a number that's the same as the blocks, but with the group number instead of the tabulation number.

    STATEFP,COUNTYFP,TRACTCE,BLKGRPCE,POPULATION,LATITUDE,LONGITUDE
    42,001,030101,1,2580,+40.015805,-077.081172
    42,001,030102,1,1136,+39.940818,-076.995904
    …


### `PA_Congress.csv`

The B-Districting districts, assigned to census blocks.

    420010308003003,9
    420010308003004,9
    …

Downloaded from [here](http://bdistricting.com/2010/PA_Congress/).


### `PA_county_fips.csv`

A list of Pennsylvania counties and their corresponding [FIPS code](http://en.wikipedia.org/wiki/FIPS_county_code).

    Adams,001
    Allegheny,003
    …

### `2012_PA_county_data.json`

Generated from county vote information scraped from the Pennsylvania [election returns site](http://www.electionreturns.state.pa.us/ElectionsInformation.aspx).

    [
        {
            "raw": {…},             # The raw data from the site, by contests.
            "votes": {              # The votes organized by party.
                "senate": {
                    "rep": 25209,
                    "dem": 15582
                },
                "president": {
                    "rep": 26490,
                    "dem": 14893
                },
                "house": {
                    "rep": 27142,
                    "dem": 11955
                }
            },
            "fips": "001",
            "id": 1,
            "name": "Adams"
        },
        …
    ]



## More information

* [Census products](http://www.census.gov/population/www/cen2010/glance/index.html)
* [TIGER shapes](http://www.census.gov/geo/www/tiger/tgrshp2010/tgrshp2010.html) ([ftp - organized by county](ftp://ftp2.census.gov/geo/pvs/tiger2010st/42_Pennsylvania/))
* [Census Block assignment files](https://www.census.gov/geo/www/2010census/baf/baf_main.html)
* [TileMill](http://mapbox.com/tilemill/) - for making visualizations
* [pyshp](http://code.google.com/p/pyshp/) - Python shapefile library
* [Kartograph](http://kartograph.org/) - Python and JavaScript mapping libraries
* [Using MongoDB to store geographic data](http://www.paolocorti.net/2009/12/06/using-mongodb-to-store-geographic-data/)


## Authors

* [Alec Perkins](http://github.com/alecperkins)


## License

Unlicensed aka Public Domain. See [/UNLICENSE](https://github.com/alecperkins/un-gerrymander/blob/master/UNLICENSE) for more information.

