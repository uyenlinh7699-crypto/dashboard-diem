import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import MaxNLocator
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
color_map = {
    "D05": "#F5793A",
    "D12": "#A95AA1",
    "D13": "#85C0F9",
    "D14": "#0F2080"
} 

st.set_page_config(layout="wide")

# ===== LOAD DATA =====
@st.cache_data
def load_data():
    df_D05 = pd.read_csv("AMA301_2511_1_D05.csv")
    df_D12 = pd.read_csv("AMA301_2511_1_D12.csv")
    df_D13 = pd.read_csv("AMA301_2511_1_D13.csv")
    df_D14 = pd.read_csv("AMA301_2511_1_D14.csv")

    df_D05["Lớp"] = "D05"
    df_D12["Lớp"] = "D12"
    df_D13["Lớp"] = "D13"
    df_D14["Lớp"] = "D14"
    
    df_raw = pd.concat(
        [df_D05, df_D12, df_D13, df_D14],
        ignore_index=True
    )

    df = df_raw.copy()   

    return df_raw, df

df_raw, df = load_data()

# ===== CHUYỂN HỆ 10 → HỆ 4 =====
def convert_to_4(score):
    if score >= 9.5: return 4.0
    elif score >= 9.0: return 3.7
    elif score >= 8.5: return 3.4
    elif score >= 8.0: return 3.2
    elif score >= 7.5: return 3.0
    elif score >= 7.0: return 2.8
    elif score >= 6.5: return 2.6
    elif score >= 6.0: return 2.4
    elif score >= 5.5: return 2.2
    elif score >= 5.0: return 2.0
    elif score >= 4.5: return 1.8
    elif score >= 4.0: return 1.6
    else: return 0

df["Điểm_4"] = df["Điểm_tổng_hợp"].apply(convert_to_4)

# ===== PHÂN LOẠI BUH =====
def classify(score):
    if score >= 3.6:
        return "Xuất sắc"
    elif score >= 3.2:
        return "Giỏi"
    elif score >= 2.5:
        return "Khá"
    elif score >= 2.0:
        return "Trung bình"
    else:
        return "Yếu"

df["Xếp loại"] = df["Điểm_4"].apply(classify)

# ===== SIDEBAR =====
st.sidebar.header("🎛️ Bộ lọc")

selected_class = st.sidebar.multiselect(
    "Chọn lớp",
    df["Lớp"].unique(),
    default=df["Lớp"].unique()
)

min_score, max_score = st.sidebar.slider(
    "Khoảng điểm",
    0.0, 10.0, (0.0, 10.0)
)
selected_type_sidebar = st.sidebar.selectbox(
    "Chọn xếp loại",
    ["Tất cả", "Xuất sắc", "Giỏi", "Khá", "Trung bình", "Yếu"]
) 
filtered_df = df[
    (df["Lớp"].isin(selected_class)) &
    (df["Điểm_tổng_hợp"] >= min_score) &
    (df["Điểm_tổng_hợp"] <= max_score)
]
if selected_type_sidebar != "Tất cả":
    filtered_df = filtered_df[filtered_df["Xếp loại"] == selected_type_sidebar]
# ===== TITLE =====
st.title("📊 PHÂN TÍCH ĐIỂM SINH VIÊN (D05, D12, D13, D14)")

# ===== KPI =====
st.subheader("📌 Tổng quan")
col1, col2, col3, col4 = st.columns(4)
mean10 = filtered_df["Điểm_tổng_hợp"].mean()
mean4 = filtered_df["Điểm_4"].mean()
col1.metric("Điểm TB (hệ 10)", round(mean10, 1) if not pd.isna(mean10) else 0)
col2.metric("Điểm TB (hệ 4)", round(mean4, 1) if not pd.isna(mean4) else 0)
max_score = filtered_df["Điểm_tổng_hợp"].max()
col3.metric("Cao nhất", max_score if not pd.isna(max_score) else 0)
col4.metric("Tổng SV", filtered_df.shape[0])

# ===== RANKING =====
st.subheader("🏆 Xếp hạng lớp")

avg_class = filtered_df.groupby("Lớp")["Điểm_tổng_hợp"].mean().sort_values(ascending=False)
st.bar_chart(avg_class)

# ===== HISTOGRAM =====
st.subheader("📈 Phân bố điểm")

fig, ax = plt.subplots()
for lop in selected_class:
    subset = filtered_df[filtered_df["Lớp"] == lop]
    if len(subset) > 0:
        ax.hist(
            subset["Điểm_tổng_hợp"],
            bins=10,
            alpha=0.6,
            label=lop,
            color=color_map.get(lop)
        )
ax.legend(title="Lớp", frameon=True, edgecolor='black')
ax.yaxis.set_major_locator(MaxNLocator(integer=True))

# --- Phần Thêm mới để làm đẹp ---
ax.set_title("Phân bố điểm tổng hợp theo lớp", fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel("Điểm tổng hợp", fontweight='bold')
ax.set_ylabel("Số lượng sinh viên", fontweight='bold')
ax.grid(True, linestyle='--', alpha=0.5) # Thêm lưới dễ nhìn
for spine in ax.spines.values(): # Thêm đường viền đen xung quanh
    spine.set_edgecolor('black')
    spine.set_linewidth(1)
# ---------------------------------

st.pyplot(fig)

# ===== BOXPLOT =====
st.subheader("📦 Boxplot")

fig2, ax2 = plt.subplots()
valid_classes = [lop for lop in selected_class if len(filtered_df[filtered_df["Lớp"] == lop]) > 0]
data = [filtered_df[filtered_df["Lớp"] == lop]["Điểm_tổng_hợp"] for lop in valid_classes]
box = ax2.boxplot(
    data,
    labels=valid_classes,
    patch_artist=True,
    medianprops=dict(color='black', linewidth=2),
    boxprops=dict(linewidth=1.5),
    whiskerprops=dict(linewidth=1.5),
    capprops=dict(linewidth=1.5)
)
for patch, lop in zip(box['boxes'], selected_class):
    patch.set_facecolor(color_map.get(lop))

# --- Phần Thêm mới để làm đẹp ---
ax2.set_title("Biểu đồ Boxplot: Khoảng phân tán điểm", fontsize=14, fontweight='bold', pad=15)
ax2.set_xlabel("Lớp học", fontweight='bold')
ax2.set_ylabel("Điểm tổng hợp", fontweight='bold')
ax2.grid(True, linestyle='--', alpha=0.5, axis='y') # Chỉ bật lưới ngang cho Boxplot
for spine in ax2.spines.values():
    spine.set_edgecolor('black')
    spine.set_linewidth(1)
# ---------------------------------

st.pyplot(fig2)

# ===== SCATTER =====
st.subheader("🔍 Tương quan")

fig3, ax3 = plt.subplots()
scatter_df = filtered_df.dropna(subset=["Thi_cuối_kì", "Điểm_tổng_hợp"])
sns.scatterplot(
    data=scatter_df,
    x="Thi_cuối_kì",
    y="Điểm_tổng_hợp",
    hue="Lớp",
    palette=color_map,
    alpha=0.6,
    edgecolor="black",
    ax=ax3
)
sns.regplot(
    data=scatter_df, x="Thi_cuối_kì", y="Điểm_tổng_hợp", scatter=False, color="black", ax=ax3)

# --- Phần Thêm mới để làm đẹp ---
ax3.set_title("Tương quan giữa Điểm thi cuối kì và Điểm tổng hợp", fontsize=14, fontweight='bold', pad=15)
ax3.set_xlabel("Điểm thi cuối kì", fontweight='bold')
ax3.set_ylabel("Điểm tổng hợp", fontweight='bold')
ax3.legend(title="Lớp", frameon=True, edgecolor='black')
ax3.grid(True, linestyle='--', alpha=0.5)
for spine in ax3.spines.values():
    spine.set_edgecolor('black')
    spine.set_linewidth(1)
# ---------------------------------

st.pyplot(fig3)
# ===== HEATMAP =====
st.subheader("📊 Heatmap")

corr_df = filtered_df[[
    "Chuyên_cần",
    "Kiểm_tra_GK",
    "Thảo_luận_BTN_TT",
    "Thi_cuối_kì",
    "Điểm_tổng_hợp"
]].dropna()

corr = corr_df.corr()

fig4, ax4 = plt.subplots()
sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", ax=ax4, linewidths=0.5, linecolor='black') # Thêm viền cho các ô

# --- Phần Thêm mới để làm đẹp ---
ax4.set_title("Ma trận tương quan giữa các thành phần điểm", fontsize=14, fontweight='bold', pad=15)
plt.xticks(rotation=45, ha='right') # Xoay nhãn trục X để không bị đè lên nhau
# ---------------------------------

st.pyplot(fig4)

# ===== PHÂN LOẠI =====
st.subheader("📊 Phân loại")

fig5, ax5 = plt.subplots(figsize=(8, 5))
crosstab_df = pd.crosstab(filtered_df["Lớp"], filtered_df["Xếp loại"]).fillna(0)

# Sắp xếp lại thứ tự xếp loại cho logic từ cao xuống thấp (nếu cần)
order = ["Xuất sắc", "Giỏi", "Khá", "Trung bình", "Yếu"]
crosstab_df = crosstab_df.reindex(columns=[x for x in order if x in crosstab_df.columns])

crosstab_df.plot(kind='bar', ax=ax5, colormap='viridis', edgecolor='black') # Vẽ bar chart với màu đẹp và viền đen

# --- Phần Thêm mới để làm đẹp ---
ax5.set_title("Thống kê Xếp loại sinh viên theo lớp", fontsize=14, fontweight='bold', pad=15)
ax5.set_xlabel("Lớp học", fontweight='bold')
ax5.set_ylabel("Số lượng sinh viên", fontweight='bold')
ax5.legend(title="Xếp loại", frameon=True, edgecolor='black')
ax5.grid(True, linestyle='--', alpha=0.5, axis='y')
plt.xticks(rotation=0) # Để tên lớp nằm ngang cho dễ đọc
for spine in ax5.spines.values():
    spine.set_edgecolor('black')
    spine.set_linewidth(1)
# ---------------------------------

st.pyplot(fig5)

# ===== TOP =====
st.subheader("🏆 Top sinh viên")

col1, col2 = st.columns(2)

with col1:
    st.write("Top 5 cao nhất")
    st.dataframe(filtered_df.sort_values(by="Điểm_tổng_hợp", ascending=False).head(5))

with col2:
    st.write("Top 5 thấp nhất")
    st.dataframe(filtered_df.sort_values(by="Điểm_tổng_hợp", ascending=True).head(5))

# ===== BẢNG CHI TIẾT =====
st.subheader("📋 Danh sách sinh viên")

selected_type = st.selectbox(
    "Chọn xếp loại",
    ["Tất cả", "Xuất sắc", "Giỏi", "Khá", "Trung bình", "Yếu"],
    key="filter_main"
)

if selected_type == "Tất cả":
    display_df = filtered_df
else:
    display_df = filtered_df[filtered_df["Xếp loại"] == selected_type]

st.dataframe(display_df)

# ===== PDF =====
st.subheader("📤 Xuất PDF")

def create_pdf():
    pdfmetrics.registerFont(TTFont('DejaVu', 'DejaVuSans.ttf'))
    doc = SimpleDocTemplate("report.pdf")
    styles = getSampleStyleSheet()

    styles["Normal"].fontName = "DejaVu"
    styles["Title"].fontName = "DejaVu"

    content = []
    content.append(Paragraph("BÁO CÁO PHÂN TÍCH ĐIỂM", styles["Title"]))
    content.append(Spacer(1, 20))

    mean = round(filtered_df["Điểm_tổng_hợp"].mean(), 2)
    content.append(Paragraph(f"Điểm trung bình: {mean}", styles["Normal"]))
    content.append(Paragraph(f"Tổng sinh viên: {df_raw.shape[0]}", styles["Normal"]))

    doc.build(content)

if st.button("Tạo PDF"):
    create_pdf()
    st.success("Đã tạo PDF")
