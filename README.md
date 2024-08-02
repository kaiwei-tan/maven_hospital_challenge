# Overview
For the Maven Hospital Challenge, I play an analytics consultant reporting high-level KPIs for the executive team of Massachusetts General Hospital (MGH), which should help them quickly understand their performance in certain key areas.

My submission for this challenge is available as a dashboard on [Streamlit Cloud](https://maven-hospital-challenge-kaiweitan.streamlit.app/).

## Approach
I approached this task by imagining a meeting between hospital executives and building a dashboard which would provide talking points for the attendees. Having experienced building slides and dashboards for C-suite meetings, I recognized that such a dashboard would have to be as simple as possible - conveying the exact amount of information they need to make decisions (no more, no less).

As such, I structured the project in a way that could tell a story about the hospital's performance, and then lead to some descriptive analytics, where attendees could take away actionable insights. Being an executive-level overview, information also needed to be delivered in as simple visualizations as possible.

Fortunately, to anchor this story, the case provided 4 key metrics which appeared most important to the executive team. Below are my interpretations on their implications:
- **Readmission rates**: Relates to quality of treatment
- **Length of stay**: Relates to process efficiency
- **Encounter cost**: Relates to cost management
- **Insurance coverage**: Relates to insurance relations

# Data
The dataset contained about 11 years (2011 to 2022) of records of individual hospital visits (encounters), which are linked to information on patient identities/demographics, procedures conducted, costs, and insurance.

From the data, it was possible to query in depth information of each encounters, from who the patient was, to how long it took, what procedures the patient underwent, how much it cost, and how much was covered by insurance (if any).

# Assumptions
I made some assumptions on the expected audience of the report, which would influence its design as seen below.

## Stakeholders
This page on MGH leadership provided some clues as to who might show up in meetings where this report would be used. Besides the usual expected corporate leadership, the source points towards Chairs of Service (presumably heads of department) possibly being attendees as well.

This meant that medical departments under MGH should be able to take away some high-level ideas on what to improve from the report as well.

## Frequency
This blog post provided some insights on the routine of a healthcare executive. The main takeaway from this post was that board meetings could be as frequent as once a month. As such, I decided to design the dashboard such that monthly reports could be provided.

## Time frame
Given that 2022-01 was the last complete month in the data, I provided monthly reports

# Dashboard
Since simplicity was key in this dashboard, the overall design intends to make navigation as minimal as possible. Visualizations are also made as simple as possible, so information can be digested easily and quickly.

Here is how I imagine an executive meeting would be conducted, with the report as the visual material:
- Select the correct month's report (should be the latest complete month by default)
- View key metrics on top
- Using the trend graphs below, compare this month's key metrics with the previous month
- Switching to descriptive graphs below, discuss the areas of improvement with relation to the changes in key metrics from the previous month
This assumed meeting flow is hence reflected in how elements of the report are ordered.

## Current month performance
![image](https://github.com/user-attachments/assets/39b62bac-6622-42de-8899-f7aa7d2e2c21)
This is what shows up first upon selecting a particular month's report. These are simply numbers which the audience can digest relatively easily and quickly.

## Month-on-month (MoM) comparisons
From my experience observing executive-level meetings, and they often like to compare the current period with the previous. As such, this part of the report provides the talking points they need, divided into 4 sections relating to the key metrics (patient admissions, length of stay, encounter cost, and insurance coverage) as mentioned earlier.

A choice I made in the visualization was to use bar graphs instead of line graphs (which may be the more expected choice for time series data). This is because we are only comparing between two months every time, and in this case bars would have more visual impact.

Similar to PowerPoint presentations, I also conditionally-generated headlines for each section to convey the intended message of their respective visualizations.
![image](https://github.com/user-attachments/assets/73d13da7-215b-4d70-904f-f685f6fd8f70)

## Descriptive drill-down
I was initially hesitant on including these visualizations as I felt that the above might already be enough material for a 30-minute discussion. However, I decided that further insights are important in furthering the story of this report, and by providing the additional information in separate tabs, we leave it as a choice for presenters.

Because of the variety of fields available, I found myself with a lot of freedom of what to present here. I decided on what to show for each section as a continuation of what was already presented regarding the key metrics (patient admissions, length of stay, encounter cost, and insurance coverage):
- **Patient admissions**: By showing which age groups have been readmitted the most, respective departments can optimize care for more vulnerable age groups accordingly.
- **Length of stay**: By showing which age groups spend the most time in the hospital, various hospital services can improve speed and response times for more vulnerable age groups accordingly.
- **Encounter cost**: By showing which encounter classes cost the most, related hospital services can manage their costs accordingly.
- **Insurance coverage**: By showing which procedures are most costly for non-insured patients, insurance relations can work with providers on improving coverage for these procedures.
![image](https://github.com/user-attachments/assets/ff2f9629-ed02-4077-ba91-848d1f650fe9)

## Color scheme
Overall this report uses a simple (teal) color scheme based on the MGH logo. In line with the design simplicity, all graphs only use two colors - the darker color highlights key information, while all other elements use a lighter color.
