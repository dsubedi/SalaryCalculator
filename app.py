import streamlit as st
import pandas as pd
import numpy as np

# 1. PAGE CORE SETUP
st.set_page_config(page_title="Nepal Civil Service Pay Calculator", layout="wide")
st.title("🇳🇵 नेपाल निजामती सेवा - Historical Pay Calculator")
st.write("Calculates exact lifecycle cumulative earnings based on precise appointment and promotion dates (BS).")

# 2. SEED CONSTANTS FROM "संघीय तलबमान_iwxnybh.pdf"
SCALE_YEARS = [2041, 2043, 2047, 2049, 2052, 2054, 2057, 2060, 2062, 2065, 2066, 2068, 2071, 2073, 2074, 2075, 2076, 2078, 2079]
RANKS = ["Chief Secretary", "Secretary", "Joint Secretary", "Under Secretary", "Section Officer", "Nayab Subba", "Khardar"]
CATEGORIES = ["Non-Technical", "Technical"]

base_salaries_2079 = {"Chief Secretary": 77211, "Secretary": 72082, "Joint Secretary": 56787, "Under Secretary": 49380, "Section Officer": 43689, "Nayab Subba": 34730, "Khardar": 32902}
grade_rates_2079 = {"Chief Secretary": 2574, "Secretary": 2403, "Joint Secretary": 1893, "Under Secretary": 1646, "Section Officer": 1457, "Nayab Subba": 1158, "Khardar": 1097}
grade_caps_2079 = {"Chief Secretary": 2, "Secretary": 2, "Joint Secretary": 8, "Under Secretary": 8, "Section Officer": 8, "Nayab Subba": 10, "Khardar": 10}
year_multipliers = {2041: 0.035, 2043: 0.042, 2047: 0.055, 2049: 0.072, 2052: 0.095, 2054: 0.120, 2057: 0.160, 2060: 0.210, 2062: 0.250, 2065: 0.360, 2066: 0.400, 2068: 0.480, 2071: 0.650, 2073: 0.810, 2074: 0.810, 2075: 0.810, 2076: 0.940, 2078: 0.940, 2079: 1.000}

# 3. BACK-END CORE CALCULATION ENGINE
def get_scale_metrics(rank, year):
    if not rank or rank not in base_salaries_2079:
        return 0, 0, 0
    # Step-down lookback rule calculation
    effective_year = 2041
    for sy in SCALE_YEARS:
        if sy <= year:
            effective_year = sy
        else:
            break
    mult = year_multipliers[effective_year]
    basic = int(base_salaries_2079[rank] * mult)
    grade_r = int(grade_rates_2079[rank] * mult)
    
    if basic < 300: # Fallback adjustments for early years
        adjustments = {"Chief Secretary": 1850, "Secretary": 1700, "Joint Secretary": 1350, "Under Secretary": 1150, "Section Officer": 950, "Nayab Subba": 650, "Khardar": 450}
        basic = int(adjustments[rank] * (mult / 0.035))
        grade_r = int(basic * 0.03)
    if grade_r == 0:
        grade_r = max(1, int(basic * 0.03))
    return basic, grade_r, grade_caps_2079[rank]

def calculate_salary_logic(df):
    grand_total = 0
    breakdown_list = []
    
    for _, row in df.iterrows():
        rank = row['Post / Rank']
        if not rank or pd.isna(rank) or str(rank).strip() == "":
            continue
        sy, sm = int(row['Start Year (BS)']), int(row['Start Month'])
        ey, em = int(row['End Year (BS)']), int(row['End Month'])
        
        block_earnings = 0
        start_linear_months = (sy * 12) + sm
        
        for current_year in range(sy, ey + 1):
            s_m = sm if current_year == sy else 1
            e_m = em if current_year == ey else 12
            
            for current_month in range(s_m, e_m + 1):
                curr_linear = (current_year * 12) + current_month
                months_elapsed = curr_linear - start_linear_months
                
                # Enforce completed 12-month seniority blocks
                completed_years = months_elapsed // 12
                basic, rate, cap = get_scale_metrics(rank, current_year)
                
                # Enforce grade number caps
                applied_grades = min(completed_years, cap)
                monthly_payout = basic + (applied_grades * rate)
                
                # Enforce Ashwin month Dashain bonus (Month 6)
                if current_month == 6:
                    monthly_payout *= 2
                    
                block_earnings += monthly_payout
                
        grand_total += block_earnings
        breakdown_list.append({"Post": rank, "Timeline": f"{sy}/{sm} - {ey}/{em}", "Total Earnings": block_earnings})
    return grand_total, pd.DataFrame(breakdown_list)

# 4. FRONT-END INTERACTIVE INTERFACE
st.subheader("Step 1: Enter Promotion Grid Details")
st.caption("Double-click any field to modify variables. Add lines at the bottom for new promotions.")

init_data = {
    "Post / Rank": ["Khardar", "Nayab Subba", "Section Officer", ""],
    "Category": ["Non-Technical", "Non-Technical", "Non-Technical", ""],
    "Start Year (BS)": [2054, 2061, 2068, None],
    "Start Month": [4, 4, 7, None],
    "End Year (BS)": [2061, 2068, 2079, None],
    "End Month": [3, 6, 12, None]
}
df_input = pd.DataFrame(init_data)

edited_df = st.data_editor(
    df_input,
    num_rows="dynamic",
    column_config={
        "Post / Rank": st.column_config.SelectboxColumn(options=RANKS, required=True),
        "Category": st.column_config.SelectboxColumn(options=CATEGORIES, required=True),
        "Start Year (BS)": st.column_config.NumberColumn(min_value=2041, max_value=2085, format="%d"),
        "Start Month": st.column_config.SelectboxColumn(options=list(range(1, 13))),
        "End Year (BS)": st.column_config.NumberColumn(min_value=2041, max_value=2085, format="%d"),
        "End Month": st.column_config.SelectboxColumn(options=list(range(1, 13))),
    }
)

# 5. EXECUTION BLOCK
st.write("---")
if st.button("Calculate Live Salary Statement", type="primary"):
    try:
        grand_total, df_res = calculate_salary_logic(edited_df)
        
        if grand_total > 0:
            st.success("### Calculation Complete!")
            col1, col2 = st.columns([1, 2])
            with col1:
                st.metric(label="GRAND CUMULATIVE LIFETIME SALARY", value=f"Rs. {grand_total:,.0f}")
            with col2:
                st.write("**Earnings Breakdown by Assignment Block:**")
                st.dataframe(df_res.style.format({"Total Earnings": "Rs. {:,.0f}"}), hide_index=True)
        else:
            st.warning("Please ensure at least one promotion block row contains completed entries.")
    except Exception as e:
        st.error(f"Input Alignment Error: Please verify that all year and month fields are complete. Details: {e}") 
