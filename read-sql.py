import re

sql = open('/Users/carl/code/Carl and Sally/carlandsally.sql', 'r', encoding='utf-8', errors='replace').read()

print(f"File size: {len(sql):,} chars")

# Find the posts table insert blocks
blocks = re.findall(r"INSERT INTO `wp_pylpxs_posts`.*?;\n", sql, re.DOTALL)
print(f"Found {len(blocks)} INSERT blocks for posts table")

# Extract individual rows more carefully
# Each row starts with ( and contains the post data
# Column order in WP: ID, post_author, post_date, post_date_gmt, post_content, post_title, ...
all_rows = []
for block in blocks:
    # Find all value tuples
    # Use a simpler approach - split on known patterns
    content = block[block.find('VALUES'):]
    # Find each row
    rows = re.split(r'\),\s*\(', content)
    for row in rows:
        row = row.strip().strip('(').strip(')')
        all_rows.append(row[:100])

print(f"\nFirst 5 raw rows (first 100 chars each):")
for r in all_rows[:5]:
    print(repr(r))

# Try to find post titles and content using a different approach
# Look for post_status = 'publish'
published = re.findall(r"'publish'", sql)
print(f"\nOccurrences of 'publish': {len(published)}")

# Show a chunk of the posts insert to understand structure
if blocks:
    print(f"\nFirst 500 chars of first INSERT block:")
    print(blocks[0][:500])
