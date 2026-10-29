"""
FraudLens AI - Executive Modern Slide Deck Generator
Matches the modern, card-based, minimalist layout of the reference presentation:
- 13 structured widescreen (16:9) slides
- Card containers with rounded corners, subtle borders, and structured grids
- Hero stat metric cards with large figures and labels
- Visual pipeline flow indicators
- Bottom key takeaway / summary callout bars
- Distinctive, premium FinTech / Cyber Risk theme
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

# Theme Palette (Distinctive FinTech Risk Theme)
BG_DARK = RGBColor(11, 19, 41)         # Deep midnight navy
BG_LIGHT = RGBColor(248, 250, 252)     # Crisp slate-50
CARD_BG = RGBColor(255, 255, 255)      # Pure white card
CARD_BORDER = RGBColor(226, 232, 240)  # Subtle border
BANNER_BG = RGBColor(238, 242, 255)    # Soft indigo tint
BANNER_BORDER = RGBColor(99, 102, 241) # Indigo accent

TEXT_MAIN = RGBColor(15, 23, 42)       # Slate-900
TEXT_MUTED = RGBColor(71, 85, 105)     # Slate-600
TEXT_WHITE = RGBColor(255, 255, 255)
TAG_COLOR = RGBColor(37, 99, 235)      # Royal blue
ACCENT_CYAN = RGBColor(56, 189, 248)   # Cyan
ACCENT_GREEN = RGBColor(16, 185, 129)  # Emerald
ACCENT_RED = RGBColor(239, 68, 68)     # Rose
ACCENT_PURPLE = RGBColor(147, 51, 234) # Purple

def set_slide_background(slide, color):
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg.fill.solid()
    bg.fill.fore_color.rgb = color
    bg.line.fill.background()
    return bg

def add_header(slide, tag_text, title_text, dark=False):
    header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(11.7), Inches(1.1))
    tf = header_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    
    p_tag = tf.paragraphs[0]
    p_tag.text = tag_text.upper()
    p_tag.font.size = Pt(10)
    p_tag.font.bold = True
    p_tag.font.color.rgb = ACCENT_CYAN if dark else TAG_COLOR
    
    p_title = tf.add_paragraph()
    p_title.text = title_text
    p_title.font.size = Pt(24)
    p_title.font.bold = True
    p_title.font.color.rgb = TEXT_WHITE if dark else TEXT_MAIN
    p_title.space_before = Pt(4)

def add_card(slide, left, top, width, height, bg_color=CARD_BG, border_color=CARD_BORDER):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    if border_color:
        card.line.color.rgb = border_color
        card.line.width = Pt(1)
    else:
        card.line.fill.background()
    return card

def add_bottom_bar(slide, text, highlight_label="Key Takeaway:"):
    bar = add_card(slide, Inches(0.8), Inches(6.5), Inches(11.733), Inches(0.55), bg_color=BANNER_BG, border_color=BANNER_BORDER)
    # add accent strip on the left
    strip = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(6.5), Inches(0.08), Inches(0.55))
    strip.fill.solid()
    strip.fill.fore_color.rgb = BANNER_BORDER
    strip.line.fill.background()
    
    tb = slide.shapes.add_textbox(Inches(1.05), Inches(6.52), Inches(11.3), Inches(0.5))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    
    r1 = p.add_run()
    r1.text = f"{highlight_label} "
    r1.font.bold = True
    r1.font.size = Pt(11)
    r1.font.color.rgb = BANNER_BORDER
    
    r2 = p.add_run()
    r2.text = text
    r2.font.size = Pt(11)
    r2.font.color.rgb = TEXT_MAIN


def build_deck(output_path="reports/FraudLens_AI_Presentation.pptx"):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # =========================================================================
    # SLIDE 1: Title Slide (Dark Theme)
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1, BG_DARK)
    
    # Title Text
    t_box = s1.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(11.7), Inches(3.2))
    tf1 = t_box.text_frame
    tf1.word_wrap = True
    
    p0 = tf1.paragraphs[0]
    p0.text = "CAPSTONE PRESENTATION OVERVIEW"
    p0.font.size = Pt(11)
    p0.font.bold = True
    p0.font.color.rgb = ACCENT_CYAN
    
    p1 = tf1.add_paragraph()
    p1.text = "FraudLens AI: Real-Time Financial\nFraud Decision-Support Engine"
    p1.font.size = Pt(36)
    p1.font.bold = True
    p1.font.color.rgb = TEXT_WHITE
    p1.space_before = Pt(8)
    
    p2 = tf1.add_paragraph()
    p2.text = "A machine learning pipeline combining cost-sensitive classification and unsupervised anomaly detection for instant transaction risk triage."
    p2.font.size = Pt(15)
    p2.font.color.rgb = RGBColor(148, 163, 184)
    p2.space_before = Pt(12)
    
    # Bottom Left Card: Presenter Details
    c1 = add_card(s1, Inches(0.8), Inches(5.3), Inches(4.5), Inches(1.5), bg_color=RGBColor(21, 32, 63), border_color=RGBColor(38, 52, 92))
    tb_c1 = s1.shapes.add_textbox(Inches(1.0), Inches(5.45), Inches(4.1), Inches(1.2))
    tf_c1 = tb_c1.text_frame
    p_c1_0 = tf_c1.paragraphs[0]
    p_c1_0.text = "PRESENTER DETAILS"
    p_c1_0.font.size = Pt(10)
    p_c1_0.font.bold = True
    p_c1_0.font.color.rgb = RGBColor(148, 163, 184)
    
    p_c1_1 = tf_c1.add_paragraph()
    p_c1_1.text = "Manish Patil"
    p_c1_1.font.size = Pt(14)
    p_c1_1.font.bold = True
    p_c1_1.font.color.rgb = TEXT_WHITE
    
    p_c1_2 = tf_c1.add_paragraph()
    p_c1_2.text = "Machine Learning PBL Project (100 Marks)"
    p_c1_2.font.size = Pt(11)
    p_c1_2.font.color.rgb = ACCENT_CYAN

    # Bottom Right Card: Deliverables & Links
    c2 = add_card(s1, Inches(5.6), Inches(5.3), Inches(6.9), Inches(1.5), bg_color=RGBColor(21, 32, 63), border_color=RGBColor(38, 52, 92))
    tb_c2 = s1.shapes.add_textbox(Inches(5.8), Inches(5.45), Inches(6.5), Inches(1.2))
    tf_c2 = tb_c2.text_frame
    p_c2_0 = tf_c2.paragraphs[0]
    p_c2_0.text = "PROJECT DELIVERABLES & DEPLOYMENT"
    p_c2_0.font.size = Pt(10)
    p_c2_0.font.bold = True
    p_c2_0.font.color.rgb = RGBColor(148, 163, 184)
    
    p_c2_1 = tf_c2.add_paragraph()
    p_c2_1.text = "💻 Repository: github.com/Manish-Patil33/FraudLens-Al-"
    p_c2_1.font.size = Pt(12)
    p_c2_1.font.bold = True
    p_c2_1.font.color.rgb = TEXT_WHITE
    
    p_c2_2 = tf_c2.add_paragraph()
    p_c2_2.text = "🌐 Live Web App: fraudlensai1.streamlit.app"
    p_c2_2.font.size = Pt(12)
    p_c2_2.font.bold = True
    p_c2_2.font.color.rgb = ACCENT_CYAN

    s1.notes_slide.notes_text_frame.text = "Welcome evaluators. Today I am presenting FraudLens AI, a complete machine learning pipeline for real-time transaction fraud triage."

    # =========================================================================
    # SLIDE 2: Project Foundation
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2, BG_LIGHT)
    add_header(s2, "PROJECT FOUNDATION", "FraudLens AI Core Objective & Framework")
    
    # Card 1: Dual-Engine Prototype
    c_s2_1 = add_card(s2, Inches(0.8), Inches(2.0), Inches(5.7), Inches(3.8))
    tb = s2.shapes.add_textbox(Inches(1.1), Inches(2.3), Inches(5.1), Inches(3.2))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "🛡️ Dual-Engine Triage System"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = TEXT_MAIN
    
    p_desc = tf.add_paragraph()
    p_desc.text = "\nProactive decision-support engine engineered to intercept fraudulent transactions in sub-15ms before catastrophic fund liquidation occurs across payment rails.\n\nCombines supervised classification with unsupervised anomaly detection to guarantee zero-day protection."
    p_desc.font.size = Pt(12.5)
    p_desc.font.color.rgb = TEXT_MUTED

    # Card 2: Severe Imbalance Benchmark
    c_s2_2 = add_card(s2, Inches(6.8), Inches(2.0), Inches(5.7), Inches(3.8))
    tb2 = s2.shapes.add_textbox(Inches(7.1), Inches(2.3), Inches(5.1), Inches(3.2))
    tf2 = tb2.text_frame
    tf2.word_wrap = True
    p = tf2.paragraphs[0]
    p.text = "⚖️ The Extreme Imbalance Problem"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = TEXT_MAIN
    
    p_desc2 = tf2.add_paragraph()
    p_desc2.text = "\nIn real-world digital banking, fraud accounts for less than 0.5% of total volume.\n\nA trivial majority baseline predicting 100% legitimate transactions achieves 99.5% accuracy but stops $0 of financial theft.\n\nFraudLens AI replaces naive metrics with PR-AUC and cost-benefit financial matrices."
    p_desc2.font.size = Pt(12.5)
    p_desc2.font.color.rgb = TEXT_MUTED

    add_bottom_bar(s2, "Optimizing financial loss prevention and precision-recall trade-offs over vanity accuracy scores.", "Key Takeaway:")

    # =========================================================================
    # SLIDE 3: Operational Context
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3, BG_LIGHT)
    add_header(s3, "OPERATIONAL CONTEXT", "Solving the Financial Risk Triage Problem")
    
    # Card 1: Analyst Workflow
    add_card(s3, Inches(0.8), Inches(2.0), Inches(5.7), Inches(3.5))
    tb = s3.shapes.add_textbox(Inches(1.1), Inches(2.3), Inches(5.1), Inches(3.0))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "👥 Fraud Analyst Workflow"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = TEXT_MAIN
    p_d = tf.add_paragraph()
    p_d.text = "\nEnables bank operations to automate 98%+ of low-risk transactions frictionlessly, while directing investigator focus strictly to pre-flagged high-probability syndicates and compromised accounts."
    p_d.font.size = Pt(13)
    p_d.font.color.rgb = TEXT_MUTED

    # Card 2: Review Signal
    add_card(s3, Inches(6.8), Inches(2.0), Inches(5.7), Inches(3.5))
    tb = s3.shapes.add_textbox(Inches(7.1), Inches(2.3), Inches(5.1), Inches(3.0))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "🚦 3-Tier Decision Routing"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = TEXT_MAIN
    p_d = tf.add_paragraph()
    p_d.text = "\nModel outputs a calibrated 0-100 risk score governing progressive actions:\n• Score < 35: Frictionless APPROVE\n• 35 - 75: Step-Up CHALLENGE (Biometric/MFA)\n• >= 75: AUTO-BLOCK & Fraud Queue"
    p_d.font.size = Pt(13)
    p_d.font.color.rgb = TEXT_MUTED

    # 3 Badges at bottom
    badges = [
        ("⚡ Early Intervention", "Pre-liquidation interception"),
        ("🛡️ Human-in-the-Loop", "Targeted fraud queue triage"),
        ("💰 Resource Optimization", "99% reduction in alert fatigue")
    ]
    for idx, (b_title, b_sub) in enumerate(badges):
        b_x = Inches(0.8 + idx * 4.0)
        c_b = add_card(s3, b_x, Inches(5.8), Inches(3.73), Inches(1.1), bg_color=CARD_BG, border_color=CARD_BORDER)
        tb_b = s3.shapes.add_textbox(b_x + Inches(0.2), Inches(5.9), Inches(3.3), Inches(0.9))
        tf_b = tb_b.text_frame
        p_b1 = tf_b.paragraphs[0]
        p_b1.text = b_title
        p_b1.font.bold = True
        p_b1.font.size = Pt(12)
        p_b1.font.color.rgb = TAG_COLOR
        p_b2 = tf_b.add_paragraph()
        p_b2.text = b_sub
        p_b2.font.size = Pt(10)
        p_b2.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 4: Data Architecture
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4, BG_LIGHT)
    add_header(s4, "DATA ARCHITECTURE", "Dataset Composition & Imbalance Structure")
    
    # 4 Metric Cards
    metrics_s4 = [
        ("60,000", "Total Transactions", TAG_COLOR),
        ("14", "Schema Attributes", ACCENT_GREEN),
        ("15+", "Synthesized Features", ACCENT_PURPLE),
        ("300 / 59,700", "Class Imbalance (0.50% Fraud)", ACCENT_RED)
    ]
    for idx, (m_val, m_lbl, m_col) in enumerate(metrics_s4):
        x_pos = Inches(0.8 + idx * 3.0)
        add_card(s4, x_pos, Inches(1.9), Inches(2.73), Inches(1.6))
        tb = s4.shapes.add_textbox(x_pos, Inches(2.05), Inches(2.73), Inches(1.3))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        p.text = m_val
        p.font.size = Pt(26)
        p.font.bold = True
        p.font.color.rgb = m_col
        
        p_l = tf.add_paragraph()
        p_l.alignment = PP_ALIGN.CENTER
        p_l.text = m_lbl
        p_l.font.size = Pt(10.5)
        p_l.font.color.rgb = TEXT_MUTED

    # Two lower cards
    add_card(s4, Inches(0.8), Inches(3.8), Inches(5.7), Inches(2.3))
    tb = s4.shapes.add_textbox(Inches(1.1), Inches(4.0), Inches(5.1), Inches(1.9))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "📊 Schema Dimensions"
    p.font.bold = True
    p.font.size = Pt(14)
    p.font.color.rgb = TEXT_MAIN
    p_d = tf.add_paragraph()
    p_d.text = "Origin/destination balances before & after, transaction amounts, device trust scores (fingerprinting), location geo-velocity risk, access channel, and hourly simulation time steps (720 hours / 30 days)."
    p_d.font.size = Pt(11)
    p_d.font.color.rgb = TEXT_MUTED
    p_d.space_before = Pt(4)

    add_card(s4, Inches(6.8), Inches(3.8), Inches(5.7), Inches(2.3))
    tb = s4.shapes.add_textbox(Inches(7.1), Inches(4.0), Inches(5.1), Inches(1.9))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "🌐 Benchmark Foundation"
    p.font.bold = True
    p.font.size = Pt(14)
    p.font.color.rgb = TEXT_MAIN
    p_d = tf.add_paragraph()
    p_d.text = "Modeled on authoritative Kaggle PaySim mobile money simulation logs (ntnu-testimon/paysim1). Faithfully reproduces realistic economic distributions, long-tail amounts, and behavioral fraud signatures."
    p_d.font.size = Pt(11)
    p_d.font.color.rgb = TEXT_MUTED
    p_d.space_before = Pt(4)

    add_bottom_bar(s4, "Preserving true extreme class imbalance is required to guarantee authentic evaluation.", "Data Principle:")

    # =========================================================================
    # SLIDE 5: Exploratory Data Analysis
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5, BG_LIGHT)
    add_header(s5, "EXPLORATORY DATA ANALYSIS", "Data Quality Audit & Empirical Fraud Footprints")
    
    # Left Card: Quality Audit
    add_card(s5, Inches(0.8), Inches(1.9), Inches(5.7), Inches(4.3))
    tb = s5.shapes.add_textbox(Inches(1.1), Inches(2.2), Inches(5.1), Inches(3.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "🔍 Quality Audit & Distributions"
    p.font.bold = True
    p.font.size = Pt(16)
    p.font.color.rgb = TEXT_MAIN
    
    items_qa = [
        ("✔ Zero Missing Values:", "Complete 60,000 transaction records with automated median/mode imputation fallback."),
        ("✔ No Exact Duplicates:", "High feature variance across genuine accounts and recipients."),
        ("⚠ Extreme Power-Law Skew:", "Amounts span $1 to $1.5M; stabilized via log1p transformation to normalize heavy tails.")
    ]
    for h, b in items_qa:
        p_i = tf.add_paragraph()
        p_i.text = f"{h} {b}"
        p_i.font.size = Pt(11.5)
        p_i.font.color.rgb = TEXT_MUTED
        p_i.space_before = Pt(10)

    # Right Card: Key Behavioral Signals
    add_card(s5, Inches(6.8), Inches(1.9), Inches(5.7), Inches(4.3))
    tb = s5.shapes.add_textbox(Inches(7.1), Inches(2.2), Inches(5.1), Inches(3.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "🚨 Critical Fraud Signatures"
    p.font.bold = True
    p.font.size = Pt(16)
    p.font.color.rgb = TEXT_MAIN
    
    sigs = [
        ("100% Rail Concentration:", "All fraud strictly confined to TRANSFER and CASH_OUT operations (illicit siphon & liquidation)."),
        ("Off-Peak Cyber Attack Window:", "Fraud spikes between 00:00 and 05:00 hours when manual oversight is minimal."),
        ("94.6% Account Liquidation:", "Originator balance dropped to exactly $0.00 after transaction execution.")
    ]
    for h, b in sigs:
        p_i = tf.add_paragraph()
        p_i.text = f"• {h} {b}"
        p_i.font.size = Pt(11.5)
        p_i.font.color.rgb = TEXT_MUTED
        p_i.space_before = Pt(10)

    add_bottom_bar(s5, "Correlation confirms strong linear predictive signals between balance drainage and fraudulent intent.", "Finding:")

    # =========================================================================
    # SLIDE 6: Data Engineering & Leakage Prevention
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6, BG_LIGHT)
    add_header(s6, "DATA ENGINEERING", "Leakage-Safe Preprocessing Pipeline")
    
    # 3 Flow Cards with Arrows
    flow_steps = [
        ("80 / 20 Stratified Split", "48,000 Train / 12,000 Test preserve exact 0.50% rare fraud proportion."),
        ("Feature Engineering", "Balance reconciliation deltas and cyber trust indices synthesized row-wise."),
        ("Strict Transformer Isolation", "RobustScaler fitted strictly on training fold; test set purely transformed.")
    ]
    for idx, (s_title, s_desc) in enumerate(flow_steps):
        x = Inches(0.8 + idx * 4.0)
        add_card(s6, x, Inches(2.2), Inches(3.73), Inches(2.4))
        tb = s6.shapes.add_textbox(x + Inches(0.25), Inches(2.5), Inches(3.23), Inches(1.9))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = f"0{idx+1}. {s_title}"
        p.font.bold = True
        p.font.size = Pt(14)
        p.font.color.rgb = TAG_COLOR
        
        p_d = tf.add_paragraph()
        p_d.text = s_desc
        p_d.font.size = Pt(11.5)
        p_d.font.color.rgb = TEXT_MUTED
        p_d.space_before = Pt(8)

    # Wide bottom card: Cross-Validation Integrity
    add_card(s6, Inches(0.8), Inches(4.9), Inches(11.733), Inches(1.3))
    tb = s6.shapes.add_textbox(Inches(1.1), Inches(5.1), Inches(11.1), Inches(0.9))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "🔄 Cross-Validation & Production Serving Integrity"
    p.font.bold = True
    p.font.size = Pt(13)
    p.font.color.rgb = TEXT_MAIN
    p_d = tf.add_paragraph()
    p_d.text = "Every preprocessing transformer (RobustScaler, OneHotEncoder) is serialized into preprocessor.joblib. Production web serving mirrors exact training preprocessing with zero leakage."
    p_d.font.size = Pt(11)
    p_d.font.color.rgb = TEXT_MUTED
    p_d.space_before = Pt(2)

    add_bottom_bar(s6, "Splitting before transforming ensures test evaluation perfectly reflects production conditions.", "Integrity Guarantee:")

    # =========================================================================
    # SLIDE 7: Feature Engineering
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7, BG_LIGHT)
    add_header(s7, "FEATURE ENGINEERING", "Domain-Specific Feature Synthesis & Attribution")
    
    f_cards = [
        ("error_balance_orig", "Balance Reconciliation", "(newbalanceOrig + amount) - oldbalanceOrg. In legitimate transfers, delta is 0. In fraud, attackers siphon funds causing massive balance discrepancy errors (38.4% importance)."),
        ("orig_account_drained", "Liquidation Sentinel", "Binary flag triggering when origin balance is wiped to exactly $0.00. Identifies complete account drainage in automated bot attacks (21.7% importance)."),
        ("combined_risk_index", "Cyber Trust Score", "Fuses device fingerprint trust score with geo-velocity IP risk. Catches emulators, VPN proxies, and sudden location hops (17.2% importance).")
    ]
    for idx, (f_code, f_title, f_desc) in enumerate(f_cards):
        x = Inches(0.8 + idx * 4.0)
        add_card(s7, x, Inches(2.0), Inches(3.73), Inches(4.2))
        tb = s7.shapes.add_textbox(x + Inches(0.25), Inches(2.3), Inches(3.23), Inches(3.6))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = f_title
        p.font.bold = True
        p.font.size = Pt(15)
        p.font.color.rgb = TEXT_MAIN
        
        p_c = tf.add_paragraph()
        p_c.text = f"Feature: {f_code}"
        p_c.font.bold = True
        p_c.font.size = Pt(11)
        p_c.font.color.rgb = TAG_COLOR
        p_c.space_before = Pt(4)
        
        p_d = tf.add_paragraph()
        p_d.text = f_desc
        p_d.font.size = Pt(11)
        p_d.font.color.rgb = TEXT_MUTED
        p_d.space_before = Pt(8)

    add_bottom_bar(s7, "Domain-engineered features account for over 60% of total model predictive power.", "Feature Ranking:")

    # =========================================================================
    # SLIDE 8: Model Selection & Tuning Search
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8, BG_LIGHT)
    add_header(s8, "ALGORITHM EVALUATION", "Model Selection & Architecture Benchmarking")
    
    # Left Comparison Table Card
    add_card(s8, Inches(0.8), Inches(1.9), Inches(6.5), Inches(4.3))
    tb = s8.shapes.add_textbox(Inches(1.1), Inches(2.2), Inches(5.9), Inches(3.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Candidate Family Comparison"
    p.font.bold = True
    p.font.size = Pt(16)
    p.font.color.rgb = TEXT_MAIN
    
    models_comp = [
        ("Logistic Regression (Cost-Sensitive)", "Evaluated", "PR-AUC: 0.9962"),
        ("HistGradientBoosting", "Evaluated", "PR-AUC: 0.9834"),
        ("XGBoost (scale_pos_weight = 150)", "Evaluated", "PR-AUC: 0.9997"),
        ("Isolation Forest (Unsupervised Anomaly)", "Evaluated", "PR-AUC: 0.9997"),
        ("Random Forest (Balanced Subsample)", "Selected Champion", "PR-AUC: 1.0000")
    ]
    for m_name, m_status, m_score in models_comp:
        p_m = tf.add_paragraph()
        p_m.text = f"• {m_name} — {m_status} ({m_score})"
        p_m.font.size = Pt(11)
        p_m.font.color.rgb = TAG_COLOR if "Selected" in m_status else TEXT_MUTED
        p_m.space_before = Pt(8)

    # Right Big Hero Metric Box (Blue)
    hero = add_card(s8, Inches(7.6), Inches(1.9), Inches(4.9), Inches(4.3), bg_color=TAG_COLOR, border_color=None)
    tb_h = s8.shapes.add_textbox(Inches(7.8), Inches(2.6), Inches(4.5), Inches(3.0))
    tf_h = tb_h.text_frame
    tf_h.word_wrap = True
    p_h1 = tf_h.paragraphs[0]
    p_h1.alignment = PP_ALIGN.CENTER
    p_h1.text = "1.0000"
    p_h1.font.size = Pt(46)
    p_h1.font.bold = True
    p_h1.font.color.rgb = TEXT_WHITE
    
    p_h2 = tf_h.add_paragraph()
    p_h2.alignment = PP_ALIGN.CENTER
    p_h2.text = "Champion Model PR-AUC"
    p_h2.font.size = Pt(16)
    p_h2.font.bold = True
    p_h2.font.color.rgb = TEXT_WHITE
    p_h2.space_before = Pt(4)
    
    p_h3 = tf_h.add_paragraph()
    p_h3.alignment = PP_ALIGN.CENTER
    p_h3.text = "Random Forest Ensemble\n100 Trees | Balanced Subsampling"
    p_h3.font.size = Pt(12)
    p_h3.font.color.rgb = RGBColor(219, 234, 254)
    p_h3.space_before = Pt(8)

    add_bottom_bar(s8, "Champion selection is governed by Precision-Recall AUC under severe rare-event conditions.", "Selection Criterion:")

    # =========================================================================
    # SLIDE 9: Test Set Evaluation
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9, BG_LIGHT)
    add_header(s9, "VALIDATION PERFORMANCE", "Test Set Evaluation (12,000 Holdout Samples)")
    
    # 5 Big Metric Cards
    metrics_eval = [
        ("100.0%", "Accuracy", TAG_COLOR),
        ("1.0000", "PR-AUC (KPI)", ACCENT_GREEN),
        ("1.0000", "ROC-AUC", ACCENT_PURPLE),
        ("100.0%", "Precision", TAG_COLOR),
        ("100.0%", "Recall (60/60)", ACCENT_GREEN)
    ]
    for idx, (m_val, m_lbl, m_col) in enumerate(metrics_eval):
        x = Inches(0.8 + idx * 2.4)
        add_card(s9, x, Inches(1.9), Inches(2.2), Inches(1.6))
        tb = s9.shapes.add_textbox(x, Inches(2.05), Inches(2.2), Inches(1.3))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        p.text = m_val
        p.font.size = Pt(24)
        p.font.bold = True
        p.font.color.rgb = m_col
        
        p_l = tf.add_paragraph()
        p_l.alignment = PP_ALIGN.CENTER
        p_l.text = m_lbl
        p_l.font.size = Pt(10)
        p_l.font.color.rgb = TEXT_MUTED

    # Confusion Matrix Card
    add_card(s9, Inches(0.8), Inches(3.8), Inches(5.7), Inches(2.4))
    tb_cm = s9.shapes.add_textbox(Inches(1.1), Inches(4.0), Inches(5.1), Inches(2.0))
    tf_cm = tb_cm.text_frame
    p_cm = tf_cm.paragraphs[0]
    p_cm.text = "Confusion Matrix (12,000 Holdout Tests)"
    p_cm.font.bold = True
    p_cm.font.size = Pt(13)
    p_cm.font.color.rgb = TEXT_MAIN
    
    cm_items = [
        ("True Negatives (TN): 11,940", "Legitimate approved without friction"),
        ("False Positives (FP): 0", "Zero false alert disruptions"),
        ("False Negatives (FN): 0", "Zero fraud allowed to escape"),
        ("True Positives (TP): 60", "All 60 fraud attacks intercepted")
    ]
    for c_t, c_d in cm_items:
        p_i = tf_cm.add_paragraph()
        p_i.text = f"• {c_t} — {c_d}"
        p_i.font.size = Pt(10.5)
        p_i.font.color.rgb = TEXT_MUTED
        p_i.space_before = Pt(3)

    # Baseline Comparison Card
    add_card(s9, Inches(6.8), Inches(3.8), Inches(5.7), Inches(2.4))
    tb_b = s9.shapes.add_textbox(Inches(7.1), Inches(4.0), Inches(5.1), Inches(2.0))
    tf_b = tb_b.text_frame
    p_b = tf_b.paragraphs[0]
    p_b.text = "Baseline Benchmark Comparison"
    p_b.font.bold = True
    p_b.font.size = Pt(13)
    p_b.font.color.rgb = TEXT_MAIN
    
    p_bd = tf_b.add_paragraph()
    p_bd.text = "Significant gain over naive majority class prediction:\n• Majority Baseline: Catches 0% of fraud ($1.56M loss)\n• FraudLens AI: Catches 100% of fraud with 0% false positives\n• Average Inference Latency: 12.4 milliseconds."
    p_bd.font.size = Pt(11)
    p_bd.font.color.rgb = TEXT_MUTED
    p_bd.space_before = Pt(6)

    add_bottom_bar(s9, "Near-perfect separation achieved through balance error reconciliation and isolation trees.", "Result:")

    # =========================================================================
    # SLIDE 10: Error Analysis & Thresholding
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10, BG_LIGHT)
    add_header(s10, "ERROR ANALYSIS", "Trade-Off Analysis & Adaptive Thresholding")
    
    # False Alarm Card (Red tint)
    add_card(s10, Inches(0.8), Inches(2.0), Inches(5.7), Inches(2.8), bg_color=RGBColor(254, 242, 242), border_color=RGBColor(254, 202, 202))
    tb = s10.shapes.add_textbox(Inches(1.1), Inches(2.3), Inches(5.1), Inches(2.3))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "⚠️ False Alarms (Customer Friction)"
    p.font.bold = True
    p.font.size = Pt(16)
    p.font.color.rgb = ACCENT_RED
    p_d = tf.add_paragraph()
    p_d.text = "\nConsumes bank operational investigator hours and causes customer churn by needlessly declining legitimate transactions.\n\nFraudLens AI reduces False Positive Rate to 0.0000% on the benchmark stream."
    p_d.font.size = Pt(11.5)
    p_d.font.color.rgb = TEXT_MUTED

    # Missed Fraud Card (Red tint)
    add_card(s10, Inches(6.8), Inches(2.0), Inches(5.7), Inches(2.8), bg_color=RGBColor(254, 242, 242), border_color=RGBColor(254, 202, 202))
    tb = s10.shapes.add_textbox(Inches(7.1), Inches(2.3), Inches(5.1), Inches(2.3))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "🚨 Missed Fraud (Capital Drain)"
    p.font.bold = True
    p.font.size = Pt(16)
    p.font.color.rgb = ACCENT_RED
    p_d = tf.add_paragraph()
    p_d.text = "\nHigh-value account siphons bypass filters unflagged, resulting in permanent financial loss and regulatory penalties.\n\nFraudLens AI achieved 100% recall, preventing $1.56M in fraudulent losses."
    p_d.font.size = Pt(11.5)
    p_d.font.color.rgb = TEXT_MUTED

    # Stakeholder Threshold Card
    add_card(s10, Inches(0.8), Inches(5.1), Inches(11.733), Inches(1.2))
    tb = s10.shapes.add_textbox(Inches(1.1), Inches(5.25), Inches(11.1), Inches(0.9))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "🤝 Stakeholder Threshold Alignment"
    p.font.bold = True
    p.font.size = Pt(13)
    p.font.color.rgb = TEXT_MAIN
    p_d = tf.add_paragraph()
    p_d.text = "Operating classification threshold is calibrated at 0.125 to balance investigator labor vs fraud loss. Borderline transactions (scores 35-75) trigger step-up biometric challenges rather than outright declines."
    p_d.font.size = Pt(11)
    p_d.font.color.rgb = TEXT_MUTED

    add_bottom_bar(s10, "Calibrated routing stops bot liquidations while protecting user checkout conversion.", "Operational Takeaway:")

    # =========================================================================
    # SLIDE 11: Financial Impact & ROI
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_background(s11, BG_LIGHT)
    add_header(s11, "FINANCIAL IMPACT", "Executive Balance Sheet & Dollar ROI")
    
    # 4 Financial Metric Cards
    metrics_fin = [
        ("$1,567,200", "Total Fraud at Risk", TEXT_MUTED),
        ("$1,567,200", "Fraud Losses Intercepted", ACCENT_GREEN),
        ("$1,500", "Operational Review Cost", ACCENT_RED),
        ("$1,565,700", "Net Financial Savings", TAG_COLOR)
    ]
    for idx, (m_val, m_lbl, m_col) in enumerate(metrics_fin):
        x = Inches(0.8 + idx * 3.0)
        add_card(s11, x, Inches(1.9), Inches(2.73), Inches(1.6))
        tb = s11.shapes.add_textbox(x, Inches(2.05), Inches(2.73), Inches(1.3))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        p.text = m_val
        p.font.size = Pt(24)
        p.font.bold = True
        p.font.color.rgb = m_col
        
        p_l = tf.add_paragraph()
        p_l.alignment = PP_ALIGN.CENTER
        p_l.text = m_lbl
        p_l.font.size = Pt(10.5)
        p_l.font.color.rgb = TEXT_MUTED

    # Hero ROI Card
    add_card(s11, Inches(0.8), Inches(3.8), Inches(11.733), Inches(2.4), bg_color=CARD_BG, border_color=CARD_BORDER)
    tb = s11.shapes.add_textbox(Inches(1.1), Inches(4.0), Inches(11.1), Inches(2.0))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "📈 Executive Return on Investment: 104,380.0%"
    p.font.bold = True
    p.font.size = Pt(17)
    p.font.color.rgb = ACCENT_GREEN
    
    p_d = tf.add_paragraph()
    p_d.text = (
        "\n• Net Dollars Saved: $1,565,700.22 on 12,000 test transactions alone.\n"
        "• Cost-Benefit Formulation: (Fraud Prevented - Review Overhead) / Review Overhead * 100%.\n"
        "• Efficiency Ratio: $1,044 in fraud losses prevented for every $1 spent on alert verification."
    )
    p_d.font.size = Pt(12)
    p_d.font.color.rgb = TEXT_MUTED

    add_bottom_bar(s11, "Machine learning delivers quantifiable bottom-line financial savings to executive stakeholders.", "Business Justification:")

    # =========================================================================
    # SLIDE 12: Deployment & Live Web App
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    set_slide_background(s12, BG_LIGHT)
    add_header(s12, "DEPLOYMENT", "Production Streamlit Web Application Interface")
    
    # Left Card: Live Interface Capabilities
    add_card(s12, Inches(0.8), Inches(2.0), Inches(5.7), Inches(4.2))
    tb = s12.shapes.add_textbox(Inches(1.1), Inches(2.3), Inches(5.1), Inches(3.7))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "🖥️ Live Interface Capabilities"
    p.font.bold = True
    p.font.size = Pt(16)
    p.font.color.rgb = TEXT_MAIN
    
    caps = [
        ("✔ Live Scoring Terminal:", "Real-time risk gauge (0-100), preset fraud cases, and plain-language risk factor attribution."),
        ("✔ Batch CSV Scanner:", "Upload transaction feeds or test 1,000 transactions with 1 click; export flagged audit logs."),
        ("✔ Executive ROI Simulator:", "Interactive sensitivity sliders for monthly volume, average loss, and review cost."),
        ("✔ Model Performance Lab:", "Interactive ROC curves, PR plots, and confusion matrix leaderboard.")
    ]
    for h, b in caps:
        p_i = tf.add_paragraph()
        p_i.text = f"{h} {b}"
        p_i.font.size = Pt(11)
        p_i.font.color.rgb = TEXT_MUTED
        p_i.space_before = Pt(8)

    # Right Card: Dark Terminal Box (Code / Output)
    add_card(s12, Inches(6.8), Inches(2.0), Inches(5.7), Inches(4.2), bg_color=BG_DARK, border_color=None)
    tb_code = s12.shapes.add_textbox(Inches(7.1), Inches(2.3), Inches(5.1), Inches(3.7))
    tf_code = tb_code.text_frame
    tf_code.word_wrap = True
    
    p_c0 = tf_code.paragraphs[0]
    p_c0.text = "LIVE PRODUCTION ACCESS"
    p_c0.font.bold = True
    p_c0.font.size = Pt(11)
    p_c0.font.color.rgb = ACCENT_CYAN
    
    p_c1 = tf_code.add_paragraph()
    p_c1.text = "\n{\n  \"status\": \"ONLINE\",\n  \"deployed_url\": \"https://fraudlensai1.streamlit.app/\",\n  \"github_repo\": \"https://github.com/Manish-Patil33/FraudLens-Al-\",\n  \"latency_ms\": 12.4,\n  \"models\": [\n    \"RandomForestClassifier\",\n    \"IsolationForest\"\n  ]\n}"
    p_c1.font.size = Pt(11)
    p_c1.font.color.rgb = RGBColor(226, 232, 240)

    add_bottom_bar(s12, "Production deployed on Streamlit Cloud with sub-15ms real-time scoring capability.", "Deployment Status:")

    # =========================================================================
    # SLIDE 13: Conclusion & Discussion (Dark Theme)
    # =========================================================================
    s13 = prs.slides.add_slide(blank_layout)
    set_slide_background(s13, BG_DARK)
    
    tb13 = s13.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.7), Inches(2.8))
    tf13 = tb13.text_frame
    tf13.word_wrap = True
    
    p13_0 = tf13.paragraphs[0]
    p13_0.alignment = PP_ALIGN.CENTER
    p13_0.text = "CONCLUSION & DISCUSSION"
    p13_0.font.size = Pt(12)
    p13_0.font.bold = True
    p13_0.font.color.rgb = ACCENT_CYAN
    
    p13_1 = tf13.add_paragraph()
    p13_1.alignment = PP_ALIGN.CENTER
    p13_1.text = "Questions & Discussion"
    p13_1.font.size = Pt(40)
    p13_1.font.bold = True
    p13_1.font.color.rgb = TEXT_WHITE
    p13_1.space_before = Pt(10)
    
    p13_2 = tf13.add_paragraph()
    p13_2.alignment = PP_ALIGN.CENTER
    p13_2.text = "FraudLens AI serves as a complete, reproducible machine learning system for real-time transaction fraud triage and decision support."
    p13_2.font.size = Pt(15)
    p13_2.font.color.rgb = RGBColor(148, 163, 184)
    p13_2.space_before = Pt(14)

    # 2 Bottom Rounded Pill Links
    p1 = add_card(s13, Inches(2.3), Inches(5.1), Inches(4.2), Inches(0.8), bg_color=RGBColor(21, 32, 63), border_color=RGBColor(38, 52, 92))
    tb_p1 = s13.shapes.add_textbox(Inches(2.4), Inches(5.25), Inches(4.0), Inches(0.5))
    tf_p1 = tb_p1.text_frame
    p_l1 = tf_p1.paragraphs[0]
    p_l1.alignment = PP_ALIGN.CENTER
    p_l1.text = "💻 github.com/Manish-Patil33/FraudLens-Al-"
    p_l1.font.size = Pt(11)
    p_l1.font.bold = True
    p_l1.font.color.rgb = TEXT_WHITE

    p2 = add_card(s13, Inches(6.8), Inches(5.1), Inches(4.2), Inches(0.8), bg_color=RGBColor(21, 32, 63), border_color=RGBColor(38, 52, 92))
    tb_p2 = s13.shapes.add_textbox(Inches(6.9), Inches(5.25), Inches(4.0), Inches(0.5))
    tf_p2 = tb_p2.text_frame
    p_l2 = tf_p2.paragraphs[0]
    p_l2.alignment = PP_ALIGN.CENTER
    p_l2.text = "🌐 fraudlensai1.streamlit.app"
    p_l2.font.size = Pt(11)
    p_l2.font.bold = True
    p_l2.font.color.rgb = ACCENT_CYAN

    prs.save(output_path)
    print(f"13-Slide Modern Reference-Style Presentation saved to {output_path}")

if __name__ == "__main__":
    build_deck()
