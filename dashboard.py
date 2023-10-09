import streamlit as st
import pandas as pd
import numpy as np

from scipy import stats
import math

import matplotlib as mpl

import matplotlib.colors as mcolors

import matplotlib.pyplot as plt


plt.rcParams['figure.dpi'] = 600

lfont = {'fontname':'Bahnschrift'}
hfont = {'fontname':'Rockwell Nova'}



my_cmap = mpl.colors.LinearSegmentedColormap.from_list("",['#e0a4c0','white','#58becb'])
my_dullmap = mpl.colors.LinearSegmentedColormap.from_list("",['#d7d4c2','#bbb496','#a0976d'])
norm = mpl.colors.Normalize(vmin=0, vmax=100,clip = True)
mapper = plt.cm.ScalarMappable(norm=norm, cmap=my_cmap)
mapper2 = plt.cm.ScalarMappable(norm=norm, cmap=my_dullmap)
        
st.header('Percentile Dashboard App')
st.write('by @analyticswba')

st.write("\n\n\nA tool to show performance levels for any outfield player in England's top four leagues over the past 3 seasons.\nData up to date as at 16/05/23.")
st.write('\n\nPlease set the parameters and click run to see your visualisation.\n\nIt is recommended to set minimum number of 90s to at least a third /of the bar.')

season  = st.selectbox('Select season', options = ['2023/24','2022/23','2021/22','2020/21'])

league  = st.selectbox('Select league', options = ['Premier League','Championship','League One','League Two'])

position  = st.selectbox('Select position', options = ['Centre-back','Full-back','Centre-midfielder','Attacking-midfielder',
            'Winger','Striker'])


if league.lower() == 'championship':
	file_part_1 = 'Champ'
elif league.lower() == 'premier league':
	file_part_1 = 'PL'
elif league.lower() == 'top 5 eu leagues':
	file_part_1 = 'Top 5'
elif league.lower() == 'league one':
	file_part_1 = 'L1'
elif league.lower() == 'league two':
	file_part_1 = 'L2'

if position.lower() =='centre-midfielder':
	file_part_2 = 'CM'
elif position.lower() == 'winger':
	file_part_2 = 'W'
elif position.lower() == 'striker':
	file_part_2 = 'ST'
elif position.lower() == 'centre-back':
	file_part_2 = 'CB'
elif position.lower() == 'full-back':
	file_part_2 = 'FB'
elif position.lower() == 'attacking-midfielder':
	file_part_2 = 'AM'

file_part_3 = season[-2:]

file = file_part_1 + ' '+file_part_2+ ' '+file_part_3

df = pd.read_csv(file+'.csv')

narrative = pd.read_csv('metric narrative.csv')




df.fillna(0, inplace=True)

df['90s'] = df['Minutes played']/90
df['Shots'] = df['Shots'] - (df['Direct free kicks per 90'] * df['90s'])
df['Shots per 90'] = df['Shots per 90'] - df['Direct free kicks per 90']
df['NPxG'] = (df['xG'] - (df['Penalties taken']*0.76)) - (df['Direct free kicks per 90']*df['90s']*0.06)
df['NPxG per 90'] = (df['NPxG'] / df['90s'])
df['NPxG/ shot'] = df['NPxG'] / df['Shots']
df['Shots/ touch'] = df['Shots per 90'] / df['Touches in box per 90']
df['NPxG/ touch'] = df['NPxG per 90'] / df['Touches in box per 90']
df['Head goals, %'] = df['Head goals'] / df['Non-penalty goals']*100
df['Smart passes per 100 passes'] = df['Smart passes per 90'] / df['Passes per 90']*100
df['Accurate passes per 90'] = df['Passes per 90'] * df['Accurate passes, %']/100

df['NP Goals'] = df['Goals'] - round(df['Penalties taken'] * (df['Penalty conversion, %']/100),0)

df['FKs per 90'] = df['Free kicks per 90'] - df['Direct free kicks per 90']
df['xA per 100 passes'] = (df['xA per 90'] - (df['FKs per 90']*0.03229416)  - (df['Corners per 90']*0.02223348))/ df['Accurate passes per 90']*100

#df['xA per 100 passes'] = df['xA per 90'] / df['Accurate passes per 90']*100
df['Progressive passes per 100 passes'] = df['Progressive passes per 90'] / df['Passes per 90']*100
df['Bounce passes, %'] = (df['Passes per 90'] - (df['Forward passes per 90']+df['Lateral passes per 90']))/df['Passes per 90']*100
df['Finishing, %'] = df['Non-penalty goals per 90'] / df['NPxG per 90']*100

df['Lateral passes per 90'] = df['Passes per 90'] - df['Forward passes per 90'] - df['Back passes per 90']
df['Back pass, %'] = round(df['Back passes per 90'] / df['Passes per 90'] *100,1)
df['Lateral pass, %'] = round(df['Lateral passes per 90'] / df['Passes per 90'] *100,1)
df['Forward pass, %'] = round(df['Forward passes per 90'] / df['Passes per 90'] *100,1)

df['Short / medium pass, %'] = round(df['Short / medium passes per 90'] / df['Passes per 90']*100,1)
df['Long pass, %'] = round(df['Long passes per 90'] / df['Passes per 90']*100,1)

df['Crosses per 100 passes'] = df['Crosses per 90'] / df['Passes per 90'] * 100


df['Accurate crosses per 90'] = df['Crosses per 90'] * df['Accurate crosses, %'] / 100

df['Accurate passes to penalty area per 90'] = df['Passes to penalty area per 90'] * df['Accurate passes to penalty area, %'] / 100

df['Cross / pass to penalty area ratio'] = df['Crosses per 90'] / df['Passes to penalty area per 90']


max_nineties = df['90s'].max()
nineties_range = range(1,int(max_nineties)-1)
nineties = st.select_slider('Select minimum number of 90s',options = nineties_range)



df = df[df['90s']>=nineties].reset_index()
del df['index']

cols = list(df.columns)
del cols[0:21]
for col in cols:
    col_z = col + '_z'
    df[col_z] = (df[col] - df[col].mean())/df[col].std(ddof=0)
df = df.reset_index()
del df['index']

metrics  = list(df)
metrics = metrics[7:]
metrics.remove('Birth country')
metrics.remove('Passport country')
metrics.remove('Foot')
metrics.remove('Height')
metrics.remove('Weight')
metrics.remove('On loan')


for x in range(len(metrics)):
    metric = metrics[x]
    df[metric+' - raw'] = df[metric]
    df[metric] = df[metric].rank(pct=True)*100
    

player  = st.selectbox('Select player', options = df['Player'])

df_player = df[df['Player']==player].reset_index()
del df_player['index']


button = st.button('Run')

if button == True:

    st_offensive_metrics = ['NPxG per 90','Shots per 90','NPxG/ shot','Touches in box per 90','Shots/ touch','Offensive duels per 90',
                           'Offensive duels won, %']
    st_creative_metrics = ['xA per 90','xA per 100 passes','Dribbles per 90','Successful dribbles, %','Through passes per 90',
                            'Passes to penalty area per 90','Accurate passes to penalty area, %']
    st_defensive_metrics = ['Aerial duels per 90','Aerial duels won, %','Defensive duels per 90','Defensive duels won, %','PAdj Interceptions',
                           'PAdj Sliding tackles','Fouls per 90']
    st_passing_metrics = ['Passes per 90','Accurate passes, %','Progressive passes per 90','Accurate progressive passes, %',
                         'Passes to final third per 90','Accurate passes to final third, %','Crosses per 90','Accurate crosses, %']

    cm_passing_and_progression_metrics = ['Passes per 90','Accurate passes, %','Progressive passes per 100 passes','Accurate progressive passes, %',
                                       'Passes to final third per 90','Accurate passes to final third, %','Progressive runs per 90']

    cm_creative_and_offensive_metrics = ['xA per 90','xA per 100 passes','Through passes per 90','Passes to penalty area per 90',
                                       'Accurate passes to penalty area, %','NPxG per 90','Shots per 90','NPxG/ shot']
    cm_defensive_metrics = ['Aerial duels per 90','Aerial duels won, %','Defensive duels per 90','Defensive duels won, %','PAdj Interceptions',
                           'PAdj Sliding tackles','Shots blocked per 90','Fouls per 90']
    cm_pass_profile_metrics = ['Average pass length, m','Short / medium pass, %','Long pass, %','Back pass, %','Lateral pass, %',
                              'Forward pass, %']


    w_creative_metrics = ['xA per 90','xA per 100 passes','Crosses per 90','Crosses per 100 passes','Accurate crosses, %','Through passes per 90',
                           'Cross / pass to penalty area ratio','Dribbles per 90','Successful dribbles, %']

    w_offensive_metrics = ['NPxG per 90','Shots per 90','NPxG/ shot','Touches in box per 90','Shots/ touch','Offensive duels per 90',
                           'Offensive duels won, %']

    w_passing_and_progression_metrics = ['Passes per 90','Accurate passes, %','Progressive passes per 100 passes','Accurate progressive passes, %',
                                       'Passes to final third per 90','Accurate passes to final third, %','Progressive runs per 90']

    w_defensive_metrics = ['Aerial duels per 90','Aerial duels won, %','Defensive duels per 90','Defensive duels won, %','PAdj Interceptions',
                           'PAdj Sliding tackles','Shots blocked per 90','Fouls per 90']





    cb_defensive_metrics = ['Aerial duels per 90','Aerial duels won, %','Defensive duels per 90','Defensive duels won, %','PAdj Interceptions',
                           'PAdj Sliding tackles','Shots blocked per 90','Fouls per 90']

    cb_passing_and_progression_metrics = ['Passes per 90','Accurate passes, %','Progressive passes per 100 passes','Accurate progressive passes, %',
                                         'Passes to final third per 90','Accurate passes to final third, %','Progressive runs per 90']

    cb_offensive_and_creative_metrics = ['NPxG per 90','NPxG/ shot','xA per 90','Through passes per 90','Passes to penalty area per 90',
                                       'Accurate passes to penalty area, %','Dribbles per 90','Successful dribbles, %']

    cb_pass_profile_metrics = ['Average pass length, m','Short / medium pass, %','Long pass, %','Back pass, %','Lateral pass, %',
                              'Forward pass, %']



    fb_defensive_metrics = ['Aerial duels per 90','Aerial duels won, %','Defensive duels per 90','Defensive duels won, %','PAdj Interceptions',
                           'PAdj Sliding tackles','Shots blocked per 90','Fouls per 90']

    fb_passing_and_progression_metrics = ['Passes per 90','Accurate passes, %','Progressive passes per 100 passes','Accurate progressive passes, %',
                                       'Passes to final third per 90','Accurate passes to final third, %','Progressive runs per 90']

    fb_creative_and_offensive_metrics = ['xA per 90','xA per 100 passes','Crosses per 90','Crosses per 100 passes','Accurate crosses, %',
                           'Dribbles per 90','Successful dribbles, %','NPxG per 90','NPxG/ shot']

    fb_pass_profile_metrics = ['Average pass length, m','Short / medium pass, %','Long pass, %','Back pass, %','Lateral pass, %',
                              'Forward pass, %']


    am_creative_metrics = ['xA per 90','xA per 100 passes','Through passes per 90','Passes to penalty area per 90',
                        'Accurate passes to penalty area, %','Crosses per 90','Accurate crosses, %','Dribbles per 90','Successful dribbles, %']

    am_offensive_metrics = ['NPxG per 90','Shots per 90','NPxG/ shot','Touches in box per 90','Shots/ touch','Offensive duels per 90',
                           'Offensive duels won, %']

    am_passing_and_progression_metrics = ['Passes per 90','Accurate passes, %','Progressive passes per 100 passes','Accurate progressive passes, %',
                                       'Passes to final third per 90','Accurate passes to final third, %','Progressive runs per 90']

    am_pass_profile_metrics = ['Average pass length, m','Short / medium pass, %','Long pass, %','Back pass, %','Lateral pass, %',
                              'Forward pass, %']


    raw = ' - raw'



    if position.lower() =='striker':
        prefix = 'st'
        choice_1 = 'offensive'
        selected_metrics_1 = prefix+'_'+choice_1 + '_metrics'

        choice_2 = 'creative'
        selected_metrics_2 = prefix+'_'+choice_2 + '_metrics'

        choice_3 = 'defensive'
        selected_metrics_3 = prefix+'_'+choice_3 + '_metrics'

        choice_4 = 'passing'
        selected_metrics_4 = prefix+'_'+choice_4 + '_metrics'

        metric_x= 'Shots per 90 - raw'
        metric_y = 'NPxG per 90 - raw'

        metric_x_2 = 'Passes per 90 - raw'
        metric_y_2 = 'Aerial duels per 90 - raw'
        print('done striker')
        

    elif position.lower() =='centre-midfielder':
        prefix = 'cm'
        choice_1 = 'passing_and_progression'
        selected_metrics_1 = prefix+'_'+choice_1 + '_metrics'

        choice_2 = 'creative_and_offensive'
        selected_metrics_2 = prefix+'_'+choice_2 + '_metrics'

        choice_3 = 'defensive'
        selected_metrics_3 = prefix+'_'+choice_3 + '_metrics'

        choice_4 = 'pass_profile'
        selected_metrics_4 = prefix+'_'+choice_4 + '_metrics'

        metric_x= 'Progressive passes per 90 - raw'
        metric_y = 'Progressive runs per 90 - raw'

        metric_x_2 = 'Successful defensive actions per 90 - raw'
        metric_y_2 = 'NPxG per 90 - raw'
        print('done2')
         

    elif position.lower() =='winger':
        prefix = 'w'
        choice_1 = 'creative'
        selected_metrics_1 = prefix+'_'+choice_1 + '_metrics'

        choice_2 = 'offensive'
        selected_metrics_2 = prefix+'_'+choice_2 + '_metrics'

        choice_3 = 'passing_and_progression'
        selected_metrics_3 = prefix+'_'+choice_3 + '_metrics'

        choice_4 = 'defensive'
        selected_metrics_4 = prefix+'_'+choice_4 + '_metrics'

        metric_x= 'NPxG per 90 - raw'
        metric_y = 'xA per 90 - raw'

        metric_x_2 = 'Cross / pass to penalty area ratio - raw'
        metric_y_2 = 'Dribbles per 90'
        print('done3')

    elif position.lower() =='centre-back':
        prefix = 'cb'
        choice_1 = 'defensive'
        selected_metrics_1 = prefix+'_'+choice_1 + '_metrics'

        choice_2 = 'passing_and_progression'
        selected_metrics_2 = prefix+'_'+choice_2 + '_metrics'

        choice_3 = 'offensive_and_creative'
        selected_metrics_3 = prefix+'_'+choice_3 + '_metrics'

        choice_4 = 'pass_profile'
        selected_metrics_4 = prefix+'_'+choice_4 + '_metrics'

        metric_x= 'Defensive duels won, % - raw'
        metric_y = 'Aerial duels won, % - raw'

        metric_x_2 = 'Progressive passes per 90 - raw'
        metric_y_2 = 'Progressive runs per 90 - raw'
        print('done5')
        

    elif position.lower() =='full-back':
        prefix = 'fb'
        choice_1 = 'defensive'
        selected_metrics_1 = prefix+'_'+choice_1 + '_metrics'

        choice_2 = 'passing_and_progression'
        selected_metrics_2 = prefix+'_'+choice_2 + '_metrics'

        choice_3 = 'creative_and_offensive'
        selected_metrics_3 = prefix+'_'+choice_3 + '_metrics'

        choice_4 = 'pass_profile'
        selected_metrics_4 = prefix+'_'+choice_4 + '_metrics'

        metric_x= 'Defensive duels won, % - raw'
        metric_y = 'Aerial duels won, % - raw'

        metric_x_2 = 'Progressive passes per 90 - raw'
        metric_y_2 = 'xA per 90 - raw'
        print('done6')
        
        
    elif position.lower() =='attacking-midfielder':
        prefix = 'am'
        choice_1 = 'creative'
        selected_metrics_1 = prefix+'_'+choice_1 + '_metrics'

        choice_2 = 'offensive'
        selected_metrics_2 = prefix+'_'+choice_2 + '_metrics'

        choice_3 = 'passing_and_progression'
        selected_metrics_3 = prefix+'_'+choice_3 + '_metrics'

        choice_4 = 'pass_profile'
        selected_metrics_4 = prefix+'_'+choice_4 + '_metrics'

        metric_x= 'NPxG per 90 - raw'
        metric_y = 'Shots per 90 - raw'

        metric_x_2 = 'xA per 90 - raw'
        metric_y_2 = 'Dribbles per 90 - raw'
        print('done7')
        
        

    else:
        print('failed after first')



    df_selected_metrics_1 = df_player[eval(selected_metrics_1)]

    df_selected_metrics_1 = df_selected_metrics_1.T
    df_selected_metrics_1 = df_selected_metrics_1.reset_index()
    df_selected_metrics_1.columns = ['metric','percentile']

    df_selected_metrics_1.sort_index(ascending=False, ignore_index=True, inplace=True)
                          
    df_selected_metrics_1['colour'] = ' '

    df_selected_metrics_1['colour'] = df_selected_metrics_1['percentile'].apply(lambda x: mcolors.to_hex(mapper.to_rgba(x)))




    selected_metrics_raw_1 = [x + raw for x in eval(selected_metrics_1)]


    df_selected_metrics_raw_1 = df_player[selected_metrics_raw_1]

    df_selected_metrics_raw_1.columns = df_selected_metrics_raw_1.columns.str.rstrip(" - raw")

    df_selected_metrics_raw_1 = df_selected_metrics_raw_1.T
    df_selected_metrics_raw_1 = df_selected_metrics_raw_1.reset_index()
    df_selected_metrics_raw_1.columns = ['metric','raw']

    df_selected_metrics_raw_1.sort_index(ascending=False, ignore_index=True, inplace=True)


    df_selected_metrics_1 = df_selected_metrics_1.merge(df_selected_metrics_raw_1,on='metric',how='left')


    #gm stands for goal metrics
    df_selected_metrics_2 = df_player[eval(selected_metrics_2)]

    df_selected_metrics_2 = df_selected_metrics_2.T
    df_selected_metrics_2 = df_selected_metrics_2.reset_index()
    df_selected_metrics_2.columns = ['metric','percentile']

    df_selected_metrics_2.sort_index(ascending=False, ignore_index=True, inplace=True)
                          
    df_selected_metrics_2['colour'] = ' '

    df_selected_metrics_2['colour'] = df_selected_metrics_2['percentile'].apply(lambda x: mcolors.to_hex(mapper.to_rgba(x)))



    #gr stands for goal raw numbers

    selected_metrics_raw_2 = [x + raw for x in eval(selected_metrics_2)]


    df_selected_metrics_raw_2 = df_player[selected_metrics_raw_2]

    df_selected_metrics_raw_2.columns = df_selected_metrics_raw_2.columns.str.rstrip(" - raw")

    df_selected_metrics_raw_2 = df_selected_metrics_raw_2.T
    df_selected_metrics_raw_2 = df_selected_metrics_raw_2.reset_index()
    df_selected_metrics_raw_2.columns = ['metric','raw']

    df_selected_metrics_raw_2.sort_index(ascending=False, ignore_index=True, inplace=True)


    df_selected_metrics_2 = df_selected_metrics_2.merge(df_selected_metrics_raw_2,on='metric',how='left')

    df_selected_metrics_3 = df_player[eval(selected_metrics_3)]

    df_selected_metrics_3 = df_selected_metrics_3.T
    df_selected_metrics_3 = df_selected_metrics_3.reset_index()
    df_selected_metrics_3.columns = ['metric','percentile']

    df_selected_metrics_3.sort_index(ascending=False, ignore_index=True, inplace=True)
                          
    df_selected_metrics_3['colour'] = ' '

    df_selected_metrics_3['colour'] = df_selected_metrics_3['percentile'].apply(lambda x: mcolors.to_hex(mapper.to_rgba(x)))



    #gr stands for goal raw numbers

    selected_metrics_raw_3 = [x + raw for x in eval(selected_metrics_3)]


    df_selected_metrics_raw_3 = df_player[selected_metrics_raw_3]

    df_selected_metrics_raw_3.columns = df_selected_metrics_raw_3.columns.str.rstrip(" - raw")

    df_selected_metrics_raw_3 = df_selected_metrics_raw_3.T
    df_selected_metrics_raw_3 = df_selected_metrics_raw_3.reset_index()
    df_selected_metrics_raw_3.columns = ['metric','raw']

    df_selected_metrics_raw_3.sort_index(ascending=False, ignore_index=True, inplace=True)


    df_selected_metrics_3 = df_selected_metrics_3.merge(df_selected_metrics_raw_3,on='metric',how='left')

    df_selected_metrics_4 = df_player[eval(selected_metrics_4)]

    df_selected_metrics_4 = df_selected_metrics_4.T
    df_selected_metrics_4 = df_selected_metrics_4.reset_index()
    df_selected_metrics_4.columns = ['metric','percentile']

    df_selected_metrics_4.sort_index(ascending=False, ignore_index=True, inplace=True)
                          
    df_selected_metrics_4['colour'] = ' '

    if selected_metrics_4 == prefix+'_pass_profile_metrics':
        df_selected_metrics_4['colour'] = df_selected_metrics_4['percentile'].apply(lambda x: mcolors.to_hex(mapper2.to_rgba(x)))
    else:
        df_selected_metrics_4['colour'] = df_selected_metrics_4['percentile'].apply(lambda x: mcolors.to_hex(mapper.to_rgba(x)))



    selected_metrics_raw_4 = [x + raw for x in eval(selected_metrics_4)]


    df_selected_metrics_raw_4 = df_player[selected_metrics_raw_4]

    df_selected_metrics_raw_4.columns = df_selected_metrics_raw_4.columns.str.rstrip(" - raw")

    df_selected_metrics_raw_4 = df_selected_metrics_raw_4.T
    df_selected_metrics_raw_4 = df_selected_metrics_raw_4.reset_index()
    df_selected_metrics_raw_4.columns = ['metric','raw']

    df_selected_metrics_raw_4.sort_index(ascending=False, ignore_index=True, inplace=True)


    df_selected_metrics_4 = df_selected_metrics_4.merge(df_selected_metrics_raw_4,on='metric',how='left')

    if position.lower() == 'striker':
        narrative = narrative[(narrative['strengths']!='blocking shots')&(narrative['strengths']!='defensive positioning')].reset_index()
        del narrative['index']
        
    elif position.lower() == 'attacking midfielder':
        narrative = narrative[(narrative['strengths']!='blocking shots')&(narrative['strengths']!='defensive positioning')].reset_index()
        del narrative['index'] 
        
    elif position.lower() == 'winger':
        narrative = narrative[(narrative['strengths']!='blocking shots')&(narrative['strengths']!='defensive positioning')].reset_index()
        del narrative['index'] 
        
    elif position.lower() == 'centre-midfielder':
        narrative = narrative[(narrative['strengths']!='link up play')&(narrative['strengths']!='defensive positioning')
                             &(narrative['strengths']!='finishing')].reset_index()
        del narrative['index']  

    elif position.lower() == 'full-back':
        narrative = narrative[(narrative['strengths']!='link up play')&(narrative['strengths']!='finishing')].reset_index()
        del narrative['index']  
        
    elif position.lower() == 'centre-back':
        narrative = narrative[(narrative['strengths']!='link up play')&(narrative['strengths']!='finishing')
                             &(narrative['strengths']!='dribbling')&(narrative['strengths']!='crossing')].reset_index()
        del narrative['index']  

    attributes = list(narrative['strengths'].unique())

    for x in range(len(attributes)):
        #adding eac attribute to df1 as 0s
        attribute = attributes[x]

        #getting the metrics for each attribute
        df_attributes = narrative
        df_attributes = df_attributes[df_attributes['strengths']==attribute].reset_index()
        del df_attributes['index']
        #setting each attribute to 0 so there's something to add the first metric to
        df[attribute] = 0
        for y in range(len(df_attributes)):
            #getting the metrics and weightings for each attribute
            metric = df_attributes['metrics'][y]
            weighting = df_attributes['weighting'][y]
            df[attribute] = df[attribute]+ (df[metric] * weighting)
            df[attribute] = df[attribute].rank(pct=True)*100

    df_strengths = df[df['Player']==player].reset_index()
    del df_strengths['index']

    df_strengths = df_strengths[attributes]


    df_strengths = df_strengths.T.reset_index()
    df_strengths.columns = ['Metric','Score']


    good_scores = df_strengths[df_strengths['Score']>=80].reset_index()
    del good_scores['index']

    bad_scores = df_strengths[df_strengths['Score']<=20].reset_index()
    del bad_scores['index'] 

    good_scores = good_scores.sort_values(by='Score',ascending=False).reset_index()
    del good_scores['index']

    bad_scores = bad_scores.sort_values(by='Score',ascending=True).reset_index()
    del bad_scores['index']



    good_list = good_scores['Metric'].unique()
    good = '\n'.join(good_list)

    bad_list = bad_scores['Metric'].unique()
    bad = '\n'.join(bad_list)


    mean_x = df[metric_x].mean()
    mean_y = df[metric_y].mean()

    median_x = df[metric_x].median()
    median_y = df[metric_y].median()

    min_x = df[metric_x].min()
    max_x = df[metric_x].max()

    min_y = df[metric_y].min()
    max_y = df[metric_y].max()

    label_x = metric_x.rstrip(" - raw")
    label_y = metric_y.rstrip(" - raw")

    title = label_y + ' & ' + label_x


    mean_x_2 = df[metric_x_2].mean()
    mean_y_2 = df[metric_y_2].mean()

    median_x_2 = df[metric_x_2].median()
    median_y_2 = df[metric_y_2].median()

    min_x_2 = df[metric_x_2].min()
    max_x_2 = df[metric_x_2].max()

    min_y_2 = df[metric_y_2].min()
    max_y_2 = df[metric_y_2].max()

    label_x_2 = metric_x_2.rstrip(" - raw")
    label_y_2 = metric_y_2.rstrip(" - raw")

    title_2 = label_y_2 + ' & ' + label_x_2


    style_rating = 98


    fig, ax = plt.subplots(3,2,figsize=(30,20))

    ax1 = plt.subplot2grid((3,2), (0,0))
    ax2 = plt.subplot2grid((3,2), (0,1))

    ax3 = plt.subplot2grid((3,2), (1,0))
    ax4 = plt.subplot2grid((3,2), (1,1))

    ax5 = plt.subplot2grid((3,2), (2,0))
    ax6 = plt.subplot2grid((3,2), (2,1))

    fig.set_facecolor('#00031F')
    ax1.patch.set_facecolor('#00031F')
    ax2.patch.set_facecolor('#00031F')
    ax3.patch.set_facecolor('#00031F')
    ax4.patch.set_facecolor('#00031F')
    ax5.patch.set_facecolor('#00031F')
    ax6.patch.set_facecolor('#00031F')


    plt.subplots_adjust(left=0.1,
                            bottom=0.1, 
                            right=0.9, 
                            top=0.9, 
                            wspace=0.6, 
                            hspace=0.3)


    #title - 
    fig.text(-0.15,0.95,player+' ('+str(int(df_player['Age'][0]))+')\n'+df_player['Team within selected timeframe'][0],size=50,**hfont,c='w',ha='center',va='top')

    fig.text(-0.15,0.87,league+' - '+season+'\n'+position.title()+' Template',
             size=30,**lfont,c='w',ha='center',va='top')


    #90s and minutes

    fig.text(-0.18,0.79,'90s',
             size=30,**lfont,c='w',ha='center',va='top')

    t = fig.text(-0.18, 0.76, str(round(df_player['90s - raw'][0],1)), size=40, c='#00031F',ha='center',
                va='top',**lfont)
    t.set_bbox(dict(facecolor='#58becb', alpha=1, edgecolor=None))           




    fig.text(-0.12,0.79,'Minutes',
             size=30,**lfont,c='w',ha='center',va='top')

    t = fig.text(-0.12, 0.76, str(round(df_player['Minutes played - raw'][0],0)), size=40, c='#00031F',ha='center',
                va='top',**lfont)
    t.set_bbox(dict(facecolor='#58becb', alpha=1, edgecolor=None))    





    #goals and xG

    fig.text(-0.18,0.7,'Goals',
             size=30,**lfont,c='w',ha='center',va='top')

    t = fig.text(-0.18, 0.67, int(df_player['NP Goals - raw'][0]), size=40, c='#00031F',ha='center',
                va='top',**lfont)
    t.set_bbox(dict(facecolor='#58becb', alpha=1, edgecolor=None))           




    fig.text(-0.12,0.7,'npxG',
             size=30,**lfont,c='w',ha='center',va='top')

    t = fig.text(-0.12, 0.67, str(round(df_player['NPxG - raw'][0],1)), size=40, c='#00031F',ha='center',
                va='top',**lfont)
    t.set_bbox(dict(facecolor='#58becb', alpha=1, edgecolor=None))    



    #assists and xA

    fig.text(-0.18,0.61,'Assists',
             size=30,**lfont,c='w',ha='center',va='top')

    t = fig.text(-0.18, 0.58, int(df_player['Assists - raw'][0]), size=40, c='#00031F',ha='center',
                va='top',**lfont)
    t.set_bbox(dict(facecolor='#58becb', alpha=1, edgecolor=None))           




    fig.text(-0.12,0.61,'xAssists',
             size=30,**lfont,c='w',ha='center',va='top')

    t = fig.text(-0.12, 0.58, str(round(df_player['xA - raw'][0],1)), size=40, c='#00031F',ha='center',
                va='top',**lfont)
    t.set_bbox(dict(facecolor='#58becb', alpha=1, edgecolor=None))    



    fig.text(-0.15,0.52,'Stengths',size=30,**lfont,c='w',ha='center',va='top')
    fig.text(-0.22,0.49,good.title(),size=22, c='#58becb',ha='left',
                va='top',**lfont)

    fig.text(-0.15,0.32,'Weaknesses',size=30,**lfont,c='w',ha='center',va='top')
    fig.text(-0.22,0.29,bad.title(),size=22, c='#e0a4c0',ha='left',
                va='top',**lfont)


    #role rating with box behind it - probably change colour dependent on rating
    # fig.text(-0.15,0.52,position_style_title.title()+' Rating',
    #          size=35,**lfont,c='w',ha='center',va='top')

    # t = fig.text(-0.15, 0.49, str(style_rating), size=60, c='#00031F',ha='center',
    #             va='top',**lfont)
    # t.set_bbox(dict(facecolor='#58becb', alpha=1, edgecolor=None))
          

        
        
        
    #percentile lines    
    ax1.hlines(y=df_selected_metrics_1['metric'], xmin=0, xmax=df_selected_metrics_1['percentile'],color=df_selected_metrics_1['colour'],lw=200/len(df_selected_metrics_1),zorder=8)

    #raw numbers on percentile line
    for g in range(len(df_selected_metrics_1)):
        ax1.text(1,df_selected_metrics_1['metric'][g],str(round(df_selected_metrics_1['raw'][g],2)),size=150/len(df_selected_metrics_1),c='#00031F',ha='left',va='center',zorder=9,**lfont)


    #name of metrics and percentiles
    ax1.set_yticks(df_selected_metrics_1['metric'])
    ax1.set_xticks([0,10,25,50,75,90,100])


    #size of metric names and percentiles
    ax1.tick_params(axis='x', colors='w', size=0,labelsize=15)
    ax1.tick_params(axis='y', colors='w', size = 0,labelsize=20)


    #half way mark
    ax1.plot([50,50],[-0.5,len(df_selected_metrics_1)-0.5],linestyle='dashed',c='#b3b1b0',lw=4,zorder=9)


    #stretching viz to always go to 100
    ax1.plot([100,100],[-0.5,len(df_selected_metrics_1)-0.5],c='#b3b1b0',lw=1,zorder=1,alpha=0)

    #adding vertical grid lines for percentiles
    ax1.grid(axis='x',linewidth=2,zorder=1,alpha=0.4,linestyle='dashed')

    #adding the name of the group of metrics
    ax1.text(0,len(df_selected_metrics_1)-0.2,choice_1.replace("_", " ").replace("and","&").title(),size=30,c='w',ha='left',va='bottom',**hfont)


    #################################


    ax2.hlines(y=df_selected_metrics_2['metric'], xmin=0, xmax=df_selected_metrics_2['percentile'],color=df_selected_metrics_2['colour'],lw=200/len(df_selected_metrics_2),zorder=8)



    for a in range(len(df_selected_metrics_2)):
        ax2.text(1,df_selected_metrics_2['metric'][a],str(round(df_selected_metrics_2['raw'][a],2)),size=150/len(df_selected_metrics_2),c='#00031F',ha='left',va='center',zorder=9,**lfont)


    ax2.set_yticks(df_selected_metrics_2['metric'])
    ax2.set_xticks([0,10,25,50,75,90,100])


    ax2.tick_params(axis='x', colors='w', size=0,labelsize=15)
    ax2.tick_params(axis='y', colors='w', size = 0,labelsize=20)



    ax2.plot([50,50],[-0.5,len(df_selected_metrics_2)-0.5],linestyle='dashed',c='#b3b1b0',lw=4,zorder=9)

    ax2.plot([100,100],[-0.5,len(df_selected_metrics_2)-0.5],c='#b3b1b0',lw=1,zorder=1,alpha=0)


    ax2.grid(axis='x',linewidth=2,zorder=1,alpha=0.4,linestyle='dashed')


    ax2.text(0,len(df_selected_metrics_2)-0.2,choice_2.replace("_", " ").replace("and","&").title(),size=30,c='w',ha='left',va='bottom',**hfont)




    #####################################

    ax3.hlines(y=df_selected_metrics_3['metric'], xmin=0, xmax=df_selected_metrics_3['percentile'],color=df_selected_metrics_3['colour'],lw=200/len(df_selected_metrics_3),zorder=8)



    for p in range(len(df_selected_metrics_3)):
        ax3.text(1,df_selected_metrics_3['metric'][p],str(round(df_selected_metrics_3['raw'][p],2)),size=150/len(df_selected_metrics_3),c='#00031F',ha='left',va='center',zorder=9,**lfont)


    ax3.set_yticks(df_selected_metrics_3['metric'])
    ax3.set_xticks([0,10,25,50,75,90,100])


    ax3.tick_params(axis='x', colors='w', size=0,labelsize=15)
    ax3.tick_params(axis='y', colors='w', size = 0,labelsize=20)



    ax3.plot([50,50],[-0.5,len(df_selected_metrics_3)-0.5],linestyle='dashed',c='#b3b1b0',lw=4,zorder=9)

    ax3.plot([100,100],[-0.5,len(df_selected_metrics_3)-0.5],c='#b3b1b0',lw=1,zorder=1,alpha=0)


    ax3.grid(axis='x',linewidth=2,zorder=1,alpha=0.4,linestyle='dashed')


    ax3.text(0,len(df_selected_metrics_3)-0.2,choice_3.replace("_", " ").replace("and","&").title(),size=30,c='w',ha='left',va='bottom',**hfont)





    ##############################


    ax4.hlines(y=df_selected_metrics_4['metric'], xmin=0, xmax=df_selected_metrics_4['percentile'],color=df_selected_metrics_4['colour'],lw=200/len(df_selected_metrics_4),zorder=8)



    for c in range(len(df_selected_metrics_4)):
        ax4.text(1,df_selected_metrics_4['metric'][c],str(round(df_selected_metrics_4['raw'][c],2)),size=150/len(df_selected_metrics_4),c='#00031F',ha='left',va='center',zorder=9,**lfont)


    ax4.set_yticks(df_selected_metrics_4['metric'])
    ax4.set_xticks([0,10,25,50,75,90,100])


    ax4.tick_params(axis='x', colors='w', size=0,labelsize=15)
    ax4.tick_params(axis='y', colors='w', size = 0,labelsize=20)



    ax4.plot([50,50],[-0.5,len(df_selected_metrics_4)-0.5],linestyle='dashed',c='#b3b1b0',lw=4,zorder=9)

    ax4.plot([100,100],[-0.5,len(df_selected_metrics_4)-0.5],c='#b3b1b0',lw=1,zorder=1,alpha=0)


    ax4.grid(axis='x',linewidth=2,zorder=1,alpha=0.4,linestyle='dashed')


    ax4.text(0,len(df_selected_metrics_4)-0.2,choice_4.replace("_", " ").replace("and","&").title(),size=30,c='w',ha='left',va='bottom',**hfont)




    ##########################


    # fig, ax5 = plt.subplots(figsize=(13.5,8.5))
    # fig.set_facecolor('#00031F')
    # ax5.patch.set_facecolor('#00031F')

    ax5.spines['bottom'].set_color('#00031F')
    ax5.spines['left'].set_color('#00031F')
    ax5.spines['top'].set_color('#00031F') 
    ax5.spines['right'].set_color('#00031F')


    ax5.set_xlabel(label_x, color='w', size = 25,**lfont)
    ax5.set_ylabel(label_y, color='w', size = 25,**lfont)


    ax5.tick_params(axis='x', colors='w', size=0,labelsize=20)
    ax5.tick_params(axis='y', colors='w', size = 0,labelsize=20)




    ax5.scatter( df[metric_x],df[metric_y], color = '#e0a4c0', s= 200,zorder=5,alpha = 0.4)

    for x in range(len(df)):
        if df['Player'][x] == player:
            ax5.scatter( df[metric_x][x],df[metric_y][x], color = '#58becb', edgecolors = 'w', s= 500,lw=2,zorder=7,alpha = 1)

    ax5.plot([mean_x,mean_x], [min_y,max_y],color='w',lw=4,zorder=6,alpha  = 0.4)
    ax5.plot([min_x,max_x],[mean_y,mean_y], color='w',lw=4,zorder=6,alpha  = 0.4)


    ax5.text(min_x,max_y*1.05,title,size=30,c='w',ha='left',va='bottom',**hfont)



    ###############################

    ax6.spines['bottom'].set_color('#00031F')
    ax6.spines['left'].set_color('#00031F')
    ax6.spines['top'].set_color('#00031F') 
    ax6.spines['right'].set_color('#00031F')


    ax6.set_xlabel(label_x_2, color='w', size = 25,**lfont)
    ax6.set_ylabel(label_y_2, color='w', size = 25,**lfont)


    ax6.tick_params(axis='x', colors='w', size=0,labelsize=20)
    ax6.tick_params(axis='y', colors='w', size = 0,labelsize=20)




    ax6.scatter( df[metric_x_2],df[metric_y_2], color = '#e0a4c0', s= 200,zorder=5,alpha = 0.4)

    for x in range(len(df)):
        if df['Player'][x] == player:
            ax6.scatter( df[metric_x_2][x],df[metric_y_2][x], color = '#58becb', edgecolors = 'w', s= 500,lw=2,zorder=7,alpha = 1)

    ax6.plot([mean_x_2,mean_x_2], [min_y_2,max_y_2],color='w',lw=4,zorder=6,alpha  = 0.4)
    ax6.plot([min_x_2,max_x_2],[mean_y_2,mean_y_2], color='w',lw=4,zorder=6,alpha  = 0.4)


    ax6.text(min_x_2,max_y_2*1.05,title_2,size=30,c='w',ha='left',va='bottom',**hfont)

    st.pyplot(fig)
