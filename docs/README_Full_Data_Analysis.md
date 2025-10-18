# Full Data Analysis – Streaming Platform User Insights

## Overview
This project presents an exploratory and statistical analysis of user engagement data from a streaming platform. The goal is to identify key demographic patterns, subscription behaviors, and consumption trends that can inform data-driven business decisions.  

The analysis was performed using **Python** and **pandas**, leveraging descriptive statistics and visual exploration to uncover patterns across different user segments.

---

## Dataset Description
The dataset contains **5,000 user records**, each representing individual subscription and activity data.  

| Column | Description | Type |
|:--|:--|:--|
| `user_id` | Unique identifier for each user | `object` |
| `age` | Age of the user | `int64` |
| `country` | Country where the user is located | `object` |
| `subscription_type` | Subscription plan (e.g., Basic, Standard, Premium) | `object` |
| `registration_date` | Date when the user registered | `object` |
| `total_watch_time_hours` | Total watch time in hours | `float64` |

---

## Objectives
- Perform **data cleaning** and type conversion to prepare the dataset for analysis.  
- Generate **descriptive statistics** for numerical and categorical variables.  
- Explore **user demographics** (age, country distribution).  
- Analyze **subscription type popularity** and its relationship with user activity.  
- Identify **watch time trends** across age groups and regions.  

---

## Key Analyses
The notebook includes:
1. **Descriptive statistics** for all columns (central tendency and dispersion).  
2. **Visual analysis** using histograms, boxplots, and bar charts.  
3. **Country-level comparisons** of average watch time and subscription type distribution.  
4. **Correlation analysis** between age and watch time.  
5. **Insights and observations** summarizing the main behavioral trends among users.

---

## Technologies Used
- Python 3  
- Jupyter Notebook  
- pandas, numpy  
- matplotlib, seaborn  
- datetime  

---

## Results Summary
- The **average user age** is approximately **41.6 years**, with most users between **30 and 55 years old**.  
- The **Basic** plan has the highest number of subscribers, but **Premium** users show the highest average watch time.  
- Users from **Mexico** represent the largest portion of the dataset.  
- There is a **moderate positive correlation** between user age and total watch time.  
- The dataset suggests possible segmentation opportunities based on subscription type and age group.

---

## Conclusion
This analysis demonstrates how structured user data can be used to generate actionable insights for streaming platforms. By combining statistical methods and visualization techniques, the notebook provides a foundation for further analyses, such as churn prediction or recommendation systems.

---