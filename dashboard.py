import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

st.set_page_config(layout="wide")

# ===== LOAD DATA =====
@st.cache_data
def load_data():
    df_D05 = pd.read_csv(r"C:\Users\MSI\Downloads\Big Data\AMA301_2511_1_D05.csv", encoding="utf-8-sig")
    df_D12 = pd.read_csv(r"C:\Users\MSI\Downloads\Big Data\AMA301_2511_1_D12.csv", encoding="utf-8-sig")
    df_D13 = pd.read_csv(r"C:\Users\MSI\Downloads\Big Data\AMA301_2511_1_D13.csv", encoding="utf-8-sig")
    df_D14 = pd.read_csv(r"C:\Users\MSI\Downloads\Big Data\AMA301_2511_1_D14.csv", encoding="utf-8-sig")

    df_D05["Lớp"] = "D05"
    df_D12["Lớp"] = "D12"
    df_D13["Lớp"] = "D13"
    df_D14["Lớp"] = "D14"

    df = pd.concat([df_D05, df_D12, df_D13, df_D14])
    df = df.dropna(subset=["Thi_cuối_kì", "Điểm_tổng_hợp"])

    return df

df = load_data()

# ===== PHÂN LOẠI =====
def classify(score):
    if score >= 8.5:
        return "Giỏi"
    elif score >= 7:
        return "Khá"
    elif score >= 5:
        return "Trung bình"
    else:
        return "Yếu"

df["Xếp loại"] = df["Điểm_tổng_hợp"].apply(classify)

# ===== SIDEBAR =====
st.sidebar.header(" Bộ lọc")

selected_class = st.sidebar.multiselect(
    "Chọn lớp",
    df["Lớp"].unique(),
    default=df["Lớp"].unique()
)

min_score, max_score = st.sidebar.slider(
    "Khoảng điểm",
    0.0, 10.0, (0.0, 10.0)
)

filtered_df = df[
    (df["Lớp"].isin(selected_class)) &
    (df["Điểm_tổng_hợp"] >= min_score) &
    (df["Điểm_tổng_hợp"] <= max_score)
]

# ===== TITLE =====
st.title("📊 PHÂN TÍCH ĐIỂM SINH VIÊN (D05, D12, D13, D14)")

# ===== KPI =====
st.subheader("📌 Tổng quan")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Điểm TB", round(filtered_df["Điểm_tổng_hợp"].mean(), 2))
col2.metric("Cao nhất", filtered_df["Điểm_tổng_hợp"].max())
col3.metric("Thấp nhất", filtered_df["Điểm_tổng_hợp"].min())
col4.metric("Số SV", len(filtered_df))

# ===== RANKING LỚP =====
st.subheader("🏆 Xếp hạng lớp theo điểm trung bình")

avg_class = filtered_df.groupby("Lớp")["Điểm_tổng_hợp"].mean().sort_values(ascending=False)

st.dataframe(avg_class)

st.bar_chart(avg_class)

# ===== HISTOGRAM =====
st.subheader(" Phân bố điểm")

fig, ax = plt.subplots()

for lop in selected_class:
    subset = filtered_df[filtered_df["Lớp"] == lop]
    ax.hist(subset["Điểm_tổng_hợp"], bins=10, alpha=0.5, label=lop)

ax.legend()
ax.set_xlabel("Điểm")
ax.set_ylabel("Số SV")
ax.yaxis.set_major_locator(MaxNLocator(integer=True))

st.pyplot(fig)

# ===== BOXPLOT =====
st.subheader(" So sánh phân bố điểm")

fig2, ax2 = plt.subplots()

data = [filtered_df[filtered_df["Lớp"] == lop]["Điểm_tổng_hợp"] for lop in selected_class]

ax2.boxplot(data, labels=selected_class)

st.pyplot(fig2)

# ===== SCATTER =====
import seaborn as sns

st.subheader(" Mối quan hệ giữa điểm Final và điểm Tổng")

fig, ax = plt.subplots()

# scatter + màu theo lớp
sns.scatterplot(
    data=filtered_df,
    x="Thi_cuối_kì",
    y="Điểm_tổng_hợp",
    hue="Lớp",
    alpha=0.6,
    edgecolor="black",
    ax=ax
)

# regression line (toàn bộ dữ liệu)
sns.regplot(
    data=filtered_df,
    x="Thi_cuối_kì",
    y="Điểm_tổng_hợp",
    scatter=False,
    color="black",
    ax=ax
)

# grid nhẹ
ax.grid(True, linestyle='--', alpha=0.3)

ax.set_xlabel("Điểm Final")
ax.set_ylabel("Điểm Tổng")

st.pyplot(fig)
#Biểu đồ Heatmap tương quan
import seaborn as sns

st.subheader(" Ma trận tương quan giữa các loại điểm")

# chọn các cột cần phân tích
corr = filtered_df[[
    "Chuyên_cần",
    "Kiểm_tra_GK",
    "Thảo_luận_BTN_TT",
    "Thi_cuối_kì",
    "Điểm_tổng_hợp"
]].corr()

# style đẹp
sns.set(style="white")

fig, ax = plt.subplots()

sns.heatmap(
    corr,
    annot=True,          # hiện số
    fmt=".2f",           # format 2 số thập phân
    cmap="coolwarm",     # màu giống hình bạn gửi
    linewidths=0.5,      # viền ô
    cbar=True,           # thanh màu
    ax=ax
)

ax.set_title("Ma trận tương quan giữa các loại điểm")

st.pyplot(fig)
# ===== PHÂN LOẠI =====
st.subheader("📊 Phân loại sinh viên")

st.bar_chart(pd.crosstab(filtered_df["Lớp"], filtered_df["Xếp loại"]))

# ===== TOP =====
st.subheader("🏆 Top sinh viên")

col1, col2 = st.columns(2)

with col1:
    st.write("### 🥇 Top 5 cao nhất")
    st.dataframe(filtered_df.sort_values(by="Điểm_tổng_hợp", ascending=False).head(5))

with col2:
    st.write("### ⚠️ Top 5 thấp nhất")
    st.dataframe(filtered_df.sort_values(by="Điểm_tổng_hợp", ascending=True).head(5))

# ===== BẢNG CHI TIẾT =====
st.subheader("📋 Danh sách sinh viên")

selected_type = st.selectbox(
    "Chọn xếp loại",
    ["Tất cả", "Giỏi", "Khá", "Trung bình", "Yếu"]
)

if selected_type == "Tất cả":
    display_df = filtered_df
else:
    display_df = filtered_df[filtered_df["Xếp loại"] == selected_type]

st.dataframe(display_df)

# ===== INSIGHT =====
st.subheader(" Nhận xét tổng hợp")

for lop in selected_class:
    subset = filtered_df[filtered_df["Lớp"] == lop]

    if len(subset) == 0:
        continue

    mean = subset["Điểm_tổng_hợp"].mean()
    std = subset["Điểm_tổng_hợp"].std()
    skew = subset["Điểm_tổng_hợp"].skew()

    st.write(f"###  Lớp {lop}")

    if mean > 8:
        st.write(" Đề dễ")
    elif mean > 6.5:
        st.write(" Đề trung bình")
    else:
        st.write(" Đề khó")

    if skew < 0:
        st.write(" Lệch trái")
    else:
        st.write(" Lệch phải")

    if std < 1:
        st.write(" Phân loại kém")

    gioi_ratio = len(subset[subset["Xếp loại"] == "Giỏi"]) / len(subset)

    if gioi_ratio > 0.5:
        st.write(" Tỷ lệ giỏi cao → đề dễ")

    weak = len(subset[subset["Điểm_tổng_hợp"] < 5])

    if weak > 0:
        st.write(f" Có {weak} SV yếu")

# ===== FOOTER =====
st.markdown("---")
st.markdown("📌 Dashboard phục vụ phân tích và đánh giá chất lượng đề thi & sinh viên")
#Xuất PDF
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def create_pdf():
    pdfmetrics.registerFont(TTFont('DejaVu', 'DejaVuSans.ttf'))

    doc = SimpleDocTemplate("report.pdf")
    styles = getSampleStyleSheet()

    styles["Normal"].fontName = "DejaVu"
    styles["Title"].fontName = "DejaVu"

    content = []

    # ===== TITLE =====
    content.append(Paragraph("BÁO CÁO PHÂN TÍCH ĐIỂM SINH VIÊN", styles["Title"]))
    content.append(Spacer(1, 20))

    # ===== THỐNG KÊ =====
    mean = round(filtered_df["Điểm_tổng_hợp"].mean(), 2)
    max_score = filtered_df["Điểm_tổng_hợp"].max()
    min_score = filtered_df["Điểm_tổng_hợp"].min()

    content.append(Paragraph(f"Điểm trung bình: {mean}", styles["Normal"]))
    content.append(Paragraph(f"Điểm cao nhất: {max_score}", styles["Normal"]))
    content.append(Paragraph(f"Điểm thấp nhất: {min_score}", styles["Normal"]))
    content.append(Paragraph(f"Số sinh viên: {len(filtered_df)}", styles["Normal"]))

    content.append(Spacer(1, 20))

    # ===== INSIGHT =====
    content.append(Paragraph("NHẬN XÉT:", styles["Normal"]))
    content.append(Spacer(1, 10))

    if mean > 8:
        content.append(Paragraph("- Đề thi có xu hướng dễ", styles["Normal"]))
    elif mean > 6.5:
        content.append(Paragraph("- Đề thi ở mức trung bình", styles["Normal"]))
    else:
        content.append(Paragraph("- Đề thi khó", styles["Normal"]))

    if filtered_df["Điểm_tổng_hợp"].skew() < 0:
        content.append(Paragraph("- Phân phối lệch trái (nhiều điểm cao)", styles["Normal"]))
    else:
        content.append(Paragraph("- Phân phối lệch phải", styles["Normal"]))

    if filtered_df["Điểm_tổng_hợp"].std() < 1:
        content.append(Paragraph("- Khả năng phân loại chưa tốt", styles["Normal"]))

    content.append(Spacer(1, 20))

    # ===== TOP SINH VIÊN =====
    top = filtered_df.sort_values(by="Điểm_tổng_hợp", ascending=False).head(3)

    content.append(Paragraph("TOP SINH VIÊN:", styles["Normal"]))
    content.append(Spacer(1, 10))

    for _, row in top.iterrows():
        content.append(Paragraph(
            f"- {row['Họ']} {row['Tên']} ({row['Lớp']}): {row['Điểm_tổng_hợp']}",
            styles["Normal"]
        ))

    doc.build(content)
import os

st.subheader("📤 Xuất báo cáo PDF")

if st.button("📄 Tạo PDF"):
    create_pdf()
    st.success("Đã tạo PDF!")

    # mở file vừa tạo
    with open("report.pdf", "rb") as file:
        st.download_button(
            label="⬇️ Tải file PDF",
            data=file,
            file_name="report.pdf",
            mime="application/pdf"
        )