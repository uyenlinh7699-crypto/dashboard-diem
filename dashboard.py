import plotly.express as px
import io
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

st.set_page_config(
    page_title="Edu-Analytics | Phân tích chất lượng môn Toán cao cấp 1", 
    page_icon="🎓", 
    layout="wide",
    initial_sidebar_state="expanded" 
)

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
# 1. Thêm Tiêu đề/Logo thương hiệu nổi bật
st.sidebar.markdown("<h2 style='text-align: center; color: #F5793A;'>🎓 Group 5</h2>", unsafe_allow_html=True)
st.sidebar.markdown("---") # Đường gạch ngang phân cách

# 2. Khu vực bộ lọc chính
st.sidebar.header("🎛️ Bộ lọc dữ liệu")

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

# 3. Thêm thông báo hướng dẫn UX ở cuối
st.sidebar.markdown("---")
st.sidebar.info("💡 **Mẹo:** Dùng bộ lọc để thu hẹp phạm vi phân tích. Các biểu đồ bên phải sẽ tự động cập nhật theo lựa chọn của bạn.")

filtered_df = df[
    (df["Lớp"].isin(selected_class)) &
    (df["Điểm_tổng_hợp"] >= min_score) &
    (df["Điểm_tổng_hợp"] <= max_score)
]
if selected_type_sidebar != "Tất cả":
    filtered_df = filtered_df[filtered_df["Xếp loại"] == selected_type_sidebar]

# ---> THÊM ĐOẠN CODE NÀY VÀO <---
if filtered_df.empty:
    st.warning("⚠️ Không tìm thấy sinh viên nào thỏa mãn điều kiện lọc. Vui lòng điều chỉnh lại Lớp, Khoảng điểm hoặc Xếp loại ở Sidebar.")
    st.stop() # Lệnh này sẽ dừng vẽ các biểu đồ bên dưới để tránh lỗi
# ---------------------------------
# ===== TITLE =====
st.title("📊PHÂN TÍCH CHẤT LƯỢNG MÔN TOÁN CAO CẤP 1 (D05, D12, D13, D14)")
# ===== THÔNG TIN HỌC PHẦN =====
# 1. Khai báo từ điển lưu trữ thông tin thi của từng lớp
course_info = {
    "D05": {"Mã học phần": "AMA301_2511_1_D05", "Ngày, giờ thi": "24/01/2026, 13h00"},
    "D12": {"Mã học phần": "AMA301_2511_1_D12", "Ngày, giờ thi": "25/01/2026, 07h00"},
    "D13": {"Mã học phần": "AMA301_2511_1_D13", "Ngày, giờ thi": "25/01/2026, 07h00"},
    "D14": {"Mã học phần": "AMA301_2511_1_D14", "Ngày, giờ thi": "25/01/2026, 08h30"}
}

# 2. Xử lý logic hiển thị dựa trên bộ lọc Sidebar
if len(selected_class) == 1:
    # Nếu người dùng chỉ chọn ĐÚNG 1 lớp
    lop_duy_nhat = selected_class[0]
    ma_hp_hien_thi = course_info[lop_duy_nhat]["Mã học phần"]
    ngay_thi_hien_thi = course_info[lop_duy_nhat]["Ngày, giờ thi"]
else:
    # Nếu người dùng chọn từ 2 lớp trở lên, hoặc chọn "Tất cả"
    ma_hp_hien_thi = "AMA301_2511_1"
    ngay_thi_hien_thi = "Nhiều ca thi (Vui lòng chọn 1 lớp cụ thể)"

# 3. Hiển thị lên giao diện (Dùng container và chia cột cho đẹp)
with st.container():
    st.markdown("### 📝 Thông tin lớp học phần")
    col_info1, col_info2, col_info3 = st.columns(3)
    
    with col_info1:
        st.write("**Hệ:** Chính quy")
        st.write("**Môn học:** Toán cao cấp 1")
        
    with col_info2:
        st.write("**Năm học:** 2025-2026")
        st.write("**Học kỳ:** HK01")
        
    with col_info3:
        st.write(f"**Mã học phần:** {ma_hp_hien_thi}")
        st.write(f"**Ngày, giờ thi:** {ngay_thi_hien_thi}")
        
st.markdown("---") # Đường kẻ ngang phân cách trước khi vào các Tabs
# --------------------------------
# 🌟 TÍNH NĂNG 1: TẠO 3 TABS PHÂN TRANG (st.tabs)
tab1, tab2, tab3 = st.tabs(["📊 Tổng quan lớp", "🔍 Phân tích chuyên sâu", "🧑‍🎓 Tra cứu cá nhân (Radar)"])

# ==========================================
# TAB 1: TỔNG QUAN
# ==========================================
with tab1:
    st.subheader("📌 Tổng quan KPI")
    col1, col2, col3, col4 = st.columns(4)
    mean10 = filtered_df["Điểm_tổng_hợp"].mean()
    mean4 = filtered_df["Điểm_4"].mean()
    col1.metric("Điểm TB (hệ 10)", round(mean10, 1) if not pd.isna(mean10) else 0)
    col2.metric("Điểm TB (hệ 4)", round(mean4, 1) if not pd.isna(mean4) else 0)
    max_score = filtered_df["Điểm_tổng_hợp"].max()
    col3.metric("Cao nhất", max_score if not pd.isna(max_score) else 0)
    col4.metric("Tổng SV", filtered_df.shape[0])

    st.markdown("---")
    
    colA, colB = st.columns(2)
    with colA:
        st.subheader("🏆 Xếp hạng lớp")
        avg_class = filtered_df.groupby("Lớp")["Điểm_tổng_hợp"].mean().reset_index()
        avg_class = avg_class.sort_values(by="Điểm_tổng_hợp", ascending=False)
        fig_rank = px.bar(
            avg_class, x="Lớp", y="Điểm_tổng_hợp", color="Lớp",
            color_discrete_map=color_map, text_auto='.2f'
        )
        fig_rank.update_traces(marker_line_color='black', marker_line_width=1.2)
        st.plotly_chart(fig_rank, use_container_width=True)

    with colB:
        st.subheader("📊 Phân loại sinh viên")
        crosstab_df = pd.crosstab(filtered_df["Lớp"], filtered_df["Xếp loại"]).reset_index()
        order = ["Lớp", "Xuất sắc", "Giỏi", "Khá", "Trung bình", "Yếu"]
        crosstab_df = crosstab_df[[col for col in order if col in crosstab_df.columns]]
        melted_df = crosstab_df.melt(id_vars="Lớp", var_name="Xếp loại", value_name="Số lượng")
        fig_class = px.bar(
            melted_df, x="Lớp", y="Số lượng", color="Xếp loại",
            barmode="group", text_auto=True,
            color_discrete_sequence=px.colors.qualitative.Set2 
        )
        fig_class.update_traces(marker_line_color='black', marker_line_width=1)
        st.plotly_chart(fig_class, use_container_width=True)

    st.markdown("---")

    colC, colD = st.columns(2)
    with colC:
        st.subheader("📈 Phân bố điểm (Histogram)")
        fig_hist = px.histogram(
            filtered_df, x="Điểm_tổng_hợp", color="Lớp",
            color_discrete_map=color_map, nbins=20, barmode="overlay", opacity=0.7
        )
        fig_hist.update_traces(marker_line_color='black', marker_line_width=1)
        st.plotly_chart(fig_hist, use_container_width=True)

    with colD:
        st.subheader("📦 Khoảng phân tán (Boxplot)")
        fig_box = px.box(
            filtered_df, x="Lớp", y="Điểm_tổng_hợp", color="Lớp",
            color_discrete_map=color_map, points=False
        )
        fig_box.update_traces(marker_line_color='black', marker_line_width=1)
        st.plotly_chart(fig_box, use_container_width=True)


# ==========================================
# TAB 2: PHÂN TÍCH CHUYÊN SÂU
# ==========================================
with tab2:
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("🔍 Phân tích Tương quan")
        corr_options = {
            "Điểm thi cuối kì": "Thi_cuối_kì",
            "Điểm kiểm tra GK (20%)": "Kiểm_tra_GK",
            "Điểm Thảo luận, BTN, TT (20%)": "Thảo_luận_BTN_TT",
            "Điểm chuyên cần (10%)": "Chuyên_cần"
        }
        selected_corr_name = st.selectbox("Chọn thành phần điểm để đối chiếu với Điểm tổng hợp:", options=list(corr_options.keys()))
        x_col = corr_options[selected_corr_name]

        fig3, ax3 = plt.subplots(figsize=(6, 5))
        scatter_df = filtered_df.dropna(subset=[x_col, "Điểm_tổng_hợp"])
        sns.scatterplot(data=scatter_df, x=x_col, y="Điểm_tổng_hợp", hue="Lớp", palette=color_map, alpha=0.6, edgecolor="black", ax=ax3)
        sns.regplot(data=scatter_df, x=x_col, y="Điểm_tổng_hợp", scatter=False, color="black", ax=ax3)

        ax3.set_title(f"Tương quan: {selected_corr_name}", fontweight='bold')
        ax3.set_xlabel(selected_corr_name)
        ax3.set_ylabel("Điểm tổng hợp")
        ax3.grid(True, linestyle='--', alpha=0.5)
        for spine in ax3.spines.values(): spine.set_edgecolor('black')
        st.pyplot(fig3)

    with col_right:
        st.subheader("📊 Ma trận tương quan (Heatmap)")
        corr_df = filtered_df[["Chuyên_cần", "Kiểm_tra_GK", "Thảo_luận_BTN_TT", "Thi_cuối_kì", "Điểm_tổng_hợp"]].dropna()
        corr = corr_df.corr()
        fig4, ax4 = plt.subplots(figsize=(6, 5))
        sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", ax=ax4, linewidths=0.5, linecolor='black') 
        plt.xticks(rotation=45, ha='right') 
        st.pyplot(fig4)


# ==========================================
# TAB 3: TRA CỨU CÁ NHÂN  
# ==========================================
with tab3:
    st.subheader("🎯 Tra cứu & Đánh giá năng lực cá nhân (Radar Chart)")
    
    # Tạo cột Tên hiển thị (MSSV - Họ Tên)
    filtered_df["Tên_Hiển_Thị"] = filtered_df["MSSV"].astype(str) + " - " + filtered_df["Họ"].fillna("") + " " + filtered_df["Tên"].fillna("")
    
    # Hộp thoại chọn Sinh viên
    selected_student = st.selectbox("🔍 Nhập MSSV hoặc Tên sinh viên để phân tích:", filtered_df["Tên_Hiển_Thị"].unique())
    
    if selected_student:
        # Lấy dữ liệu của sinh viên được chọn
        student_data = filtered_df[filtered_df["Tên_Hiển_Thị"] == selected_student].iloc[0]
        
        col_radar, col_info = st.columns([2, 1])
        
        with col_radar:
            # 🌟 TÍNH NĂNG 2: VẼ RADAR CHART
            categories = ['Chuyên cần', 'Kiểm tra GK', 'Thảo luận & Bài tập', 'Thi cuối kì']
            
            # Điểm của sinh viên (Thêm phần tử đầu tiên vào cuối để tạo thành vòng khép kín)
            student_scores = [student_data['Chuyên_cần'], student_data['Kiểm_tra_GK'], student_data['Thảo_luận_BTN_TT'], student_data['Thi_cuối_kì']]
            student_scores += [student_scores[0]] 
            
            # Điểm trung bình của lớp làm hệ quy chiếu
            class_avg = [filtered_df['Chuyên_cần'].mean(), filtered_df['Kiểm_tra_GK'].mean(), filtered_df['Thảo_luận_BTN_TT'].mean(), filtered_df['Thi_cuối_kì'].mean()]
            class_avg += [class_avg[0]]
            
            # Đóng danh mục categories
            categories += [categories[0]]

            fig_radar = go.Figure()
            # Vẽ vùng điểm của sinh viên
            fig_radar.add_trace(go.Scatterpolar(
                r=student_scores, theta=categories, fill='toself',
                name=f'SV: {student_data["Tên"]}', line_color='#F5793A'
            ))
            # Vẽ vùng điểm trung bình lớp
            fig_radar.add_trace(go.Scatterpolar(
                r=class_avg, theta=categories, fill='toself',
                name='Trung bình toàn lớp', line_color='#85C0F9', opacity=0.7
            ))

            fig_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
                showlegend=True,
                title=f"Bản đồ Năng lực: {student_data['Họ']} {student_data['Tên']}"
            )
            st.plotly_chart(fig_radar, use_container_width=True)

        with col_info:
            st.info(f"**Lớp:** {student_data['Lớp']}")
            st.success(f"**Điểm hệ 10:** {student_data['Điểm_tổng_hợp']} \n\n **Điểm hệ 4:** {student_data['Điểm_4']}")
            st.warning(f"**Xếp loại:** {student_data['Xếp loại']}")
            
            # Nhận xét tự động từ AI (Dựa trên Radar)
            st.write("📝 **Chẩn đoán nhanh:**")
            if student_data['Thi_cuối_kì'] < class_avg[3]:
                st.error("Cảnh báo: Điểm thi cuối kì thấp hơn mặt bằng chung. Cần chú trọng ôn tập lý thuyết/thực hành chuyên sâu.")
            elif student_data['Chuyên_cần'] < 7:
                st.error("Cảnh báo: Tỷ lệ vắng mặt cao, nguy cơ ảnh hưởng thái độ học tập.")
            else:
                st.success("Phong độ học tập ổn định, bám sát hoặc vượt mức trung bình của lớp.")

    st.markdown("---")
    
# ===== BẢNG CHI TIẾT & XUẤT PDF =====
    st.subheader("📋 Bảng điểm chi tiết & Xuất File")
    
    col_filter, col_pdf = st.columns([3, 1])
    
    with col_filter:
        selected_type = st.selectbox("Lọc danh sách theo Xếp loại:", ["Tất cả", "Xuất sắc", "Giỏi", "Khá", "Trung bình", "Yếu"], key="filter_main")
        display_df = filtered_df if selected_type == "Tất cả" else filtered_df[filtered_df["Xếp loại"] == selected_type]
    
    st.dataframe(display_df[["MSSV", "Họ", "Tên", "Lớp", "Chuyên_cần", "Kiểm_tra_GK", "Thảo_luận_BTN_TT", "Thi_cuối_kì", "Điểm_tổng_hợp", "Xếp loại"]])

    with col_pdf:
        st.write("") # Dóng hàng
        st.write("")
        
        def create_pdf_buffer(df_export):
            buffer = io.BytesIO()
            pdfmetrics.registerFont(TTFont('DejaVu', 'DejaVuSans.ttf'))
            doc = SimpleDocTemplate(buffer)
            styles = getSampleStyleSheet()

            styles["Normal"].fontName = "DejaVu"
            styles["Title"].fontName = "DejaVu"
            styles["Heading2"].fontName = "DejaVu"

            content = []
            
            # 1. Tiêu đề
            content.append(Paragraph("BÁO CÁO TỔNG QUAN PHÂN TÍCH ĐIỂM", styles["Title"]))
            content.append(Spacer(1, 20))

            # 2. Thống kê tổng quan
            content.append(Paragraph("1. Tổng quan dữ liệu", styles["Heading2"]))
            content.append(Spacer(1, 10))
            
            mean10 = round(df_export["Điểm_tổng_hợp"].mean(), 2) if not pd.isna(df_export["Điểm_tổng_hợp"].mean()) else 0
            mean4 = round(df_export["Điểm_4"].mean(), 2) if not pd.isna(df_export["Điểm_4"].mean()) else 0
            max_score = df_export["Điểm_tổng_hợp"].max() if not pd.isna(df_export["Điểm_tổng_hợp"].max()) else 0
            
            content.append(Paragraph(f"- Tổng số sinh viên: {df_export.shape[0]}", styles["Normal"]))
            content.append(Paragraph(f"- Điểm trung bình (Hệ 10): {mean10} | (Hệ 4): {mean4}", styles["Normal"]))
            content.append(Paragraph(f"- Điểm cao nhất: {max_score}", styles["Normal"]))
            content.append(Spacer(1, 15))

            # 3. Thống kê xếp loại
            content.append(Paragraph("2. Thống kê Xếp loại", styles["Heading2"]))
            content.append(Spacer(1, 10))
            
            xep_loai_counts = df_export["Xếp loại"].value_counts()
            order = ["Xuất sắc", "Giỏi", "Khá", "Trung bình", "Yếu"]
            
            for xl in order:
                count = xep_loai_counts.get(xl, 0)
                percent = round((count / df_export.shape[0]) * 100, 1) if df_export.shape[0] > 0 else 0
                content.append(Paragraph(f"- {xl}: {count} sinh viên ({percent}%)", styles["Normal"]))

            # Đóng gói PDF
            doc.build(content)
            buffer.seek(0)
            return buffer

        def show_success_toast():
            st.toast("✅ Đã tải Báo cáo PDF thành công!", icon="🎉")

        st.download_button(
            label="📥 Tải PDF Báo Cáo",
            data=create_pdf_buffer(filtered_df),
            file_name="Bao_Cao_TCC1.pdf",
            mime="application/pdf",
            on_click=show_success_toast,
            use_container_width=True
        )
