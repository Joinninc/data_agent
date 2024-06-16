import sqlite3
import pandas as pd

def create_tables(conn):
    c = conn.cursor()
    
    # # Create fixed_assets_list table if it doesn't exist
    # c.execute('''
    #     CREATE TABLE IF NOT EXISTS fixed_assets_list (
    #         Asset_ID INT PRIMARY KEY,
    #         Asset_Class TEXT,
    #         Acquisition_Cost DECIMAL(10, 2),
    #         Depreciable_Basis DECIMAL(10, 2),
    #         Useful_Life_years INT,
    #         Depreciation_Method TEXT
    #     )
    # ''')


#     c.execute('''
#     CREATE TABLE IF NOT EXISTS fixed_assets_list (
#         Asset_ID INT PRIMARY KEY,
#         Asset_Class TEXT,
#         Asset_Description TEXT,
#         Acquisition_Cost DECIMAL(10, 2),
#         Acquisition_Date DATE,
#         Useful_Life_years INT,
#         Salvage_Value DECIMAL(10, 2),
#         Depreciation_Method TEXT,
#         Depreciable_Basis DECIMAL(10, 2),
#         Annual_Depreciation DECIMAL(10, 2)
#     )
# ''')


    # Drop the fixed_assets_list table if it exists
    c.execute('DROP TABLE IF EXISTS fixed_assets_list;')

    # Create fixed_assets_list table with updated schema
    c.execute('''
        CREATE TABLE IF NOT EXISTS fixed_assets_list (
            Asset_ID INT PRIMARY KEY,
            Asset_Class TEXT,
            Asset_Description TEXT,
            Acquisition_Cost DECIMAL(10, 2),
            Acquisition_Date DATE,  
            Useful_Life_Years INT,
            Salvage_Value DECIMAL(10, 2),
            Depreciation_Method TEXT,
            Depreciable_Basis DECIMAL(10, 2)
            );
           ''')

# Annual_Depreciation DECIMAL(10, 2)


# Drop the Table-A-2-Mid-Quarter-Convention table if it exists
    c.execute('''
    DROP TABLE IF EXISTS "macrs_depreciation";
''')

    # Create macrs_depreciation table if it doesn't exist
    c.execute('''
        CREATE TABLE macrs_depreciation (
            Asset_ID INT,
            Depreciation_Year INT,
            Depreciation_Amount DECIMAL(10, 2),
            Accumulated_Depreciation DECIMAL(18, 2),
            Book_Value DECIMAL(18, 2),
            FOREIGN KEY (Asset_ID) REFERENCES fixed_assets_list(Asset_ID)
        )
    ''')




    c.execute('''
    DROP TABLE IF EXISTS "Table B-1-Table-of-Class-Lives-and-Recovery-Periods";
''')


    # Create Table B-1-Table-of-Class-Lives-and-Recovery-Periods if it doesn't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS "Table B-1-Table-of-Class-Lives-and-Recovery-Periods" (
            Asset_Class TEXT,
            GDS_MACRS_Recovery_Period_years INT
        )
    ''')

    # Drop the Table-A-1-Half-Year-Convention table if it exists
    c.execute('''
    DROP TABLE IF EXISTS "Table-A-1-Half-Year-Convention";
''')


    # Create Table-A-1-Half-Year Convention if it doesn't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS "Table-A-1-Half-Year Convention" (
            Year INT,
            ThreeYear DECIMAL(10, 2),
            FiveYear DECIMAL(10, 2),
            SevenYear DECIMAL(10, 2),
            TenYear DECIMAL(10, 2),
            FifteenYear DECIMAL(10, 2),
            TwentyYear DECIMAL(10, 2)
        )
    ''')


# Drop the Table-A-2-Mid-Quarter-Convention table if it exists
    c.execute('''
    DROP TABLE IF EXISTS "Table-A-2-Mid-Quarter-Convention";
''')


    # Create Table-A-2-Mid-Quarter-Convention if it doesn't exist
    c.execute('''
        CREATE TABLE "Table-A-2-Mid-Quarter-Convention" (
            Year INT,
            ThreeYear DECIMAL(10, 2),
            FiveYear DECIMAL(10, 2),
            SevenYear DECIMAL(10, 2),
            TenYear DECIMAL(10, 2),
            FifteenYear DECIMAL(10, 2),
            TwentyYear DECIMAL(10, 2)
        )
    ''')
    
    conn.commit()

def populate_tables(conn):
    # Read the data from CSV files
    table_b_1_class_lives = pd.read_csv('db/data/table_b_1_class_lives.csv')
    table_a_1_half_year = pd.read_csv('db/data/table_a_1_half_year.csv')
    table_a_2_mid_quarter = pd.read_csv('db/data/table_a_2_mid_quarter.csv')

    # Insert data into Table B-1-Table-of-Class-Lives-and-Recovery-Periods
    table_b_1_class_lives.to_sql('Table B-1-Table-of-Class-Lives-and-Recovery-Periods', conn, if_exists='replace', index=False)

    # Insert data into Table-A-1-Half-Year Convention
    table_a_1_half_year.to_sql('Table-A-1-Half-Year Convention', conn, if_exists='replace', index=False)

    # Insert data into Table-A-2-Mid-Quarter-Convention
    table_a_2_mid_quarter.to_sql('Table-A-2-Mid-Quarter-Convention', conn, if_exists='replace', index=False)

    conn.commit()

def initialize_database(db_path):
    conn = sqlite3.connect(db_path)
    create_tables(conn)
    populate_tables(conn)
    conn.close()
