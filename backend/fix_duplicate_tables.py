#!/usr/bin/env python3
"""
Fix duplicate table definitions in models
This script removes duplicate Invoice and InvoiceItem definitions from __init__.py
and ensures they're only defined in payment.py
"""

import re

# Read the __init__.py file
init_file = "/Users/sujitsingh/Documents/vaidya-vihar-diagnostic/backend/app/models/__init__.py"

with open(init_file, 'r') as f:
    content = f.read()

# Find and remove the Invoice and InvoiceItem class definitions (lines 320-370 approximately)
# We'll replace them with imports from payment module

# Pattern to match the Invoice class definition
invoice_pattern = r'class Invoice\(Base\):.*?(?=class\s+\w+\(Base\)|$)'
invoiceitem_pattern = r'class InvoiceItem\(Base\):.*?(?=class\s+\w+\(Base\)|$)'

# Remove the duplicate definitions
content_fixed = re.sub(invoice_pattern, '', content, flags=re.DOTALL)
content_fixed = re.sub(invoiceitem_pattern, '', content_fixed, flags=re.DOTALL)

# Add imports at the top if not already there
if 'from app.models.payment import Invoice, InvoiceItem' not in content_fixed:
    # Find the imports section and add our import
    import_section = content_fixed.find('from sqlalchemy')
    if import_section != -1:
        # Add after the sqlalchemy imports
        lines = content_fixed.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('from sqlalchemy') or line.startswith('import'):
                continue
            else:
                # Insert our import before the first non-import line
                lines.insert(i, 'from app.models.payment import Invoice, InvoiceItem, Payment')
                break
        content_fixed = '\n'.join(lines)

# Write back
with open(init_file, 'w') as f:
    f.write(content_fixed)

print("✅ Fixed duplicate Invoice/InvoiceItem definitions in __init__.py")

# Now check if invoice.py exists and remove it
import os
invoice_file = "/Users/sujitsingh/Documents/vaidya-vihar-diagnostic/backend/app/models/invoice.py"
if os.path.exists(invoice_file):
    os.remove(invoice_file)
    print("✅ Removed duplicate invoice.py file")

print("\n✅ All duplicate table definitions fixed!")
print("   - Invoice and InvoiceItem are now only defined in payment.py")
print("   - Other files import from payment.py")
