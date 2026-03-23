import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Set page config
st.set_page_config(
    page_title="AI Usage Among 18-24 Year Olds",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better presentation
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 0.25rem solid #1f77b4;
    }
    .chart-container {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    conn = sqlite3.connect(r"c:\Users\22kel\OneDrive - Michigan State University\Coding\mydata.db")
    df = pd.read_sql_query("SELECT * FROM [in];", conn)
    conn.close()

    return df

df = load_data()

# Age range selector in sidebar
st.sidebar.header("🎯 Analysis Settings")
age_min, age_max = st.sidebar.slider(
    "Select Age Range for Analysis",
    min_value=int(df['age'].min()),
    max_value=int(df['age'].max()),
    value=(13, 17),  # Default to actual data range
    step=1,
    key="age_range"
)

# Filter data by selected age range
filtered_df = df[df['age'].between(age_min, age_max)].copy()

# Update title to reflect actual data
st.markdown(f'<h1 class="main-header">🤖 AI Usage Among {age_min}-{age_max} Year Olds</h1>', unsafe_allow_html=True)
st.markdown(f"### Research Analysis Dashboard (Ages {age_min}-{age_max})")

# Sidebar filters
st.sidebar.header("🎛️ Additional Filters")

# Demographic filters
st.sidebar.subheader("Demographics")
sex_filter = st.sidebar.multiselect(
    "Gender",
    options=["Male", "Female"],
    default=["Male", "Female"],
    key="sex_filter"
)

income_filter = st.sidebar.multiselect(
    "Income Level",
    options=["Less than $20,000", "$20,000-$39,999", "$40,000-$59,999", "$60,000-$99,999", "$100,000 or more"],
    default=["Less than $20,000", "$20,000-$39,999", "$40,000-$59,999", "$60,000-$99,999", "$100,000 or more"],
    key="income_filter"
)

# Get available states from filtered data
available_states = sorted(filtered_df['state'].value_counts().head(10).index.tolist())
state_filter = st.sidebar.multiselect(
    "Top States",
    options=available_states,
    default=available_states[:5] if len(available_states) >= 5 else available_states,
    key="state_filter"
)

# Apply additional filters to the age-filtered data
final_filtered_df = filtered_df.copy()

if sex_filter:
    sex_map = {"Male": 1, "Female": 2}
    sex_codes = [sex_map[s] for s in sex_filter]
    final_filtered_df = final_filtered_df[final_filtered_df['sex'].isin(sex_codes)]

if income_filter:
    income_map = {
        "Less than $20,000": 1,
        "$20,000-$39,999": 2,
        "$40,000-$59,999": 3,
        "$60,000-$99,999": 4,
        "$100,000 or more": 5
    }
    income_codes = [income_map[i] for i in income_filter if i in income_map]
    final_filtered_df = final_filtered_df[final_filtered_df['income'].isin(income_codes)]

if state_filter:
    final_filtered_df = final_filtered_df[final_filtered_df['state'].isin(state_filter)]

# Key metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Total Respondents", f"{len(final_filtered_df):,}")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    total_weight = final_filtered_df['weight'].sum()
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Weighted Sample Size", f"{total_weight:,.0f}")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    avg_weight = final_filtered_df['weight'].mean()
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Average Weight", f"{avg_weight:.3f}")
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    male_pct = (final_filtered_df[final_filtered_df['sex'] == 1]['weight'].sum() / total_weight) * 100
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Male Respondents", f"{male_pct:.1f}%")
    st.markdown('</div>', unsafe_allow_html=True)

# Main content tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Overview", "🎯 Survey Responses", "👥 Demographics", "📍 Geographic", "📈 Advanced Analysis"])

with tab1:
    st.header("Overview Dashboard")

    # AI Usage Summary
    st.subheader("AI Usage Patterns Overview")

    # Create summary of Q1 responses (assuming these are AI-related questions)
    q1_cols = ['q1_msua', 'q1_msub', 'q1_msuc', 'q1_msud']

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        # Response distribution for Q1
        response_counts = {}
        for col in q1_cols:
            for response in [1, 2, 3, 4]:
                response_data = final_filtered_df[final_filtered_df[col] == response]
                if len(response_data) > 0:
                    weighted_count = response_data['weight'].sum()
                    key = f"Q1-{col[-1]}: Response {response}"
                    response_counts[key] = weighted_count

        if response_counts:
            fig = px.bar(
                x=list(response_counts.keys()),
                y=list(response_counts.values()),
                title="AI Usage Response Distribution (Weighted)",
                labels={'x': 'Question & Response', 'y': 'Weighted Count'},
                color_discrete_sequence=['#1f77b4']
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        # Device usage among selected age group
        device_counts = final_filtered_df.groupby('device')['weight'].sum().reset_index()
        device_counts = device_counts.sort_values('weight', ascending=False)

        fig = px.pie(
            device_counts,
            values='weight',
            names='device',
            title=f"Device Usage Among {age_min}-{age_max} Year Olds",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.header("Detailed Survey Responses")

    # Survey question analysis
    st.subheader("AI Usage Questions Analysis")

    question_selected = st.selectbox(
        "Select Survey Question to Analyze",
        options=["Q1 (AI Usage)", "Q2 (AI Types)", "Q3 (AI Applications)", "Q4 (AI Concerns)", "Q5 (AI Future)"],
        key="question_select"
    )

    # Map question to columns
    question_map = {
        "Q1 (AI Usage)": ['q1_msua', 'q1_msub', 'q1_msuc', 'q1_msud'],
        "Q2 (AI Types)": ['q2_msua', 'q2_msub', 'q2_msuc', 'q2_msud', 'q2_msue', 'q2_msuf', 'q2_msug', 'q2_msuh'],
        "Q3 (AI Applications)": ['q3_msua', 'q3_msub', 'q3_msuc', 'q3_msud'],
        "Q4 (AI Concerns)": ['q4_msua', 'q4_msub', 'q4_msuc', 'q4_msud'],
        "Q5 (AI Future)": ['q5_msua', 'q5_msub', 'q5_msuc', 'q5_msud', 'q5_msue', 'q5_msuf', 'q5_msug', 'q5_msuh']
    }

    cols = question_map[question_selected]

    # Create response distribution chart
    response_data = []
    for col in cols:
        for response in sorted(final_filtered_df[col].dropna().unique()):
            if pd.notna(response):
                response_subset = final_filtered_df[final_filtered_df[col] == response]
                if len(response_subset) > 0:
                    weighted_count = response_subset['weight'].sum()
                    response_data.append({
                        'Question': col,
                        'Response': f'Response {int(response)}',
                        'Weighted_Count': weighted_count
                    })

    if response_data:
        response_df = pd.DataFrame(response_data)

        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig = px.bar(
            response_df,
            x='Question',
            y='Weighted_Count',
            color='Response',
            title=f"{question_selected} - Response Distribution (Weighted)",
            barmode='stack',
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Show detailed table
        st.subheader("Detailed Response Breakdown")
        pivot_table = response_df.pivot_table(
            values='Weighted_Count',
            index='Question',
            columns='Response',
            aggfunc='sum',
            fill_value=0
        )
        st.dataframe(pivot_table.style.format("{:.0f}"))

with tab3:
    st.header("Demographic Analysis")

    st.subheader("Demographic Breakdowns of AI Usage")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        # Gender distribution
        gender_counts = final_filtered_df.groupby('sex')['weight'].sum().reset_index()
        gender_counts['sex'] = gender_counts['sex'].map({1: 'Male', 2: 'Female'})

        fig = px.pie(
            gender_counts,
            values='weight',
            names='sex',
            title=f"Gender Distribution ({age_min}-{age_max})",
            color_discrete_sequence=['#1f77b4', '#ff7f0e']
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        # Income distribution
        income_counts = final_filtered_df.groupby('income')['weight'].sum().reset_index()
        income_map = {
            1: "Less than $20,000",
            2: "$20,000-$39,999",
            3: "$40,000-$59,999",
            4: "$60,000-$99,999",
            5: "$100,000 or more"
        }
        income_counts['income'] = income_counts['income'].map(income_map)

        fig = px.bar(
            income_counts,
            x='income',
            y='weight',
            title=f"Income Distribution ({age_min}-{age_max})",
            color_discrete_sequence=['#2ca02c']
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Cross-tabulation: Gender vs AI Usage
    st.subheader("Gender vs AI Usage Patterns")

    # Create cross-tab of gender vs Q1 responses
    cross_tab_data = []
    for sex_code, sex_name in [(1, 'Male'), (2, 'Female')]:
        sex_data = final_filtered_df[final_filtered_df['sex'] == sex_code]
        for col in ['q1_msua', 'q1_msub', 'q1_msuc', 'q1_msud']:
            for response in [1, 2, 3, 4]:
                response_data = sex_data[sex_data[col] == response]
                if len(response_data) > 0:
                    weighted_count = response_data['weight'].sum()
                    cross_tab_data.append({
                        'Gender': sex_name,
                        'Question': col,
                        'Response': f'Response {response}',
                        'Weighted_Count': weighted_count
                    })

    if cross_tab_data:
        cross_df = pd.DataFrame(cross_tab_data)

        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig = px.bar(
            cross_df,
            x='Question',
            y='Weighted_Count',
            color='Gender',
            facet_col='Response',
            title="AI Usage by Gender and Response Type",
            color_discrete_sequence=['#1f77b4', '#ff7f0e']
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

with tab4:
    st.header("Geographic Analysis")

    st.subheader("AI Usage by State/Region")

    # State-level analysis
    state_data = final_filtered_df.groupby('state')['weight'].sum().reset_index()
    state_data = state_data.sort_values('weight', ascending=False).head(15)

    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    fig = px.bar(
        state_data,
        x='state',
        y='weight',
        title=f"AI Usage by State (Top 15, Ages {age_min}-{age_max})",
        color_discrete_sequence=['#d62728']
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Region analysis
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        region_data = final_filtered_df.groupby('region4')['weight'].sum().reset_index()
        region_map = {1: 'Northeast', 2: 'Midwest', 3: 'South', 4: 'West'}
        region_data['region4'] = region_data['region4'].map(region_map)

        fig = px.pie(
            region_data,
            values='weight',
            names='region4',
            title="Regional Distribution",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        # Metro vs non-metro
        metro_data = final_filtered_df.groupby('metro')['weight'].sum().reset_index()
        metro_map = {1: 'Metro', 2: 'Non-Metro'}
        metro_data['metro'] = metro_data['metro'].map(metro_map)

        fig = px.pie(
            metro_data,
            values='weight',
            names='metro',
            title="Metro vs Non-Metro Distribution",
            color_discrete_sequence=['#9467bd', '#8c564b']
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

with tab5:
    st.header("Advanced Analysis")

    st.subheader("Statistical Insights & Correlations")

    # Summary statistics
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.subheader("Survey Response Summary Statistics")

    # Calculate response patterns
    summary_stats = []
    for col in ['q1_msua', 'q1_msub', 'q1_msuc', 'q1_msud']:
        col_data = final_filtered_df[col].dropna()
        if len(col_data) > 0:
            mean_response = (col_data * final_filtered_df.loc[col_data.index, 'weight']).sum() / final_filtered_df.loc[col_data.index, 'weight'].sum()
            most_common = col_data.mode().iloc[0] if len(col_data.mode()) > 0 else 'N/A'
            response_range = f"{col_data.min()}-{col_data.max()}"

            summary_stats.append({
                'Question': col,
                'Mean Response': round(mean_response, 2),
                'Most Common': most_common,
                'Response Range': response_range,
                'Total Responses': len(col_data)
            })

    if summary_stats:
        stats_df = pd.DataFrame(summary_stats)
        st.dataframe(stats_df.style.format({
            'Mean Response': '{:.2f}',
            'Total Responses': '{:,}'
        }))
    st.markdown('</div>', unsafe_allow_html=True)

    # Weighted vs Unweighted comparison
    st.subheader("Weighted vs Unweighted Comparison")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        # Unweighted gender distribution
        unweighted_gender = final_filtered_df['sex'].value_counts().reset_index()
        unweighted_gender['sex'] = unweighted_gender['index'].map({1: 'Male', 2: 'Female'})

        fig = px.pie(
            unweighted_gender,
            values='count',
            names='sex',
            title="Unweighted Gender Distribution",
            color_discrete_sequence=['#1f77b4', '#ff7f0e']
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        # Weighted gender distribution (already shown above)
        weighted_gender = final_filtered_df.groupby('sex')['weight'].sum().reset_index()
        weighted_gender['sex'] = weighted_gender['sex'].map({1: 'Male', 2: 'Female'})

        fig = px.pie(
            weighted_gender,
            values='weight',
            names='sex',
            title="Weighted Gender Distribution",
            color_discrete_sequence=['#1f77b4', '#ff7f0e']
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("### 📊 AI Usage Research Dashboard")
st.markdown(f"**Data Source:** Survey of {age_min}-{age_max} year olds | **Analysis:** Weighted responses | **Focus:** AI adoption and usage patterns")
st.markdown("Built with Streamlit & Plotly | Ready for Vercel deployment")

# Add export functionality
if st.sidebar.button("📥 Export Summary to CSV"):
    # Create summary data for export
    summary_data = {
        'Metric': ['Total Respondents', 'Weighted Sample', 'Male %', 'Female %', 'Age Range'],
        'Value': [
            len(final_filtered_df),
            final_filtered_df['weight'].sum(),
            (final_filtered_df[final_filtered_df['sex'] == 1]['weight'].sum() / final_filtered_df['weight'].sum()) * 100,
            (final_filtered_df[final_filtered_df['sex'] == 2]['weight'].sum() / final_filtered_df['weight'].sum()) * 100,
            f"{age_min}-{age_max}"
        ]
    }
    summary_df = pd.DataFrame(summary_data)
    csv = summary_df.to_csv(index=False)
    st.sidebar.download_button(
        label="Download Summary CSV",
        data=csv,
        file_name="ai_usage_summary.csv",
        mime="text/csv"
    )