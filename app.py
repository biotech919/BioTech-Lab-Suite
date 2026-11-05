import math
import numpy as np
import pandas as pd
import streamlit as st

# --- 1. Page Configuration & Global Branding ---
st.set_page_config(
    page_title="BioTech Lab Suite | All-In-One", page_icon="🧬", layout="wide"
)

# Sidebar Branding
st.logo("https://images.unsplash.com/photo-1532187863486-abf9dbad1b69?w=100")
st.sidebar.image(
    "https://images.unsplash.com/photo-1579154204601-01588f351e67?w=400",
    caption="Precision Workflow Suite v2.2 (Lite)",
)
st.sidebar.markdown(
    "**All-In-One Research Toolkit**\nStandardized molecular biology calculations"
    " & workflow automation."
)
st.sidebar.markdown("---")

# --- Sidebar: Lab Metadata ---
st.sidebar.header("📋 Lab Metadata")
researcher_name = st.sidebar.text_input(
    "Researcher Name", value="Dr. Jane Doe"
)
notebook_id = st.sidebar.text_input(
    "Lab Notebook ID / Project", value="NB-2026-Biolab-04"
)
exp_date = st.sidebar.date_input("Experiment Date")

st.title("🧬 BioTech Lab Suite: All-In-One Workbench")
st.markdown(
    "Access your PCR master mix calculations, thermocycling protocols, gel"
    " electrophoresis estimators, and molarity/dilution tools from a single"
    " platform."
)

# --- Create Main Navigation Tabs (4 Tabs) ---
tab1, tab2, tab3, tab4 = st.tabs([
    "🧪 PCR Master Mix",
    "🌡️ Thermal Cycler",
    "📏 Gel Estimator",
    "🧮 Molarity & Dilutions",
])

# ==========================================
# TAB 1: PCR MASTER MIX CALCULATOR
# ==========================================
with tab1:
  st.header("PCR Master Mix & Pipetting Calculator")
  st.markdown(
      "Calculate precise reagent volumes, account for dead volume, and follow a"
      " benchside checklist."
  )

  col_pcr1, col_pcr2 = st.columns([1, 2])

  with col_pcr1:
    st.subheader("Experiment Parameters")
    num_samples = st.number_input(
        "Number of Samples",
        min_value=1,
        max_value=200,
        value=10,
        step=1,
        key="pcr_samples",
    )
    replicates = st.number_input(
        "Replicates per Sample",
        min_value=1,
        max_value=5,
        value=2,
        step=1,
        key="pcr_reps",
    )
    controls = st.number_input(
        "Control Reactions (+/-)",
        min_value=0,
        max_value=10,
        value=2,
        step=1,
        key="pcr_ctrl",
    )
    dead_volume_pct = (
        st.slider("Dead Volume Buffer (%)", 0.0, 20.0, 10.0, 1.0, key="pcr_dv")
        / 100.0
    )
    single_rxn_vol = st.number_input(
        "Single Reaction Total Volume (µL)",
        min_value=5.0,
        max_value=100.0,
        value=20.0,
        step=1.0,
        key="pcr_vol",
    )

    base_reactions = (num_samples * replicates) + controls
    total_reactions_with_buffer = base_reactions * (1 + dead_volume_pct)
    practical_reactions = math.ceil(total_reactions_with_buffer)

    st.markdown("---")
    st.metric("Base Reactions", base_reactions)
    st.metric(
        "Total Reactions (+ Buffer)", f"{total_reactions_with_buffer:.2f}"
    )
    st.metric("Practical Multiplier (Rounded)", practical_reactions)

  with col_pcr2:
    st.subheader("Reagent Configuration")
    if "reagents_df" not in st.session_state:
      st.session_state.reagents_df = pd.DataFrame([
          {
              "Component": "2X Taq Master Mix",
              "Vol_per_rxn_uL": 10.0,
              "Type": "Mix",
          },
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
        st.session_state.reagents_df,
        num_rows="dynamic",
        use_container_width=True,
        key="pcr_editor",
    )

    st.subheader("Master Mix Preparation Summary")
    mix_components = edited_df[edited_df["Type"] != "Template"].copy()
    mix_components["Total_Volume_uL"] = (
        mix_components["Vol_per_rxn_uL"] * practical_reactions
    )

    non_water_vol = mix_components["Vol_per_rxn_uL"].sum()
    water_vol_per_rxn = single_rxn_vol - non_water_vol

    if water_vol_per_rxn < 0:
      st.error(
          "⚠️ **Error:** Component volumes ("
          f"{non_water_vol:.2f} µL) exceed single reaction volume ("
          f"{single_rxn_vol} µL)!"
      )
    else:
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
          ]].style.format({
              "Vol_per_rxn_uL": "{:.2f}",
              "Total_Volume_uL": "{:.2f}",
          }),
          use_container_width=True,
      )

      total_mix_volume = full_master_mix_df["Total_Volume_uL"].sum()
      st.success(
          f"✅ **Total Master Mix Volume:** **{total_mix_volume:.2f} µL**"
      )

      csv_data = full_master_mix_df[[
          "Component",
          "Vol_per_rxn_uL",
          "Total_Volume_uL",
      ]].to_csv(index=False)
      st.download_button(
          label="📥 Download Master Mix Sheet (CSV)",
          data=csv_data,
          file_name=f"pcr_master_mix_{base_reactions}rxns.csv",
          mime="text/csv",
