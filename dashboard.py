import plotly.express as px
import time
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

# Chèn Logo trường ở trên cùng
st.sidebar.image("logo.png", use_container_width=True)

# 1. Thêm Tiêu đề/Logo thương hiệu nổi bật
st.sidebar.markdown("<h2 style='text-align: center; color: #F5793A;'>🎓 Group 5</h2>", unsafe_allow_html=True)
st.sidebar.markdown("---") # Đường gạch ngang phân cách

# 2. Khu vực bộ lọc chính
st.sidebar.header("🎛️ Bộ lọc dữ liệu")

selected_class = st.sidebar.multiselect(
    "Chọn lớp:",
    options=df["Lớp"].unique(),
    default=df["Lớp"].unique(),
    help="Bạn có thể chọn một hoặc nhiều lớp cùng lúc để so sánh dữ liệu."
)

min_score, max_score = st.sidebar.slider(
    "Khoảng điểm",
    0.0, 10.0, (0.0, 10.0)
)

selected_type_sidebar = st.sidebar.selectbox(
    "Chọn xếp loại",
    ["Tất cả", "Xuất sắc", "Giỏi", "Khá", "Trung bình", "Yếu"]
) 
if selected_type_sidebar == "Yếu":
    st.snow() # Màn hình sẽ đổ tuyết
    st.toast("🥶 Cảnh báo: Tình hình học tập đang đóng băng!", icon="❄️")
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

st.sidebar.markdown("---")
st.sidebar.markdown("### 👨‍💻 Đội ngũ thực hiện")
st.sidebar.info("""
**Nhóm sinh viên:**
1. **Phạm Đoàn Yến Nhi**
2. **Nguyễn Thị Huỳnh Như**
3. **Đặng Lê Thanh Trúc**
4. **Nguyễn Thị Hằng Ny**
5. **Trương Nguyễn Phương Mai**
6. **Trịnh Yến Vy**
7. **Trần Thị Bảo Ngân**

*Đề tài: Phân tích dữ liệu điểm Toán cao cấp 1*
""")
# --------------------------------
# 🌟 TÍNH NĂNG 1: TẠO 3 TABS PHÂN TRANG (st.tabs)
tab1, tab2, tab3 = st.tabs(["📊 Tổng quan lớp", "🔍 Phân tích chuyên sâu", "🧑‍🎓 Tra cứu cá nhân (Radar)"])

# ==========================================
# TAB 1: TỔNG QUAN
# ==========================================
with tab1:
    st.subheader("📌 Tổng quan")
    
    # Chia thành 5 cột để chứa đủ 5 chỉ số
    col1, col2, col3, col4, col5 = st.columns(5)
    
    # 1. Tính toán các chỉ số
    mean10 = filtered_df["Điểm_tổng_hợp"].mean()
    mean4 = filtered_df["Điểm_4"].mean() # Tính lại điểm trung bình hệ 4
    
    so_sv_qua_mon = filtered_df[filtered_df["Điểm_tổng_hợp"] >= 5.0].shape[0]
    ty_le_qua = (so_sv_qua_mon / filtered_df.shape[0]) * 100 if filtered_df.shape[0] > 0 else 0
    
    max_score = filtered_df["Điểm_tổng_hợp"].max()
    
    # 2. Hiển thị lên giao diện 5 ô Metric
    col1.metric("Điểm TB (hệ 10)", round(mean10, 1) if not pd.isna(mean10) else 0)
    col2.metric("Điểm TB (hệ 4)", round(mean4, 1) if not pd.isna(mean4) else 0) 
    col3.metric("Tỷ lệ qua môn", f"{round(ty_le_qua, 1)}%") 
    col4.metric("Cao nhất", max_score if not pd.isna(max_score) else 0)
    col5.metric("Tổng SV", filtered_df.shape[0])

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
        with st.expander("💡 Hướng dẫn đọc biểu đồ Cột"):
            st.write("""
            - **Ý nghĩa:** Dùng để so sánh nhanh mặt bằng chung giữa các lớp. 
            - **Cách đọc:** Cột càng cao thể hiện điểm trung bình lớp càng tốt. Bạn có thể rê chuột vào từng cột để xem điểm số chính xác.
            """)

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
        with st.expander("💡 Hướng dẫn đọc biểu đồ Phân loại"):
            st.write("""
            - **Ý nghĩa:** Trực quan hóa tỷ trọng học lực của từng lớp.
            - **Cách đọc:** Nhóm cột màu xanh/cam (Xuất sắc, Giỏi) càng cao cho thấy chất lượng đào tạo của lớp đó càng tích cực và sinh viên đáp ứng rất tốt chuẩn đầu ra.
            """)

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
        with st.expander("💡 Hướng dẫn đọc Histogram (Phân bố điểm)"):
            st.write("""
            - **Đỉnh ngọn núi:** Cho biết mức điểm nào đang có đông sinh viên đạt được nhất.
            - **Cách đọc:** Nếu hình dáng ngọn núi lệch hẳn về bên phải (phía 8-10 điểm), chứng tỏ đề thi vừa sức và phần đông sinh viên làm bài rất tốt. Ngược lại, nếu lệch trái là dấu hiệu đáng báo động.
            """)

    with colD:
        st.subheader("📦 Khoảng phân tán (Boxplot)")
        fig_box = px.box(
            filtered_df, x="Lớp", y="Điểm_tổng_hợp", color="Lớp",
            color_discrete_map=color_map, points=False
        )
        fig_box.update_traces(marker_line_color='black', marker_line_width=1)
        st.plotly_chart(fig_box, use_container_width=True)
        with st.expander("💡 Hướng dẫn đọc Boxplot (Hộp phân tán)"):
            st.write("""
            **1. Hộp màu ở giữa (Đại diện cho "Nhóm cốt lõi"):**
            Hãy tưởng tượng xếp điểm của cả lớp thành một hàng dọc từ thấp đến cao, sau đó loại bỏ 25% các bạn điểm thấp nhất và 25% các bạn điểm cao nhất. Chiếc hộp này chính là khoảng điểm của **50% sinh viên nằm ở khúc giữa của lớp**. 
            - Nếu hộp **ngắn**: Nghĩa là nhóm cốt lõi này có điểm rất sát nhau => Lớp học có sức học đồng đều. 
            - Nếu hộp **dài**: Nghĩa là điểm phân tán rộng => Lớp học có sự chênh lệch lớn.

            **2. Đường gạch ngang bên trong hộp (Điểm Trung vị):**
            Đây là điểm của sinh viên đứng ngay vị trí chính giữa lớp. Khác với "Điểm trung bình" dễ bị kéo tụt xuống bởi một vài điểm 0, điểm Trung vị phản ánh chính xác nhất "mặt bằng chung" thực tế của đa số sinh viên.

            **3. Hai đường râu kéo dài (Whiskers):**
            Thể hiện khoảng điểm của các sinh viên còn lại. Nếu đường râu bị kéo tuột xuống tận mức điểm rất thấp (ví dụ lớp D05), đó là tín hiệu cảnh báo có những cá nhân đang bị đuối sức và tụt hậu rất xa so với cả lớp.
            """)


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
        with st.expander("💡 Hướng dẫn đọc biểu đồ Phân tán"):
            st.write("""
            - **Dấu chấm:** Mỗi dấu chấm đại diện cho 1 sinh viên.
            - **Đường xu hướng (đường màu đen):** Cho biết mức độ tỷ lệ thuận. Đường này càng dốc hướng lên trên chứng tỏ điểm thành phần đó có tác động càng lớn đến kết quả Điểm tổng hợp cuối cùng.
            """)

    with col_right:
        st.subheader("📊 Ma trận tương quan (Heatmap)")
        corr_df = filtered_df[["Chuyên_cần", "Kiểm_tra_GK", "Thảo_luận_BTN_TT", "Thi_cuối_kì", "Điểm_tổng_hợp"]].dropna()
        corr = corr_df.corr()
        fig4, ax4 = plt.subplots(figsize=(6, 5))
        sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", ax=ax4, linewidths=0.5, linecolor='black') 
        plt.xticks(rotation=45, ha='right') 
        st.pyplot(fig4)
        with st.expander("💡 Hướng dẫn đọc Ma trận nhiệt"):
            st.write("""
            - **Màu sắc & Con số:** Màu đỏ càng đậm (tiến gần về 1) thì mức độ quyết định càng lớn. Màu xanh nhạt là ít liên quan.
            - **Cách đọc:** Hãy nhìn vào hàng ngang cuối cùng (Điểm tổng hợp). Ô nào màu đỏ đậm nhất (thường là Thi cuối kì) chính là bài kiểm tra mang tính chất quyết định sống còn đến việc sinh viên qua môn hay rớt môn.
            """)


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
            with st.expander("💡 Hướng dẫn đọc biểu đồ Năng lực cá nhân"):
                st.write("""
                - **Lớp màu xanh mờ (Nền):** Thể hiện sức học trung bình của cả lớp, dùng làm hệ quy chiếu.
                - **Lớp màu cam (Sinh viên):** Thể hiện năng lực thực tế của cá nhân.
                - **Cách chẩn đoán:** Nếu lớp màu cam căng tròn và đè lên lớp nền xanh, sinh viên học rất tốt và đều. Nếu một góc mạng nhện bị "lõm" sâu vào trong so với vùng xanh, đó chính là lỗ hổng kỹ năng mà sinh viên cần khắc phục.
                """)

        with col_info:
            st.info(f"**Lớp:** {student_data['Lớp']}")
            st.success(f"**Điểm hệ 10:** {student_data['Điểm_tổng_hợp']} \n\n **Điểm hệ 4:** {student_data['Điểm_4']}")
            st.warning(f"**Xếp loại:** {student_data['Xếp loại']}")
            
            # Nhận xét tự động từ AI (Dựa trên Radar)
            st.write("📝 **Nhận xét:**")
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
        
        # Hàm xuất PDF nâng cấp Chuẩn Hành Chính
        def create_formal_pdf(df_export, ma_hp, ngay_thi):
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.enums import TA_CENTER, TA_RIGHT
            from reportlab.lib import colors
            import io
            
            buffer = io.BytesIO()
            pdfmetrics.registerFont(TTFont('DejaVu', 'DejaVuSans.ttf'))
            
            # Cấu hình lề cho văn bản hành chính
            doc = SimpleDocTemplate(buffer, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
            styles = getSampleStyleSheet()

            # Tạo các Style chữ riêng biệt
            style_normal = ParagraphStyle(name='Normal_DJV', fontName='DejaVu', fontSize=11, leading=14)
            style_center = ParagraphStyle(name='Center_DJV', fontName='DejaVu', fontSize=11, alignment=TA_CENTER, leading=14)
            style_title = ParagraphStyle(name='Title_DJV', fontName='DejaVu', fontSize=16, alignment=TA_CENTER, spaceAfter=20, spaceBefore=20)
            style_heading = ParagraphStyle(name='Heading_DJV', fontName='DejaVu', fontSize=12, spaceAfter=10, spaceBefore=15)

            content = []
            
            # --- 1. QUỐC HIỆU & TIÊU NGỮ (Dạng Bảng 2 cột) ---
            p_left = Paragraph("NGÂN HÀNG NHÀ NƯỚC VIỆT NAM<br/>TRƯỜNG ĐẠI HỌC NGÂN HÀNG TP.HCM<br/>-------", style_center)
            p_right = Paragraph("CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM<br/>Độc lập - Tự do - Hạnh phúc<br/>-------", style_center)
            
            header_table = Table([[p_left, p_right]], colWidths=[260, 260])
            header_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
            content.append(header_table)
            content.append(Spacer(1, 10))

            # --- 2. TÊN BÁO CÁO ---
            content.append(Paragraph("BẢNG ĐIỂM HỌC PHẦN & ĐÁNH GIÁ TỔNG QUAN", style_title))

            # --- 3. THÔNG TIN HỌC PHẦN ĐỘNG ---
            info_data = [
                [Paragraph("Hệ:", style_normal), Paragraph("Chính quy", style_normal), Paragraph("Năm học:", style_normal), Paragraph("2025-2026", style_normal)],
                [Paragraph("Môn học:", style_normal), Paragraph("Toán cao cấp 1", style_normal), Paragraph("Học kỳ:", style_normal), Paragraph("HK01", style_normal)],
                [Paragraph("Mã học phần:", style_normal), Paragraph(ma_hp, style_normal), Paragraph("Ngày, giờ thi:", style_normal), Paragraph(ngay_thi, style_normal)]
            ]
            info_table = Table(info_data, colWidths=[90, 170, 90, 170])
            content.append(info_table)
            content.append(Spacer(1, 20))

            # --- 4. THỐNG KÊ XẾP LOẠI & NHẬN XÉT ---
            content.append(Paragraph("I. THỐNG KÊ & ĐÁNH GIÁ", style_heading))
            
            total_sv = df_export.shape[0]
            if total_sv > 0:
                mean10 = round(df_export["Điểm_tổng_hợp"].mean(), 2)
                xep_loai_counts = df_export["Xếp loại"].value_counts()
                
                # Tính tỷ lệ đạt (Từ Trung bình trở lên)
                so_luong_yeu = xep_loai_counts.get("Yếu", 0)
                ty_le_dat = round(((total_sv - so_luong_yeu) / total_sv) * 100, 1)
                
                content.append(Paragraph(f"- Tổng số sinh viên: {total_sv}", style_normal))
                content.append(Paragraph(f"- Điểm trung bình chung (Hệ 10): {mean10}", style_normal))
                content.append(Spacer(1, 5))
                
                # Chi tiết xếp loại
                order = ["Xuất sắc", "Giỏi", "Khá", "Trung bình", "Yếu"]
                for xl in order:
                    count = xep_loai_counts.get(xl, 0)
                    percent = round((count / total_sv) * 100, 1)
                    content.append(Paragraph(f"  + {xl}: {count} sinh viên ({percent}%)", style_normal))
                
                content.append(Spacer(1, 10))
                # AI Nhận xét tự động dựa trên số liệu
                content.append(Paragraph("Nhận xét chuyên môn:", style_heading))
                if ty_le_dat >= 90:
                    nhan_xet = f"Chất lượng học tập RẤT TỐT. Tỷ lệ sinh viên qua môn đạt {ty_le_dat}%. Đa số sinh viên nắm vững kiến thức và hoàn thành tốt bài thi."
                elif ty_le_dat >= 70:
                    nhan_xet = f"Chất lượng học tập KHÁ. Tỷ lệ qua môn đạt {ty_le_dat}%. Tuy nhiên vẫn còn một bộ phận sinh viên cần cải thiện phương pháp học tập."
                else:
                    nhan_xet = f"CẦN LƯU Ý: Tỷ lệ qua môn chỉ đạt {ty_le_dat}%. Cần rà soát lại mức độ tiếp thu của sinh viên và có biện pháp phụ đạo ở học kỳ sau."
                content.append(Paragraph(nhan_xet, style_normal))

            content.append(Spacer(1, 20))

            # --- 5. DANH SÁCH SINH VIÊN (Bảng Grid) ---
            content.append(Paragraph("II. DANH SÁCH ĐIỂM CHI TIẾT", style_heading))
            
            # Tiêu đề cột
            table_data = [["STT", "MSSV", "Họ và Tên", "Lớp", "Điểm TK", "Xếp loại"]]
            
            # Rút trích dữ liệu sinh viên (Đã dùng iterrows để chống lỗi khoảng trắng)
            for index, (_, row) in enumerate(df_export.iterrows(), 1):
                # Xử lý an toàn nếu có sinh viên bị thiếu Họ hoặc Tên
                ho = str(row['Họ']) if not pd.isna(row['Họ']) else ""
                ten = str(row['Tên']) if not pd.isna(row['Tên']) else ""
                hoten = f"{ho} {ten}".strip()
                
                table_data.append([
                    str(index), 
                    str(row['MSSV']), 
                    hoten, 
                    str(row['Lớp']), 
                    str(row['Điểm_tổng_hợp']), 
                    str(row['Xếp loại'])
                ])

            # Cấu hình vẽ bảng
            student_table = Table(table_data, colWidths=[40, 80, 150, 60, 60, 130], repeatRows=1) # repeatRows giúp lặp lại tiêu đề khi sang trang mới
            student_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey), # Màu nền xám cho dòng tiêu đề
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'), # Căn giữa tất cả
                ('ALIGN', (2, 1), (2, -1), 'LEFT'), # Riêng cột Họ Tên thì căn trái
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black), # Vẽ lưới đen
                ('FONTNAME', (0, 0), (-1, -1), 'DejaVu'), # Dùng font tiếng Việt
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
            ]))
            content.append(student_table)

            # Đóng gói PDF
            doc.build(content)
            buffer.seek(0)
            return buffer

        def show_success_toast():
            st.toast("✅ Đã xuất Bảng Điểm thành công!", icon="🎓")
            st.balloons()
        # Truyền ma_hp_hien_thi và ngay_thi_hien_thi từ logic biến ở bên trên vào hàm
        st.download_button(
            label="📥 Tải PDF Bảng Điểm ",
            data=create_formal_pdf(filtered_df, ma_hp_hien_thi, ngay_thi_hien_thi),
            file_name=f"Bang_Diem_{ma_hp_hien_thi}.pdf",
            mime="application/pdf",
            on_click=show_success_toast,
            use_container_width=True
        )
