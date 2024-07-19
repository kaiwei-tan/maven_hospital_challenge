import streamlit as st
import pandas as pd
import plotly.express as px
from helper import *

# Title
with st.container(border=False):
    col_t1, col_t2 = st.columns([1/3, 2/3])
    
    with col_t1:
        st.image("logo.jpg", use_column_width=True)

    with col_t2:
        st.title('Key Performance Report')

encounters = pd.read_csv("data/encounters.csv")
organizations = pd.read_csv("data/organizations.csv")
patients = pd.read_csv("data/patients.csv")
payers = pd.read_csv("data/payers.csv")
procedures = pd.read_csv("data/procedures.csv")

age_groups = {
    '0 – 14 years': [0, 14],
    '15 – 24 years': [15, 24],
    '25 – 54 years': [25, 54],
    '55 – 64 years': [55, 64],
    '65 years and over': [65, 999]
}

# Transform the encounters table
encounters = transform_encounters(encounters)
current_date = encounters['START'].max().date()

months = list(reversed(encounters['START_MONTH'].unique()))[1:] # assume latest month is incomplete

# Aggregate patient admissions
df_admissions = create_df_admissions(encounters, patients, age_groups, current_date)
df_admissions_grouped = get_admissions_grouped(df_admissions)
df_readmissions_grouped = get_readmissions_grouped(df_admissions)

# Aggregate length of stay
df_length = create_df_length(encounters, patients, age_groups, current_date)
df_length_grouped = get_length_grouped(df_length)
df_length_by_age_group_grouped = get_length_by_age_group_grouped(df_length)

# Aggregate encounter cost
df_cost = get_df_cost(encounters)
df_cost_grouped = get_cost_grouped(df_cost)
df_cost_by_encounter_class_grouped = get_cost_by_encounter_class_grouped(df_cost)

# Aggregate insurance coverage
df_encounter_coverage = get_df_encounter_coverage(encounters, payers, procedures)
df_encounter_coverage_grouped = get_encounter_coverage_grouped(df_encounter_coverage)
df_procedure_coverage = create_df_procedure_coverage(procedures, df_encounter_coverage)
df_procedure_coverage_grouped = get_procedure_coverage_grouped(df_procedure_coverage)

# Select monthly report
with col_t2: # this uses the same column as the dashboard title
    selected_month = st.selectbox('Select report of month:', options=months, index=0)
    previous_month = (pd.to_datetime(selected_month) - pd.DateOffset(months=1)).strftime('%Y-%m')

# Metrics
with st.container(border=False):
    col_m1, col_m2, col_m3, col_m4, col_m5, col_m6 = st.columns(6)

    with col_m1:
        with st.container(border=True):
            n_patients = df_admissions_grouped[df_admissions_grouped['START_MONTH'].isin([selected_month])]['PATIENTS'].item()
            st.metric('Patients', f'{n_patients:,}')

    with col_m2:
        with st.container(border=True):
            n_admissions = df_admissions_grouped[df_admissions_grouped['START_MONTH'].isin([selected_month])]['ADMISSIONS'].item()
            st.metric('Admissions', f'{n_admissions:,}')

    with col_m3:
        with st.container(border=True):
            df_temp = df_admissions_grouped[df_admissions_grouped['START_MONTH'].isin([selected_month])][['ADMISSIONS', 'READMISSIONS']]
            n_readmissions = (df_temp['READMISSIONS'] / df_temp['ADMISSIONS']).item()
            st.metric('Readmission rate', f'{n_readmissions:.0%}')

    with col_m4:
        with st.container(border=True):
            avg_duration = df_length_grouped[df_length_grouped['START_MONTH'].isin([selected_month])]['AVERAGE_DURATION'].item()
            st.metric('Average duration', f'{avg_duration:.1f} hours')

    with col_m5:
        with st.container(border=True):
            avg_cost = df_cost_grouped[df_cost_grouped['START_MONTH'].isin([selected_month])]['AVERAGE_COST'].item()
            st.metric('Average cost', f'${avg_cost:,.0f}')

    with col_m6:
        with st.container(border=True):
            n_procedures = df_encounter_coverage_grouped[df_encounter_coverage_grouped['START_MONTH'].isin([selected_month])]['PROCEDURES'].item()
            st.metric('Procedures covered', f'{n_procedures:,}')

# Metrics
col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.subheader('Patient admissions')
        tab1, tab2 = st.tabs(['MoM comparison', 'By age group'])

        with tab1:
            df_admissions_grouped = df_admissions_grouped[df_admissions_grouped['START_MONTH'].isin([previous_month, selected_month])].reset_index(drop=True)
            df_admissions_grouped['START_MONTH'] = pd.to_datetime(df_admissions_grouped['START_MONTH']).dt.strftime('%b %Y')
            df_admissions_grouped = df_admissions_grouped.melt(id_vars='START_MONTH')
            df_admissions_grouped['variable'] = df_admissions_grouped['variable'].str.title()

            readmissions_change = (df_admissions_grouped['value'][len(df_admissions_grouped)-1] - df_admissions_grouped['value'][len(df_admissions_grouped)-2]) / df_admissions_grouped['value'][len(df_admissions_grouped)-2]
            readmissions_direction = 'decreased' if readmissions_change < 0 else 'increased'
            if abs(readmissions_change) < 1:
                readmissions_markdown = f'Patients readmitted ***{readmissions_direction}*** by ***{abs(readmissions_change):.0%}*** from previous month.'
            elif abs(readmissions_change) > 1:
                if readmissions_change == np.inf:
                    readmissions_markdown = f'Patients readmitted ***{readmissions_direction}*** by ***100%*** from previous month.'
                else:
                    readmissions_markdown = f'Patients readmitted ***{readmissions_direction} {abs(readmissions_change):.1f}x*** from previous month.'
            elif readmissions_change == 1:
                readmissions_markdown = f'Patients readmitted ***remained the same*** from previous month.'
            elif readmissions_change == -1:
                readmissions_markdown = f'Patients readmitted ***{readmissions_direction}*** by ***{abs(readmissions_change):.0%}*** from previous month.'
            st.markdown(readmissions_markdown)
        
            admissions_grouped = px.bar(df_admissions_grouped, x='variable', y='value', color='START_MONTH', barmode='group', color_discrete_sequence=['#c3e4ec', '#048cb3']) 
            admissions_grouped.update_layout(xaxis_title='Number of patients', yaxis_title=None, yaxis=dict(showgrid=False), showlegend=True, legend_title=None, legend=dict(orientation='h', yanchor='top', y=1, xanchor='center', x=0.5))
            admissions_grouped.update_traces(hovertemplate='<b>%{y:,} patients</b>')
            st.plotly_chart(admissions_grouped, use_container_width=True, config={'displayModeBar': False})
        
        with tab2:
            df_readmissions_grouped = df_readmissions_grouped[df_readmissions_grouped['START_MONTH'].isin([selected_month])].reset_index(drop=True)
            df_readmissions_grouped = df_readmissions_grouped.sort_values(['READMISSIONS', 'AGE_GROUP'], ascending=[False, True]).reset_index(drop=True)
            df_readmissions_grouped['START_MONTH'] = pd.to_datetime(df_readmissions_grouped['START_MONTH']).dt.strftime('%b %Y')

            highest_readmission_groups = df_readmissions_grouped[df_readmissions_grouped['READMISSIONS'] == df_readmissions_grouped['READMISSIONS'].max()]['AGE_GROUP']
            highest_readmission_groups_count = len(highest_readmission_groups)
            highest_readmission_groups_str = ' and '.join(highest_readmission_groups)
            highest_readmission = df_readmissions_grouped['READMISSIONS'].max()
            start_month = df_readmissions_grouped['START_MONTH'][0]
            if highest_readmission_groups_count == 1:
                readmissions_markdown = f'Age group ***{highest_readmission_groups_str}*** had the most readmissions in {start_month}.'
            elif highest_readmission_groups_count > 1:
                readmissions_markdown = f'Age groups ***{highest_readmission_groups_str}*** had the most readmissions in {start_month}.'
            st.markdown(readmissions_markdown)
            
            readmissions_grouped = px.bar(df_readmissions_grouped, x='READMISSIONS', y='AGE_GROUP', color='AGE_GROUP', orientation='h', color_discrete_sequence=['#c3e4ec'], color_discrete_map=dict(zip(highest_readmission_groups, ['#048cb3']*highest_readmission_groups_count)))
            readmissions_grouped.update_layout(xaxis_title='Number of readmissions', yaxis_title=None, showlegend=False)
            readmissions_grouped.update_traces(hovertemplate='<b>%{x:,} readmission(s)</b>')
            st.plotly_chart(readmissions_grouped, use_container_width=True, config={'displayModeBar': False})

    with st.container(border=True):
        st.subheader('Encounter cost')
        tab3, tab4 = st.tabs(['MoM comparison', 'By encounter type'])

        with tab3:
            df_cost_grouped = df_cost_grouped[df_cost_grouped['START_MONTH'].isin([previous_month, selected_month])].reset_index(drop=True)
            df_cost_grouped['START_MONTH'] = pd.to_datetime(df_cost_grouped['START_MONTH']).dt.strftime('%b %Y')
            
            cost_change = (df_cost_grouped['AVERAGE_COST'][1] - df_cost_grouped['AVERAGE_COST'][0]) / df_cost_grouped['AVERAGE_COST'][0]
            cost_direction = 'decreased' if cost_change < 0 else 'increased'
            st.markdown(f'Average encounter cost ***{cost_direction}*** by ***{abs(cost_change):.0%}*** from previous month.')
            
            cost_grouped = px.bar(df_cost_grouped, x='START_MONTH', y='AVERAGE_COST', color='START_MONTH', color_discrete_sequence=['#c3e4ec', '#048cb3'])
            cost_grouped.update_layout(xaxis_title=None, yaxis_title='Average cost of encounter', yaxis=dict(showgrid=False), showlegend=False)
            cost_grouped.update_traces(hovertemplate='<b>$%{y:,.2f}</b>')
            st.plotly_chart(cost_grouped, use_container_width=True, config={'displayModeBar': False})
        
        with tab4:
            df_cost_by_encounter_class_grouped = df_cost_by_encounter_class_grouped[df_cost_by_encounter_class_grouped['START_MONTH'].isin([selected_month])].reset_index(drop=True)
            df_cost_by_encounter_class_grouped = df_cost_by_encounter_class_grouped.sort_values(['AVERAGE_COST', 'ENCOUNTERCLASS'], ascending=[False, True]).reset_index(drop=True)
            df_cost_by_encounter_class_grouped['START_MONTH'] = pd.to_datetime(df_cost_by_encounter_class_grouped['START_MONTH']).dt.strftime('%b %Y')

            highest_cost_group = df_cost_by_encounter_class_grouped['ENCOUNTERCLASS'][0]
            highest_cost = df_cost_by_encounter_class_grouped['AVERAGE_COST'][0]
            start_month = df_cost_by_encounter_class_grouped['START_MONTH'][0]
            st.markdown(f'Encounter class ***{highest_cost_group}*** had the highest average cost of ***${highest_cost:,.0f}*** in {start_month}.')
            
            cost_by_encounter_class_grouped = px.bar(df_cost_by_encounter_class_grouped, x='AVERAGE_COST', y='ENCOUNTERCLASS', color='ENCOUNTERCLASS', orientation='h', color_discrete_sequence=['#c3e4ec'], color_discrete_map={highest_cost_group: '#048cb3'})
            cost_by_encounter_class_grouped.update_layout(xaxis_title='Average cost of encounter', yaxis_title=None, showlegend=False)
            cost_by_encounter_class_grouped.update_traces(hovertemplate='<b>$%{x:,.2f}</b>')
            st.plotly_chart(cost_by_encounter_class_grouped, use_container_width=True, config={'displayModeBar': False})

with col2:
    with st.container(border=True):
        st.subheader('Length of stay')
        tab5, tab6 = st.tabs(['MoM comparison', 'By age group'])

        with tab5:
            df_length_grouped = df_length_grouped[df_length_grouped['START_MONTH'].isin([previous_month, selected_month])].reset_index(drop=True)
            df_length_grouped['START_MONTH'] = pd.to_datetime(df_length_grouped['START_MONTH']).dt.strftime('%b %Y')
            
            length_change = (df_length_grouped['AVERAGE_DURATION'][1] - df_length_grouped['AVERAGE_DURATION'][0]) / df_length_grouped['AVERAGE_DURATION'][0]
            length_direction = 'decreased' if length_change < 0 else 'increased'
            st.markdown(f'Average length of stay ***{length_direction}*** by ***{abs(length_change):.0%}*** from previous month.')
             
            length_grouped = px.bar(df_length_grouped, x='START_MONTH', y='AVERAGE_DURATION', color='START_MONTH', color_discrete_sequence=['#c3e4ec', '#048cb3'])
            length_grouped.update_layout(xaxis_title=None, yaxis_title='Average duration of encounter', yaxis=dict(showgrid=False), showlegend=False)
            length_grouped.update_traces(hovertemplate='<b>%{y:,.1f} hours</b>')
            st.plotly_chart(length_grouped, use_container_width=True, config={'displayModeBar': False})
        
        with tab6:
            df_length_by_age_group_grouped = df_length_by_age_group_grouped[df_length_by_age_group_grouped['START_MONTH'].isin([selected_month])].reset_index(drop=True)
            df_length_by_age_group_grouped = df_length_by_age_group_grouped.sort_values(['AVERAGE_DURATION', 'AGE_GROUP'], ascending=[False, True]).reset_index(drop=True)
            df_length_by_age_group_grouped['START_MONTH'] = pd.to_datetime(df_length_by_age_group_grouped['START_MONTH']).dt.strftime('%b %Y')

            highest_length_group = df_length_by_age_group_grouped['AGE_GROUP'][0]
            highest_length = df_length_by_age_group_grouped['AVERAGE_DURATION'][0]
            start_month = df_length_by_age_group_grouped['START_MONTH'][0]
            st.markdown(f'Age group ***{highest_length_group}*** had the longest average stay of ***{highest_length:.1f} hours*** in {start_month}.')
            
            length_by_age_group_grouped = px.bar(df_length_by_age_group_grouped, x='AVERAGE_DURATION', y='AGE_GROUP', color='AGE_GROUP', orientation='h', color_discrete_sequence=['#c3e4ec'], color_discrete_map={highest_length_group: '#048cb3'})
            length_by_age_group_grouped.update_layout(xaxis_title='Average duration of encounter', yaxis_title=None, showlegend=False)
            length_by_age_group_grouped.update_traces(hovertemplate='<b>%{x:,.1f} hours</b>')
            st.plotly_chart(length_by_age_group_grouped, use_container_width=True, config={'displayModeBar': False})

    with st.container(border=True):
        st.subheader('Insurance coverage')
        tab7, tab8 = st.tabs(['MoM comparison', 'Gaps in coverage'])

        with tab7:
            df_encounter_coverage_grouped = df_encounter_coverage_grouped[df_encounter_coverage_grouped['START_MONTH'].isin([previous_month, selected_month])].reset_index(drop=True)
            df_encounter_coverage_grouped['START_MONTH'] = pd.to_datetime(df_encounter_coverage_grouped['START_MONTH']).dt.strftime('%b %Y')
            
            coverage_change = (df_encounter_coverage_grouped['COVERAGE_RATE_COUNT'][1] - df_encounter_coverage_grouped['COVERAGE_RATE_COUNT'][0])
            coverage_direction = 'decreased' if coverage_change < 0 else 'increased'
            st.markdown(f'Percentage of procedures covered by insurance ***{coverage_direction}*** by ***{abs(coverage_change):.0%}*** from previous month.')
            
            encounter_coverage_grouped = px.bar(df_encounter_coverage_grouped, x='START_MONTH', y='COVERAGE_RATE_COUNT', color='START_MONTH', color_discrete_sequence=['#c3e4ec', '#048cb3'])      
            encounter_coverage_grouped.update_layout(xaxis_title=None, yaxis_title='Percentage of procedures covered', yaxis=dict(showgrid=False, tickformat=',.0%'), showlegend=False)
            encounter_coverage_grouped.update_traces(hovertemplate='<b>%{y:,.0%}</b>')
            st.plotly_chart(encounter_coverage_grouped, use_container_width=True, config={'displayModeBar': False})

        
        with tab8:
            df_procedure_coverage_grouped = df_procedure_coverage_grouped[df_procedure_coverage_grouped['START_MONTH'].isin([selected_month])].reset_index(drop=True)
            df_procedure_coverage_grouped = df_procedure_coverage_grouped.sort_values(['BASE_COST', 'DESCRIPTION'], ascending=[False, True]).head(5).reset_index(drop=True)
            
            highest_expense_group = df_procedure_coverage_grouped['DESCRIPTION'][0]
            highest_expense = df_procedure_coverage_grouped['BASE_COST'][0]
            start_month = df_cost_by_encounter_class_grouped['START_MONTH'][0]
            st.markdown(f'***{highest_expense_group}*** is the most expensive procedure on non-insured patients in {start_month}, with average cost of ***${highest_expense:,.0f}***.')
            
            procedure_coverage_grouped = px.bar(df_procedure_coverage_grouped, x='BASE_COST', y='DESCRIPTION', color='DESCRIPTION', orientation='h', color_discrete_sequence=['#c3e4ec'], color_discrete_map={highest_expense_group: '#048cb3'})
            procedure_coverage_grouped.update_layout(xaxis_title='Average cost of procedure', yaxis_title=None, showlegend=False)
            procedure_coverage_grouped.update_traces(textposition='inside', hovertemplate='<b>$%{x:,.2f}</b>')
            st.plotly_chart(procedure_coverage_grouped, use_container_width=True, config={'displayModeBar': False})
