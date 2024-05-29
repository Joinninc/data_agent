  
-- first make tables and insert data into them 
-- tables :  
-- fixed-assets-list
-- Table B-1-Table-of-Class-Lives-and-Recovery-Periods
-- Table-A-1-Half-Year Convention
-- Table-A-2-Mid-Quarter-Convention




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

-- Check the updated macrs_depreciation table
SELECT *
FROM macrs_depreciation
ORDER BY Asset_ID;

   
   