import plotly.express as px
import plotly.graph_objects as go
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

# ===== RANKING (Đã chuyển sang Plotly chuẩn) =====
st.subheader("🏆 Xếp hạng lớp")
avg_class = filtered_df.groupby("Lớp")["Điểm_tổng_hợp"].mean().reset_index()
avg_class = avg_class.sort_values(by="Điểm_tổng_hợp", ascending=False)

fig_rank = px.bar(
    avg_class, 
    x="Lớp", 
    y="Điểm_tổng_hợp",
    color="Lớp",
    color_discrete_map=color_map,
    text_auto='.2f', 
    title="Xếp hạng Điểm trung bình theo lớp"
)
fig_rank.update_traces(marker_line_color='black', marker_line_width=1.2)
st.plotly_chart(fig_rank, use_container_width=True)

# ===== HISTOGRAM (Đã chuyển sang Plotly chuẩn) =====
st.subheader("📈 Phân bố điểm")

fig_hist = px.histogram(
    filtered_df, 
    x="Điểm_tổng_hợp", 
    color="Lớp",
    color_discrete_map=color_map,
    nbins=20,
    barmode="overlay",
    opacity=0.7,
    title="Phân bố điểm tổng hợp theo lớp"
)
fig_hist.update_traces(marker_line_color='black', marker_line_width=1)
st.plotly_chart(fig_hist, use_container_width=True)


# ===== BOXPLOT (Đã chuyển sang Plotly chuẩn) =====
st.subheader("📦 Boxplot")

fig_box = px.box(
    filtered_df, 
    x="Lớp", 
    y="Điểm_tổng_hợp", 
    color="Lớp",
    color_discrete_map=color_map,
    points=False, # <--- Tắt hoàn toàn các chấm tròn
    title="Biểu đồ Boxplot: Khoảng phân tán điểm"
)
fig_box.update_traces(marker_line_color='black', marker_line_width=1)
st.plotly_chart(fig_box, use_container_width=True)


# ===== SCATTER (Giữ nguyên Matplotlib/Seaborn vì vẽ đường hồi quy rất tốt) =====
st.subheader("🔍 Tương quan")

# 1. Tạo từ điển ánh xạ tên hiển thị đẹp sang tên cột trong dataframe
corr_options = {
    "Điểm thi cuối kì": "Thi_cuối_kì",
    "Điểm kiểm tra GK (20%)": "Kiểm_tra_GK",
    "Điểm Thảo luận, BTN, TT (20%)": "Thảo_luận_BTN_TT",
    "Điểm chuyên cần (10%)": "Chuyên_cần" # Mình bonus thêm luôn cột chuyên cần cho đầy đủ nhé
}

# 2. Tạo Selectbox để chọn thành phần điểm làm trục X
selected_corr_name = st.selectbox(
    "Chọn thành phần điểm để phân tích tương quan:",
    options=list(corr_options.keys())
)

# Lấy tên cột tương ứng với lựa chọn
x_col = corr_options[selected_corr_name]

# 3. Vẽ biểu đồ động theo trục X đã chọn
fig3, ax3 = plt.subplots()

# Chỉ lọc bỏ các hàng bị thiếu (NaN) ở cột được chọn và cột Tổng hợp
scatter_df = filtered_df.dropna(subset=[x_col, "Điểm_tổng_hợp"])

sns.scatterplot(
    data=scatter_df,
    x=x_col,
    y="Điểm_tổng_hợp",
    hue="Lớp",
    palette=color_map,
    alpha=0.6,
    edgecolor="black",
    ax=ax3
)
sns.regplot(
    data=scatter_df, 
    x=x_col, 
    y="Điểm_tổng_hợp", 
    scatter=False, 
    color="black", 
    ax=ax3
)

# Cập nhật tiêu đề và tên trục tự động theo tên lựa chọn
ax3.set_title(f"Tương quan giữa {selected_corr_name} và Điểm tổng hợp", fontsize=14, fontweight='bold', pad=15)
ax3.set_xlabel(selected_corr_name, fontweight='bold')
ax3.set_ylabel("Điểm tổng hợp", fontweight='bold')
ax3.legend(title="Lớp", frameon=True, edgecolor='black')
ax3.grid(True, linestyle='--', alpha=0.5)
for spine in ax3.spines.values():
    spine.set_edgecolor('black')
    spine.set_linewidth(1)

st.pyplot(fig3)

# ===== HEATMAP (Giữ nguyên Matplotlib/Seaborn) =====
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
sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", ax=ax4, linewidths=0.5, linecolor='black') 

ax4.set_title("Ma trận tương quan giữa các thành phần điểm", fontsize=14, fontweight='bold', pad=15)
plt.xticks(rotation=45, ha='right') 

st.pyplot(fig4)

# ===== PHÂN LOẠI (Đã dọn dẹp lỗi và chuyển sang Plotly chuẩn) =====
st.subheader("📊 Phân loại sinh viên")

crosstab_df = pd.crosstab(filtered_df["Lớp"], filtered_df["Xếp loại"]).reset_index()
order = ["Lớp", "Xuất sắc", "Giỏi", "Khá", "Trung bình", "Yếu"]
crosstab_df = crosstab_df[[col for col in order if col in crosstab_df.columns]]

melted_df = crosstab_df.melt(id_vars="Lớp", var_name="Xếp loại", value_name="Số lượng")

fig_class = px.bar(
    melted_df, 
    x="Lớp", 
    y="Số lượng", 
    color="Xếp loại",
    barmode="group", 
    text_auto=True,
    title="Thống kê Xếp loại sinh viên theo lớp",
    color_discrete_sequence=px.colors.qualitative.Set2 
)
fig_class.update_traces(marker_line_color='black', marker_line_width=1)
st.plotly_chart(fig_class, use_container_width=True)

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
