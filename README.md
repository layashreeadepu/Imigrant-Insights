# ✨ Immigrant Job Insights: Trends, Shifts & Forecasts ✨

## 🌟 Project Summary  
**Forecasting occupational trends among immigrants using two decades of U.S. lawful permanent residency data**

This project analyzes 18 years of occupational data from immigrants granted lawful permanent residency in the U.S. The analysis highlights historical shifts, emerging patterns, and predicts future occupational demand across major job sectors. Motivated by personal job search challenges and immigration constraints, this project offers data-backed insights for students, professionals, and policymakers navigating employment dynamics in the U.S.

## 📊 Data Source  
The data was sourced from the **Office of Homeland Security Statistics (2005–2022)** through extensive automation and web scraping. Key characteristics:
- 📁 Over **4,000 Excel files** downloaded using Selenium automation
- 🌍 Coverage includes **200+ countries**
- 📆 Tracks **year-wise occupational classifications**
- 🧹 Transformed into a unified dataset with **81,000+ rows** across 177 countries

## 🛠️ Project Components

### 🔍 Data Collection & Preprocessing
- Automated web scraping of scattered files using **Selenium**
- Created a mapping dictionary to standardize **country name variations**
- Cleaned inconsistent headers, formats, and handled special codes like `'D'` using category-wise mean imputation

### 📊 Exploratory Data Analysis
- Verified **data continuity** using heatmaps
- Identified **structural classification changes** around 2006
- Merged all datasets into a tabular format for reliable trend analysis

### 📈 Occupational Trend Analysis (2005–2022)
- 📉 **Farming & Production**: Consistent decline
- 📊 **Management & Professional**: Long-term growth
- 🔻 **Service Occupations**: Sharp drop, especially post-2006
- 🪖 **Military Roles**: Steady growth trajectory
- 📐 **Construction**: Cyclical with fluctuations

### 🧬 Demographic Correlation Studies
- Analyzed relationship between **age groups** and occupational choices
- Examined correlation between **admission class** (visa type) and profession

### 🔮 Forecasting & Projections (2023–2027)
- **Sales & Office**: Expected to grow to **80,000**
- **Management Roles**: Holding steady at **120,000/year**
- **Service Jobs**: Stabilizing around **35–40,000**
- **Military**: Forecasted to **triple** from recent lows

## 🚀 Tools & Technologies Used
- **Python** (Pandas, NumPy, Matplotlib)
- **Selenium** for large-scale web scraping
- **Excel / CSV** for raw data storage
- **Correlation plots** for demographic analysis
- **Forecasting models** using time series techniques

## 🎯 Use Cases
- Workforce planning for immigration policy analysts
- Market gap identification for job seekers and career strategists
- Data-driven insights for educational and skill development programs
