import streamlit as st
import pandas as pd
import plotly.express as px
import re
from groq import Groq

# ---------------------------------------------------------
# 1. PAGE CONFIGURATION & CUSTOM CSS
# ---------------------------------------------------------
st.set_page_config(
    page_title="Crude Oil Properties Platform", 
    page_icon="https://cdn-icons-png.flaticon.com/512/3344/3344638.png", # Clean oil drop icon
    layout="wide"
)

# --- CSS FOR FONT COLORS, SIZES, AND BACKGROUND ---
st.markdown("""
    <style>
    /* 1. Light Yellow Background (Targets the main app container) */
    .stApp, [data-testid="stAppViewContainer"] { 
        background-color: #ffffe0 !important; 
    }
    
    /* 2. Main Page Title (H1) */
    h1 { 
        color: #1f77b4 !important; 
        font-size: 32px !important; 
        font-weight: bold; 
    }
    
    /* 3. Section Titles (H2, H3) */
    h2, h3 { 
        color: #1f77b4 !important; 
        font-size: 20px !important; 
        font-weight: bold; 
    }
    
    /* 4. General Text */
    p, div, span, label, .stMarkdown { 
        color: #8B4513 !important; 
        font-size: 15px !important; 
    }
    
    /* 5. Property Names (Bold text) */
    strong { 
        color: #1f77b4 !important; 
        font-weight: bold; 
    }
    
    /* 6. Table Headers (Property & Standard Method) */
    thead tr th, th { 
        color: #1f77b4 !important; 
        font-size: 15px !important; 
        font-weight: bold !important;
    }
    
    /* 7. Table Body Text */
    tbody tr td, td {
        color: #8B4513 !important;
        font-size: 14px !important;
    }

    /* 8. Widget Labels (Selectbox, Multiselect) */
    [data-testid="stWidgetLabel"] { 
        color: #1f77b4 !important; 
        font-weight: bold; 
        font-size: 15px !important; 
    }
    
    /* 9. Metrics (SARA Analysis numbers) */
    [data-testid="stMetricValue"] { 
        color: #8B4513 !important; 
        font-size: 20px !important; 
    }
    [data-testid="stMetricLabel"] { 
        color: #1f77b4 !important; 
        font-size: 15px !important; 
    }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. LOAD DATA & TOP FILTERS
# ---------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_excel("crude_oil_database_v6.xlsx")
    df = df.fillna("NA")
    
    # Fix Origin Typos
    df["Origin"] = df["Origin"].str.replace("British Colombia", "British Columbia", case=False)
    
    # --- NEW: Format Sample Numbers to always have 4 digits ---
    def format_ests(val):
        match = re.search(r'(\d+)', str(val))
        if match:
            # zfill(4) adds leading zeros until the number is 4 digits long
            return f"ESTS {match.group(1).zfill(4)}"
        return str(val)
        
    df["Sample_Number"] = df["Sample_Number"].apply(format_ests)
    
    return df

df = load_data()

def extract_ests_number(ests_str):
    match = re.search(r'(\d+)', str(ests_str))
    return int(match.group(1)) if match else 0

st.title("Crude Oil Properties Platform")
st.markdown("Select a sample to view its properties, or use the comparison tool below.")

filter_col1, filter_col2 = st.columns(2)

with filter_col1:
    origins = sorted([o for o in df["Origin"].unique() if o != "Unknown"])
    origins.append("Unknown") 
    selected_origin = st.selectbox("Filter by Origin:", ["All"] + origins)

if selected_origin != "All":
    origin_filtered_df = df[df["Origin"] == selected_origin]
else:
    origin_filtered_df = df

valid_samples = origin_filtered_df[origin_filtered_df["Density @ 15C"] != "NA"]["Sample_Number"].unique()
sorted_samples = sorted(valid_samples, key=extract_ests_number)

with filter_col2:
    selected_sample = st.selectbox("Select Sample Number (ESTS XXXX):", sorted_samples)

sample_data = df[df["Sample_Number"] == selected_sample]

# ---------------------------------------------------------
# 3. SECTION 1: GENERAL AND MAIN INFORMATION
# ---------------------------------------------------------
st.header("Section 1: General and Main Information")

col1, col2 = st.columns(2)
with col1:
    selected_temp = st.selectbox("Select Temperature (°C):", ["15", "5", "0"])
with col2:
    weathering_options = sorted(sample_data["Weathering_Fraction"].unique())
    selected_weathering = st.selectbox("Select Weathering Fraction:", weathering_options)

row = sample_data[sample_data["Weathering_Fraction"] == selected_weathering].iloc[0]

st.subheader(f"Properties for {selected_sample} - {selected_weathering} @ {selected_temp}°C")

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("**Basic Info**")
    st.write(f"**Fluid Type:** {row['Fluid_Type']}")
    st.write(f"**Origin:** {row['Origin']}")
    st.write(f"**Mass Loss:** {row['Mass_Loss_%']} % w/w")
    
    st.markdown("**Density**")
    density_col = f"Density @ {selected_temp}C"
    api_col = f"API @ {selected_temp}C"
    st.write(f"**Density:** {row[density_col]} g/mL")
    st.write(f"**API Gravity:** {row[api_col]} Degree")

with c2:
    st.markdown("**Viscosity & Tension**")
    visc_col = f"Viscosity @ {selected_temp}C"
    st.write(f"**Dynamic Viscosity:** {row[visc_col]} mPa.s")
    st.write(f"**Surface Tension @ 15C:** {row['Surface Tension @ 15C']} mN/m")
    st.write(f"**Interfacial Tension @ 15C:** {row['Interfacial Tension @ 15C']} mN/m")

with c3:
    st.markdown("**Other Properties**")
    st.write(f"**Flash Point:** {row['Flash Point']} °C")
    st.write(f"**Pour Point:** {row['Pour Point']} °C")
    st.write(f"**Sulfur Content:** {row['Sulfur Content']} % w/w")
    st.write(f"**Water Content:** {row['Water Content']} % w/w")
    st.write(f"**Wax Content:** {row['Wax Content']} % w/w")

st.markdown("**SARA Analysis (% w/w)**")
sara_col1, sara_col2, sara_col3, sara_col4 = st.columns(4)
sara_col1.metric("Saturates", row['Saturates'])
sara_col2.metric("Aromatics", row['Aromatics'])
sara_col3.metric("Resin", row['Resin'])
sara_col4.metric("Asphaltene", row['Asphaltene'])

st.markdown("---")
st.markdown("### Measurement Methods Summary")
st.markdown("*Standard testing methods as defined by the Environment Canada PDF reports.*")

methods_data = {
    "Property": [
        "Density & API Gravity", "Dynamic Viscosity", "Surface & Interfacial Tension", 
        "Flash Point", "Pour Point", "Sulfur Content", "Water Content", 
        "Wax Content & SARA", "Evaporative Mass Loss (Weathering)"
    ],
    "Standard Method": [
        "ASTM D5002", "ESTS 12.06/x.x/M (or ASTM D7042)", "ESTS 12.12/x.x/M", 
        "ASTM D7094", "ASTM D97", "ASTM D4294", "ASTM E203", 
        "ESTS 12.11/4.0/M", "ESTS 12.01/x.x/M or Pan Evaporation"
    ]
}
st.table(pd.DataFrame(methods_data))

st.divider()

# ---------------------------------------------------------
# 4. SECTION 2: COMPARISON
# ---------------------------------------------------------
st.header("Section 2: Comparison of Selected Samples")

compare_weathering = st.selectbox("Select Weathering Fraction to compare:", ["W0", "W1", "W2", "W3", "W4"])

if selected_origin != "All":
    base_compare_pool = df[df["Origin"] == selected_origin]
else:
    base_compare_pool = df

available_compare_samples = base_compare_pool[
    (base_compare_pool["Weathering_Fraction"] == compare_weathering)
]["Sample_Number"].unique()

available_compare_samples = sorted(list(set(available_compare_samples)), key=extract_ests_number)

compare_samples = st.multiselect(
    "Select samples to compare:", 
    options=available_compare_samples,
    default=available_compare_samples[:2] if len(available_compare_samples) >= 2 else available_compare_samples
)

property_options = [
    "Density @ 15C", "API @ 15C", "Density @ 5C", "API @ 5C", "Density @ 0C", "API @ 0C",
    "Viscosity @ 15C", "Viscosity @ 5C", "Viscosity @ 0C", 
    "Surface Tension @ 15C", "Interfacial Tension @ 15C", "Flash Point", "Pour Point", 
    "Sulfur Content", "Water Content", "Wax Content", 
    "Saturates", "Aromatics", "Resin", "Asphaltene"
]
compare_properties = st.multiselect(
    "Select properties to compare:", 
    options=property_options,
    default=["Density @ 15C", "Viscosity @ 15C"]
)

if compare_samples:
    download_data = df[(df["Sample_Number"].isin(compare_samples)) & (df["Weathering_Fraction"] == compare_weathering)]
    download_data = download_data.drop_duplicates(subset=["Sample_Number", "Weathering_Fraction"])
    
    if not download_data.empty:
        csv = download_data.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Selected Data as CSV",
            data=csv,
            file_name=f"crude_oil_comparison_{compare_weathering}.csv",
            mime="text/csv",
        )

if compare_samples and compare_properties:
    compare_data = df[(df["Sample_Number"].isin(compare_samples)) & (df["Weathering_Fraction"] == compare_weathering)]
    compare_data = compare_data.drop_duplicates(subset=["Sample_Number", "Weathering_Fraction"])
    compare_data = compare_data.sort_values(by="Sample_Number", key=lambda x: x.map(extract_ests_number))
    
    units_dict = {
        "Density @ 15C": "g/mL", "API @ 15C": "Degree", "Density @ 5C": "g/mL", "API @ 5C": "Degree", "Density @ 0C": "g/mL", "API @ 0C": "Degree",
        "Viscosity @ 15C": "mPa.s", "Viscosity @ 5C": "mPa.s", "Viscosity @ 0C": "mPa.s", 
        "Surface Tension @ 15C": "mN/m", "Interfacial Tension @ 15C": "mN/m", 
        "Flash Point": "°C", "Pour Point": "°C", 
        "Sulfur Content": "% w/w", "Water Content": "% w/w", "Wax Content": "% w/w", 
        "Saturates": "% w/w", "Aromatics": "% w/w", "Resin": "% w/w", "Asphaltene": "% w/w"
    }

    regular_props = [p for p in compare_properties if p not in ["Saturates", "Aromatics", "Resin", "Asphaltene"]]
    sara_props = [p for p in compare_properties if p in ["Saturates", "Aromatics", "Resin", "Asphaltene"]]
    
    # --- REGULAR PROPERTIES BAR CHART ---
    if regular_props:
        st.subheader(f"Standard Properties Comparison ({compare_weathering})")
        
        for i in range(0, len(regular_props), 2):
            cols = st.columns(2)
            
            prop1 = regular_props[i]
            with cols[0]:
                melted_1 = compare_data.melt(id_vars=["Sample_Number"], value_vars=[prop1], var_name="Property", value_name="Value")
                melted_1["Value"] = pd.to_numeric(melted_1["Value"], errors='coerce')
                
                sorted_order_1 = melted_1.dropna(subset=["Value"]).sort_values(by="Value", ascending=False)["Sample_Number"].unique()
                
                fig1 = px.bar(
                    melted_1, x="Sample_Number", y="Value", color="Sample_Number", 
                    title=f"{prop1} ({units_dict.get(prop1, '')})", text_auto=True,
                    category_orders={"Sample_Number": sorted_order_1}
                )
                fig1.update_traces(width=0.4) 
                
                # --- PLOTLY STYLING (Updated Size and Height) ---
                fig1.update_layout(
                    showlegend=False, xaxis_title="Sample", yaxis_title=units_dict.get(prop1, 'Value'),
                    title_font=dict(size=14, color="red"), # Title Red
                    font=dict(size=12, color="#1f77b4"),   # Numbers/Axis Blue
                    xaxis=dict(title_font=dict(size=12, color="#1f77b4"), tickfont=dict(size=11, color="#1f77b4")),
                    yaxis=dict(title_font=dict(size=12, color="#1f77b4"), tickfont=dict(size=11, color="#1f77b4")),
                    height=450, # Increase chart height
                    plot_bgcolor='rgba(0,0,0,0)', # Transparent background
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig1, use_container_width=True)
                
            if i + 1 < len(regular_props):
                prop2 = regular_props[i+1]
                with cols[1]:
                    melted_2 = compare_data.melt(id_vars=["Sample_Number"], value_vars=[prop2], var_name="Property", value_name="Value")
                    melted_2["Value"] = pd.to_numeric(melted_2["Value"], errors='coerce')
                    
                    sorted_order_2 = melted_2.dropna(subset=["Value"]).sort_values(by="Value", ascending=False)["Sample_Number"].unique()
                    
                    fig2 = px.bar(
                        melted_2, x="Sample_Number", y="Value", color="Sample_Number", 
                        title=f"{prop2} ({units_dict.get(prop2, '')})", text_auto=True,
                        category_orders={"Sample_Number": sorted_order_2}
                    )
                    fig2.update_traces(width=0.4)
                    
                    # --- PLOTLY STYLING ---
                    fig2.update_layout(
                        showlegend=False, xaxis_title="Sample", yaxis_title=units_dict.get(prop2, 'Value'),
                        title_font=dict(size=14, color="red"), 
                        font=dict(size=12, color="#1f77b4"),
                        xaxis=dict(title_font=dict(size=12, color="#1f77b4"), tickfont=dict(size=11, color="#1f77b4")),
                        yaxis=dict(title_font=dict(size=12, color="#1f77b4"), tickfont=dict(size=11, color="#1f77b4")),
                        height=450,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)'
                    )
                    st.plotly_chart(fig2, use_container_width=True)

    # --- SARA BAR CHART ---
    if sara_props:
        st.subheader(f"SARA Analysis Comparison ({compare_weathering})")
        
        sara_data = compare_data.dropna(subset=sara_props, how='all')
        
        if not sara_data.empty:
            sort_basis = "Saturates" if "Saturates" in sara_props else sara_props[0]
            sort_df = sara_data[["Sample_Number", sort_basis]].copy()
            sort_df[sort_basis] = pd.to_numeric(sort_df[sort_basis], errors='coerce')
            sorted_sample_order = sort_df.dropna(subset=[sort_basis]).sort_values(by=sort_basis, ascending=False)["Sample_Number"].unique()
            
            col1, col2 = st.columns(2)
            cols = [col1, col2]
            
            for i, prop in enumerate(sara_props):
                melted_sara = sara_data.melt(id_vars=["Sample_Number"], value_vars=[prop], var_name="Component", value_name="Value")
                melted_sara["Value"] = pd.to_numeric(melted_sara["Value"], errors='coerce')
                melted_sara = melted_sara.dropna(subset=["Value"])

                if not melted_sara.empty:
                    fig_sara = px.bar(
                        melted_sara, x="Sample_Number", y="Value", color="Sample_Number", 
                        title=f"{prop} (% w/w)", text_auto=True,
                        category_orders={"Sample_Number": sorted_sample_order} 
                    )
                    fig_sara.update_traces(width=0.4)
                    
                    # --- PLOTLY STYLING ---
                    fig_sara.update_layout(
                        showlegend=False, xaxis_title="Sample", yaxis_title="% w/w", margin=dict(t=40, b=40, l=40, r=20),
                        title_font=dict(size=14, color="red"), 
                        font=dict(size=12, color="#1f77b4"),
                        xaxis=dict(title_font=dict(size=12, color="#1f77b4"), tickfont=dict(size=11, color="#1f77b4")),
                        yaxis=dict(title_font=dict(size=12, color="#1f77b4"), tickfont=dict(size=11, color="#1f77b4")),
                        height=450,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)'
                    )
                    
                    with cols[i % 2]:
                        st.plotly_chart(fig_sara, use_container_width=True)
        else:
            st.warning(f"No SARA data available for the selected samples at {compare_weathering}.")

# ---------------------------------------------------------
# 5. AI CHATBOT ASSISTANT (Groq)
# ---------------------------------------------------------
st.divider()
st.header("🤖 AI Data Assistant")

if st.button("🗑️ Clear Chat History"):
    st.session_state.messages = []
    st.rerun()

st.markdown("Ask a question about the database, or ask a general question about crude oil.")

# --- REPLACE WITH YOUR API KEY ---
GROQ_API_KEY = st.secrets["GROQ_API_KEY"] 
client = Groq(api_key=GROQ_API_KEY)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("E.g., Which Gulf of Mexico sample has the highest Viscosity at 15C?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # --- THE FIX: ONLY SEND THE FIRST 30 ROWS TO PREVENT TOKEN LIMIT ERROR ---
    # This gives the AI the column headers and enough context without crashing Groq.
    data_context = df.head(30).to_csv(index=False) 

    system_instruction = f"""
    You are an expert petrochemical data assistant. 
    You have access to a sample of the following crude oil database in CSV format:
    
    {data_context}
    
    Answer the user's question accurately based ONLY on the data provided above. 
    If the specific sample or property is not in this sample view, tell the user to use the dropdowns above to view it.
    If the data is 'NA', tell the user it is not available.
    """
    
    with st.chat_message("assistant"):
        with st.spinner("Analyzing database..."):
            try:
                response = client.chat.completions.create(
                    model="openai/gpt-oss-120b", 
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.0
                )
                
                answer = response.choices[0].message.content
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
                
            except Exception as e:
                st.error(f"Error: {e}")

# --- ATTRIBUTION FOOTER ---
st.divider()
st.markdown(
    """
    <div style='text-align: center; font-size: 14px; color: gray;'>
        <p><b>Data Attribution</b></p>
        <p>Contains information licensed under the <a href="https://open.canada.ca/en/open-government-licence-canada" target="_blank">Open Government Licence – Canada</a>.</p>
        <p>Original Data Source: Environment and Climate Change Canada (ECCC) Crude Oil and Petroleum Product Database.</p>
    </div>
    """, 
    unsafe_allow_html=True
)