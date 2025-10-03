import streamlit as st
import pandas as pd
from datetime import date, timedelta
from services.data import fetch_price_history, validate_dates
from services.indicators import add_indicators
from utils.plotting import plot_ta_panels, plot_price_volume_panels


def render_analysis():
    st.subheader("Phân tích cơ bản")

    # Stock symbol input with validation
    symbol = st.text_input(
        "Mã cổ phiếu *",
        value="VNM",
        placeholder="Nhập mã cổ phiếu (VIC, VNM, HPG, HDB, VCB...)",
        help="Mã cổ phiếu bắt buộc phải nhập để phân tích"
    )
    symbol_error = ""

    # Date range inputs
    col1, col2 = st.columns(2)
    with col1:
        start = st.date_input(
            "Từ ngày *",
            value=date.today() - timedelta(days=365),
            help="Ngày bắt đầu lấy dữ liệu"
        )
    with col2:
        end = st.date_input(
            "Đến ngày *",
            value=date.today(),
            help="Ngày kết thúc lấy dữ liệu"
        )
    date_error = ""

    mode = st.radio("Chế độ hiển thị", ["Giá + Khối lượng", "Phân tích kỹ thuật"],
                    index=0, horizontal=True)

    if st.button("Tải dữ liệu"):
        # Validate symbol
        if not symbol or not symbol.strip():
            symbol_error = "❌ Vui lòng nhập mã cổ phiếu hợp lệ."

        # Validate dates
        elif start >= end:
            date_error = "❌ Ngày bắt đầu phải nhỏ hơn ngày kết thúc."

        else:
            try:
                print(f"[analysis] inputs: symbol={symbol}, start={start}, end={end}")
                start_s, end_s = validate_dates(start.isoformat(), end.isoformat())
                df = fetch_price_history(symbol, start_s, end_s)

                if df.empty:
                    symbol_error = f"❌ Không có dữ liệu cho mã **{symbol}** trong khoảng thời gian đã chọn."
                else:
                    # Chuẩn hoá dữ liệu
                    for c in ["open", "high", "low", "close", "volume"]:
                        if c in df.columns:
                            df[c] = pd.to_numeric(df[c], errors='coerce')

                    if "date" in df.columns:
                        df = df.sort_values("date")

                    st.session_state["analysis_df"] = df
                    st.session_state["analysis_meta"] = {
                        "symbol": symbol, "start": start_s, "end": end_s}
            except Exception as e:
                symbol_error = f"❌ Lỗi khi tải dữ liệu: {e}"

    # Hiển thị lỗi ngay dưới input
    if symbol_error:
        st.error(symbol_error)
    if date_error:
        st.error(date_error)

    # Render data nếu đã có
    df_cached = st.session_state.get("analysis_df")
    meta = st.session_state.get("analysis_meta", {})
    if isinstance(df_cached, pd.DataFrame) and not df_cached.empty:
        st.caption(f"Số dòng dữ liệu: {len(df_cached)}")
        st.dataframe(df_cached.tail(5))

        csv = df_cached.to_csv(index=False).encode('utf-8-sig')
        st.download_button("Tải CSV", csv,
                           file_name=f"{meta.get('symbol','SYMB')}_{meta.get('start','')}_{meta.get('end','')}.csv",
                           mime="text/csv")

        # Compute indicators once per render
        try:
            df_ind = add_indicators(df_cached.copy())
        except Exception as e:
            print(f"[analysis] indicators error: {e}")
            df_ind = df_cached

        if mode == "Giá + Khối lượng":
            fig_pv = plot_price_volume_panels(
                df_ind, title=f"Price & Volume for {meta.get('symbol','')}")
            st.pyplot(fig_pv)
        else:
            fig_panels = plot_ta_panels(
                df_ind, title=f"Technical Analysis for {meta.get('symbol','')}")
            st.pyplot(fig_panels)
