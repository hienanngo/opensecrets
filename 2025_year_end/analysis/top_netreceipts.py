import pandas as pd

# Read the CSV file
df = pd.read_csv('filtered_races.csv')

# Clean and convert Netreceipts to numeric
df['Netreceipts'] = df['Netreceipts'].str.replace(',', '').astype(float)

# Filter for Democrats and Republicans only
df = df[df['PARTY'].isin(['D', 'R'])]

# Get top candidate by party for each district
top_candidates = df.loc[df.groupby(['DISTRICT', 'PARTY'])['Netreceipts'].idxmax()]

# Sort and display
top_candidates = top_candidates.sort_values(['DISTRICT', 'PARTY'])
print(top_candidates[['DISTRICT', 'NAME', 'PARTY', 'Netreceipts', 'INCUMBENCY', 'Previously held by']])

# Save to CSV
top_candidates[['DISTRICT', 'NAME', 'PARTY', 'Netreceipts', 'INCUMBENCY', 'Previously held by']].to_csv('top_by_district.csv', index=False)