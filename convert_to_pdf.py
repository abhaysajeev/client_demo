#!/usr/bin/env python3
"""
Simple Markdown to PDF converter for API documentation
"""
import os
import subprocess

# Read the markdown file
with open('API_DOC.md', 'r') as f:
    content = f.read()

# Create HTML with styling
html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 40px auto;
            padding: 0 20px;
            color: #333;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
            padding: 10px;
            background: #ecf0f1;
            border-left: 4px solid #3498db;
        }}
        h3 {{
            color: #555;
            margin-top: 20px;
        }}
        pre {{
            background: #2c3e50;
            color: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        code {{
            background: #f8f9fa;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
        pre code {{
            background: none;
            padding: 0;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #3498db;
            color: white;
        }}
        tr:nth-child(even) {{
            background-color: #f2f2f2;
        }}
        strong {{
            color: #2c3e50;
        }}
        hr {{
            border: none;
            border-top: 2px solid #3498db;
            margin: 30px 0;
        }}
    </style>
</head>
<body>
"""

# Simple markdown to HTML conversion
lines = content.split('\n')
in_code_block = False
in_table = False
code_block_content = []

for line in lines:
    # Handle code blocks
    if line.strip().startswith('```'):
        if in_code_block:
            html_content += '<pre><code>' + '\n'.join(code_block_content) + '</code></pre>\n'
            code_block_content = []
            in_code_block = False
        else:
            in_code_block = True
        continue
    
    if in_code_block:
        code_block_content.append(line.replace('<', '&lt;').replace('>', '&gt;'))
        continue
    
    # Headers
    if line.startswith('# '):
        html_content += f'<h1>{line[2:]}</h1>\n'
    elif line.startswith('## '):
        html_content += f'<h2>{line[3:]}</h2>\n'
    elif line.startswith('### '):
        html_content += f'<h3>{line[4:]}</h3>\n'
    # Horizontal rule
    elif line.strip() == '---':
        html_content += '<hr>\n'
    # Table
    elif line.strip().startswith('|'):
        if not in_table:
            html_content += '<table>\n'
            in_table = True
        cells = [cell.strip() for cell in line.split('|')[1:-1]]
        if all(cell.replace('-', '').strip() == '' for cell in cells):
            continue  # Skip separator row
        tag = 'th' if '**' in line or line.strip().startswith('| Parameter') else 'td'
        html_content += '<tr>'
        for cell in cells:
            cell = cell.replace('**', '').replace('✅', '✓').replace('❌', '✗')
            html_content += f'<{tag}>{cell}</{tag}>'
        html_content += '</tr>\n'
    else:
        if in_table and not line.strip().startswith('|'):
            html_content += '</table>\n'
            in_table = False
        if line.strip():
            # Bold text
            line = line.replace('**', '<strong>').replace('**', '</strong>')
            html_content += f'<p>{line}</p>\n'
        else:
            html_content += '<br>\n'

if in_table:
    html_content += '</table>\n'

html_content += """
</body>
</html>
"""

# Write HTML file
with open('API_DOC.html', 'w') as f:
    f.write(html_content)

print("HTML file created: API_DOC.html")

# Try to convert to PDF using wkhtmltopdf if available
try:
    subprocess.run(['wkhtmltopdf', '--version'], capture_output=True, check=True)
    subprocess.run(['wkhtmltopdf', 'API_DOC.html', 'API_DOCUMENTATION.pdf'], check=True)
    print("PDF created successfully: API_DOCUMENTATION.pdf")
except (FileNotFoundError, subprocess.CalledProcessError):
    print("wkhtmltopdf not available. Using chromium/chrome instead...")
    try:
        # Try chromium-browser
        subprocess.run([
            'chromium-browser',
            '--headless',
            '--disable-gpu',
            '--no-sandbox',
            '--print-to-pdf=API_DOCUMENTATION.pdf',
            'API_DOC.html'
        ], check=True)
        print("PDF created successfully using chromium: API_DOCUMENTATION.pdf")
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("Could not create PDF automatically.")
        print("Please open API_DOC.html in a browser and print to PDF manually.")
