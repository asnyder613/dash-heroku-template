import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import dash
from jupyter_dash import JupyterDash
#import dash_core_components as dcc
from dash import dcc as dcc
#import dash_html_components as html
from dash import html as html
from dash.dependencies import Input, Output
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

gss = pd.read_csv("https://github.com/jkropko/DS-6001/raw/master/localdata/gss2018.csv",
                 encoding='cp1252', na_values=['IAP','IAP,DK,NA,uncodeable', 'NOT SURE',
                                               'DK', 'IAP, DK, NA, uncodeable', '.a', "CAN'T CHOOSE"], low_memory=False)

mycols = ['id', 'wtss', 'sex', 'educ', 'region', 'age', 'coninc',
          'prestg10', 'mapres10', 'papres10', 'sei10', 'satjob',
          'fechld', 'fefam', 'fepol', 'fepresch', 'meovrwrk'] 
gss_clean = gss[mycols]
gss_clean = gss_clean.rename({'wtss':'weight', 
                              'educ':'education', 
                              'coninc':'income', 
                              'prestg10':'job_prestige',
                              'mapres10':'mother_job_prestige', 
                              'papres10':'father_job_prestige', 
                              'sei10':'socioeconomic_index', 
                              'fechld':'relationship', 
                              'fefam':'male_breadwinner', 
                              'fehire':'hire_women', 
                              'fejobaff':'preference_hire_women', 
                              'fepol':'men_bettersuited', 
                              'fepresch':'child_suffer',
                              'meovrwrk':'men_overwork'},axis=1)
gss_clean.age = gss_clean.age.replace({'89 or older':'89'})
gss_clean.age = gss_clean.age.astype('float')

#saving as python string 
par = "According to ['Quick Facts About the Gender Wage Gap'](https://www.americanprogress.org/article/quick-facts-gender-wage-gap/) by Robin Bleiweis, the gender wage gap is a continuing problem in the U.S. Despite making significant progress in fair and equal employment for women alongside men, differences in employee roles, years of experience, hours worked, and discrimination all contribute to a significantly lower income rate for women than men, especially for women of color (Bleiwes). [Pew Research](https://www.pewresearch.org/social-trends/2023/03/01/the-enduring-grip-of-the-gender-pay-gap/) quantifies this, stating: 'In 2022, American women typically earned 82 cents for every dollar earned by men. That was about the same as in 2002, when they earned 80 cents to the dollar' (Kochhar). This is exacerbated by the pressures put on women by family life and childbearing, and is especially notable for women of color (Kochhar). Both Kochhar and Bleiweis note that the closing of the gender pay gap has stalled despite gains in education for women, and that continued societal changes is necessary to finish closing the gender wage gap. \n \n The GSS survey is a longstanding study of American social behavior and attitudes. The survey collects data on how Americans feel about social issues such as crime, group tolerance, political attitudes, and more. According to 'About the GSS', 'It is the only full-probability, personal-interview survey designed to monitor changes in both social characteristics and attitudes currently being conducted in the United States.'"

gss_display = gss_clean.groupby('sex').agg({'income':'mean',
                                      'job_prestige':'mean',
                                      'socioeconomic_index':'mean',
                                      'education':'mean'})

gss_display = gss_display.rename({'income':'Income',
                                   'job_prestige':'Occupational Prestige',
                                   'socioeconomic_index':'Socioeconomic Status',
                                   'education':'Years of Education'}, axis=1)
gss_display = round(gss_display, 2)
gss_display = gss_display.reset_index().rename({'sex':'Gender'}, axis=1)
table2 = ff.create_table(gss_display)

gss_breadwinner = pd.crosstab(gss_clean.male_breadwinner, gss_clean.sex).reset_index()
gss_breadwinner = pd.melt(gss_breadwinner, id_vars = 'male_breadwinner', value_vars = ['male', 'female'])
gss_breadwinner = gss_breadwinner.rename({'value':'Count'}, axis=1)

fig3 = px.bar(gss_breadwinner, x='male_breadwinner', y='Count', color='sex',
            labels={'male_breadwinner':'Level of Agreement', 'colpercent': 'Count'},
            hover_data = ['Count', 'sex', 'male_breadwinner'],
            barmode = 'group')
fig3.update_layout(showlegend=True)
fig3.update(layout=dict(title=dict(x=0.5)))

fig4 = px.scatter(gss_clean, x='job_prestige', y='income', color='sex', 
                 trendline='ols',
                 opacity = .3,
                 height=600, width=600,
                 labels={'job_prestige':'Occupational Prestige', 
                        'income':'Income',
                        'sex': 'Gender',
                        'education': 'Years of Education',
                        'socioeconomic_index': 'Socioeconomic Index'},
                 hover_data=['education', 'socioeconomic_index'])
fig4.update(layout=dict(title=dict(x=0.5)))

fig5a = px.box(gss_clean, y='income', x = 'sex', color = 'sex',
                   labels={'income':'Income', 'sex': 'Gender'})
fig5a.update_layout(showlegend=False)


fig5b = px.box(gss_clean, y='job_prestige', x = 'sex', color = 'sex',
                  labels={'job_prestige':'Job Prestige', 'sex': 'Gender'})
fig5b.update_layout(showlegend=False)

gss_gender = gss_clean[['income', 'sex', 'job_prestige']]
gss_gender['prestige'] = pd.cut(gss_gender.job_prestige, 6, ordered=True)
gss_gender = gss_gender.dropna()

fig6 = px.box(gss_gender, x='job_prestige', y = 'income', color = 'sex',
             facet_col='prestige', facet_col_wrap=2,
                   labels={'job_prestige':'Occupational Prestige', 'income': 'Income', 'sex':''},
                   title = 'Distribution of Income & Job Prestige by Gender',
            width=800, height=800,
            color_discrete_map = {'male':'blue', 'female':'red'})
fig6.update(layout=dict(title=dict(x=0.5)))

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(
    [
        html.H1("Exploring the Gender Wage Gap with GSS Survey Data") ,
        
        dcc.Markdown(children = par),
        
        html.H3("Comparing Income, Occupational Prestige, Socioeconomic Index, and Years of Education by Gender"),
        
        dcc.Graph(figure=table2),
        
        html.H3("Levels of Agreement with the statement: 'It is much better for everyone involved if the man is the achiever outside the home and the woman takes care of the home and family' by gender"),
        
        dcc.Graph(figure=fig3),
        
        html.H3("Comparison of Occupational Prestige & Income by Gender"),
        
        dcc.Graph(figure=fig4),
        
        html.Div([
            
            html.H4("Distribution of Income by Gender"),
                    
            dcc.Graph(figure=fig5a)], style = {'width':'48%', 'float':'left'}),
        
        html.Div([
            
            html.H4("Distribution of Job Prestige by Gender"),
            
            dcc.Graph(figure=fig5b)], style = {'width':'48%', 'float':'right'}),
        
        html.H3("Distribution of Income & Job Prestige by Gender"),
        
        dcc.Graph(figure=fig6)
    ]
)

if __name__ == '__main__':
    app.run_server(debug=True, port=8051, host='0.0.0.0')
