import dash
from dash import html
from dash import dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import altair as alt
# from vega_datasets import data
# import json
from dash import Input, Output, State, MATCH, ALL

#data
import pandas as pd
import numpy as np
import altair as alt
from textwrap import wrap
import base64

app = dash.Dash(__name__, title='Overview Dashboard', external_stylesheets = [dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
server = app.server
app.config.suppress_callback_exceptions = True

############################## Data #########################################

image_filename_small = 'Small.png' # replace with your own image
encoded_image_small = base64.b64encode(open(image_filename_small, 'rb').read())
image_filename_Medium = 'Medium.png' # replace with your own image
encoded_image_Medium = base64.b64encode(open(image_filename_Medium, 'rb').read())

#### BY ####

def loaddata(filename, rateType):
    cur_filepath = filename
    data = pd.read_csv(cur_filepath)
    df = data.melt(var_name='Year',value_name='Unemployment rate')
    df['Rate type'] = rateType
    return df

unemploy_df_all = loaddata("unemployment.csv", "All population")
unemploy_df_metro = loaddata("unemployment_metro.csv", "Census metropolitan area and census agglomeration")
unemploy_df_nonmetro = loaddata("unemployment_Nonmetro.csv", "Non-census metropolitan area and non-census agglomeration")
unemploy_df_all = pd.concat([unemploy_df_all,unemploy_df_metro,unemploy_df_nonmetro])

#### YS ####

df_YS = pd.read_csv("population.csv")
df_YS_selected=df_YS.iloc[:, [0,1,3,4,11]]
df_YS_selected = df_YS_selected[df_YS_selected["Statistical Area Classification (SAC)"].isin(["All census subdivisions","Within CMAs","Within CAs","Outside CMAs/CAs"])]
df_YS_selected["content_name"]=df_YS_selected["Population and dwelling counts (3)"].apply(lambda x:x.split(",")[0])
df_YS_selected['content_name'] = df_YS_selected['content_name'].apply(wrap, args=[20])

#### SZ ####
# employment data
employment_filepath = "employment.csv"
employ_data = pd.read_csv(employment_filepath)
employ_df_all = employ_data.melt(id_vars=['Lable'], var_name=['Year'], value_name='employment')


def plot_unemploy_chart(rate_type = 'all', start_year=2011, end_year=2021):
    # if rate_type == 'all':
    #     unemploy_df = unemploy_df_all
    # else:
    #     unemploy_df = unemploy_df_all
    unemploy_df = unemploy_df_all[(unemploy_df_all['Year'].astype(int) >= start_year) & (unemploy_df_all['Year'].astype(int) <= end_year)]
    line = alt.Chart(unemploy_df).mark_line(
        point=alt.OverlayMarkDef(color="blue")
    ).encode(
        x=alt.X('Year', title=None),
        y='Unemployment rate',
        color = alt.Color('Rate type', legend=alt.Legend(title=None,
            orient='none',
            legendX=0, legendY=-50)
        ),
        tooltip=['Unemployment rate']
    ).properties(width=290, height=200).configure_legend(labelLimit= 0)

    return line.interactive().to_html()
unemploy_chart = html.Iframe(id='unemployment_rate_chart',srcDoc=plot_unemploy_chart(rate_type = 'all', start_year=2011, end_year=2021),style={'width': '100%', 'height': '400px'})

def func_population(prov_name,area):
    df_sub = df_YS_selected[df_YS_selected["GEO"]==prov_name]
    df_sub1 = df_sub[df_sub["Statistical Area Classification (SAC)"]==area]
    tit = "Population and dwelling counts"
    if prov_name is not None:
        tit = tit + " of "+prov_name
    chart = (
        alt.Chart(df_sub1,title=tit)
        .mark_bar()
        .encode(
            x=alt.X('content_name'),
            y="VALUE",
        ).configure_axis(labelLimit=600,title = "")
        .properties(height=200, width=280))
    return chart.to_html()
pop_chart = html.Iframe(
    id="plot1",
    srcDoc=func_population(prov_name="Canada",area = "All census subdivisions"),
    style={'width': '100%', 'height': '400px'},
)

# employment plot
def plot_employ_chart(rate_type = 'all', start_year=2011, end_year=2021):
    employ_df = employ_df_all[(employ_df_all['Year'].astype(int) >= start_year) & (employ_df_all['Year'].astype(int) <= end_year)]
    line = alt.Chart(employ_df).mark_line(
        point=alt.OverlayMarkDef(color="blue")
    ).encode(
        x=alt.X('Year', title=None),
        y=alt.Y('employment', title='Employment (x 1000)', axis=alt.Axis(format='~s')),
        color = alt.Color('Lable', legend=alt.Legend(
            title=None,
            orient='none',
            legendX=0, legendY=-50)
        ),
        tooltip=['employment']
    ).properties(width=290, height=200).configure_legend(labelLimit= 0)

    return line.interactive().to_html()
employ_chart = html.Iframe(id='employment_pop_chart',srcDoc=plot_employ_chart(rate_type = 'all', start_year=2011, end_year=2021),style={'width': '100%', 'height': '400px'})



component_UnemploymentRate = dbc.Card([
        # html.Div("School List", style = {"margin": "auto", "width": "822px"}),
        html.H4("Unemployment Rate", style = {"margin": "auto", "width": "98%", "marginTop":"15px", "marginBottom":"0px"}),
        html.Hr(style = {"margin": "10px 10px"}),
        html.Div(
        [
            # dbc.Col(component_heatmap, width="auto"),
            dbc.Row(
                [
                    dbc.Col([
                            dbc.Row([
                                dbc.Col([
                                    html.Div('Start Year', style={"font-size": "small"}),
                                    dcc.Dropdown(id='start_year', options = [x for x in range (2011,2022)], value = 2011)
                                ], width={"size": 5, "offset": 1}),
                                dbc.Col([
                                    html.Div('End Year', style={"font-size": "small"}),
                                    dcc.Dropdown(id='end_year', options = [x for x in range (2011,2022)], value = 2021)
                                ], width=5),
                            ]),

                            unemploy_chart
                        ], width=4, style = {"padding-left": 0, "border-right": "rgb(220 220 220) solid 1px", "height": "350px", "marginTop": "10px"}),
                    dbc.Col([
                        html.Div([
                                html.H5("Key Indicator: Unemployment Rate"),
                                html.Div("The unemployment rate is the number of unemployed persons expressed as a percentage of the labour force. The unemployment rate for a particular group (age, sex, marital status, etc.) is the number unemployed in that group expressed as a percentage of the labour force for that group. Estimates are percentages, rounded to the nearest tenth.", style={"marginTop": "10px"}),
                                html.Div("The line chart on the left side shows change of the unemployment rate in selected time period.", style={"marginTop": "10px"}),
                                html.Div("(Default: 2011 to 2021)", style={"marginTop": "0px"}),
                                html.Div("For overview purpose, only all population, Census metropolitan area (CMA) and census agglomerationare (CA), Non-census metropolitan area (Non-CMA) and non-census agglomeration (Non-CA) are shown here. You can find more detailed information and apply more filters on the detail page.", style={"marginTop": "10px"}),
                                html.Div("Reference: Statistics Canada. Table 14-10-0375-01  Employment and unemployment rate, annual", style={"marginTop": "10px", "font-size": "small"}),
                                html.Div([
                                    dbc.Button(
                                        "Detail",
                                        href="https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1410037501",
                                        external_link=True,
                                        color="primary",
                                    ),
                                ], style = {"position": "absolute", "bottom":"15px", "right": "20px"}),
                            ], style ={"marginTop": "10px"})

                        ])

                ],style = {"margin": "auto", "width": '100%'}
            ),

        ], style = {"height":"360px", "width": "100%"})

    ],style = {"width":"100%", "height":"450px", "marginTop":"20px"})

component_RCBP_Dscription = dbc.Card([
        html.H3("Rural Canada Business Profile from 2017 to 2019", style = {"margin": "auto", "width": "98%", "marginTop":"15px", "marginBottom":"0px"}),
        html.Hr(style = {"margin": "10px 10px"}),
        html.Div(
        [
            # dbc.Col(component_heatmap, width="auto"),
            dbc.Row(
                [
                    #dbc.Col([
                        html.Div([
                                # html.H5("Title"),
                                html.Div("The Rural Canada Business Profiles database (RCBP) provides data on counts and key financial indicators of small and medium sized businesses with a theme classification by rural and urban areas of Canada. The RCBP has a similar methodology to the Financial Performance Data (FPD). In contrast to the FPD, the RCBP notably features a rural and urban breakdown.", style={"marginTop": "10px"}),
                                html.Div("Key terms definition:", style={"marginTop": "10px"}),
                                html.Div("Net profit to equity ratio: This ratio is calculated as (net profit * 100) / (equity). This percentage indicates the profitability of a business. The higher the ratio, the relatively better the profitability. ", style={"marginTop": "10px"}),
                                html.Div("Current debt to equity ratio: This ratio is calculated as (current liabilities * 100) / (equity). This percentage is a measure of liquidity, which indicates a firm’s relative ability to pay its short-term debts. The lower the positive ratio, the more liquid the business. ", style={"marginTop": "10px"}),
                                html.Div("Debt to equity ratio: This ratio is calculated as (total liabilities) / (total equity). This is a solvency ratio that indicates a firm’s ability to pay its long-term debts. The lower the positive ratio, the more solvent the business. ", style={"marginTop": "10px"}),
                                html.Div("Revenue to equity ratio: This ratio is calculated as (total revenue) / (equity). It provides an indication of the economic productivity of capital. ", style={"marginTop": "10px"}),
                                html.Div("Total Number of Business: The count of businesses in each category",style={"marginTop": "10px"}),
                                html.Div("Total Revenue: It calculate as number of businesses * average revenue",style={"marginTop": "10px"}),
                                html.Div("Expense Breakdown: Total expense in different categories",style={"marginTop": "10px"}),
                                html.Div("Direct Expense: Cost of sales",style={"marginTop": "10px"}),
                                html.Div("Indirect Expense: Operating expense",style={"marginTop": "10px"}),
                                html.Div("Net profit: It calculated as total revenue – total expense",style={"marginTop": "10px"}),
                                html.Div([
                                    dbc.Button(
                                        "Detail",
                                        href="https://www150.statcan.gc.ca/n1/pub/45-20-0004/452000042022001-eng.htm",
                                        external_link=True,
                                        color="primary",
                                    ),
                                ], style = {"position": "absolute", "bottom":"1040px", "right": "20px"}),
                            ], style ={"marginTop": "0px"})

                    #    ])

                ],style = {"margin": "auto", "width": '100%'}
            ),

        ], style = {"height":"540px", "width": "100%"}),
        html.Hr(style = {"margin": "10px 10px"}),
        html.Div(
        [
            dbc.Row(
                [
                    dbc.Col([
                            html.A([
                                html.Img(src='data:image/png;base64,{}'.format(encoded_image_small.decode()), style={'width': '590px', "marginTop": "0px"}),
                            ], href='https://public.tableau.com/app/profile/tingwen7851/viz/SmallBusinessDashboard/Dashboard1')
                        ], width=6, style = {"padding-left": 0, "border-right": "rgb(220 220 220) solid 1px", "height": "450px", "marginTop": "10px"}),
                    dbc.Col([
                            html.A([
                                html.Img(src='data:image/png;base64,{}'.format(encoded_image_Medium.decode()), style={'width': '590px', "marginTop": "10px"}),
                            ], href='https://public.tableau.com/app/profile/tingwen7851/viz/MediumBusinessProfile/Dashboard2')
                        ], width=6)

                ],style = {"margin": "auto", "width": '100%'}
            ),

        ], style = {"height":"470px", "width": "100%"}),
        html.Hr(style = {"margin": "15px 10px"}),
        html.Div(
        [
            dbc.Row(
                [
                    dbc.Col([
                        html.Div([
                                html.H5("Small Sized Businesses"),
                                html.Div("The dashboard shows the general information of the small sized business in Canada from 2017 to 2019.", style={"marginTop": "10px"}),
                                html.Div("This group includes all businesses operating in Canada reporting total annual revenues between $30,000 and $5,000,000 (inclusive).", style={"marginTop": "10px"}),
                                html.Div("Filters applied: ", style={'fontWeight': '600',"marginTop": "10px"}),
                                html.Div("Time period: 2017,2018 and 2019", style={"marginTop": "10px"}),
                                html.Div("Location Indicator: Rural, Urban", style={"marginTop": "10px"}),
                                html.Div("Industry: Businesses are classified by industry using the business's North American Industry Classification System (NAICS) 201715 industry assignment on the BR. ", style={"marginTop": "10px"}),
                                html.Div("Geography: Provinces in Canada", style={"marginTop": "10px"}),
                                html.Div("Incorporation Status: Incorporated, Unincorporated", style={"marginTop": "10px"}),
                                html.Div("*Not applied to financial ratios where this data is missing.", style={"marginTop": "10px"}),
                                html.Div("*Due to the data suppression, please use \"All industries\" in industry filter, \"Canada\" in geography filter to see the overall information.", style={"marginTop": "0px"}),
                            ], style ={"marginTop": "10px"})
                        ], width=6, style = {"padding-left": 0, "border-right": "rgb(220 220 220) solid 1px", "height": "375px", "marginTop": "10px"}),
                    dbc.Col([
                        html.Div([
                                html.H5("Medium Sized Businesses"),
                                html.Div("The dashboard shows the general information of the medium sized business in Canada from 2017 to 2019.This group includes all businesses operating in Canada reporting total annual revenues between $5,000,001 and $20,000,000 (inclusive). Owing to the lower counts of medium businesses, the RCBP only provides national level tables for such businesses in order to be able to protect confidentiality. Rural and urban breakdowns at the Canada level are provided for medium businesses, but no provincial/territorial breakdowns in order to protect confidentiality of identifiable businesses.", style={"marginTop": "10px"}),
                                html.Div("Filters applied: ", style={'fontWeight': '600',"marginTop": "10px"}),
                                html.Div("Time period: 2017,2018 and 2019", style={"marginTop": "10px"}),
                                html.Div("Location Indicator: Rural, Urban", style={"marginTop": "10px"}),
                                html.Div("Industry: Businesses are classified by industry using the business's North American Industry Classification System (NAICS) 201715 industry assignment on the BR.", style={"marginTop": "10px"}),
                                html.Div("*Due to data suppression, please use \"All industries\" in industry filter.", style={"marginTop": "10px"}),
                            ], style ={"marginTop": "10px"})

                        ], width=6)

                ],style = {"margin": "auto", "width": '100%'}
            ),

        ], style = {"height":"380px", "width": "100%"}),

    ],style = {"width":"100%", "height":"1650px", "marginTop":"20px"})

component_population = dbc.Card([
        # html.Div("School List", style = {"margin": "auto", "width": "822px"}),
        html.H4("Population and dwelling counts", style = {"margin": "auto", "width": "98%", "marginTop":"15px", "marginBottom":"0px"}),
        html.Hr(style = {"margin": "10px 10px"}),
        html.Div(
        [
            # dbc.Col(component_heatmap, width="auto"),
            dbc.Row(
                [
                    dbc.Col([
                            dbc.Row([
                                dbc.Col([
                                    html.Div('Province', style={"font-size": "small"}),
                                    dcc.Dropdown(id='pop_dropdown', options = [i for i in df_YS_selected['GEO'].unique()], value = 'Canada')
                                ], width={"size": 10, "offset": 1}),
                                dbc.Col([
                                    html.Div('Area Type', style={"font-size": "small"}),
                                    dcc.Dropdown(id='area', options = [i for i in df_YS_selected['Statistical Area Classification (SAC)'].unique()], value = "All census subdivisions")
                                ], width={"size": 10, "offset": 1}),
                            ]),

                            pop_chart
                        ], width=4, style = {"padding-left": 0, "border-right": "rgb(220 220 220) solid 1px", "height": "430px", "marginTop": "10px"}),
                    dbc.Col([
                        html.Div([
                                html.H5("Key Indicator: Population and dwelling counts"),
                                html.Div("The data is from Census of Population in 2021. You can choose the provinces and the area types to see the population, total private dwellings and private dwellings occupied by usual residents in 2021."),
                                html.Div("The 2021 Census population counts for a particular geographic area represent the number of Canadians whose usual place of residence is in that area, regardless of where they happened to be on Census Day. Also included are any Canadians who were staying in that area on Census Day and who had no usual place of residence elsewhere in Canada, as well as those considered to be non-permanent residents.", style={"marginTop": "10px"}),
                                html.Div("The dwelling counts refer to total private dwellings and private dwellings occupied by usual residents in Canada.  ", style={"marginTop": "10px"}),
                                html.Div("For the area types, CMA refers to a census metropolitan area, and CA refers to a census agglomeration. A CMA must have a total population of at least 100,000 of which 50,000 or more must live in the core. A CA must have a core population of at least 10,000.", style={"marginTop": "10px"}),
                                html.Div("Reference: Statistics Canada.  Table 98-10-0016-01  Population and dwelling counts by the Statistical Area Classification", style={"marginTop": "10px", "font-size": "small"}),

                                html.Div([
                                    dbc.Button(
                                        "Detail",
                                        href="https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=9810001601",
                                        external_link=True,
                                        color="primary",
                                    ),
                                ], style = {"position": "absolute", "bottom":"15px", "right": "20px"}),
                            ], style ={"marginTop": "10px"})

                        ])

                ],style = {"margin": "auto", "width": '100%'}
            ),

        ], style = {"height":"360px", "width": "100%"})

    ],style = {"width":"100%", "height":"550px", "marginTop":"5px"})

component_Employment = dbc.Card([
        # html.Div("School List", style = {"margin": "auto", "width": "822px"}),
        html.H4("Employment", style = {"margin": "auto", "width": "98%", "marginTop":"15px", "marginBottom":"0px"}),
        html.Hr(style = {"margin": "10px 10px"}),
        html.Div(
        [
            # dbc.Col(component_heatmap, width="auto"),
            dbc.Row(
                [
                    dbc.Col([
                            dbc.Row([
                                dbc.Col([
                                    html.Div('Start Year', style={"font-size": "small"}),
                                    dcc.Dropdown(id='employment_start_year', options = [x for x in range (2011,2022)], value = 2011)
                                ], width={"size": 5, "offset": 1}),
                                dbc.Col([
                                    html.Div('End Year', style={"font-size": "small"}),
                                    dcc.Dropdown(id='employment_end_year', options = [x for x in range (2011,2022)], value = 2021)
                                ], width=5),
                            ]),

                            employ_chart
                        ], width=4, style = {"padding-left": 0, "border-right": "rgb(220 220 220) solid 1px", "height": "370px", "marginTop": "10px"}),
                    dbc.Col([
                        html.Div([
                                html.H5("Key Indicator: Employment"),
                                html.Div("The employment is the number of persons who, during the reference week, worked for pay or profit, or performed unpaid family work or had a job but were not at work due to own illness or disability, personal or family responsibilities, labour dispute, vacation, or other reason. Those persons on layoff and persons without work but who had a job to start at a definite date in the future are not considered employed. Estimates in thousands, rounded to the nearest hundred.", style={"marginTop": "10px"}),
                                html.Div("The line chart on the left side shows the changes of the employment in selected time period.", style={"marginTop": "10px"}),
                                html.Div("(Default: 2011 to 2021)", style={"marginTop": "0px"}),
                                html.Div("For overview purpose, only all population, Census metropolitan area (CMA) and census agglomerationare (CA), Non-census metropolitan area (Non-CMA) and non-census agglomeration (Non-CA) are shown here. You can find more detailed information and apply more filters on the detail page.", style={"marginTop": "10px"}),
                                html.Div("Reference: Statistics Canada. Table 14-10-0375-01  Employment and unemployment rate, annual", style={"marginTop": "10px", "font-size": "small"}),
                                html.Div([
                                    dbc.Button(
                                        "Detail",
                                        href="https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1410037501",
                                        external_link=True,
                                        color="primary",
                                    ),
                                ], style = {"position": "absolute", "bottom":"15px", "right": "20px"}),
                            ], style ={"marginTop": "10px"})

                        ])

                ],style = {"margin": "auto", "width": '100%'}
            ),

        ], style = {"height":"360px", "width": "100%"})

    ],style = {"width":"100%", "height":"470px", "marginTop":"20px"})


dashboard_width = "1250px"
dashboard_width_inside = "1210px"
## Layout
app.layout = dbc.Container([
    dbc.Row(
        [
            component_RCBP_Dscription

        ],style = {"margin": "auto", "width": dashboard_width}
    ),
    dbc.Row(
        dbc.Card([
            html.H3("Key Indicators", style = {"margin": "auto", "width": "98%", "marginTop":"15px", "marginBottom":"0px"}),
            html.Hr(style = {"margin": "10px 10px"}),
            dbc.Row(
            [
                component_population

            ],style = {"margin": "auto", "width": dashboard_width_inside}
            ),
            dbc.Row(
                [
                    component_Employment

                ],style = {"margin": "auto", "width": dashboard_width_inside}
            ),
            dbc.Row(
                [
                    component_UnemploymentRate

                ],style = {"margin": "auto", "width": dashboard_width_inside, "marginBottom":'20px'}
            ),
        ],style = {"margin": "auto", "marginTop":"20px","width": dashboard_width}),
    ),
    
    

], style = {"max-width": "2000px"})

# Callback functions
@app.callback(
    Output('unemployment_rate_chart','srcDoc'), # Specifies where the output "goes"
    Input('start_year', 'value'),
    Input('end_year', 'value')
    )
def update_plot(startYear, endYear): #, in_out_state = 1, room_board = 1

    newplot = plot_unemploy_chart(rate_type = 'all', start_year=startYear, end_year=endYear)
    return newplot

# Callback functions
@app.callback(
    Output('plot1','srcDoc'), # Specifies where the output "goes"
    Input('pop_dropdown', 'value'),
    Input('area','value')
    )
def update_plot(pop_dropdown,area): #, in_out_state = 1, room_board = 1
    newplot = func_population(prov_name=pop_dropdown,area = area)
    return newplot

# Employment
@app.callback(
    Output('employment_pop_chart','srcDoc'), # Specifies where the output "goes"
    Input('employment_start_year', 'value'),
    Input('employment_end_year', 'value')
    )
def update_plot(startYear, endYear): #, in_out_state = 1, room_board = 1

    newplot = plot_employ_chart(rate_type = 'all', start_year=startYear, end_year=endYear)
    return newplot


if __name__ == "__main__":
    app.run_server(host="127.0.0.4")