import pandas as pd

def load_depreciation_table(file_path):
    return pd.read_csv(file_path)

def calculate_macrs_depreciation(acquisition_cost, acquisition_date, useful_life, salvage_value, depreciation_method, depreciation_table):
    # Calculate the depreciable basis
    depreciable_basis = acquisition_cost - salvage_value

    # Get the year since acquisition
    current_year = pd.Timestamp.today().year - pd.Timestamp(acquisition_date).year + 1
    if current_year < 1:
        current_year = 1

    # Get the depreciation rate for the given useful life
    depreciation_rate = float(depreciation_table.loc[current_year - 1, str(useful_life) + '-year'].strip('%')) / 100

    # Calculate the annual depreciation
    if depreciation_method.lower() == 'straight line':
        annual_depreciation = depreciable_basis / useful_life
    elif depreciation_method.lower() == 'db':
        annual_depreciation = depreciable_basis * depreciation_rate * 2

    # Calculate the accumulated depreciation and book value
    accumulated_depreciation = annual_depreciation * (current_year - 1)
    book_value = acquisition_cost - accumulated_depreciation

    # Return the results
    return {
        'Depreciable Basis': depreciable_basis,
        'Annual Depreciation': annual_depreciation,
        'Accumulated Depreciation': accumulated_depreciation,
        'Book Value': book_value
    }

def calculate_depreciation_for_assets(assets, depreciation_tables):
    results = []
    for asset in assets:
        asset_id = asset['Asset ID']
        asset_class = asset['Asset Class']
        acquisition_cost = asset['Acquisition Cost']
        acquisition_date = asset['Acquisition Date']
        useful_life = asset['Useful Life (years)']
        salvage_value = asset['Salvage Value']
        depreciation_method = asset['Depreciation Method']

        depreciation_table = depreciation_tables[asset_class]

        depreciation_results = calculate_macrs_depreciation(acquisition_cost, acquisition_date, useful_life, salvage_value, depreciation_method, depreciation_table)

        result = {
            'Asset ID': asset_id,
            'Asset Class': asset_class,
            'Acquisition Cost': acquisition_cost,
            'Acquisition Date': acquisition_date,
            'Useful Life (years)': useful_life,
            'Salvage Value': salvage_value,
            'Depreciation Method': depreciation_method,
            **depreciation_results
        }

        results.append(result)

    return results

# Load depreciation tables
table_a1 = load_depreciation_table('Table-A-1-Half-Year Convention.csv')

# Define assets
assets = [
    {
        'Asset ID': 1,
        'Asset Class': '00.11',
        'Acquisition Cost': 5000,
        'Acquisition Date': '2020-01-15',
        'Useful Life (years)': 7,
        'Salvage Value': 500,
        'Depreciation Method': 'Straight Line'
    },
    {
        'Asset ID': 2,
        'Asset Class': '00.11',
        'Acquisition Cost': 1200,
        'Acquisition Date': '2023-01-20',
        'Useful Life (years)': 7,
        'Salvage Value': 120,
        'Depreciation Method': 'Straight Line'
    }
]

# Calculate depreciation for assets
results = calculate_depreciation_for_assets(assets, {'00.11': table_a1})

# Display results
for result in results:
    print(result)
