import streamlit as st
import pandas as pd
import base64
import json
from datetime import date
import io

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# =========================================
# ✅ 설정: 이미지, 옵션, 스타일
# =========================================

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as img:
        return f"data:image/png;base64,{base64.b64encode(img.read()).decode()}"

sample_image = encode_image_to_base64("./data/sample.png")

with open("./config_options.json", "r", encoding="utf-8") as f:
    options = json.load(f)

region_list = options["region"]
email_list = options["email"]
phase_list = options["phase"]

st.set_page_config(layout="wide")
st.title("🧬 자가진단표")

st.markdown("""
<style>
.block-container { padding-top: 2.5rem; }
.pill-container {
    display: flex; flex-wrap: wrap; gap: 8px; margin: 1rem 0;
}
.custom-pill {
    padding: 6px 14px;
    border-radius: 999px;
    font-size: 0.9rem;
    font-weight: 500;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# =========================================
# ✅ 상단 입력 필드
# =========================================

col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 2])
with col1:
    selected_date = st.date_input("📅 날짜", value=date.today())
with col2:
    selected_region = st.selectbox("📍 지역", region_list)
with col3:
    selected_email = st.selectbox("📧 관리자 이메일", email_list)
with col4:
    selected_phase = st.selectbox("🐖 사육단계", phase_list)

# =========================================
# ✅ CSV 불러오기 및 기본 값 설정
# =========================================

symptom_df = pd.read_csv("./data/symptoms.csv")
anatomic_df = pd.read_csv("./data/anatomy.csv")
antibiotics_df = pd.read_csv("./data/antibiotics.csv")

symptom_df["사진"] = sample_image
symptom_df["체크"] = False

anatomic_df["사진"] = sample_image
anatomic_df["체크"] = False

antibiotics_df["사진"] = sample_image
antibiotics_df["Effective"] = False
antibiotics_df["Ineffective"] = False

# =========================================
# ✅ 증상 / 해부학 / 항생제 입력 테이블
# =========================================

def create_data_editor(df, columns, label):
    return st.data_editor(
        df,
        column_config=columns,
        use_container_width=True,
        hide_index=True,
        key=label
    )

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("🔍 관측 증상")
    edited_symptoms = create_data_editor(symptom_df, {
        "사진": st.column_config.ImageColumn("사진", width="60px"),
        "체크": st.column_config.CheckboxColumn("체크", width="70px")
    }, "symptoms")

with col2:
    st.subheader("🪝 해부학 소견")
    edited_anatomy = create_data_editor(anatomic_df, {
        "사진": st.column_config.ImageColumn("사진", width="60px"),
        "체크": st.column_config.CheckboxColumn("체크", width="70px")
    }, "anatomy")

with col3:
    st.subheader("💊 항생제 효과")
    edited_antibiotics = create_data_editor(antibiotics_df, {
        "사진": st.column_config.ImageColumn("사진", width="60px"),
        "Effective": st.column_config.CheckboxColumn("효과 있음", width="70px"),
        "Ineffective": st.column_config.CheckboxColumn("효과 없음", width="70px")
    }, "antibiotics")

# =========================================
# ✅ 선택 결과 렌더링 (Pill)
# =========================================

def render_pills(labels, color):
    if labels:
        pill_html = '<div class="pill-container">'
        for label in labels:
            pill_html += f'<span class="custom-pill" style="background-color: {color};">{label}</span>'
        pill_html += '</div>'
        st.markdown(pill_html, unsafe_allow_html=True)

symptom_labels = [f"{row['구분']}/{row['증상']}" for _, row in edited_symptoms.iterrows() if row["체크"]]
anatomy_labels = [f"{row['구분']}/{row['소견']}" for _, row in edited_anatomy.iterrows() if row["체크"]]
effective_labels = [f"{row['Class']}/{row['항목']}" for _, row in edited_antibiotics.iterrows() if row["Effective"]]
ineffective_labels = [f"{row['Class']}/{row['항목']}" for _, row in edited_antibiotics.iterrows() if row["Ineffective"]]

r1, r2, r3 = st.columns(3)
with r1:
    render_pills(symptom_labels, "#007BFF")
with r2:
    render_pills(anatomy_labels, "#DC3545")
with r3:
    render_pills(effective_labels, "#28a745")
    render_pills(ineffective_labels, "#ffc107")

if not (symptom_labels or anatomy_labels or effective_labels or ineffective_labels):
    st.info("하나 이상의 항목을 선택해주세요.")

# =========================================
# ✅ PDF 저장 (표 & 한글 폰트 적용)
# =========================================

pdfmetrics.registerFont(TTFont("FONT", "./fonts/CJONLYONENEWbodyRegular.ttf"))

def korean_paragraph(text, style):
    return Paragraph(str(text), style)

def generate_pdf_korean(date, region, email, phase,
                        edited_symptoms, edited_anatomy, edited_antibiotics):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)

    base_style = getSampleStyleSheet()
    custom_style = ParagraphStyle("FONT", parent=base_style["Normal"], fontName="FONT", fontSize=11)
    heading_style = ParagraphStyle("FONT-Heading", parent=base_style["Heading4"], fontName="FONT")
    title_style = ParagraphStyle(
    "FONT-Title",
    parent=base_style["Heading1"],
    fontName="FONT",
    fontSize=18,  # 원하는 크기로 조절 가능
    leading=22,
    spaceAfter=12,
)

    elements = [
        Paragraph("▣ 자가진단 상단 입력 정보", title_style),
        Paragraph(f"- 날짜: {date}", custom_style),
        Paragraph(f"- 지역: {region}", custom_style),
        Paragraph(f"- 관리자 이메일: {email}", custom_style),
        Paragraph(f"- 사육단계: {phase}", custom_style),
        Spacer(1, 12),
    ]

    # 🔍 관측 증상
    elements.append(Paragraph("- 관측 증상", heading_style))
    data = [[korean_paragraph("구분", custom_style), korean_paragraph("증상", custom_style)]]
    for _, row in edited_symptoms.iterrows():
        if row["체크"]:
            data.append([korean_paragraph(row["구분"], custom_style),
                         korean_paragraph(row["증상"], custom_style)])
    if len(data) == 1:
        data.append([korean_paragraph("-", custom_style),
                     korean_paragraph("선택된 항목 없음", custom_style)])
    table = Table(data)
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
                               ("GRID", (0, 0), (-1, -1), 0.5, colors.grey)]))
    elements.extend([table, Spacer(1, 12)])

    # 🪝 해부학 소견
    elements.append(Paragraph("- 해부학 소견", heading_style))
    data = [[korean_paragraph("구분", custom_style), korean_paragraph("소견", custom_style)]]
    for _, row in edited_anatomy.iterrows():
        if row["체크"]:
            data.append([korean_paragraph(row["구분"], custom_style),
                         korean_paragraph(row["소견"], custom_style)])
    if len(data) == 1:
        data.append([korean_paragraph("-", custom_style),
                     korean_paragraph("선택된 항목 없음", custom_style)])
    table = Table(data)
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.pink),
                               ("GRID", (0, 0), (-1, -1), 0.5, colors.grey)]))
    elements.extend([table, Spacer(1, 12)])

    # 💊 항생제 효과
    elements.append(Paragraph("- 항생제 효과", heading_style))
    data = [[korean_paragraph("Class", custom_style),
             korean_paragraph("항목", custom_style),
             korean_paragraph("효과", custom_style)]]
    for _, row in edited_antibiotics.iterrows():
        if row["Effective"]:
            data.append([korean_paragraph(row["Class"], custom_style),
                         korean_paragraph(row["항목"], custom_style),
                         korean_paragraph("효과 있음", custom_style)])
        elif row["Ineffective"]:
            data.append([korean_paragraph(row["Class"], custom_style),
                         korean_paragraph(row["항목"], custom_style),
                         korean_paragraph("효과 없음", custom_style)])
    if len(data) == 1:
        data.append([korean_paragraph("-", custom_style),
                     korean_paragraph("-", custom_style),
                     korean_paragraph("선택된 항목 없음", custom_style)])
    table = Table(data)
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.lightgreen),
                               ("GRID", (0, 0), (-1, -1), 0.5, colors.grey)]))
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)
    return buffer

# ✅ 다운로드 버튼 (col5)
with col5:
    today_date = date.today().strftime("%y%m%d")
    pdf_data = generate_pdf_korean(
        selected_date, selected_region, selected_email, selected_phase,
        edited_symptoms, edited_anatomy, edited_antibiotics
    )
    st.download_button(
        label="📥 PDF 다운로드",
        data=pdf_data,
        file_name=f"자가진단_입력정보_{today_date}.pdf",
        mime="application/pdf"
    )
