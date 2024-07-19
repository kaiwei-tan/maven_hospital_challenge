import streamlit as st
import pandas as pd
import numpy as np

def transform_encounters(encounters):
    encounters['START'] = pd.to_datetime(encounters['START'])
    encounters['STOP'] = pd.to_datetime(encounters['STOP'])
    encounters['START_MONTH'] = encounters['START'].dt.strftime('%Y-%m')
    encounters['STAY_DURATION'] = (encounters['STOP'] - encounters['START']) / pd.Timedelta(hours=1)

    return encounters

def create_df_admissions(encounters, patients, age_groups:dict, current_date):
    df_admissions = pd.merge(
        encounters[['Id', 'START', 'START_MONTH', 'PATIENT', 'ENCOUNTERCLASS']],
        patients[['Id', 'BIRTHDATE', 'GENDER']].rename(columns={'Id': 'PATIENT'}),
        on='PATIENT',
        how='left'
    )

    df_admissions['AGE'] = (pd.to_datetime(current_date) - pd.to_datetime(df_admissions['BIRTHDATE'])).apply(lambda x: np.floor(x.days/365.25)).astype(int)
    df_admissions['AGE_GROUP'] = None
    for age_group, age_range in age_groups.items():
        df_admissions['AGE_GROUP'] = np.where(
            (df_admissions['AGE'] >= age_range[0]) & (df_admissions['AGE'] <= age_range[1]),
            age_group,
            df_admissions['AGE_GROUP']
        )

    df_admissions['IS_ADMISSION'] = np.where(df_admissions['ENCOUNTERCLASS'] == 'inpatient', 1, 0)
    df_admissions['ADMISSION_ORDER'] = df_admissions.groupby(['PATIENT', 'IS_ADMISSION'])['START'].rank().astype(int)
    df_admissions['IS_READMISSION'] = np.where((df_admissions['IS_ADMISSION'] == 1) & (df_admissions['ADMISSION_ORDER'] > 1), 1, 0)

    return df_admissions

@st.cache_data
def get_admissions_grouped(df_admissions):
    df_admissions_grouped = df_admissions.groupby('START_MONTH').agg(
        PATIENTS = ('PATIENT', 'nunique'),
        ADMISSIONS = ('IS_ADMISSION', 'sum'),
        READMISSIONS = ('IS_READMISSION', 'sum'), 
    ).reset_index()

    return df_admissions_grouped

@st.cache_data
def get_readmissions_grouped(df_admissions):
    df_readmissions_grouped = df_admissions.groupby(['START_MONTH', 'AGE_GROUP']).agg(
        ADMISSIONS = ('IS_ADMISSION', 'sum'),
        READMISSIONS = ('IS_READMISSION', 'sum'),
    ).reset_index()

    df_readmissions_grouped['READMISSION_RATE'] = df_readmissions_grouped['READMISSIONS'] / df_readmissions_grouped['ADMISSIONS']
    df_readmissions_grouped = df_readmissions_grouped.dropna()

    return df_readmissions_grouped

def create_df_length(encounters, patients, age_groups:dict, current_date):
    df_length = pd.merge(
    encounters[['Id', 'START', 'STOP', 'START_MONTH', 'PATIENT', 'STAY_DURATION']],
    patients[['Id', 'BIRTHDATE', 'GENDER']].rename(columns={'Id': 'PATIENT'}),
    on='PATIENT',
    how='left'
    )

    df_length['AGE'] = (pd.to_datetime(current_date) - pd.to_datetime(df_length['BIRTHDATE'])).apply(lambda x: np.floor(x.days/365.25)).astype(int)
    df_length['AGE_GROUP'] = None
    for age_group, age_range in age_groups.items():
        df_length['AGE_GROUP'] = np.where(
            (df_length['AGE'] >= age_range[0]) & (df_length['AGE'] <= age_range[1]),
            age_group,
            df_length['AGE_GROUP']
        )

    return df_length

@st.cache_data
def get_length_grouped(df_length):
    df_length_grouped = df_length.groupby('START_MONTH').agg(
        AVERAGE_DURATION = ('STAY_DURATION', 'mean')
    ).reset_index()

    return df_length_grouped

@st.cache_data
def get_length_by_age_group_grouped(df_length):
    df_length_grouped = df_length.groupby(['START_MONTH', 'AGE_GROUP']).agg(
        AVERAGE_DURATION = ('STAY_DURATION', 'mean')
    ).reset_index()

    return df_length_grouped

def get_df_cost(encounters):
    df_cost = encounters[['Id', 'START', 'START_MONTH', 'ENCOUNTERCLASS', 'TOTAL_CLAIM_COST']]

    return df_cost

@st.cache_data
def get_cost_grouped(df_cost):
    df_cost_grouped = df_cost.groupby('START_MONTH').agg(
        AVERAGE_COST = ('TOTAL_CLAIM_COST', 'mean')
    ).reset_index()
    
    return df_cost_grouped

@st.cache_data
def get_cost_by_encounter_class_grouped(df_cost):
    df_cost_grouped = df_cost.groupby(['START_MONTH', 'ENCOUNTERCLASS']).agg(
        AVERAGE_COST = ('TOTAL_CLAIM_COST', 'mean')
    ).reset_index()

    return df_cost_grouped

def get_df_encounter_coverage(encounters, payers, procedures):
    df_encounter_coverage = pd.merge(
        encounters[['Id', 'PATIENT', 'START', 'START_MONTH', 'TOTAL_CLAIM_COST', 'PAYER_COVERAGE', 'PAYER']],
        payers[['Id', 'NAME']].rename(columns={'Id': 'PAYER'}),
        on='PAYER',
        how='left'
    )

    df_encounter_coverage['IS_COVERED'] = np.where(df_encounter_coverage['NAME'] == 'NO_INSURANCE', 0, 1)

    df_procedures = procedures.groupby(['ENCOUNTER', 'PATIENT']).agg(
        PROCEDURES = ('ENCOUNTER', 'count'),
        TOTAL_PROCEDURE_COST = ('BASE_COST', 'sum')
    ).reset_index()

    df_encounter_coverage = df_encounter_coverage.merge(
        df_procedures.rename(columns={'ENCOUNTER': 'Id'}),
        on=['Id', 'PATIENT'],
        how='left'
    )

    df_encounter_coverage['PROCEDURES'] = df_encounter_coverage['PROCEDURES'].fillna(0).astype(int)
    df_encounter_coverage['TOTAL_PROCEDURE_COST'] = df_encounter_coverage['TOTAL_PROCEDURE_COST'].fillna(0)

    return df_encounter_coverage

@st.cache_data
def get_encounter_coverage_grouped(df_encounter_coverage):
    df_encounter_coverage_grouped = df_encounter_coverage.groupby(['START_MONTH', 'IS_COVERED']).agg(
        PROCEDURES = ('PROCEDURES', 'sum'),
        PROCEDURE_COST = ('TOTAL_PROCEDURE_COST', 'sum')
    ).reset_index()

    df_encounter_coverage_grouped_temp = df_encounter_coverage.groupby(['START_MONTH']).agg(
        TOTAL_PROCEDURES = ('PROCEDURES', 'sum'),
        TOTAL_PROCEDURE_COST = ('TOTAL_PROCEDURE_COST', 'sum')
    ).reset_index()

    df_encounter_coverage_grouped = df_encounter_coverage_grouped.merge(df_encounter_coverage_grouped_temp, on='START_MONTH')
    df_encounter_coverage_grouped = df_encounter_coverage_grouped[df_encounter_coverage_grouped['IS_COVERED'] == 1]
    df_encounter_coverage_grouped['COVERAGE_RATE_COUNT'] = df_encounter_coverage_grouped['PROCEDURES'] / df_encounter_coverage_grouped['TOTAL_PROCEDURES']
    df_encounter_coverage_grouped['COVERAGE_RATE_COST'] = df_encounter_coverage_grouped['PROCEDURE_COST'] / df_encounter_coverage_grouped['TOTAL_PROCEDURE_COST']

    return df_encounter_coverage_grouped

def create_df_procedure_coverage(procedures, df_encounter_coverage):
    df_procedure_coverage = pd.merge(
        procedures[['ENCOUNTER', 'PATIENT', 'DESCRIPTION', 'BASE_COST']].rename(columns={'ENCOUNTER': 'Id'}),
        df_encounter_coverage[['Id', 'PATIENT', 'START', 'START_MONTH', 'IS_COVERED']],
        on=['Id', 'PATIENT'],
        how='left'
    )

    return df_procedure_coverage

@st.cache_data
def get_procedure_coverage_grouped(df_procedure_coverage):
    df_procedure_coverage_grouped = df_procedure_coverage[df_procedure_coverage['IS_COVERED'] == 0].groupby(['START_MONTH', 'DESCRIPTION']).agg(
        BASE_COST = ('BASE_COST', 'mean')
    ).reset_index()

    return df_procedure_coverage_grouped