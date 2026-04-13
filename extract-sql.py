import re, html, os

sql = open('/Users/carl/code/Carl and Sally/carlandsally.sql', 'r', encoding='utf-8', errors='replace').read()

print(f"File size: {len(sql):,} chars\n")

# Find all INSERT blocks for posts
blocks = re.findall(r"INSERT INTO `wp_pylpxs_posts`.*?;\n", sql, re.DOTALL)
print(f"Found {len(blocks)} INSERT blocks\n")

# Extract rows - WP column order:
# ID, post_author, post_date, post_date_gmt, post_content, post_title, post_excerpt,
# post_status, comment_status, ping_status, post_password, post_name, ...post_type...
posts = []
for block in blocks:
    # Split into individual rows by finding ),(
    # First get past VALUES
    val_start = block.find('VALUES\n') + 7
    content = block[val_start:]
    
    # Use a state machine to split rows properly
    rows_raw = []
    depth = 0
    current = []
    i = 0
    while i < len(content):
        c = content[i]
        if c == '(' and depth == 0:
            depth = 1
            current = []
        elif c == ')' and depth == 1:
            # Check it's not inside a string
            rows_raw.append(''.join(current))
            depth = 0
        elif depth == 1:
            current.append(c)
        i += 1
    
    for row in rows_raw:
        # Parse fields - split on commas but respect quoted strings
        fields = []
        in_quote = False
        escaped = False
        field = []
        for c in row:
            if escaped:
                field.append(c)
                escaped = False
            elif c == '\\':
                field.append(c)
                escaped = True
            elif c == "'" and not in_quote:
                in_quote = True
                field.append(c)
            elif c == "'" and in_quote:
                in_quote = False
                field.append(c)
            elif c == ',' and not in_quote:
                fields.append(''.join(field).strip())
                field = []
            else:
                field.append(c)
        fields.append(''.join(field).strip())
        
        if len(fields) >= 8:
            post_id = fields[0]
            post_date = fields[2].strip("'")[:10]
            post_content = fields[4].strip("'").replace("\\'", "'").replace('\\n', '\n')
            post_title = fields[5].strip("'").replace("\\'", "'")
            post_status = fields[7].strip("'")
            post_type = fields[20].strip("'") if len(fields) > 20 else 'unknown'
            
            posts.append({
                'id': post_id,
                'date': post_date,
                'title': post_title,
                'content': post_content,
                'status': post_status,
                'type': post_type
            })

print(f"Extracted {len(posts)} total rows\n")
print("=" * 60)

# Show all posts and pages
for p in posts:
    if p['title'] or p['content']:
        print(f"\n[{p['type'].upper()}] id:{p['id']} status:{p['status']} date:{p['date']}")
        print(f"TITLE: {p['title']}")
        print(f"CONTENT ({len(p['content'])} chars):")
        print(p['content'][:800])
        print("-" * 40)

# Also check for any options (site title, tagline etc)
options = re.findall(r"INSERT INTO `wp_pylpxs_options`.*?;\n", sql, re.DOTALL)
if options:
    print("\n\n=== SITE OPTIONS ===")
    blogname = re.search(r"'blogname','([^']+)'", sql)
    blogdesc = re.search(r"'blogdescription','([^']+)'", sql)
    if blogname: print(f"Site name: {blogname.group(1)}")
    if blogdesc: print(f"Tagline: {blogdesc.group(1)}")
