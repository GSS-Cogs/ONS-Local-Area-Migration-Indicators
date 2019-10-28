# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.4'
#       jupytext_version: 1.2.4
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# Local area migration indicators UK: Migration Flows

# +
from gssutils import *

scraper = Scraper('https://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/' \
                  'migrationwithintheuk/datasets/localareamigrationindicatorsunitedkingdom')
scraper
# -

#sheets = scraper.distribution().as_databaker()
#tab = [t for t in sheets if t.name == 'Migration Flows'][0]
tab = next(t for t in scraper.distributions[0].as_databaker() if t.name == 'Migration Flows')

MigrationArea = tab.filter('Area Code').fill(DOWN).is_not_blank().is_not_whitespace()
Area = tab.filter('Area Name').fill(DOWN).is_not_blank().is_not_whitespace()
Period = tab.filter(contains_string('Mid-')).is_not_number() - tab.filter(contains_string('Population'))
migration = tab.filter(contains_string('Migration')).is_not_number()
migration = HDim(migration,'Migration',CLOSEST,LEFT)
migration.AddCellValueOverride('Internal Migration\n (within UK)', 'Internal Migration (within UK)')
flow = tab.filter(contains_string('Inflow')) | tab.filter(contains_string('Outflow'))
obs = tab.same_row(MigrationArea) - Area - MigrationArea 
obs = obs - tab.filter(contains_string('Population')).fill(DOWN)

Dimensions = [
            HDim(Period,'Mid Year',CLOSEST,LEFT),
            HDim(MigrationArea,'Geography', DIRECTLY, LEFT),
            migration,
            HDim(flow,'Flow',DIRECTLY,ABOVE),
            HDimConst('Measure Type', 'Count'),
            HDimConst('Unit','People')
            ]
c1 = ConversionSegment(obs, Dimensions, processTIMEUNIT=True)
savepreviewhtml(c1)

tidy = c1.topandas()

# We can drop the mid year population estimates, as these form a separate dataset.

tidy = tidy[~tidy['Migration'].str.match('^Mid-[0-9]{4} Population Estimate$')].copy()

tidy['OBS'].replace('', pd.np.nan, inplace=True)
tidy.dropna(subset=['OBS'], inplace=True)
tidy['Value'] = tidy['OBS'].astype(int)

tidy['Mid Year'] = tidy['Mid Year'].str.replace(r'^Mid-([0-9]{4}) to Mid-([0-9]{4})\s*$',
                                                      lambda m: f"{m.group(1)}-06-30T00:00:00/P1Y")

tidy = tidy[['Mid Year','Geography','Migration','Flow','Measure Type','Value','Unit']]

# +
from pathlib import Path
destinationFolder = Path('out')
destinationFolder.mkdir(exist_ok=True, parents=True)

#tidy.to_csv(destinationFolder / ('migrationflows.csv'), index = False)
tidy.to_csv(destinationFolder / ('observations.csv'), index = False)

# +
scraper.dataset.family = 'migration'
scraper.dataset.license = 'http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/'

with open(destinationFolder / 'dataset.trig', 'wb') as metadata:
    metadata.write(scraper.generate_trig())
# -

tidy


