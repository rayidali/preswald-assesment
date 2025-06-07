import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from preswald import text, table, plotly
import duckdb

######################################################################################
# 0. Color Scheme & Plot Theme
######################################################################################
# I'm using a cohesive color scheme and applying a uniform style to all Plotly figures.

COLOR_SCHEME = {
    'primary': '#2C3E50',    # Dark blue
    'secondary': '#3498DB',  # Light blue
    'accent': '#E74C3C',     # Red
    'background': '#ECF0F1'  # Light gray
}

def apply_theme(fig):
    """Apply a consistent design theme to Plotly figures."""
    fig.update_layout(
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(
            family="Arial, sans-serif",
            size=12,
            color=COLOR_SCHEME['primary']
        ),
        title=dict(
            font=dict(
                size=20,
                color=COLOR_SCHEME['primary']
            ),
            x=0.5,
            xanchor='center'
        ),
        margin=dict(t=40, l=20, r=20, b=20)
    )
    return fig

######################################################################################
# 1. Introduction & Dataset Background
######################################################################################
text("# 🏆 AI Job Market & Cost of Living Analysis for 2025\n")

text("""
I am excited to share my data-driven exploration of the 2025 AI job market. In this report, 
I integrate two main datasets:

1. **AI Job Market & Salary Analysis 2025**  
   - **Source**: Multiple job platforms (e.g., LinkedIn, Indeed, Glassdoor).  
   - **Scope**: 15,000+ positions from 50+ countries.  
   - **Key Columns**: Salary (USD), Experience Level, Remote Ratio, Required Skills, 
     Posting Date, and more.  
   - **Potential Use Cases**: Salary prediction, geographic trend analysis, skill demand insights.

2. **Cost of Living (CoL) 2024**  
   - **Source**: [Numbeo](https://www.numbeo.com/cost-of-living/cpi_explained.jsp).  
   - **Scope**: Indexes relative to New York City (NYC = 100).  
   - **Key Indices**:  
       - **Cost of Living Index (Excl. Rent)**  
       - **Cost of Living Plus Rent Index**  
       - **Local Purchasing Power Index**  
   - **Interpretation**: If a city's Cost of Living Index is 120, it is ~20% more expensive 
     than NYC (excluding rent). A Local Purchasing Power of 40 means, on average, 
     the purchasing power is 60% lower than NYC.

By merging these datasets, I can address important questions such as:  
- Does living in a region with a *high* nominal salary actually provide strong **real** purchasing power?  
- Which countries strike the best balance between **competitive salaries** and **affordable living**?

Let's dive in!
""")

######################################################################################
# 2. Load & Validate the Main AI Dataset
######################################################################################
df = pd.read_csv('data/my_data.csv')

text("## 1) AI Job Dataset Quality & Overview\n")

text("""
First, I'll examine the **AI Job dataset**. This dataset, titled 
**Global AI Job Market & Salary Trends 2025**, encompasses 15,000+ postings 
covering a range of roles and countries. It's perfect for analyzing 
compensation, in-demand skills, and remote work patterns.
""")

# A. Missing Values
missing_values = df.isnull().sum()
missing_df = pd.DataFrame({
    'Column': missing_values.index,
    'Missing Values': missing_values.values,
    'Percentage': (missing_values.values / len(df) * 100).round(2)
})

text("### A. Missing Values Analysis")
table(missing_df, title="📝 Missing Values by Column")

# B. Salary Distribution
salary_stats = df['salary_usd'].describe().round(2)
text("### B. Salary Statistics")
table(pd.DataFrame(salary_stats).reset_index(), title="📊 Salary Stats")

# C. Identify Outliers
Q1 = df['salary_usd'].quantile(0.25)
Q3 = df['salary_usd'].quantile(0.75)
IQR = Q3 - Q1
outliers = df[
    (df['salary_usd'] < (Q1 - 1.5 * IQR)) | 
    (df['salary_usd'] > (Q3 + 1.5 * IQR))
]
text(f"🔎 I identified {len(outliers)} potential outliers in the salary range. "
     "These might be very high or very low salaries, but I'll keep them for now "
     "unless they distort the overall analysis.")

# D. Experience Level Distribution - Now as a Visualization
if 'experience_level' in df.columns:
    text("### C. Visualizing Experience Level Distribution\n")
    exp_levels_count = df['experience_level'].value_counts().reset_index()
    exp_levels_count.columns = ['experience_level','count']

    fig_exp = px.bar(
        exp_levels_count,
        x='experience_level',
        y='count',
        title="Count of Job Postings by Experience Level",
        color='experience_level'
    )
    fig_exp = apply_theme(fig_exp)
    plotly(fig_exp)

    text("""
I plotted the frequency of each **experience_level**. This can help me see, for example, 
whether Senior (SE) positions dominate the dataset or if Entry (EN) roles are equally common.
""")

######################################################################################
# 3. Preliminary Data Exploration
######################################################################################
text("# 2) Preliminary Exploration\n")
text("""
Now I'll do a high-level analysis of correlations, salary distributions by experience, 
and time-series trends in AI job postings.
""")

# A) Correlation Analysis
text("### A. Correlation Matrix of Key Metrics\n")
numeric_cols = ['salary_usd', 'years_experience', 'benefits_score', 'remote_ratio']
corr_df = df[numeric_cols].corr().round(2)

fig_corr = px.imshow(
    corr_df,
    title="Correlation Matrix (Salary, Experience, Benefits, Remote)",
    color_continuous_scale='RdBu',
    aspect='auto'
)
fig_corr = apply_theme(fig_corr)
plotly(fig_corr)

text("""
Here, I'm checking if there's a strong correlation between salary and years of experience, 
or if remote jobs typically pay more or less. Deeper reds or blues on the matrix 
would indicate strong correlations (positive or negative).
""")

# B) Salary Distribution by Experience
text("### B. Salary Distribution by Experience\n")
fig_salary_dist = px.box(
    df,
    x="experience_level",
    y="salary_usd",
    title="Salary Distribution per Experience Level",
    color="experience_level",
    color_discrete_sequence=px.colors.qualitative.Set3
)
fig_salary_dist = apply_theme(fig_salary_dist)
plotly(fig_salary_dist)

text("""
Box plots allow me to see the median, quartiles, and outliers. I notice that 
Executive (EX) roles might have a higher median salary, but occasionally 
some Senior (SE) roles surpass that.
""")

# C) Time-Series Analysis
text("### C. Time-Series of Job Postings & Salaries\n")
df['month'] = pd.to_datetime(df['posting_date']).dt.strftime('%Y-%m')
time_series_df = df.groupby('month').agg({
    'job_id': 'count',
    'salary_usd': 'mean',
    'years_experience': 'mean'
}).reset_index()

time_series_df['job_growth'] = time_series_df['job_id'].pct_change() * 100
time_series_df['salary_growth'] = time_series_df['salary_usd'].pct_change() * 100

fig_ts = go.Figure()
fig_ts.add_trace(go.Scatter(
    x=time_series_df['month'],
    y=time_series_df['job_id'],
    name="Job Postings",
    line=dict(color=COLOR_SCHEME['primary'], width=2)
))
fig_ts.add_trace(go.Scatter(
    x=time_series_df['month'],
    y=time_series_df['salary_usd'],
    name="Avg Salary",
    line=dict(color=COLOR_SCHEME['secondary'], width=2),
    yaxis="y2"
))
fig_ts.update_layout(
    title="Monthly Job Postings vs. Average Salary",
    yaxis2=dict(overlaying="y", side="right"),
    showlegend=True,
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
)
fig_ts = apply_theme(fig_ts)
plotly(fig_ts)

text("""
I'm using a dual-axis chart: the left axis tracks the number of job postings, while the right 
axis measures average salaries over time. If there's a significant spike in postings, 
I might see either a subsequent dip or rise in salary depending on supply-demand dynamics.
""")

######################################################################################
# 4. SQL-Based Insights (Skills & Remote Work & Geographic)
######################################################################################
text("# 3) SQL-Driven Insights\n")

text("""
To dig deeper, I use DuckDB to run SQL queries on this dataset. This approach 
makes grouping, filtering, and aggregation straightforward, while letting me 
present results in an interactive format.
""")

con = duckdb.connect(database=':memory:')
con.register('jobs', df)

# 4a) Skills Analysis
if 'required_skills' in df.columns:
    text("### A. Top Required Skills\n")
    skills_query = """
    WITH split_skills AS (
        SELECT TRIM(unnest(string_split(required_skills, ','))) as skill
        FROM jobs
    )
    SELECT skill, COUNT(*) as count
    FROM split_skills
    WHERE skill != ''
    GROUP BY skill
    ORDER BY count DESC
    LIMIT 10
    """
    skills_df = con.execute(skills_query).df()
    
    fig_skills = px.bar(
        skills_df,
        x="skill",
        y="count",
        title="Top 10 Most Requested Skills",
        color="count",
        color_continuous_scale='Viridis'
    )
    fig_skills = apply_theme(fig_skills)
    plotly(fig_skills)

    text("""
Here, I can see which skills appear most frequently in AI job postings. 
Common contenders are Python, TensorFlow, PyTorch, and cloud platforms like AWS or GCP.
""")

# 4b) Remote Work Analysis - Visualization Instead of Table
text("### B. Remote Work Analysis\n")
remote_stats_query = """
SELECT 
    remote_ratio,
    ROUND(AVG(salary_usd), 2) as avg_salary,
    COUNT(*) as job_count
FROM jobs
GROUP BY remote_ratio
ORDER BY remote_ratio
"""
remote_stats = con.execute(remote_stats_query).df()

text("""
I'm exploring how average salaries and job counts vary with different remote ratios:
- **0%** = Fully On-Site
- **50%** = Hybrid
- **100%** = Fully Remote
""")

fig_remote = px.bar(
    remote_stats,
    x='remote_ratio',
    y='avg_salary',
    color='remote_ratio',
    title='Average Salary by Remote Ratio',
    text='avg_salary'
)
fig_remote = apply_theme(fig_remote)
plotly(fig_remote)

text("""
From this chart, I can tell if fully remote roles (100% ratio) typically pay higher or lower 
than on-site or hybrid roles. I also look at how many such roles exist in the dataset.
""")

# 4c) Geographic Analysis
text("### C. Geographic Analysis\n")
geo_stats_query = """
SELECT 
    company_location,
    ROUND(AVG(salary_usd), 2) as avg_salary,
    COUNT(*) as job_count,
    ROUND(AVG(remote_ratio), 2) as avg_remote_ratio
FROM jobs
GROUP BY company_location
ORDER BY avg_salary DESC
LIMIT 10
"""
geo_stats = con.execute(geo_stats_query).df()

text("""
Below are the top 10 countries by average salary, along with job counts and average 
remote ratios. This provides a quick glimpse into which regions might be most lucrative.
""")
table(geo_stats, title="🌍 Top 10 Countries by Avg Salary")

fig_map = px.choropleth(
    geo_stats,
    locations='company_location',
    locationmode='country names',
    color='avg_salary',
    hover_name='company_location',
    hover_data={
        'avg_salary': ':$.2f',
        'job_count': True,
        'avg_remote_ratio': ':,.0%'
    },
    color_continuous_scale='Viridis',
    title='Global Distribution of AI Job Salaries'
)
fig_map = apply_theme(fig_map)
plotly(fig_map)

######################################################################################
# 5. Cost of Living Data & PPP Calculations
######################################################################################
text("# 4) Incorporating Cost of Living (CoL) for a Realistic Salary View\n")

text("""
One of my primary objectives is to calculate a **PPP (Purchasing Power Parity) - adjusted salary**. 
A high nominal salary might not go far in a very expensive area. Conversely, a moderate salary might 
have excellent purchasing power in a more affordable country.

**Cost of Living Dataset**  
According to [Numbeo](https://www.numbeo.com/cost-of-living/cpi_explained.jsp), 
all indices are relative to NYC = 100.  
- **Cost of Living Index**: Excludes rent or mortgage.  
- **Rent Index**: Reflects rental costs vs. NYC.  
- **Cost of Living Plus Rent Index**: A combined figure.  
- **Local Purchasing Power Index**: If 40, it means ~60% lower purchasing power than NYC.

I'll merge this dataset with our AI jobs data using DuckDB, then compute an adjusted salary metric.
""")

# A) Load CoL Data
col_df = pd.read_csv('data/cost_of_living_2024.csv')

text("### A. Cost of Living Data Overview\n")
col_missing = col_df.isnull().sum()
col_missing_df = pd.DataFrame({
    'Column': col_missing.index,
    'Missing': col_missing.values
})

table(col_missing_df, title="Missing Values in CoL Dataset")

desc_col = col_df.describe(include='all').round(2)
table(desc_col.reset_index(), title="Cost of Living Dataset Stats")

text("""
Numbeo's data covers multiple aspects such as groceries, restaurants, and local purchasing power, 
all with NYC = 100 as a baseline.
""")

# B) Merge Datasets
text("### B. Merging CoL Data with AI Jobs\n")
con.register('cost_living', col_df)

merge_query = """
SELECT 
  j.*,
  c."Cost of Living Index" AS col_index,
  c."Cost of Living Plus Rent Index" AS col_plus_rent,
  c."Local Purchasing Power Index" AS lpp
FROM jobs j
LEFT JOIN cost_living c
  ON TRIM(j.company_location) = TRIM(c."Country")
"""
merged_df = con.execute(merge_query).df()

table(merged_df.head(6), title="Merged AI Jobs + CoL Data (Sample)")

text("""
I now have columns like `col_index`, `col_plus_rent`, and `lpp` merged onto each row, 
matching by **company_location**. 
""")

# C) Weighted CoL & PPP Formula
text("### C. Weighted Cost of Living & PPP Salary Calculation\n")

text("""
**Equation** for my PPP Salary:

PPP_Salary = salary_usd * (Local Purchasing Power / 100) / (Weighted CoL / 100)

Where:
- Weighted CoL = 50% * Cost of Living Index + 50% * Cost of Living Plus Rent Index
- Local Purchasing Power is clamped between 30 and 80
- Weighted CoL is clamped between 40 and 150
- Only salaries >= 2000 USD are considered
""")

merged_df['col_index'] = pd.to_numeric(merged_df['col_index'], errors='coerce')
merged_df['col_plus_rent'] = pd.to_numeric(merged_df['col_plus_rent'], errors='coerce')
merged_df['lpp'] = pd.to_numeric(merged_df['lpp'], errors='coerce')

def weighted_col(row):
    if pd.notnull(row['col_index']) and pd.notnull(row['col_plus_rent']):
        val = 0.5 * row['col_index'] + 0.5 * row['col_plus_rent']
    elif pd.isnull(row['col_index']) and pd.isnull(row['col_plus_rent']):
        return None
    else:
        val = row['col_index'] if pd.notnull(row['col_index']) else row['col_plus_rent']
    return max(40, min(val, 150))

def clamp_lpp(x):
    if pd.isnull(x):
        return None
    return max(30, min(x, 80))

merged_df['weighted_col'] = merged_df.apply(weighted_col, axis=1)
merged_df['clamped_lpp'] = merged_df['lpp'].apply(clamp_lpp)

def compute_ppp(row):
    if pd.isnull(row['weighted_col']) or pd.isnull(row['clamped_lpp']):
        return None
    if row['salary_usd'] < 2000:
        return None
    return row['salary_usd'] * (row['clamped_lpp'] / 100.0) / (row['weighted_col'] / 100.0)

merged_df['PPP_Salary'] = merged_df.apply(compute_ppp, axis=1)
filtered_df = merged_df.dropna(subset=['PPP_Salary']).copy()

# D) Outlier Removal via IQR
Q1_p = filtered_df['PPP_Salary'].quantile(0.25)
Q3_p = filtered_df['PPP_Salary'].quantile(0.75)
IQR_p = Q3_p - Q1_p
low_cut = Q1_p - 1.5 * IQR_p
high_cut = Q3_p + 1.5 * IQR_p

final_df = filtered_df[(filtered_df['PPP_Salary'] >= low_cut) & (filtered_df['PPP_Salary'] <= high_cut)].copy()

text("#### Checking the Distribution of Our Final PPP Salaries")
ppp_desc = final_df['PPP_Salary'].describe().round(2)
table(ppp_desc.reset_index(), title="PPP Salary Stats (Post-Filter)")

######################################################################################
# 6. Ranking Countries by PPP Salary
######################################################################################
text("### D. Ranking Countries by PPP Salary (≥10 Job Postings)\n")

text("""
Finally, I want to see which countries stand out once I've adjusted for cost of living 
and local purchasing power. I only include countries that have **at least 10 job postings** 
for more reliable averages.
""")

con.register('final_table', final_df)
ranking_query = """
WITH country_agg AS (
    SELECT 
        company_location,
        AVG(salary_usd) AS avg_nominal,
        AVG(PPP_Salary) AS avg_ppp,
        COUNT(*) AS job_count
    FROM final_table
    GROUP BY company_location
)
SELECT
  company_location,
  ROUND(avg_nominal, 2) AS avg_nominal_salary,
  ROUND(avg_ppp, 2) AS avg_ppp_salary,
  job_count
FROM country_agg
WHERE job_count >= 10
ORDER BY avg_ppp_salary DESC
LIMIT 10
"""
best_countries = con.execute(ranking_query).df()

table(best_countries, title="🌍 Top 10 Countries by PPP-Adjusted Salary")

fig_best = px.bar(
    best_countries,
    x='company_location',
    y='avg_ppp_salary',
    hover_data=['avg_nominal_salary','job_count'],
    title='PPP-Adjusted Salary Ranking (Aggressive Filtering)'
)
fig_best = apply_theme(fig_best)
plotly(fig_best)

text("""
If a country still appears unusually high after all this filtering, it's likely due to the 
underlying data: either the cost of living index is too low or local purchasing power is too high, 
or the AI dataset has only elite positions listed for that region.
""")

######################################################################################
# 7. Conclusion & Next Steps
######################################################################################
text("## 5) Conclusion & Next Steps\n")

text("""
**In summary**, I combined a **Global AI Job Market** dataset with a 
**Cost of Living** dataset from Numbeo to get a sense of 'real' salary potential. 
By carefully filtering out outliers and clamping suspiciously high or low cost-of-living values, 
I aimed to make the PPP (Purchasing Power Parity) salary metric more realistic.

**Key Observations**:
1. Certain roles, especially at the Senior and Executive levels, command notable pay.
2. Remote opportunities can offer strong compensation, though it's not always higher than onsite.
3. Once cost of living is factored in, some countries that appear average at first might have 
   excellent 'bang for your buck,' while high-paying regions can lose some luster if rents 
   and daily expenses are very high.

**Challenges**:
- If any region still shows inflated PPP salaries, it likely means the data for 
  cost of living or job listings in that region is incomplete or not representative of the norm.
- Manual data cleaning or adjusting thresholds further (like requiring a minimum of 20 job postings) 
  can improve reliability.

**Future Directions**:
- Adding GDP growth or unemployment data could show how economic factors intertwine with AI salaries.
- A deeper skills analysis might reveal which competencies specifically drive up PPP salaries.

Thank you for reading my report! I hope this provides helpful insights into how to incorporate 
cost-of-living metrics into AI salary analyses.
""")

# Close the DuckDB connection
con.close()

text("---")
text("### ✅ End of Report")
text("I hope you found these findings as fascinating as I did. "
     "Feel free to reach out with any questions or suggestions for deeper exploration!")
