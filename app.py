import streamlit as st
import pandas as pd
import plotly.express as px
import re
import json
from groq import Groq
import io 
# ---------------------------------------------------------
# 1. PAGE CONFIGURATION & CUSTOM CSS
# ---------------------------------------------------------
st.set_page_config(
    page_title="Crude Oil Properties Platform", 
    page_icon="🛢️", 
    #page_icon="https://cdn-icons-png.flaticon.com/512/8028/8028133.png", 
    layout="wide"
)

# --- CSS FOR FONT COLORS, SIZES, AND BACKGROUND ---
st.markdown("""
    <style>
    
    /* Make sure the header is transparent so it doesn't block the background */
    [data-testid="stHeader"] {
        background-color: transparent !important;
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

    /* 10. FIX MULTISELECT TAGS AND INPUT BOX */
    /* Style the little tags (bubbles) */
    [data-testid="stMultiSelect"] [data-baseweb="tag"] {
        background-color: #1f77b4 !important; /* Keep tags blue */
        color: #ffffff !important;            /* Keep tag text white */
        border: 1px solid #ffffff !important; /* Add a white border for contrast */
    }
    
    [data-testid="stMultiSelect"] [data-baseweb="tag"] span {
        color: #ffffff !important; 
    }

    /* Change the main input box background to Light Green */
    [data-testid="stMultiSelect"] [data-baseweb="select"] > div {
        background-color: #e0f7fa !important; /* Light Green/Cyan background */
        border: 1px solid #1f77b4 !important; /* Blue border around the box */
    }
    
    /* Ensure the typed text inside the box is dark brown */
    [data-testid="stMultiSelect"] input {
        color: #8B4513 !important;
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
# 5. AI CHATBOT ASSISTANT (Groq + Plotting Tool)
# ---------------------------------------------------------
st.divider()
st.header("🤖 AI Data Assistant")

if st.button("🗑️ Clear Chat History"):
    st.session_state.messages = []
    st.rerun()

st.markdown("Ask a question about the database, or ask the AI to plot properties.")

# --- REPLACE WITH YOUR API KEY ---
GROQ_API_KEY = st.secrets["GROQ_API_KEY"] 
client = Groq(api_key=GROQ_API_KEY)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("E.g., Plot density versus viscosity for Gulf of Mexico"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # --- SMART RETRIEVAL ---
    search_df = df.copy()
    prompt_lower = prompt.lower()
    
    # Check if the user is asking about a specific origin
    found_origin = False
    for origin in df["Origin"].unique():
        if str(origin).lower().split(",")[0] in prompt_lower:
            search_df = df[df["Origin"] == origin]
            found_origin = True
            break
            
    # If they ask about a specific sample number
    ests_match = re.search(r'(ests\s?\d+)', prompt_lower)
    if ests_match:
        search_df = df[df["Sample_Number"].str.lower() == ests_match.group(1).replace(" ", " ").strip()]
        
    if len(search_df) == len(df):
        search_df = df.head(150)

    data_context = search_df.to_csv(index=False) 

    system_instruction = f"""
    You are an expert petrochemical data assistant. 
    You have access to the following crude oil database in CSV format:
    
    {data_context}
    
    Answer the user's question accurately based ONLY on the data provided above. 
    If the specific sample or property is not in this sample view, tell the user to use the dropdowns above to view it.
    If the data is 'NA', tell the user it is not available.
    
    IMPORTANT: If the user asks you to plot, graph, or compare two properties visually (e.g., Density vs Viscosity), 
    you MUST use the 'plot_data' tool.

    If the user specifies a weathering fraction (like W0, W1), you MUST pass it to the 'weathering_filter' parameter in the plot_data tool.
    """

    # --- DEFINE THE PLOTTING TOOL ---
    tools = [
        {
            "type": "function",
            "function": {
                "name": "plot_data",
                "description": "Create a scatter plot to compare two numerical properties (e.g., Density vs Viscosity) for a specific origin or sample.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "x_column": {
                            "type": "string", 
                            "description": "The exact column name for the X-axis (e.g., 'Density @ 15C')."
                        },
                        "y_column": {
                            "type": "string", 
                            "description": "The exact column name for the Y-axis (e.g., 'Viscosity @ 15C')."
                        },
                        "origin_filter": {
                            "type": "string", 
                            "description": "Optional: Filter the plot by a specific origin (e.g., 'Gulf of Mexico, USA')."
                        }
                    },
                    "required": ["x_column", "y_column"]
                }
            }
        }
    ]
    
    with st.chat_message("assistant"):
        with st.spinner("Analyzing database..."):
            try:
                # 1. Call Groq with the tools
                response = client.chat.completions.create(
                    model="openai/gpt-oss-120b", 
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": prompt}
                    ],
                    tools=tools,
                    tool_choice="auto", # Let the AI decide if it needs to plot
                    temperature=0.0
                )
                
                response_message = response.choices[0].message
                tool_calls = response_message.tool_calls

                if tool_calls:
                    for tool_call in tool_calls:
                        function_args = json.loads(tool_call.function.arguments)
                        
                        if tool_call.function.name == "plot_data":
                            st.write("*(Generating plot...)*")
                            x_col = function_args.get("x_column")
                            y_col = function_args.get("y_column")
                            origin = function_args.get("origin_filter")
                            weathering = function_args.get("weathering_filter")
                            
                            # Filter the data for the plot
                            plot_df = df.copy()
                            if origin and origin != "All":
                                plot_df = plot_df[plot_df["Origin"].str.contains(origin, case=False, na=False)]
                            if weathering:
                                plot_df = plot_df[plot_df["Weathering_Fraction"] == weathering]
                            
                            # Clean data for plotting
                            plot_df = plot_df.dropna(subset=[x_col, y_col])
                            plot_df[x_col] = pd.to_numeric(plot_df[x_col], errors='coerce')
                            plot_df[y_col] = pd.to_numeric(plot_df[y_col], errors='coerce')

                            if not plot_df.empty:
                                # Create the Plotly chart
                                fig = px.scatter(
                                    plot_df, 
                                    x=x_col, 
                                    y=y_col, 
                                    color="Sample_Number",
                                    hover_data=["Weathering_Fraction", "Origin"],
                                    title=f"{y_col} vs {x_col} ({origin if origin else 'All'}) - {weathering if weathering else 'All Weatherings'}"
                                )
                                fig.update_layout(title_font=dict(size=16, color="red"), font=dict(size=12, color="#1f77b4"))
                                
                                st.plotly_chart(fig, use_container_width=True)
                                
                                # Inform the AI that the plot was successful
                                temp_messages = st.session_state.messages.copy()
                                temp_messages.append(response_message)
                                temp_messages.append({
                                    "tool_call_id": tool_call.id, "role": "tool", "name": "plot_data", 
                                    "content": f"Plot successfully generated for {len(plot_df)} data points with weathering filter: {weathering}."
                                })
                            else:
                                st.warning(f"Could not find data to plot for {x_col} and {y_col}.")

                    # 2. Second API Call: Ask AI to summarize the plot
                    second_response = client.chat.completions.create(
                        model="openai/gpt-oss-120b",
                        messages=temp_messages  # <--- CHANGE THIS FROM st.session_state.messages
                    )
                    answer = second_response.choices[0].message.content
                    st.markdown(answer)
                    # Now we only save the simple text answer to the history
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    # No tool needed, just print the text answer
                    answer = response_message.content
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