#python IPPS EDA
#import packages
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style = "darkgrid")
import plotly as py
import plotly.graph_objs as go

#read in csv
ipps = pd.read_csv("/Users/connorduplessis/github/PythonMedicareAnalysis/IPPS.csv")
#drop columns not needed for this analysis
ipps2 = ipps.drop(['Provider Id', 'Provider Name', 'Provider Street Address', 'Provider City', 'Provider Zip Code', 'Hospital Referral Region Description', ' Total Discharges ', ' Average Total Payments ', 'Average Medicare Payments'], axis=1)
#calculate average amount billed for each state at each DRG
ipps3 = ipps2.groupby(['DRG Definition', 'Provider State'])[' Average Covered Charges '].mean().reset_index(name = 'Average Billing')
#rank each state for affordability for each DRG
staterank = ipps3.groupby(['DRG Definition'])['Average Billing'].rank(axis = 'columns').reset_index(name = 'DRG Rank')
#add rankings into dataset
ipps3['Rank'] = staterank['DRG Rank']
#calculate each states average ranking
ipps4 = ipps3.groupby(['Provider State'])['Rank'].mean().reset_index(name = 'Average DRG Rank').sort_values('Average DRG Rank', ascending = False)

#population data pulled from http://worldpopulationreview.com/states/
pop = pd.read_csv("/Users/connorduplessis/github/PythonMedicareAnalysis/population2.csv")
#sort data alphabetically to read in with population
ipps4 = ipps4.sort_values('Provider State').reset_index()
pop = pop.sort_values('State').reset_index()
newcol = pop['Population']
#merge population numbers to dataset
ipps5 = ipps4.assign(Population = newcol).sort_values('Population')
ipps5
#It seems like the states with larger populations are higher on the rankings, lets see how correlated they are
corplot = sns.regplot(x = 'Average DRG Rank', y = 'Population', data = ipps5)
correlation = ipps5[['Average DRG Rank','Population']].corr()
correlation
#with only 44% correlation, population is not a good indicator of medicare claims Charges
#What about certain regions of the country being more or less expensive than others? Let's take a look

mapdata = [ dict(
        type='choropleth',
        locations = ipps5['Provider State'],
        z = ipps5['Average DRG Rank'].astype(float),
        locationmode = 'USA-states',
        marker = dict(
            line = dict (
                color = 'rgb(255,255,255)',
                width = 2
            ) ),
        colorbar = dict(
            title = "Average Rank")
        ) ]

layout = dict(
        title = 'Average Medicare Claims Ranking<br>(Hover for breakdown)',
        geo = dict(
            scope='usa',
            projection=dict( type='albers usa' ),
            showlakes = True,
            lakecolor = 'rgb(255, 255, 255)'),
             )

fig = dict( data=mapdata, layout=layout )
py.offline.plot( fig, filename='statemap.html' )

#From this map it doesn't appear that any particular region of the country is more or less expensive than others. More analysis needed
