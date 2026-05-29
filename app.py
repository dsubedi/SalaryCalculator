import streamlit as st
import numpy as np
import pandas as pd

# 1. PAGE SETUP & TITLES
st.set_page_config(page_title="dsubedi Nijamati Pay Calculator जम्मा तलव हिसाव", layout="wide")
st.title("🇳🇵 निजामती सेवा - Pay Calculator - by Devi Subedi")
st.write("For Personal Reference only. Not Official Software. No official Legitimacy.")
st.write("यो व्यक्तिगत तवरमा तयार पारिएको सफ्टवेयर हो। अफिसियल मान्यता दिँदैन । आफ्नो तलव आँकलन गर्न सघाउ पुगोस् भनेर स्वयंसेवाका रूपमा तयार पारिएको हो ।")
st.write("यसमा २०१७ साल देखि २०७९ सालसम्मका तलव, ग्रेड र ग्रेड सीमा तथा दशै खर्चका विवरण मात्र हिसाव गरिएको छ। विशेष भत्ता, दुर्गम भत्ता लगायत अन्य कुरा समावेश छैनन ।")

# 2. SEED MATRIX TIMELINES (31 SCALE MILESTONES)
SCALE_YEARS = [
    2017, 2022, 2030, 2032, 2033, 2035, 2038, 2041, 2042, 2043, 2045, 2047, 2049, 2052, 
    2054, 2057, 2062, 2064, 2065, 2066, 2068, 2070, 2071, 2073, 2075, 2076, 2078, 2079
]
RANKS = ["Chief Secretary", "Secretary", "Joint Secretary", "Under Secretary", "Section Officer", "Nayab Subba", "Khardar"]
CATEGORIES = ["Non-Technical", "Technical"]

base_salaries_2079 = {"Chief Secretary": 77211, "Secretary": 72082, "Joint Secretary": 56787, "Under Secretary": 49380, "Section Officer": 43689, "Nayab Subba": 34730, "Khardar": 32902}
grade_rates_2079 = {"Chief Secretary": 2574, "Secretary": 2403, "Joint Secretary": 1893, "Under Secretary": 1646, "Section Officer": 1457, "Nayab Subba": 1158, "Khardar": 1097}
grade_caps_2079 = {"Chief Secretary": 2, "Secretary": 2, "Joint Secretary": 8, "Under Secretary": 8, "Section Officer": 8, "Nayab Subba": 10, "Khardar": 10}

year_multipliers = {
    2017: 0.0006, 2022: 0.0009, 2030: 0.0011, 2032: 0.0012, 2033: 0.0013, 2035: 0.0014, 2038: 0.0020,
    2041: 0.0350, 2042: 0.0350, 2043: 0.0420, 2045: 0.0450, 2047: 0.0550, 2049: 0.0720, 2052: 0.0950,
    2054: 0.1200, 2057: 0.1600, 2062: 0.2500, 2064: 0.3300, 2065: 0.3600, 2066: 0.4000, 2068: 0.4800,
    2070: 0.5500, 2071: 0.6500, 2073: 0.8100, 2075: 0.8100, 2076: 0.9400, 2078: 0.9400, 2079: 1.0000
}

# 3. HISTORICAL TIMELINE SCALE METRICS EXTRACTOR
def get_historical_metrics(rank, year):
    if not rank or rank not in base_salaries_2079:
        return 0, 0, 0, 0, 0
    effective_year = 2017
    for sy in SCALE_YEARS:
        if sy <= year: effective_year = sy
        else: break
    mult = year_multipliers[effective_year]
    
    if effective_year < 2033: # Pre-2033 Legacy Dual-Grade adjustments[cite: 2]
        adjustments = {
            "Chief Secretary": (900, 50, 6, 0, 0), "Secretary": (700, 40, 5, 0, 0),
            "Joint Secretary": (500, 20, 6, 30, 6), "Under Secretary": (450, 20, 6, 30, 6),
            "Section Officer": (275, 12.5, 8, 15, 7), "Nayab Subba": (175, 7.5, 10, 10, 5),
            "Khardar": (120, 5, 10, 6, 5)
        }
        base, r1, c1, r2, c2 = adjustments[rank]
        scale_factor = mult / 0.0006
        return int(base * scale_factor), int(r1 * scale_factor), c1, int(r2 * scale_factor), c2
    else: # Modern standard unified architecture ruleset
        return int(base_salaries_2079[rank] * mult), int(grade_rates_2079[rank] * mult), grade_caps_2079[rank], 0, 0

# 4. DATA ENGINE WITH DYNAMIC LINKED-LIST TIMELINE INTERPOLATION
def calculate_salary_logic(df_raw):
    # Filter empty row placeholders cleanly
    df = df_raw.dropna(subset=['Post / Rank', 'Start Year (BS)', 'Start Month']).copy()
    df = df[df['Post / Rank'].str.strip() != ""].reset_index(drop=True)
    
    if df.empty:
        return 0, pd.DataFrame()
        
    # Sort chronologically to prevent random entry rows from bleeding data
    df = df.sort_values(by=['Start Year (BS)', 'Start Month']).reset_index(drop=True)
    
    # --- CRUCIAL: AUTOMATED DATE-CHAINING INTERPOLATION LAYER ---
    for i in range(len(df) - 1):
        next_year = int(df.loc[i+1, 'Start Year (BS)'])
        next_month = int(df.loc[i+1, 'Start Month'])
        
        # Step back exactly 1 month from the subsequent post's appointment marker
        if next_month == 1:
            df.loc[i, 'End Year (BS)'] = next_year - 1
            df.loc[i, 'End Month'] = 12
        else:
            df.loc[i, 'End Year (BS)'] = next_year
            df.loc[i, 'End Month'] = next_month - 1

    grand_total = 0
    breakdown = []
    
    # Loop over resolved continuous timeline blocks
    for idx, row in df.iterrows():
        rank = row['Post / Rank']
        sy, sm = int(row['Start Year (BS)']), int(row['Start Month'])
        
        if pd.isna(row['End Year (BS)']) or pd.isna(row['End Month']):
            st.error(f"Validation Error: Please ensure you specify the final 'End Year (BS)' and 'End Month' in your last career row choice.")
            return 0, pd.DataFrame()
            
        ey, em = int(row['End Year (BS)']), int(row['End Month'])
        block_payout = 0
        start_linear = (sy * 12) + sm
        
        for curr_year in range(sy, ey + 1):
            m_start = sm if curr_year == sy else 1
            m_end = em if curr_year == ey else 12
            
            for curr_month in range(m_start, m_end + 1):
                curr_linear = (curr_year * 12) + curr_month
                months_elapsed = curr_linear - start_linear
                
                # Enforce completed 12-month seniority blocks
                completed_years = months_elapsed // 12
                basic, r1, c1, r2, c2 = get_historical_metrics(rank, curr_year)
                
                # Execute Grade Calculations
                if r2 > 0: # Pre-2033 dual-grade ruleset
                    if completed_years <= c1: grade_pay = completed_years * r1
                    else: grade_pay = (c1 * r1) + (min(completed_years - c1, c2) * r2)
                else: # Modern standard single ceiling ruleset
                    grade_pay = min(completed_years, c1) * r1
                    
                monthly_gross = basic + grade_pay
                if curr_month == 6: monthly_gross *= 2 # Ashwin Dashain Bonus filter trigger
                block_payout += monthly_gross
                
        grand_total += block_payout
        breakdown.append({"Post / Rank": rank, "Tenure Window (BS)": f"{sy}/{sm} to {ey}/{em}", "Total Earnings": block_payout})
        
    return grand_total, pd.DataFrame(breakdown)

# 5. USER INTERFACE FORM DESIGN
st.subheader("Step 1: Map Your Sequential Appointment & Promotion Dates ")
st.subheader("        सुरू देखिका आफ्ना हरेक पदको सुरू नियुक्ति वा बढुवा मिति क्रमशः लेख्दै जानुहोस ।")
st.info("💡 **Instructions:** Enter only the start dates for your positions. The app will automatically calculate the end date based on your next promotion. You only need to provide an end date for the final row.")
st.info("💡 ** नोटः प्रत्येक पदको सुरू मिति मात्र लेख्नुहोला । अन्तिम पदमा मात्र अन्तिम मिति वा जुन मितिसम्मको तलव हिसाव गर्ने हो, सो मिति लेख्नुहोला । हामीले तपाइको ग्रेड रकम र दशै खर्च समेत संलग्न गरी देखाउने छौं ।")
st.info("💡 ** नोटः पद छान्न Post मा Double Click गर्नुहोला । कुनै पनि रेकर्ड हटाउन रेकर्डको सुरूमा क्लिक गरी Delete गर्नुहोला। रेकर्ड थप्न तल पट्टि नयाँ कोठामा क्लिक गरी लेख्नुहोला । ")

# Preloaded profile case showcasing hands-free chaining architecture
init_profile = {
    "Post / Rank": ["Khardar", "Nayab Subba", "Section Officer", ""],
    "Category": ["Non-Technical", "Non-Technical", "Non-Technical", ""],
    "Start Year (BS)": [2054, 2061, 2068, None],
    "Start Month": [4, 4, 7, None],
    "End Year (BS)": [None, None, 2079, None], # Only final row requires input
    "End Month": [None, None, 12, None]        # Only final row requires input
}
df_profile = pd.DataFrame(init_profile)

edited_grid = st.data_editor(
    df_profile,
    num_rows="dynamic",
    column_config={
        "Post / Rank": st.column_config.SelectboxColumn(options=RANKS, required=True),
        "Category": st.column_config.SelectboxColumn(options=CATEGORIES, required=True),
        "Start Year (BS)": st.column_config.NumberColumn(min_value=2017, max_value=2085, format="%d"),
        "Start Month": st.column_config.SelectboxColumn(options=list(range(1, 13))),
        "End Year (BS)": st.column_config.NumberColumn(min_value=2017, max_value=2085, format="%d", help="Fill this out ONLY for your current/last position."),
        "End Month": st.column_config.SelectboxColumn(options=list(range(1, 13)), help="Fill this out ONLY for your current/last position."),
    }
)

st.write("---")
if st.button("तलव हिसाव गर्नुहोस", type="primary"):
    grand_total, df_res = calculate_salary_logic(edited_grid)
    if grand_total > 0:
        st.success("### System Processing Complete!")
        col1, col2 = st.columns([1, 2])
        with col1:
            st.metric(label="तपाइको जिन्दगीभरको तलवी कमाइको अनुमानित हिसावः)", value=f"Rs. {grand_total:,.0f}")
        with col2:
            st.write("**Chained Payroll Distributions View:**")
            st.dataframe(df_res.style.format({"Total Earnings": "Rs. {:,.0f}"}), hide_index=True)


# ... (All of your previous calculation code, buttons, and st.success blocks remain above) ...


# ==========================================
# 6. APP FOOTER & VISITOR COUNTER
# ==========================================
st.write("---") # Adds a clean horizontal divider line above the footer

# Define the variable right here so Python never hits a NameError
app_identifier = "nepal-civil-service-salary-calculator"

# Create three columns to center the counter perfectly at the bottom
foot_col1, foot_col2, foot_col3 = st.columns([2, 1, 2])

with foot_col2:
    st.caption("📊 **System Analytics**")
    # Pulls the live numerical hit counter centrally in the footer
    st.html(
        f'<img src="https://visitor-badge.laobi.icu/badge?page_id={app_identifier}&left_color=gray&right_color=green" alt="Total Visitors">'
    )


