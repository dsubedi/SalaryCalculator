import streamlit as st
import numpy as np
import pandas as pd

# 1. PAGE SETUP & TITLES
st.set_page_config(page_title="dsubedi Nijamati Pay Calculator जम्मा तलव हिसाव", layout="wide")
st.title("🇳🇵 निजामती सेवा - Pay Calculator - by Devi Subedi")
st.write("For Personal Reference only. Not Official Software. No official Legitimacy.")
st.write("यो व्यक्तिगत तवरमा तयार पारिएको सफ्टवेयर हो। अफिसियल मान्यता दिँदैन । आफ्नो तलव आँकलन गर्न सघाउ पुगोस् भनेर स्वयंसेवाका रूपमा तयार पारिएको हो ।")
st.write("यसमा २०१७ साल देखि २०७९ सालसम्मका तलव, ग्रेड र ग्रेड सीमा तथा दशै खर्चका विवरण मात्र हिसाव गरिएको छ। विशेष भत्ता, दुर्गम भत्ता लगायत अन्य सुविधा समावेश छैनन ।")

# 2. SEED MATRIX TIMELINES (31 SCALE MILESTONES)
SCALE_YEARS = [
    2017, 2022, 2030, 2032, 2033, 2035, 2038, 2041, 2042, 2043, 2045, 2047, 2049, 2052, 
    2054, 2057, 2062, 2064, 2065, 2066, 2068, 2070, 2071, 2073, 2075, 2076, 2078, 2079
]
RANKS = [
    "Chief Secretary", "Secretary", "Joint Secretary", "Under Secretary", 
    "Section Officer", "Nayab Subba", "Khardar", "Mukhiya", "NG Class IV", "Classless"
]
CATEGORIES = ["Non-Technical", "Technical"]

# ADJUSTED 2079 BASE SALARIES:
base_salaries_2079 = {
    "Chief Secretary": 77211, 
    "Secretary": 72082, 
    "Joint Secretary": 56787, 
    "Under Secretary": 49380, 
    "Section Officer": 43689, 
    "Nayab Subba": 34730, 
    "Khardar": 32902,
    "Mukhiya": 32010,       
    "NG Class IV": 24010,   
    "Classless": 23010      
}

# ADJUSTED GRADE INCREMENT RATES:
grade_rates_2079 = {
    "Chief Secretary": 2574, 
    "Secretary": 2403, 
    "Joint Secretary": 1893, 
    "Under Secretary": 1646, 
    "Section Officer": 1457, 
    "Nayab Subba": 1158, 
    "Khardar": 1097,
    "Mukhiya": 801,
    "NG Class IV": 801,
    "Classless": 767
}

# ADJUSTED CEILING CEILINGS (GRADE CAPS):
grade_caps_2079 = {
    "Chief Secretary": 2, 
    "Secretary": 2, 
    "Joint Secretary": 8, 
    "Under Secretary": 8, 
    "Section Officer": 8, 
    "Nayab Subba": 10, 
    "Khardar": 10,
    "Mukhiya": 2,           
    "NG Class IV": 6,       
    "Classless": 5          
}
year_multipliers = {
    2017: 0.0006, 2022: 0.0009, 2030: 0.0011, 2032: 0.0012, 2033: 0.0013, 2035: 0.0014, 2038: 0.0020,
    2041: 0.0350, 2042: 0.0350, 2043: 0.0420, 2045: 0.0450, 2047: 0.0550, 2049: 0.0720, 2052: 0.0950,
    2054: 0.1200, 2057: 0.1600, 2062: 0.2500, 2064: 0.3300, 2065: 0.3600, 2066: 0.4000, 2068: 0.4800,
    2070: 0.5500, 2071: 0.6500, 2073: 0.8100, 2075: 0.8100, 2076: 0.9400, 2078: 0.9400, 2079: 1.0000
}

# ==========================================
# 3. HISTORICAL TIMELINE SCALE METRICS EXTRACTOR
# ==========================================
def get_historical_metrics(rank, year):
    if not rank or rank not in base_salaries_2079:
        return 0, 0, 0, 0, 0
        
    effective_year = 2017
    for sy in SCALE_YEARS:
        if sy <= year:
            effective_year = sy
        else:
            break
            
    mult = year_multipliers[effective_year]
    
    if effective_year < 2033: 
        adjustments = {
            "Chief Secretary": (900, 50, 6, 0, 0), 
            "Secretary": (700, 40, 5, 0, 0),
            "Joint Secretary": (500, 20, 6, 30, 6), 
            "Under Secretary": (450, 20, 6, 30, 6),
            "Section Officer": (275, 12.5, 8, 15, 7), 
            "Nayab Subba": (175, 7.5, 10, 10, 5),
            "Khardar": (120, 5, 10, 6, 5),
            "Mukhiya": (75, 3, 10, 4, 5),
            "NG Class IV": (55, 2, 10, 2.5, 4),
            "Classless": (45, 1, 10, 1.5, 10)
        }
        base, r1, c1, r2, c2 = adjustments[rank]
        scale_factor = mult / 0.0006
        return int(base * scale_factor), int(r1 * scale_factor), c1, int(r2 * scale_factor), c2
    else:
        # Standard unified architecture ruleset
        basic = int(base_salaries_2079[rank] * mult)
        grade_r = int(grade_rates_2079[rank] * mult)
        return basic, grade_r, grade_caps_2079[rank], 0, 0

# 4. DATA ENGINE WITH DYNAMIC LINKED-LIST TIMELINE INTERPOLATION
def calculate_salary_logic(df_raw, savings_pct, interest_rate):
    df = df_raw.dropna(subset=['Post / Rank', 'Start Year (BS)', 'Start Month']).copy()
    df = df[df['Post / Rank'].str.strip() != ""].reset_index(drop=True)
    
    if df.empty:
        return 0, 0, pd.DataFrame(), pd.DataFrame()
        
    df = df.sort_values(by=['Start Year (BS)', 'Start Month']).reset_index(drop=True)
    
    # --- AUTOMATED DATE-CHAINING INTERPOLATION LAYER ---
    for i in range(len(df) - 1):
        next_year = int(df.loc[i+1, 'Start Year (BS)'])
        next_month = int(df.loc[i+1, 'Start Month'])
        
        if next_month == 1:
            df.loc[i, 'End Year (BS)'] = next_year - 1
            df.loc[i, 'End Month'] = 12
        else:
            df.loc[i, 'End Year (BS)'] = next_year
            df.loc[i, 'End Month'] = next_month - 1

    grand_total = 0
    total_accumulated_savings = 0.0
    monthly_interest_rate = (interest_rate / 100.0) / 12.0
    savings_factor = savings_pct / 100.0
    
    breakdown_by_post = []
    breakdown_by_year = []
    
    # Loop over resolved continuous timeline blocks
    for idx, row in df.iterrows():
        rank = row['Post / Rank']
        sy, sm = int(row['Start Year (BS)']), int(row['Start Month'])
        
        if pd.isna(row['End Year (BS)']) or pd.isna(row['End Month']):
            st.error(f"Validation Error: Please ensure you specify the final 'End Year (BS)' and 'End Month' in your last career row choice.")
            return 0, 0, pd.DataFrame(), pd.DataFrame()
            
        ey, em = int(row['End Year (BS)']), int(row['End Month'])
        
        block_salary = 0
        block_grade = 0
        block_festival = 0
        
        start_linear = (sy * 12) + sm
        
        for curr_year in range(sy, ey + 1):
            m_start = sm if curr_year == sy else 1
            m_end = em if curr_year == ey else 12
            
            year_salary = 0
            year_grade = 0
            year_festival = 0
            year_savings_deposited = 0.0
            year_interest_earned = 0.0
            
            for curr_month in range(m_start, m_end + 1):
                curr_linear = (curr_year * 12) + curr_month
                months_elapsed = curr_linear - start_linear
                
                completed_years = months_elapsed // 12
                basic, r1, c1, r2, c2 = get_historical_metrics(rank, curr_year)
                
                # Execute Grade Calculations
                if r2 > 0: # Pre-2033 dual-grade ruleset
                    if completed_years <= c1: 
                        grade_pay = completed_years * r1
                    else: 
                        grade_pay = (c1 * r1) + (min(completed_years - c1, c2) * r2)
                else: # Modern standard single ceiling ruleset
                    grade_pay = min(completed_years, c1) * r1
                    
                month_earnings = basic + grade_pay
                year_salary += basic
                year_grade += grade_pay
                
                # Execute Ashwin Dashain Bonus filter trigger (Month 6 = Ashwin)
                month_festival = 0
                if curr_month == 6: 
                    month_festival = (basic + grade_pay)
                    year_festival += month_festival
                
                total_month_pay = month_earnings + month_festival
                
                # 📈 INTEGRATED MONTHLY COMPOUND INTEREST ENGINE
                monthly_savings_deposit = total_month_pay * savings_factor
                interest_this_month = (total_accumulated_savings + monthly_savings_deposit) * monthly_interest_rate
                total_accumulated_savings = (total_accumulated_savings + monthly_savings_deposit) * (1.0 + monthly_interest_rate)
                
                year_savings_deposited += monthly_savings_deposit
                year_interest_earned += interest_this_month
            
            block_salary += year_salary
            block_grade += year_grade
            block_festival += year_festival
            
            year_total = year_salary + year_grade + year_festival
            breakdown_by_year.append({
                "Year": f"{curr_year} BS",
                "Post": rank,
                "Salary": year_salary,
                "Grade": year_grade,
                "Festival": year_festival,
                "Total Payout": year_total,
                "Savings Deposited": year_savings_deposited,      
                "Interest Earned": year_interest_earned,          
                "Accumulated Savings Balance": total_accumulated_savings
            })
                    
        block_total = block_salary + block_grade + block_festival
        grand_total += block_total
        
        breakdown_by_post.append({
            "Post": rank, 
            "Tenure Window": f"{sy}/{sm:02d} to {ey}/{em:02d}", 
            "Total Salary Amt": block_salary,
            "Total Grade Amt": block_grade,
            "Total Festival Allowance Amt": block_festival,
            "Grand Total Earnings": block_total
        })
        
    return grand_total, total_accumulated_savings, pd.DataFrame(breakdown_by_post), pd.DataFrame(breakdown_by_year)

# Initialize persistent safety flags for the schedule button render contexts
if "render_schedule" not in st.session_state:
    st.session_state.render_schedule = False

# 5. USER INTERFACE FORM DESIGN
st.subheader("Step 1: Map Your Sequential Appointment & Promotion Dates ")
st.subheader("       सुरू देखिका आफ्ना हरेक पदको सुरू नियुक्ति वा बढुवा मिति क्रमशः लेख्दै जानुहोस ।")

st.info("💡 **Instructions:** Enter only the start dates for your positions. The app will automatically calculate the end date based on your next promotion. You only need to provide an end date for the final row.")
st.info("💡 ** नोटः प्रत्येक पदको सुरू मिति मात्र लेख्नुहोला । अन्तिम पदमा मात्र अन्तिम मिति वा जुन मितिसम्मको तलव हिसाव गर्ने हो, सो मिति लेख्नुहोला । हामीले तपाइको ग्रेड रकम र दशै खर्च समेत संलग्न गरी देखाउने छौं ।")

# Preloaded profile case showcasing hands-free chaining architecture
init_profile = {
    "Post / Rank": ["Khardar", "Nayab Subba", "Section Officer", ""],
    "Category": ["Non-Technical", "Non-Technical", "Non-Technical", ""],
    "Start Year (BS)": [2054, 2061, 2068, None],
    "Start Month": [4, 4, 7, None],
    "End Year (BS)": [None, None, 2079, None], 
    "End Month": [None, None, 12, None]        
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
    st.session_state.render_schedule = False  
    grand_total, total_savings, df_res, df_yearly = calculate_salary_logic(edited_grid, 1.0, 5.0)
    
    st.session_state.calc_success = True
    st.session_state.grand_total = grand_total
    st.session_state.df_res = df_res
    st.session_state.df_yearly = df_yearly
    st.session_state.edited_grid = edited_grid

# ⚠️ EVERYTHING BELOW DEPENDS ON CALCULATIONS AND IS SECURELY INDENTED 
if st.session_state.get("calc_success", False):
    grand_total = st.session_state.grand_total
    df_res = st.session_state.df_res
    df_yearly = st.session_state.df_yearly
    edited_grid = st.session_state.edited_grid
    
    st.success("### System Processing Complete!")
    st.metric(label="तपाइको जिन्दगीभरको तलवी कमाइको अनुमानित हिसावः", value=f"Rs. {grand_total:,.0f}")
    st.write("---")
    
    # Display Table 1: Chained Payroll Distributions View
    st.write("**Chained Payroll Distributions View:**")
    formatted_df = df_res.style.format({
        "Total Salary Amt": "Rs. {:,.0f}",
        "Total Grade Amt": "Rs. {:,.0f}",
        "Total Festival Allowance Amt": "Rs. {:,.0f}",
        "Grand Total Earnings": "Rs. {:,.0f}"
    })
    st.dataframe(formatted_df, use_container_width=True, hide_index=True)
    st.write("---")
    
    # Display Table 2: Year-by-Year Optional Expander Breakdown
    with st.expander("🔍 View Year-by-Year Detailed Breakdown (वर्षगत विस्तृत विवरण हेर्नुहोस्)"):
        st.write("Detailed chronological audit history generated directly from active Personnel Record matrices:")
        clean_yearly_df = df_yearly.drop(columns=["Accumulated Savings Balance", "Savings Deposited", "Interest Earned"], errors="ignore")
        formatted_yearly_df = clean_yearly_df.style.format({
            "Salary": "Rs. {:,.0f}",
            "Grade": "Rs. {:,.0f}",
            "Festival": "Rs. {:,.0f}",
            "Total Payout": "Rs. {:,.0f}"
        })
        st.dataframe(formatted_yearly_df, use_container_width=True, hide_index=True)
        
    st.write("---")
    
    # FINALE INTERACTIVE SAVINGS INTERFACE
    st.warning(f"### 🏦 Had You Saved Some Money? (एउटा आँखा खोल्ने हिसाव)")
    st.write("Adjust the parameters below to see how a small monthly savings plan would look today with compound interest:")
    
    inp_col1, inp_col2 = st.columns(2)
    with inp_col1:
        pct_input = st.number_input("Monthly Savings Goal (%)", min_value=0.1, max_value=100.0, value=1.0, step=0.5, key="final_pct_input")
    with inp_col2:
        rate_input = st.number_input("Bank Interest Rate (% p.a.)", min_value=0.0, max_value=25.0, value=5.0, step=0.25, key="final_rate_input")
        
    # Re-calculate live data matrix vectors on the fly using the updated live inputs
    _, active_savings, _, df_yearly_live = calculate_salary_logic(edited_grid, pct_input, rate_input)
    
    # 🟢 PERFECTLY INDENTED: This line can never throw a NameError now!
    st.write(f"यदि तपाइले मासिक तलवको केवल **{pct_input}%** मात्र रकम **{rate_input}%** व्याजदरमा बैंकमा बचाएको भए मासिक चक्रवर्ती व्याजले आजसम्मः ")
    st.markdown(f"## 💰 You would have **Rs. {active_savings:,.0f}** money saved in your bank account today!")
    st.caption("A small financial discipline compounded over time creates massive lifelong security. Start saving today!")
    st.write("---")
    
    # SCHEDULE BUTTON WITH ISOLATED SAVINGS & INTEREST COLUMNS
    if st.button("📊 Show Annual Accumulation Schedule (वार्षिक बचत तालिका हेर्नुहोस्)", type="secondary"):
        st.session_state.render_schedule = True
        
    if st.session_state.render_schedule:
        st.info("### 📈 Chronological Wealth Accumulation Schedule")
        st.write("This table isolates how your custom monthly savings grew year-by-year with explicit out-of-pocket deposits vs compound interest injections:")
        
        schedule_view_df = df_yearly_live[["Year", "Post", "Total Payout", "Savings Deposited", "Interest Earned", "Accumulated Savings Balance"]].copy()
        schedule_view_df.columns = ["Year", "Post", "Annual Total Pay", "Annual Savings Added", "Annual Interest Earned", "Accumulated Savings Balance"]
        
        formatted_schedule_df = schedule_view_df.style.format({
            "Annual Total Pay": "Rs. {:,.0f}",
            "Annual Savings Added": "Rs. {:,.0f}",
            "Annual Interest Earned": "Rs. {:,.0f}",
            "Accumulated Savings Balance": "Rs. {:,.0f}"
        })
        st.dataframe(formatted_schedule_df, use_container_width=True, hide_index=True)


# ==========================================
# 6. APP FOOTER & VISITOR COUNTER
# ==========================================
st.write("---") 

app_identifier = "nepal-civil-service-salary-calculator"
foot_col1, foot_col2, foot_col3 = st.columns([2, 1, 2])

with foot_col2:
    st.caption("📊 **System Analytics**")
    st.html(
        f'<img src="https://visitor-badge.laobi.icu/badge?page_id={app_identifier}&left_color=gray&right_color=green" alt="Total Visitors">'
    )
