from attackcti import attack_client
from pandas import *
from pandas.io.json import json_normalize
import numpy as np
import altair as alt
import itertools

alt.renderers.enable('altair_viewer')
lift = attack_client()

all_techniques = lift.get_techniques(stix_format=False)
techniques_normalized = json_normalize(all_techniques)

techniques = techniques_normalized.reindex(['matrix','platform','tactic','technique','technique_id','data_sources'], axis=1)
techniques_with_data_sources=techniques[techniques.data_sources.notnull()].reset_index(drop=True)

techniques_data_source=techniques_with_data_sources
attributes_3 = ['data_sources']

for a in attributes_3:
    s = techniques_data_source.apply(lambda x: pandas.Series(x[a]),axis=1).stack().reset_index(level=1, drop=True)
    s.name = a
    techniques_data_source = techniques_data_source.drop(a, axis=1).join(s).reset_index(drop=True)

techniques_data_source_2 = techniques_data_source.reindex(['matrix','platform','tactic','technique','technique_id','data_sources'], axis=1)
techniques_data_source_3 = techniques_data_source_2.replace(['Process monitoring','Application logs'],['Process Monitoring','Application Logs'])
data_source_distribution = pandas.DataFrame({
    'Data Source': list(techniques_data_source_3.groupby(['data_sources'])['data_sources'].count().keys()),
    'Count of Techniques': techniques_data_source_3.groupby(['data_sources'])['data_sources'].count().tolist()})
bars = alt.Chart(data_source_distribution,width=800,height=300).mark_bar().encode(x ='Data Source',y='Count of Techniques',color='Data Source').properties(width=1200)
bars.show()
