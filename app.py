from io import BytesIO
import math
import numpy as np
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
import streamlit as st

# --- 1. Page Configuration & Global Branding ---
st.set_page_config(
    page_title="BioTech Lab Suite | All-In-One", page_icon="🧬", layout="wide"
)

# Sidebar Branding
st.logo("https://images.unsplash.com/photo-1532187863486-abf9dbad1b69?w=100")
st.sidebar.image(
    "https://images.unsplash.com/photo-1579154204601-01588f351e67?w=400",
    caption="Precision Workflow Suite v2.3 (No-Plot)",
)
st.sidebar.markdown(
    "**All-In-One Research Toolkit**\nStandardized molecular biology calculations"
    " & cell culture tracking."
)
st.sidebar.markdown("---")

# --- Sidebar: Lab Metadata for PDF Reports ---
st.sidebar.header("📋 Lab Report Metadata")
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
    " electrophoresis estimators, molarity tools, and cell culture trackers"
    " from a single platform."
)

# --- PDF Generation Helper Function ---


def create_lab_report_pdf(
    pcr_df,
    protocol_df,
    base_reactions,
    practical_reactions,
    researcher,
    nb_id,
    date_str,
):
  buffer = BytesIO()
  doc = SimpleDocTemplate(
      buffer,
      pagesize=letter,
      rightMargin=36,
      leftMargin=36,
      topMargin=36,
      bottomMargin=36,
  )
  elements = []

  styles = getSampleStyleSheet()
  title_style = ParagraphStyle(
      "ReportTitle",
      parent=styles["Heading1"],
      fontSize=18,
      textColor=colors.HexColor("#1f77b4"),
      spaceAfter=4,
  )
  subtitle_style = ParagraphStyle(
      "ReportSubtitle",
      parent=styles["Normal"],
      fontSize=9,
      textColor=colors.HexColor("#666666"),
      spaceAfter=12,
  )
  heading_style = ParagraphStyle(
      "SectionHeading",
      parent=styles["Heading2"],
      fontSize=11,
      textColor=colors.HexColor("#333333"),
      spaceBefore=10,
      spaceAfter=6,
  )

  # Header
  elements.append(
      Paragraph("🧬 BioTech Lab Suite - Experiment Summary Report", title_style)
  )
  elements.append(
      Paragraph(
          "Precision Workflow Suite | Standardized Molecular Biology Protocol",
          subtitle_style,
      )
  )

  # Metadata Table Block
  meta_data = [
      [
          Paragraph(f"<b>Researcher:</b> {researcher}", styles["Normal"]),
          Paragraph(f"<b>Date:</b> {date_str}", styles["Normal"]),
      ],
      [
          Paragraph(f"<b>Notebook ID:</b> {nb_id}", styles["Normal"]),
          Paragraph(
              f"<b>Reactions:</b> {base_reactions} base ({practical_reactions}"
              " w/ buffer)",
              styles["Normal"],
          ),
      ],
  ]
  t_meta = Table(meta_data, colWidths=[270, 270])
  t_meta.setStyle(
      TableStyle([
          ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8f9fa")),
          ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#dcdcdc")),
          ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e5e5")),
          ("TOPPADDING", (0, 0), (-1, -1), 6),
          ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
          ("LEFTPADDING", (0, 0), (-1, -1), 8),
          ("RIGHTPADDING", (0, 0), (-1, -1), 8),
      ])
  )
  elements.append(t_meta)
  elements.append(Spacer(1, 15))

  # PCR Summary Section
  elements.append(Paragraph("1. PCR Master Mix Preparation", heading_style))
  pcr_table_data = [list(pcr_df.columns)] + pcr_df.values.tolist()
  t_pcr = Table(pcr_table_data, colWidths=[240, 150, 150])
  t_pcr.setStyle(
      TableStyle([
          ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f0f4f8")),
          ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1f77b4")),
          ("ALIGN", (0, 0), (-1, -1), "LEFT"),
          ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
          ("FONTSIZE", (0, 0), (-1, -1), 9),
          ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
          ("TOPPADDING", (0, 0), (-1, -1), 6),
          ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dcdcdc")),
      ])
  )
  elements.append(t_pcr)
  elements.append(Spacer(1, 15))

  # Thermal Cycler Profile Section
  elements.append(Paragraph("2. Thermal Cycler Protocol", heading_style))
  proto_table_data = [list(protocol_df.columns)] + protocol_df.values.tolist()
  t_proto = Table(proto_table_data, colWidths=[180, 120, 120, 120])
  t_proto.setStyle(
      TableStyle([
          ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f0f4f8")),
          ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1f77b4")),
          ("ALIGN", (0, 0), (-1, -1), "LEFT"),
          ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
          ("FONTSIZE", (0, 0), (-1, -1), 9),
          ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
          ("TOPPADDING", (0, 0), (-1, -1), 6),
          ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dcdcdc")),
      ])
  )
  elements.append(t_proto)

  doc.build(elements)
  buffer.seek(0)
  return buffer


# --- Create Main Navigation Tabs (5 Tabs) ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🧪 PCR Master Mix",
    "🌡️ Thermal Cycler",
    "📏 Gel Estimator",
    "🧮 Molarity & Dilutions",
    "🧫 Cell Culture Tracker",
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

      col_dl1, col_dl2 = st.columns(2)
      with col_dl1:
        csv_data = full_master_mix_df[[
            "Component",
            "Vol_per_rxn_uL",
            "Total_Volume_uL",
        ]].to_csv(index=False)
        st.download_button(
            label="📥 Download CSV Sheet",
            data=csv_data,
            file_name=f"pcr_master_mix_{base_reactions}rxns.csv",
            mime="text/csv",
            key="pcr_download",
        )

      with col_dl2:
        if "protocol_df" not in locals():
          protocol_df = pd.DataFrame(
              columns=["Step", "Temp (°C)", "Time", "Cycles"]
          )

        pdf_buffer = create_lab_report_pdf(
            full_master_mix_df[
                ["Component", "Vol_per_rxn_uL", "Total_Volume_uL"]
            ],
            protocol_df,
            base_reactions,
            practical_reactions,
            researcher=researcher_name,
            nb_id=notebook_id,
            date_str=str(exp_date),
        )
        st.download_button(
            label="📄 Download Lab Report (PDF)",
            data=pdf_buffer,
            file_name=f"lab_report_{notebook_id}.pdf",
            mime="application/pdf",
            key="pdf_download_btn",
        )

      st.markdown("---")
      st.subheader("Benchside Pipetting Checklist")
      for idx, row in full_master_mix_df.iterrows():
        st.checkbox(
            f"Add **{row['Component']}**: **{row['Total_Volume_uL']:.2f} µL**"
            f" total ({row['Vol_per_rxn_uL']:.2f} µL/rxn)",
            key=f"check_{idx}",
        )

# ==========================================
# TAB 2: THERMAL CYCLER PROTOCOL BUILDER
# ==========================================
with tab2:
  st.header("Thermal Cycler Protocol Configuration")
  st.markdown("Configure your thermocycling instrument settings and run times.")

  tc1, tc2, tc3 = st.columns(3)
  with tc1:
    init_temp = st.number_input(
        "Init. Denaturation Temp (°C)", 90.0, 99.0, 95.0, key="tc_init_t"
    )
    init_time = st.number_input(
        "Init. Denaturation Time (sec)", 10, 600, 180, key="tc_init_s"
    )
  with tc2:
    num_cycles = st.number_input("Cycle Count", 10, 50, 35, key="tc_cycles")
    denat_temp = st.number_input(
        "Cycle Denat. Temp (°C)", 90.0, 98.0, 95.0, key="tc_den_t"
    )
    denat_time = st.number_input(
        "Cycle Denat. Time (sec)", 5, 120, 30, key="tc_den_s"
    )
  with tc3:
    anneal_temp = st.number_input(
        "Annealing Temp (°C)", 45.0, 72.0, 58.0, key="tc_ann_t"
    )
    anneal_time = st.number_input(
        "Annealing Time (sec)", 5, 120, 30, key="tc_ann_s"
    )
    extend_temp = st.number_input(
        "Extension Temp (°C)", 60.0, 75.0, 72.0, key="tc_ext_t"
    )
    extend_time = st.number_input(
        "Extension Time (sec)", 10, 300, 45, key="tc_ext_s"
    )

  final_ext_temp = st.number_input(
      "Final Extension Temp (°C)", 60.0, 75.0, 72.0, key="f_temp"
  )
  final_ext_time = st.number_input(
      "Final Extension Time (sec)", 0, 600, 300, key="f_time"
  )

  protocol_data = [
      {
          "Step": "Initial Denaturation",
          "Temp (°C)": init_temp,
          "Time": f"{init_time} sec",
          "Cycles": "1",
      },
      {
          "Step": "Denaturation",
          "Temp (°C)": denat_temp,
          "Time": f"{denat_time} sec",
          "Cycles": f"{num_cycles}",
      },
      {
          "Step": "Annealing",
          "Temp (°C)": anneal_temp,
          "Time": f"{anneal_time} sec",
          "Cycles": f"{num_cycles}",
      },
      {
          "Step": "Extension",
          "Temp (°C)": extend_temp,
          "Time": f"{extend_time} sec",
          "Cycles": f"{num_cycles}",
      },
      {
          "Step": "Final Extension",
          "Temp (°C)": final_ext_temp,
          "Time": f"{final_ext_time} sec",
          "Cycles": "1",
      },
      {"Step": "Hold", "Temp (°C)": 4.0, "Time": "Indefinite", "Cycles": "1"},
  ]

  protocol_df = pd.DataFrame(protocol_data)
  st.subheader("Protocol Summary Table")
  st.dataframe(protocol_df, use_container_width=True)

  total_cycling_seconds = init_time + (
      num_cycles * (denat_time + anneal_time + extend_time)
  ) + final_ext_time
  st.info(
      f"⏱️ **Estimated Total PCR Run Time:**"
      f" ~{total_cycling_seconds / 60:.1f} minutes"
  )

# ==========================================
# TAB 3: GEL ELECTROPHORESIS SIZE ESTIMATOR
# ==========================================
with tab3:
  st.header("DNA Gel Electrophoresis Size Estimator")
  st.markdown(
      "Estimate unknown fragment sizes using log-linear migration analysis"
      " against a DNA ladder."
  )

  col_gel1, col_gel2 = st.columns([1, 1])

  with col_gel1:
    st.subheader("1. DNA Ladder Standard")
    if "ladder_df" not in st.session_state:
      st.session_state.ladder_df = pd.DataFrame({
          "Fragment Name": [
              "10 kb",
              "8 kb",
              "6 kb",
              "4 kb",
              "3 kb",
              "2 kb",
              "1.5 kb",
              "1 kb",
          ],
          "Size (bp)": [10000, 8000, 6000, 4000, 3000, 2000, 1500, 1000],
          "Migration Distance (mm)": [
              12.0,
              15.5,
              19.8,
              26.5,
              32.0,
              41.0,
              48.5,
              58.0,
          ],
      })

    edited_ladder = st.data_editor(
        st.session_state.ladder_df,
        num_rows="dynamic",
        use_container_width=True,
        key="gel_ladder",
    )

    unknown_distance = st.number_input(
        "Unknown Band Migration Distance (mm from well)",
        min_value=1.0,
        max_value=150.0,
        value=35.0,
        step=0.5,
        key="gel_unknown",
    )

  with col_gel2:
    st.subheader("2. Standard Curve & Estimation")
    valid_data = edited_ladder.dropna()
    sizes = valid_data["Size (bp)"].values
    distances = valid_data["Migration Distance (mm)"].values

    if len(sizes) < 3:
      st.warning(
          "⚠️ Please provide at least 3 valid ladder points for the standard"
          " curve."
      )
    else:
      log_sizes = np.log10(sizes)
      slope, intercept = np.polyfit(log_sizes, distances, 1)

      estimated_log_size = (unknown_distance - intercept) / slope
      estimated_size = 10**estimated_log_size

      st.success(
          f"🎯 **Estimated Fragment Size:** **{int(round(estimated_size))}"
          " bp**"
      )
      st.metric("Regression Slope ($m$)", f"{slope:.4f}")
      st.metric("Regression Intercept ($b$)", f"{intercept:.4f}")
      st.info(
          "📊 Standard curve calculated via log-linear regression successfully"
          " without external plotting dependencies."
      )

# ==========================================
# TAB 4: MOLARITY & DILUTIONS CALCULATOR
# ==========================================
with tab4:
  st.header("Molarity, Mass & Serial Dilution Calculator")
  st.markdown(
      "Perform rapid laboratory calculations for buffer preparation and"
      " dilutions."
  )

  sub_tab1, sub_tab2 = st.tabs(
      ["⚖️ Mass from Molarity", "🧪 Stock & Serial Dilutions"]
  )

  with sub_tab1:
    st.subheader("Calculate Solute Mass Required")
    col_m1, col_m2 = st.columns(2)
    with col_m1:
      target_conc = st.number_input(
          "Target Concentration", value=1.0, format="%.4f", key="mol_conc"
      )
      unit_conc = st.selectbox(
          "Concentration Unit",
          ["M (mol/L)", "mM (mmol/L)", "µM (µmol/L)"],
          key="mol_unit",
      )
      mw = st.number_input(
          "Molecular Weight (g/mol or Da)",
          value=150.0,
          format="%.2f",
          key="mol_mw",
      )
    with col_m2:
      target_vol = st.number_input(
          "Target Volume", value=100.0, format="%.2f", key="mol_vol"
      )
      unit_vol = st.selectbox(
          "Volume Unit", ["mL", "L", "µL"], key="vol_unit"
      )

    conc_mol_l = target_conc
    if "mM" in unit_conc:
      conc_mol_l = target_conc / 1000.0
    elif "µM" in unit_conc:
      conc_mol_l = target_conc / 1000000.0

    vol_l = target_vol
    if "mL" in unit_vol:
      vol_l = target_vol / 1000.0
    elif "µL" in unit_vol:
      vol_l = target_vol / 1000000.0

    required_mass_g = conc_mol_l * vol_l * mw
    required_mass_mg = required_mass_g * 1000.0
    required_mass_ug = required_mass_g * 1000000.0

    st.markdown("---")
    st.success(
        f"✅ **Required Solute Mass:** **{required_mass_g:.4f} g** ("
        f"**{required_mass_mg:.2f} mg** / **{required_mass_ug:.1f} µg**)"
    )

  with sub_tab2:
    st.subheader("Stock Dilution ($C_1V_1 = C_2V_2$)")
    col_d1, col_d2 = st.columns(2)
    with col_d1:
      c1 = st.number_input(
          "Stock Concentration ($C_1$)", value=10.0, format="%.2f", key="dil_c1"
      )
      v2 = st.number_input(
          "Final Desired Volume ($V_2$, mL)",
          value=10.0,
          format="%.2f",
          key="dil_v2",
      )
    with col_d2:
      c2 = st.number_input(
          "Final Desired Concentration ($C_2$)",
          value=1.0,
          format="%.2f",
          key="dil_c2",
      )

    if c1 > 0:
      v1 = (c2 * v2) / c1
      v_diluent = v2 - v1
      st.markdown("---")
      st.info(
          f"📌 **Preparation Instructions:** Mix **{v1:.3f} mL** of stock"
          f" solution ($C_1$) with **{v_diluent:.3f} mL** of diluent"
          f" (buffer/water) to achieve **{v2:.2f} mL** at concentration"
          f" **{c2}**."
      )

# ==========================================
# TAB 5: CELL CULTURE TRACKER
# ==========================================
with tab5:
  st.header("Mammalian Cell Culture Passaging & Doubling Time Tracker")
  st.markdown(
      "Calculate split ratios, monitor cell confluence, and determine"
      " population doubling time (PDT)."
  )

  c_col1, c_col2 = st.columns(2)

  with c_col1:
    st.subheader("1. Seeding & Confluence Parameters")
    cell_line = st.text_input("Cell Line Name", value="HEK293T")
    current_confluence = st.slider(
        "Current Confluence (%)", min_value=10, max_value=100, value=80, step=5
    )
    target_split_confluence = st.slider(
        "Target Seeding Confluence (%)",
        min_value=10,
        max_value=90,
        value=30,
        step=5,
    )
    flask_growth_area = st.selectbox(
        "Culture Vessel Size",
        ["T-25 flask (25 cm²)", "T-75 flask (75 cm²)", "10 cm dish (55 cm²)"],
    )

    estimated_split_ratio = current_confluence / target_split_confluence
    st.info(
        f"📌 **Recommended Split Ratio:** ~1:{estimated_split_ratio:.1f}"
        f" (based on {current_confluence}% to {target_split_confluence}% target)"
    )

  with c_col2:
    st.subheader("2. Population Doubling Time (PDT)")
    st.markdown(
        "Formula: $PDT = \\frac{t \\times \\log(2)}{\\log(N_f) - \\log(N_i)}$"
    )

    n_initial = st.number_input(
        "Initial Cell Count ($N_i$, e.g., seeded)",
        value=0.5,
        format="%.2f",
        help="In millions",
    )
    n_final = st.number_input(
        "Harvested Cell Count ($N_f$, e.g., collected)",
        value=4.0,
        format="%.2f",
        help="In millions",
    )
    time_elapsed_hrs = st.number_input(
        "Time Elapsed ($t$, hours)",
        min_value=1.0,
        max_value=336.0,
        value=72.0,
        step=1.0,
    )

    if n_initial > 0 and n_final > n_initial and time_elapsed_hrs > 0:
      pdt_hours = (
          time_elapsed_hrs
          * np.log10(2)
          / (np.log10(n_final) - np.log10(n_initial))
      )
      num_doublings = (np.log10(n_final) - np.log10(n_initial)) / np.log10(2)

      st.success(f"⏱️ **Population Doubling Time (PDT):** **{pdt_hours:.2f} hours**")
      st.metric("Total Population Doublings", f"{num_doublings:.2f} doublings")
    else:
      st.warning(
          "⚠️ Harvested count ($N_f$) must be greater than initial count ($N_i$)"
          " for PDT calculation."
      )
