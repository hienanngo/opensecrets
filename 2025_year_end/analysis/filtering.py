import pandas as pd

# Read the CSV file
df = pd.read_csv('filtered_races.csv')

# Clean and convert Netreceipts to numeric
df['Netreceipts'] = df['Netreceipts'].str.replace(',', '').astype(float)

# Filter for Democrats and Republicans only
df = df[df['PARTY'].isin(['D', 'R'])]

# Get top candidate by party for each district
top_candidates = df.loc[df.groupby(['DISTRICT', 'PARTY'])['Netreceipts'].idxmax()]

# Calculate the absolute difference for each district
district_diffs = top_candidates.groupby('DISTRICT').apply(
    lambda x: abs(x[x['PARTY'] == 'D']['Netreceipts'].values[0] - x[x['PARTY'] == 'R']['Netreceipts'].values[0])
    if len(x) == 2 else 0
).to_dict()

# Add the difference column
top_candidates['Absolute difference'] = top_candidates['DISTRICT'].map(district_diffs)

# Reformat district names (e.g., "NY 017" -> "NY-17")
def reformat_district(district):
    parts = district.split()
    if len(parts) == 2:
        state, number = parts
        # Remove leading zeros from number
        number = str(int(number))
        return f"{state}-{number}"
    return district

top_candidates['District'] = top_candidates['DISTRICT'].apply(reformat_district)

# Fix name order (Last, First -> First Last) and add asterisk for incumbents
def format_name(name, incumbency):
    if pd.isna(name):
        return name
    # Split by comma and reverse
    parts = [part.strip() for part in name.split(',')]
    if len(parts) == 2:
        formatted_name = f"{parts[1]} {parts[0]}"
    else:
        formatted_name = name
    
    # Add asterisk if incumbent
    if incumbency == 'Incumbent':
        formatted_name += '*'
    
    return formatted_name

top_candidates['Candidate'] = top_candidates.apply(
    lambda row: format_name(row['NAME'], row['INCUMBENCY']), axis=1
)

# Select and rename columns
result = top_candidates[['District', 'Candidate', 'PARTY', 'Netreceipts', 'INCUMBENCY', 'Previously held by', 'Absolute difference']]
result.columns = ['District', 'Candidate', 'Party', 'Net receipts', 'INCUMBENCY', 'Previously held by', 'Absolute difference']

# Sort by "Previously held by" first, then by "Absolute difference"
result = result.sort_values(['Previously held by', 'Absolute difference'], ascending=[True, True])

# Display results
print(result)

# Save to CSV
result.to_csv('top_by_district_attempt.csv', index=False)
print("\n\nResults saved to 'top_by_district_attempt.csv'")