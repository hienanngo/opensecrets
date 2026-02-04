import pandas as pd
import numpy as np

# Read the CSV file
df = pd.read_csv('every_race.csv')

# Clean and convert Netreceipts and ECOH to numeric
df['Netreceipts'] = df['Netreceipts'].astype(str).str.replace(',', '').astype(float)
df['ECOH'] = df['ECOH'].astype(str).str.replace(',', '').astype(float)


# Filter OUT territories (keep only the 50 states)
#territories = ['AS 001', 'DC 001', 'GU 001', 'VI 001', 'MP 001', 'PR 001']  # Include all possible territories
# df = df[~df['DISTRICT'].isin(territories)]


# Filter for only Democrats and Republicans
df = df[df['PARTY'].isin(['D', 'R'])]

# Count parties per district
parties_per_district = df.groupby('DISTRICT')['PARTY'].apply(set).reset_index()
parties_per_district['party_count'] = parties_per_district['PARTY'].apply(len)

# 1. Count districts with only Democrats
dem_only = parties_per_district[parties_per_district['PARTY'].apply(lambda x: x == {'D'})]
print(f"1. Races where Democrats are running unchallenged: {len(dem_only)}")

# 2. Count districts with only Republicans
rep_only = parties_per_district[parties_per_district['PARTY'].apply(lambda x: x == {'R'})]
print(f"2. Races where Republicans are running unchallenged: {len(rep_only)}")

# 3. Count districts with both parties
both_parties = parties_per_district[parties_per_district['PARTY'].apply(lambda x: x == {'D', 'R'})]
print(f"3. Races with candidates from both parties: {len(both_parties)}")


# 4. For races with both parties, determine who leads in net receipts
print(f"\n4. In races with both parties:")

# Get districts with both parties
districts_with_both = both_parties['DISTRICT'].tolist()
contested_df = df[df['DISTRICT'].isin(districts_with_both)]

# 4a. Compare TOTAL fundraising by party in each district
print(f"\n   a. Based on TOTAL party fundraising per district:")

# Sum all candidates by party for each district
total_by_party = contested_df.groupby(['DISTRICT', 'PARTY'])['Netreceipts'].sum().unstack(fill_value=0)

# Count who leads when summing all candidates
dem_total_leads = (total_by_party['D'] > total_by_party['R']).sum()
rep_total_leads = (total_by_party['R'] > total_by_party['D']).sum()
total_tied = (total_by_party['D'] == total_by_party['R']).sum()

print(f"      Democrats lead (total party fundraising): {dem_total_leads}")
print(f"      Republicans lead (total party fundraising): {rep_total_leads}")
if total_tied > 0:
    print(f"      (Tied: {total_tied})")

# 4b. Compare TOP candidate from each party
print(f"\n   b. Based on TOP candidate from each party:")

# Get top candidate by party for each district
top_candidates = contested_df.loc[contested_df.groupby(['DISTRICT', 'PARTY'])['Netreceipts'].idxmax()]

# Pivot to compare top candidates
comparison = top_candidates.pivot_table(
    index='DISTRICT',
    columns='PARTY',
    values='Netreceipts',
    aggfunc='first'
)

# Count who leads
dem_top_leads = (comparison['D'] > comparison['R']).sum()
rep_top_leads = (comparison['R'] > comparison['D']).sum()
top_tied = (comparison['D'] == comparison['R']).sum()

print(f"      Democrats lead (top candidate): {dem_top_leads}")
print(f"      Republicans lead (top candidate): {rep_top_leads}")
if top_tied > 0:
    print(f"      (Tied: {top_tied})")


# 5. Calculate total Net Receipts and ECOH by party
print(f"\n5. Total fundraising across all candidates:")

# Group by party and sum
party_totals = df.groupby('PARTY').agg({
    'Netreceipts': 'sum',
    'ECOH': 'sum'
}).reset_index()

for _, row in party_totals.iterrows():
    party = 'Democrats' if row['PARTY'] == 'D' else 'Republicans'
    print(f"   {party}:")
    print(f"      Total Net Receipts: ${row['Netreceipts']:,.2f}")
    print(f"      Total Cash on Hand: ${row['ECOH']:,.2f}")

# Calculate the difference
if len(party_totals) == 2:
    dem_receipts = party_totals[party_totals['PARTY'] == 'D']['Netreceipts'].values[0]
    rep_receipts = party_totals[party_totals['PARTY'] == 'R']['Netreceipts'].values[0]
    dem_ecoh = party_totals[party_totals['PARTY'] == 'D']['ECOH'].values[0]
    rep_ecoh = party_totals[party_totals['PARTY'] == 'R']['ECOH'].values[0]
    
    print(f"\n   Difference:")
    print(f"      Net Receipts: ${abs(dem_receipts - rep_receipts):,.2f} ({('Democrats' if dem_receipts > rep_receipts else 'Republicans')} ahead)")
    print(f"      Cash on Hand: ${abs(dem_ecoh - rep_ecoh):,.2f} ({('Democrats' if dem_ecoh > rep_ecoh else 'Republicans')} ahead)")



# 6. Distribution analysis
print(f"\n6. Distribution of Net Receipts by Party:")

# Separate Democrats and Republicans
dem_df = df[df['PARTY'] == 'D']
rep_df = df[df['PARTY'] == 'R']

# Calculate distribution statistics
def calculate_distribution_stats(party_df, party_name):
    receipts = party_df['Netreceipts']
    total_receipts = receipts.sum()
    
    print(f"\n   {party_name}:")
    print(f"      Total candidates: {len(receipts)}")
    print(f"      Mean: ${receipts.mean():,.2f}")
    print(f"      Median: ${receipts.median():,.2f}")
    print(f"      Std Dev: ${receipts.std():,.2f}")
    print(f"      Min: ${receipts.min():,.2f}")
    print(f"      Max: ${receipts.max():,.2f}")
    
    # Percentiles
    print(f"      25th percentile: ${receipts.quantile(0.25):,.2f}")
    print(f"      75th percentile: ${receipts.quantile(0.75):,.2f}")
    
    # Gini coefficient (measure of inequality, 0 = perfect equality, 1 = perfect inequality)
    sorted_receipts = np.sort(receipts)
    n = len(sorted_receipts)
    cumsum = np.cumsum(sorted_receipts)
    gini = (2 * np.sum((np.arange(1, n+1)) * sorted_receipts)) / (n * np.sum(sorted_receipts)) - (n + 1) / n
    print(f"      Gini coefficient: {gini:.4f} (0=perfect equality, 1=perfect inequality)")
    
    # Top 5 candidates
    top_5_candidates = receipts.nlargest(5)
    top_5_amount = top_5_candidates.sum()
    top_5_pct = (top_5_amount / total_receipts) * 100
    print(f"      Top 5 candidates hold: ${top_5_amount:,.2f} ({top_5_pct:.1f}% of total funds)")
    
    # Top 10 candidates
    top_10_candidates = receipts.nlargest(10)
    top_10_amount = top_10_candidates.sum()
    top_10_pct = (top_10_amount / total_receipts) * 100
    print(f"      Top 10 candidates hold: ${top_10_amount:,.2f} ({top_10_pct:.1f}% of total funds)")
    
    # Concentration: % of money held by top 5% of candidates
    top_5_pct_count = max(1, int(len(receipts) * 0.05))  # At least 1 candidate
    top_5_pct_candidates = receipts.nlargest(top_5_pct_count)
    concentration_5_pct = (top_5_pct_candidates.sum() / total_receipts) * 100
    print(f"      Top 5% of candidates ({top_5_pct_count} candidates) hold: {concentration_5_pct:.1f}% of total funds")
    
    # Concentration: % of money held by top 10% of candidates
    top_10_pct_count = max(1, int(len(receipts) * 0.1))  # At least 1 candidate
    top_10_pct_candidates = receipts.nlargest(top_10_pct_count)
    concentration_10_pct = (top_10_pct_candidates.sum() / total_receipts) * 100
    print(f"      Top 10% of candidates ({top_10_pct_count} candidates) hold: {concentration_10_pct:.1f}% of total funds")
    
    # Concentration: % of money held by top candidate
    top_1 = receipts.max()
    top_1_pct = (top_1 / total_receipts) * 100
    print(f"      Top candidate holds: ${top_1:,.2f} ({top_1_pct:.1f}% of total funds)")

calculate_distribution_stats(dem_df, "Democrats")
calculate_distribution_stats(rep_df, "Republicans")

# Summary comparison
print(f"\n   Summary:")
dem_gini = (2 * np.sum((np.arange(1, len(dem_df)+1)) * np.sort(dem_df['Netreceipts']))) / (len(dem_df) * np.sum(dem_df['Netreceipts'])) - (len(dem_df) + 1) / len(dem_df)
rep_gini = (2 * np.sum((np.arange(1, len(rep_df)+1)) * np.sort(rep_df['Netreceipts']))) / (len(rep_df) * np.sum(rep_df['Netreceipts'])) - (len(rep_df) + 1) / len(rep_df)

if dem_gini < rep_gini:
    print(f"      Democrats have MORE even distribution (lower Gini: {dem_gini:.4f} vs {rep_gini:.4f})")
else:
    print(f"      Republicans have MORE even distribution (lower Gini: {rep_gini:.4f} vs {dem_gini:.4f})")