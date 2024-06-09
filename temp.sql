/*
-- This SQL script creates tables, inserts data into them, and performs various operations related to depreciation calculations and asset management.
-- Below are the details of each section of the script:

-- Tables Created:
1. fixed-assets-list
2. Table B-1-Table-of-Class-Lives-and-Recovery-Periods
3. Table-A-1-Half-Year Convention
4. Table-A-2-Mid-Quarter-Convention
5. macrs_depreciation

-- Columns in macrs_depreciation table:
1. Asset_ID (foreign key referencing fixed-assets-list)
2. Depreciation_Year
3. Depreciation_Amount
4. Accumulated_Depreciation (added later)
5. Book_Value (added later)

-- SQL Operations:
1. Inserts MACRS depreciation data using Half-Year Convention into macrs_depreciation table.
2. Inserts MACRS depreciation data using Mid-Quarter Convention into macrs_depreciation table.
3. Inserts Straight Line depreciation data into macrs_depreciation table.
4. Adds Accumulated_Depreciation column to macrs_depreciation table.
5. Adds Book_Value column to macrs_depreciation table.
6. Updates Accumulated_Depreciation and Book_Value columns in macrs_depreciation table.
7. Consolidates output with all columns from fixed_assets_list table and removes Total_Depreciation_Amount.

-- Joins and Relationships:
1. For MACRS depreciation data insertion:
   - fixed-assets-list is joined with Table B-1-Table-of-Class-Lives-and-Recovery-Periods on Asset_Class.
   - The result is cross joined with Half-Year Convention or Mid-Quarter-Convention tables.
2. For Straight Line depreciation data insertion:
   - No explicit join, but data from fixed-assets-list is used directly.

-- Columns Used in Joins:
1. fixed-assets-list: Asset_ID, Asset_Class, Depreciable_Basis, Depreciation_Method, Useful_Life_Years.
2. Table B-1-Table-of-Class-Lives-and-Recovery-Periods: AssetClass, GDSRecoveryPeriod.
3. Half-Year Convention and Mid-Quarter Convention tables: Various columns representing depreciation rates for different years.

-- Operations on macrs_depreciation table:
1. Insertions: Asset_ID, Depreciation_Year, Depreciation_Amount.
2. Updates: Accumulated_Depreciation, Book_Value.
3. Final Output: Asset_ID, Asset_Class, Acquisition_Cost, Depreciable_Basis, Useful_Life_Years, Depreciation_Method, Final_Accumulated_Depreciation, Final_Book_Value.

-- Note: The script assumes that the tables and necessary data are already present in the database.
*/


--make macrs_depreciation table    
   
   CREATE TABLE macrs_depreciation (
    Asset_ID INT,
    Depreciation_Year INT,
    Depreciation_Amount DECIMAL(10, 2),
--    PRIMARY KEY (Asset_ID),
    FOREIGN KEY (Asset_ID) REFERENCES fixed-assets-list(Asset_ID)
);

   

  
-- fixed primary key constraint    
   
 -- Insert MACRS depreciation data using Half-Year Convention
INSERT INTO macrs_depreciation (Asset_ID, Depreciation_Year, Depreciation_Amount)
SELECT 
    a.Asset_ID, 
    y.seq AS Depreciation_Year, 
    a.Depreciable_Basis * 
    (
        CASE 
            WHEN t.GDSRecoveryPeriod = 3 THEN d.ThreeYear
            WHEN t.GDSRecoveryPeriod = 5 THEN d.FiveYear
            WHEN t.GDSRecoveryPeriod = 7 THEN d.SevenYear
            WHEN t.GDSRecoveryPeriod = 10 THEN d.TenYear
            WHEN t.GDSRecoveryPeriod = 15 THEN d.FifteenYear
            WHEN t.GDSRecoveryPeriod = 20 THEN d.TwentyYear
        END / 100
    ) AS Depreciation_Amount
FROM 
    fixed-assets-list a
JOIN 
    Table B-1-Table-of-Class-Lives-and-Recovery-Periods  t
ON 
    a.Asset_Class = t."AssetClass"
CROSS JOIN 
    (SELECT 1 AS seq UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9 UNION ALL SELECT 10 UNION ALL SELECT 11 UNION ALL SELECT 12 UNION ALL SELECT 13 UNION ALL SELECT 14 UNION ALL SELECT 15 UNION ALL SELECT 16 UNION ALL SELECT 17 UNION ALL SELECT 18 UNION ALL SELECT 19 UNION ALL SELECT 20) y
JOIN 
    Table-A-1-Half-Year Convention d
ON 
    y.seq = d.Year
WHERE 
    a.Depreciation_Method = 'Double Declining Balance'
    AND y.seq <= t.GDSRecoveryPeriod;
   



   
   
  -- Insert MACRS depreciation data using Mid-Quarter Convention
INSERT INTO macrs_depreciation (Asset_ID, Depreciation_Year, Depreciation_Amount)
SELECT 
    a.Asset_ID, 
    y.seq AS Depreciation_Year, 
    a.Depreciable_Basis * 
    (
        CASE 
            WHEN t.GDSRecoveryPeriod = 3 THEN d.ThreeYear
            WHEN t.GDSRecoveryPeriod = 5 THEN d.FiveYear
            WHEN t.GDSRecoveryPeriod = 7 THEN d.SevenYear
            WHEN t.GDSRecoveryPeriod = 10 THEN d.TenYear
            WHEN t.GDSRecoveryPeriod = 15 THEN d.FifteenYear
            WHEN t.GDSRecoveryPeriod = 20 THEN d.TwentyYear
        END / 100
    ) AS Depreciation_Amount
FROM 
    fixed-assets-list a
JOIN 
    Table B-1-Table-of-Class-Lives-and-Recovery-Periods  t
ON 
    a.Asset_Class = t."AssetClass"
CROSS JOIN 
    (SELECT 1 AS seq UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9 UNION ALL SELECT 10 UNION ALL SELECT 11 UNION ALL SELECT 12 UNION ALL SELECT 13 UNION ALL SELECT 14 UNION ALL SELECT 15 UNION ALL SELECT 16 UNION ALL SELECT 17 UNION ALL SELECT 18 UNION ALL SELECT 19 UNION ALL SELECT 20) y
JOIN 
    "Table-A-2-Mid-Quarter-Convention" d
ON 
    y.seq = d.Year
WHERE 
    a.Depreciation_Method = 'Double Declining Balance'
    AND y.seq <= t.GDSRecoveryPeriod;
 


   
   
   
   
  
 -- Insert Straight Line depreciation data
INSERT INTO macrs_depreciation (Asset_ID, Depreciation_Year, Depreciation_Amount)
SELECT 
    Asset_ID, 
    seq AS Depreciation_Year, 
    Depreciable_Basis / Useful_Life_Years AS Depreciation_Amount
FROM 
    fixed-assets-list
CROSS JOIN 
    (SELECT 1 AS seq UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9 UNION ALL SELECT 10 UNION ALL SELECT 11 UNION ALL SELECT 12 UNION ALL SELECT 13 UNION ALL SELECT 14 UNION ALL SELECT 15 UNION ALL SELECT 16 UNION ALL SELECT 17 UNION ALL SELECT 18 UNION ALL SELECT 19 UNION ALL SELECT 20) y
WHERE 
    Depreciation_Method = 'Straight Line'
    AND seq <= Useful_Life_Years;  
   
   
   
   
   
   
   
   
   
   
   
   -- Add Accumulated_Depreciation column to macrs_depreciation table
ALTER TABLE macrs_depreciation
ADD COLUMN Accumulated_Depreciation DECIMAL(18, 2);

-- Add Book_Value column to macrs_depreciation table
ALTER TABLE macrs_depreciation
ADD COLUMN Book_Value DECIMAL(18, 2);

-- Update Accumulated_Depreciation and Book_Value columns in macrs_depreciation table
UPDATE macrs_depreciation AS md
SET 
    Accumulated_Depreciation = 
    (SELECT 
        SUM(Depreciation_Amount) 
    FROM 
        macrs_depreciation 
    WHERE 
        Asset_ID = md.Asset_ID AND Depreciation_Year <= md.Depreciation_Year),
    Book_Value = 
    (SELECT 
        (SELECT Acquisition_Cost FROM fixed-assets-list WHERE Asset_ID = md.Asset_ID) - 
        COALESCE(
            (SELECT 
                SUM(Depreciation_Amount) 
            FROM 
                macrs_depreciation 
            WHERE 
                Asset_ID = md.Asset_ID AND Depreciation_Year <= md.Depreciation_Year
            ),
            0)
    );

-- -- Check the updated macrs_depreciation table
-- SELECT *
-- FROM macrs_depreciation
-- ORDER BY Asset_ID;

   


 
   -- Consolidate output with all columns from fixed_assets_list table and remove Total_Depreciation_Amount
SELECT 
    a.Asset_ID,
    a.Asset_Class,
    a.Acquisition_Cost,
    a.Depreciable_Basis,
    a.Useful_Life_Years,
    a.Depreciation_Method,
    MAX(md.Accumulated_Depreciation) AS Final_Accumulated_Depreciation,
    MIN(md.Book_Value) AS Final_Book_Value
FROM 
    macrs_depreciation md
JOIN 
    assets a  
ON 
    md.Asset_ID = a.Asset_ID
GROUP BY 
    a.Asset_ID,
    a.Asset_Class,
    a.Acquisition_Cost,
    a.Depreciable_Basis,
    a.Useful_Life_Years,
    a.Depreciation_Method
ORDER BY 
    a.Asset_ID;

