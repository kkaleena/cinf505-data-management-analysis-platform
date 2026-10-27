import io
import pandas as pd
import streamlit as st
#import Db
import Data_ops as ops
# import Charts

st.set_page_config(page_title="Data Workbench", layout="wide")

# Session state
# Keep the original copy --> working with the copied excelsheet
for key, default in {"original": None, "working":None, "name":None, "last_result": None}.items():
    st.session_state.setdefault(key, default)

# User input (Selection buttons)
PAGES = ["1. Import", "2. Explore & Filter", "3. Check Data", "4. Clean Data",
         "5. Analyze", "6. Charts", "7. Export"]
page = st.sidebar.radio("Data Management and Analysis Platform", PAGES)
st.sidebar.subheader("Follow the Steps")
st.sidebar.subheader("Import -> Check -> Clean -> Analyze -> Charts -> Export")

# Starting Screen
def need_data():
    if st.session_state.working is None:
        st.info("Please import a file.")
        st.info("Follow step 1.")
        st.stop()
    return st.session_state.working

# Save the original file and work on the copy file
def load_into_session(name, df):
    st.session_state.original = df.copy()
    st.session_state.working = df.copy()
    st.session_state.name = name

# ============================ 1. IMPORT ============================
if page == PAGES[0]:
    st.title("Import your data")
    InputFile = st.file_InputFileloader("Choose a CSV or Excel (.xlsx) file", type=None)
    if InputFile is not None:
        # Input the data to database file
        try:
            df = ops.read_file(InputFile)
            name = InputFile.name.rsplit(".", 1)[0]
            Db.save_dataset(name, df)
            load_into_session(name, df)
            st.success(f"Loaded '{InputFile.name}': {len(df)} rows, {len(df.columns)} columns.")
        except ValueError as e:
            st.error(str(e))
    saved = Db.list_datasets()
    # Design interface and button
    if saved:
        st.subheader("Or open a previously saved dataset")
        choice = st.selectbox("Saved datasets", saved)
        if st.button("Open"):
            load_into_session(choice, Db.load_dataset(choice))
            st.success(f"Opened '{choice}'.")
    if st.session_state.working is not None:
        st.subheader("Preview")
        st.dataframe(st.session_state.working.head(100), use_container_width=True)

# REMINDER: add save_dataset, list_datasets & load_dataset in Db file

# ============================ 2. EXPLORE & FILTER ============================
elif page == PAGES[1]:
    st.title("Explore & filter")
    df = need_data()
    # 1. choose which columns to display (Could be more than 1 column)
    cols = st.multiselect("Columns to show", list(df.columns), default=list(df.columns))
    view = df[cols] if cols else df # when user deselect all columns --> go back to full dataset

    # 2. Filter control
    c1, c2, c3 = st.columns(3)
    FiltCont = c1.selectbox("Filter column", ["(none)"] + list(view.columns))
    # only filter if the user picked a column
    if FiltCont != "(none)":
        numeric = pd.api.types.is_numeric_dtype(view[FiltCont]) # check data type
        conds = ([">", "<", "between", "equals", "is missing"] if numeric
                 else ["contains", "equals", "is missing"])
        cond = c2.selectbox("Condition", conds)
        # v and v2 hold the user's filter values (None until set)
        v = v2 = None
        if cond in (">", "<", "between"):
            # Number box, pre-filled with the column's minimum
            v = c3.number_input("Value", value=float(view[FiltCont].min()))
            if cond == "between":
                # Second box for the upper limit, pre-filled with the maximum
                v2 = c3.number_input("and", value=float(view[FiltCont].max()))
        elif cond in ("contains", "equals"):
            v = c3.text_input("Value")
        # Apply the filter using the logic in data_ops.py
        view = ops.filter_data(view, FiltCont, cond, v, v2)

    # 3. Sorting
    # Only sort the filtered rows
    sort_col = st.selectbox("Sort by", ["(none)"] + list(view.columns))
    if sort_col != "(none)":
        # Add buttons
        asc = st.radio("Order", ["Ascending", "Descending"], horizontal=True) == "Ascending"
        view = view.sort_values(sort_col, ascending=asc)

    # 4. Show results
    # Compare the filtered row count to the full dataset
    st.caption(f"Showing {len(view)} of {len(df)} rows")
    st.dataframe(view, use_container_width=True)

    # 5. keep te result (optional)
    # Students could use it in other pages
    if st.button("Keep this view as my working data"):
        # reset_index renumbers rows 0, 1, 2... after filtering/sorting
        st.session_state.working = view.reset_index(drop=True)
        st.success("Working data updated (original is untouched).")

# ============================ 3. CHECK DATA ============================
# ============================ 4. CLEAN DATA ============================
# ============================ 5. ANALYZE ============================
# ============================ 6. CHARTS ============================
# ============================ 7. EXPORT ============================