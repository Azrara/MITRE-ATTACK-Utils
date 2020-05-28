##########Based on ATTACK PYTHON CLIENT notebooks : https://github.com/hunters-forge/ATTACK-Python-Client/blob/master/notebooks/ATT%26CK_DataSources.ipynb
from attackcti import attack_client
from pandas import *
from pandas.io.json import json_normalize
import altair as alt
import argparse

def subs(l):
    res = []
    for i in range(1, len(l) + 1):
        for combo in itertools.combinations(l, i):
            res.append(list(combo))
    return res

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

parser = argparse.ArgumentParser("Relations between ATT&CK techniques and data sources")
parser.add_argument("--visualization","-v",type=str,help="Specify a visualisation option : grouping, count or subset",required=True)
args = parser.parse_args()
option = args.visualization

################Grouping techniques with data sources by data source###########################################
if option == "grouping":
    data_source_distribution = pandas.DataFrame({
        'Data Source': list(techniques_data_source_3.groupby(['data_sources'])['data_sources'].count().keys()),
        'Count of Techniques': techniques_data_source_3.groupby(['data_sources'])['data_sources'].count().tolist()})
    bars = alt.Chart(data_source_distribution,width=800,height=300).mark_bar().encode(x ='Data Source',y='Count of Techniques',color='Data Source').properties(width=1200)
    bars.show()

elif option == "count":
    data_source_distribution_2 = pandas.DataFrame({
        'Techniques': list(techniques_data_source_3.groupby(['technique'])['technique'].count().keys()),
        'Count of Data Sources': techniques_data_source_3.groupby(['technique'])['technique'].count().tolist()})
    data_source_distribution_3 = pandas.DataFrame({
        'Number of Data Sources': list(data_source_distribution_2.groupby(['Count of Data Sources'])['Count of Data Sources'].count().keys()),
        'Count of Techniques': data_source_distribution_2.groupby(['Count of Data Sources'])['Count of Data Sources'].count().tolist()})
    bars = alt.Chart(data_source_distribution_3).mark_bar().encode(x ='Number of Data Sources',y='Count of Techniques').properties(width=500)
    bars.show()

elif option =="subset":
    df = techniques_with_data_sources[['data_sources']]
    for index, row in df.iterrows():
        row["data_sources"]=[x.lower() for x in row["data_sources"]]
        row["data_sources"].sort()
    df['subsets']=df['data_sources'].apply(subs)
    techniques_with_data_sources_preview = df
    
    attributes_4 = ['subsets']
    for a in attributes_4:
        s = techniques_with_data_sources_preview.apply(lambda x: pandas.Series(x[a]),axis=1).stack().reset_index(level=1, drop=True)
        s.name = a
        techniques_with_data_sources_preview = techniques_with_data_sources_preview.drop(a, axis=1).join(s).reset_index(drop=True)
    
    techniques_with_data_sources_subsets = techniques_with_data_sources_preview.reindex(['data_sources','subsets'], axis=1)
    techniques_with_data_sources_subsets['subsets_name']=techniques_with_data_sources_subsets['subsets'].apply(lambda x: ','.join(map(str, x)))
    techniques_with_data_sources_subsets['subsets_number_elements']=techniques_with_data_sources_subsets['subsets'].str.len()
    techniques_with_data_sources_subsets['number_data_sources_per_technique']=techniques_with_data_sources_subsets['data_sources'].str.len()
    
    subsets = techniques_with_data_sources_subsets
    subsets_ok=subsets[subsets.subsets_number_elements != 1]
    subsets_graph = subsets_ok.groupby(['subsets_name'])['subsets_name'].count().to_frame(name='subsets_count').sort_values(by='subsets_count',ascending=False)[0:15]
    subsets_graph_2 = pandas.DataFrame({
        'Data Sources': list(subsets_graph.index),
        'Count of Techniques': subsets_graph['subsets_count'].tolist()})
    bars = alt.Chart(subsets_graph_2).mark_bar().encode(x ='Data Sources', y ='Count of Techniques', color='Data Sources').properties(width=500)
    bars.show()

else:
    print("Option does not exist")
    exit()
###############################################################################################################
