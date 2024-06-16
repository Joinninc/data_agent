import streamlit as st
import pandas as pd
import sqlite3
from db.schema import initialize_database
from datetime import datetime

# Path to SQLite database
DB_PATH = 'fixed_assets.db'

# Initialize the database with necessary tables and data
initialize_database(DB_PATH)

# Function to insert fixed asset data from CSV and run depreciation queries
def process_fixed_assets(df, depreciation_method):
    # Connect to the SQLite database
    conn = sqlite3.connect(DB_PATH)

    # Insert fixed asset data into the database
    c = conn.cursor()
    c.execute("DELETE FROM fixed_assets_list")
    df.to_sql('fixed_assets_list', conn, if_exists='append', index=False)

    # Run depreciation queries
    run_depreciation_queries(conn, depreciation_method)

    # Retrieve and display results from macrs_depreciation table
    result_df = pd.read_sql_query("SELECT * FROM final_depreciation", conn)

    # Close the database connection
    conn.close()

    return result_df

# Function to run depreciation queries
def run_depreciation_queries(conn, depreciation_method):
    c = conn.cursor()

    # Create or replace the macrs_depreciation table
    c.execute('DROP TABLE IF EXISTS macrs_depreciation;')
    c.execute('''
    CREATE TABLE macrs_depreciation (
        Asset_ID INTEGER,
        Depreciation_Year INTEGER,
        Acquisition_Date DATE,
        Depreciation_Amount DECIMAL(10, 2),
        Accumulated_Depreciation DECIMAL(18, 2) DEFAULT 0,
        Book_Value DECIMAL(18, 2) DEFAULT 0
    );
    ''')

    # Insert Depreciation Data Based on the Applicable Convention
    if depreciation_method == 'Double Declining Balance':
        c.execute('''
            WITH Total_Depreciable_Basis AS (
                SELECT SUM(Depreciable_Basis) AS Total_Basis FROM fixed_assets_list
            ),
            Last_Quarter_Depreciable_Basis AS (
                SELECT SUM(Depreciable_Basis) AS Last_Quarter_Basis FROM fixed_assets_list
                WHERE CAST(SUBSTR(Acquisition_Date, 4, 2) AS INTEGER) IN (10, 11, 12)
            ),
            Mid_Quarter_Condition AS (
                SELECT CASE WHEN Last_Quarter_Basis > (Total_Basis * 0.40) THEN 'Yes' ELSE 'No' END AS Use_Mid_Quarter
                FROM Total_Depreciable_Basis, Last_Quarter_Depreciable_Basis
            )
            INSERT INTO macrs_depreciation (Asset_ID, Depreciation_Year, Depreciation_Amount)
            SELECT a.Asset_ID, y.seq AS Depreciation_Year, a.Depreciable_Basis *
                (CASE WHEN (SELECT Use_Mid_Quarter FROM Mid_Quarter_Condition) = 'Yes' THEN
                    CASE WHEN t.GDS_MACRS_Recovery_Period_years = 3 THEN mq.ThreeYear
                         WHEN t.GDS_MACRS_Recovery_Period_years = 5 THEN mq.FiveYear
                         WHEN t.GDS_MACRS_Recovery_Period_years = 7 THEN mq.SevenYear
                         WHEN t.GDS_MACRS_Recovery_Period_years = 10 THEN mq.TenYear
                         WHEN t.GDS_MACRS_Recovery_Period_years = 15 THEN mq.FifteenYear
                         WHEN t.GDS_MACRS_Recovery_Period_years = 20 THEN mq.TwentyYear
                    END / 100
                ELSE
                    CASE WHEN t.GDS_MACRS_Recovery_Period_years = 3 THEN hy.ThreeYear
                         WHEN t.GDS_MACRS_Recovery_Period_years = 5 THEN hy.FiveYear
                         WHEN t.GDS_MACRS_Recovery_Period_years = 7 THEN hy.SevenYear
                         WHEN t.GDS_MACRS_Recovery_Period_years = 10 THEN hy.TenYear
                         WHEN t.GDS_MACRS_Recovery_Period_years = 15 THEN hy.FifteenYear
                         WHEN t.GDS_MACRS_Recovery_Period_years = 20 THEN hy.TwentyYear
                    END / 100
                END) AS Depreciation_Amount
            FROM fixed_assets_list a
            JOIN "Table B-1-Table-of-Class-Lives-and-Recovery-Periods" t ON a.Asset_Class = t.Asset_Class
            CROSS JOIN (SELECT 1 AS seq UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL
                        SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9 UNION ALL SELECT 10 UNION ALL 
                        SELECT 11 UNION ALL SELECT 12 UNION ALL SELECT 13 UNION ALL SELECT 14 UNION ALL SELECT 15 UNION ALL
                        SELECT 16 UNION ALL SELECT 17 UNION ALL SELECT 18 UNION ALL SELECT 19 UNION ALL SELECT 20) y
            LEFT JOIN "Table-A-1-Half-Year Convention" hy ON y.seq = hy.Year
            LEFT JOIN "Table-A-2-Mid-Quarter-Convention" mq ON y.seq = mq.Year
            WHERE a.Depreciation_Method = 'Double Declining Balance' AND y.seq <= t.GDS_MACRS_Recovery_Period_years;
        ''')

    elif depreciation_method == 'Straight Line':
        c.execute('''
            INSERT INTO macrs_depreciation (Asset_ID, Depreciation_Year, Depreciation_Amount)
            SELECT Asset_ID, seq AS Depreciation_Year, Depreciable_Basis / Useful_Life_Years AS Depreciation_Amount
            FROM fixed_assets_list
            CROSS JOIN (SELECT 1 AS seq UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL
                        SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9 UNION ALL SELECT 10 UNION ALL 
                        SELECT 11 UNION ALL SELECT 12 UNION ALL SELECT 13 UNION ALL SELECT 14 UNION ALL SELECT 15 UNION ALL 
                        SELECT 16 UNION ALL SELECT 17 UNION ALL SELECT 18 UNION ALL SELECT 19 UNION ALL SELECT 20) y
            WHERE Depreciation_Method = 'Straight Line' AND seq <= Useful_Life_Years;
        ''')

    # Update Accumulated_Depreciation and Book_Value columns in macrs_depreciation table
    c.execute('''
        UPDATE macrs_depreciation AS md
        SET Accumulated_Depreciation = (
            SELECT SUM(Depreciation_Amount)
            FROM macrs_depreciation
            WHERE Asset_ID = md.Asset_ID AND Depreciation_Year <= md.Depreciation_Year
        ),
        Book_Value = (
            SELECT Acquisition_Cost - COALESCE(SUM(Depreciation_Amount), 0)
            FROM macrs_depreciation
            JOIN fixed_assets_list ON macrs_depreciation.Asset_ID = fixed_assets_list.Asset_ID
            WHERE macrs_depreciation.Asset_ID = md.Asset_ID AND Depreciation_Year <= md.Depreciation_Year
        )
        WHERE EXISTS (
            SELECT 1
            FROM fixed_assets_list
            WHERE Asset_ID = md.Asset_ID
        );
    ''')

    # Create final_depreciation table
    c.execute('DROP TABLE IF EXISTS final_depreciation;')
    c.execute('''
        CREATE TABLE final_depreciation AS
        SELECT a.Asset_ID, a.Asset_Class, a.Acquisition_Cost, a.Depreciable_Basis, a.Useful_Life_Years, 
               a.Depreciation_Method, MAX(md.Accumulated_Depreciation) AS Final_Accumulated_Depreciation,
               MIN(md.Book_Value) AS Final_Book_Value
        FROM macrs_depreciation md
        JOIN fixed_assets_list a ON md.Asset_ID = a.Asset_ID
        GROUP BY a.Asset_ID, a.Asset_Class, a.Acquisition_Cost, a.Depreciable_Basis, a.Useful_Life_Years, a.Depreciation_Method
        ORDER BY a.Asset_ID;
    ''')

    conn.commit()

# Streamlit app
st.title('Fixed Asset Depreciation Calculator')

# Option to select file type
file_type = st.radio("Select input file type:", ('CSV file', 'Sample data'))

if file_type == 'CSV file':
    uploaded_file = st.file_uploader("Choose a .csv file", type="csv")

    if uploaded_file is not None:
        # Preview sample data
        df = pd.read_csv(uploaded_file)
        st.write("Sample Data Preview:")
        st.write(df.head())

        # Select depreciation method
        depreciation_method = st.selectbox("Select Depreciation Method:", ['Double Declining Balance', 'Straight Line'])

        if st.button('Start'):
            # Process the uploaded CSV file
            result_df = process_fixed_assets(df, depreciation_method)
            
            # Display results
            st.write("Depreciation Calculation Results:")
            st.write(result_df)

elif file_type == 'Sample data':
    sample_files = {
        'Sample Data 1': 'db/data/sample1.csv'
        # 'Sample Data 2': 'db/data/sample2.csv'
    }
    selected_sample = st.selectbox("Select Sample Data:", list(sample_files.keys()))
    df = pd.read_csv(sample_files[selected_sample])
    
    # Preview sample data
    st.write("Sample Data Preview:")
    st.write(df.head())

    # Select depreciation method
    depreciation_method = st.selectbox("Select Depreciation Method:", ['Double Declining Balance', 'Straight Line'])

    if st.button('Start'):
        # Process the sample data
        result_df = process_fixed_assets(df, depreciation_method)
        
        # Display results
        st.write("Depreciation Calculation Results:")
        st.write(result_df)


# this above CODE IS DIFFRENT ONE 

