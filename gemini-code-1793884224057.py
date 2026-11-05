import math
import pandas as pd
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="PCR Master Mix Calculator", page_icon="🧬", layout="wide"
)

st.title("🧬 PCR Master Mix & Reaction Calculator")
st.markdown(
    "Calculate precise reagent volumes, account for dead volume, and follow a"
    " foolproof benchside checklist."
)

# --- Sidebar: Experiment Setup ---
st.sidebar.header("1. Experiment Parameters")
num_samples = st.sidebar.number_input(
    "Number of Samples", min_value=1, max_value=200, value=10, step=1
)
replicates = st.sidebar.number_input(
    "Replicates per Sample", min_value=1, max_value=5, value=2, step=1
)
controls = st.sidebar.number_input(
    "Control Reactions (+/-)", min_value=0, max_value=10, value=2, step=1
)
dead_volume_pct = (
    st.sidebar.slider("Dead Volume Buffer (%)", 0.0, 20.0, 10.0, 1.0) / 100.0
)
single_rxn_vol = st.sidebar.number_input(
    "Single Reaction Total Volume (µL)",
    min_value=5.0,
    max_value=100.0,
    value=20.0,
    step=1.0,
)

# --- Calculations ---
base_reactions = (num_samples * replicates) + controls
total_reactions_with_buffer = base_reactions * (1 + dead_volume_pct)
practical_reactions = math.ceil(
    total_reactions_with_buffer
)  # Rounded up for safe pipetting

st.sidebar.markdown("---")
st.sidebar.metric("Base Reactions", base_reactions)
st.sidebar.metric(
    "Total Reactions (+ Buffer)", f"{total_reactions_with_buffer:.2f}"
)
st.sidebar.metric("Practical Multiplier (Rounded)", practical_reactions)

# --- Main Area: Reagent Configuration ---
st.header("2. Reagent Configuration")
st.markdown(
    "Modify or add components and their volumes per single"
    f" **{single_rxn_vol} µL** reaction."
)

# Default component table
if "reagents_df" not in st.session_state:
    st.session_state.reagents_df = pd.DataFrame([
        {"Component": "2X Taq Master Mix", "Vol_per_rxn_uL": 10.0, "Type": "Mix"},
        {
            "Component": "Forward Primer (10 µM)",
            "Vol_per_rxn_uL": 0.8,
            "Type": "Primer",
        },
        {
            "Component": "Reverse Primer (10 µM)",
            "Vol_per_rxn_uL": 0.8,
            "Type": "Primer",
        },
        {
            "Component": "Template DNA",
            "Vol_per_rxn_uL": 2.0,
            "Type": "Template",
        },
    ])

edited_df = st.data_editor(
    st.session_state.reagents_df, num_rows="dynamic", use_container_width=True
)

# --- Summary & Water Calculation ---
st.header("3. Master Mix Preparation Summary")

# Calculate total volumes for master mix items (excluding separate templates)
mix_components = edited_df[edited_df["Type"] != "Template"].copy()
mix_components["Total_Volume_uL"] = (
    mix_components["Vol_per_rxn_uL"] * practical_reactions
)

# Water balance validation
non_water_vol = mix_components["Vol_per_rxn_uL"].sum()
water_vol_per_rxn = single_rxn_vol - non_water_vol

if water_vol_per_rxn < 0:
    st.error(
        "⚠️ **Error:** The sum of component volumes ("
        f"{non_water_vol:.2f} µL) exceeds the single reaction total volume ("
        f"{single_rxn_vol} µL)!"
    )
else:
    # Add water automatically to the master mix
    water_row = pd.DataFrame([{
        "Component": "Nuclease-Free Water",
        "Vol_per_rxn_uL": water_vol_per_rxn,
        "Type": "Buffer",
        "Total_Volume_uL": water_vol_per_rxn * practical_reactions,
    }])

    full_master_mix_df = pd.concat(
        [mix_components, water_row], ignore_index=True
    )

    st.dataframe(
        full_master_mix_df[[
            "Component",
            "Vol_per_rxn_uL",
            "Total_Volume_uL",
        ]].style.format({"Vol_per_rxn_uL": "{:.2f}", "Total_Volume_uL": "{:.2f}"}),
        use_container_width=True,
    )

    total_mix_volume = full_master_mix_df["Total_Volume_uL"].sum()
    st.success(
        f"✅ **Total Master Mix Volume to Prepare:** **{total_mix_volume:.2f}"
        f" µL** (for {practical_reactions} reactions including dead volume)"
    )

    # --- Benchside Checklist ---
    st.header("4. Benchside Pipetting Checklist")
    st.markdown(
        "Check off each component as you add it to your master mix tube:"
    )

    for idx, row in full_master_mix_df.iterrows():
        st.checkbox(
            f"Add **{row['Component']}**: **{row['Total_Volume_uL']:.2f} µL**"
            f" total ({row['Vol_per_rxn_uL']:.2f} µL per reaction)",
            key=f"check_{idx}",
        )

    # Separate note for template DNA
    template_rows = edited_df[edited_df["Type"] == "Template"]
    if not template_rows.empty:
        st.info(
            "📌 **Note for Template DNA:** Add"
            f" **{template_rows['Vol_per_rxn_uL'].values[0]} µL** of template"
            " individually into each sample tube/well (do not add to the master"
            " mix)."
        )