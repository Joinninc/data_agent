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
    for _, asset in assets.iterrows():
        asset_id = asset['Asset ID']
        asset_class = asset['Asset Class']
        acquisition_cost = asset['Acquisition Cost']
        acquisition_date = asset['Acquisition Date']
        useful_life = asset['Useful Life (years)']
        salvage_value = asset['Salvage Value']
        depreciation_method = asset['Depreciation Method']

        if asset_class in depreciation_tables:
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
        else:
            print(f"No depreciation table found for asset class '{asset_class}'. Skipping asset.")

    return results

# Load depreciation tables
table_a1 = load_depreciation_table('Table-A-1-Half-Year Convention.csv')

# Load fixed assets list
fixed_assets_list = pd.read_csv('fixed-assets-list.csv')

# Calculate depreciation for fixed assets
results = calculate_depreciation_for_assets(fixed_assets_list, {'00.11': table_a1})

# Display results
for result in results:
    print(result)
