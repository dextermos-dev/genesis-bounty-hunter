import csv, io, os

repo_root = "scratch/chain-love"
sdks_path = os.path.join(repo_root, "references/offers/sdks.csv")
base_sdks_path = os.path.join(repo_root, "listings/specific-networks/base/sdks.csv")

# 1. Format the row for references/offers/sdks.csv
fields = [
    'zerodev-sdk',
    'ZeroDev',
    'ZeroDev SDK',
    '["[Docs](https://docs.zerodev.app/)","[GitHub](https://github.com/zerodevapp/kernel)"]',
    'SDK',
    'TypeScript',
    '["Smart Accounts","ERC-4337","Base","Account Abstraction","Session Keys"]',
    'Modular smart account SDK supporting ERC-4337, session keys, gas sponsorship, and chain abstraction on Base and EVM networks.',
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

inserted = False
new_sdks_lines = []
target_slug = "zerodev-sdk"

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
    'zerodev-sdk',
    '',
    '!offer:zerodev-sdk',
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
