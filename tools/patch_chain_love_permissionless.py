import csv, io, os

repo_root = "scratch/chain-love"
sdks_path = os.path.join(repo_root, "references/offers/sdks.csv")
base_sdks_path = os.path.join(repo_root, "listings/specific-networks/base/sdks.csv")

# 1. Format the row for references/offers/sdks.csv
fields = [
    'permissionless',
    'Pimlico',
    'Permissionless.js',
    '["[Docs](https://docs.pimlico.io/permissionless)","[GitHub](https://github.com/pimlicolabs/permissionless.js)"]',
    'Library',
    'TypeScript',
    '["ERC-4337","Smart Accounts","Base","Account Abstraction","TypeScript"]',
    'TypeScript library built on Viem to build with ERC-4337 smart accounts, bundlers, paymasters, and ERC-7579 modular accounts across Base and EVM networks.',
    'Public',
    '',
    '$0',
    'FALSE',
    'FALSE',
    '',
    '',
    '',
    '',
    'MIT'
]

out = io.StringIO()
writer = csv.writer(out, lineterminator='')
writer.writerow(fields)
new_row_sdks = out.getvalue()

# Verify columns
row_check = next(csv.reader(io.StringIO(new_row_sdks)))
assert len(row_check) == 18, f"Expected 18 cols, got {len(row_check)}"
assert row_check[10] == "$0"

# Read existing references/offers/sdks.csv
with open(sdks_path, 'r', encoding='utf-8') as f:
    sdks_lines = f.readlines()

# Find insertion position alphabetically by slug
inserted = False
new_sdks_lines = []
target_slug = "permissionless"

for line in sdks_lines:
    if not inserted and line.strip():
        slug = line.split(',')[0].strip()
        if slug != 'slug' and slug > target_slug:
            new_sdks_lines.append(new_row_sdks + '\n')
            inserted = True
    new_sdks_lines.append(line)

if not inserted:
    new_sdks_lines.append(new_row_sdks + '\n')

with open(sdks_path, 'w', encoding='utf-8') as f:
    f.writelines(new_sdks_lines)

print("Updated references/offers/sdks.csv successfully.")

# 2. Format row for listings/specific-networks/base/sdks.csv
# Format: slug,,!offer:slug,,,,,,,,,,,,,,, (18 columns)
base_fields = [
    'permissionless',
    '',
    '!offer:permissionless',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    ''
]
out_base = io.StringIO()
writer_base = csv.writer(out_base, lineterminator='')
writer_base.writerow(base_fields)
new_row_base = out_base.getvalue()

base_row_check = next(csv.reader(io.StringIO(new_row_base)))
assert len(base_row_check) == 18, f"Expected 18 cols, got {len(base_row_check)}"

with open(base_sdks_path, 'r', encoding='utf-8') as f:
    base_lines = f.readlines()

inserted_base = False
new_base_lines = []

for line in base_lines:
    if not inserted_base and line.strip():
        slug = line.split(',')[0].strip()
        if slug != 'slug' and slug > target_slug:
            new_base_lines.append(new_row_base + '\n')
            inserted_base = True
    new_base_lines.append(line)

if not inserted_base:
    new_base_lines.append(new_row_base + '\n')

with open(base_sdks_path, 'w', encoding='utf-8') as f:
    f.writelines(new_base_lines)

print("Updated listings/specific-networks/base/sdks.csv successfully.")
