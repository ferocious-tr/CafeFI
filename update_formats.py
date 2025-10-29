#!/usr/bin/env python
"""Format tutarlarını otomatik güncelleyelim"""

import re

files_to_update = [
    'src/modules/sales.py',
    'src/modules/expenses.py',
    'src/modules/reports_ui.py',
    'src/app.py'
]

for filepath in files_to_update:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Sayı format değişiklikleri
        # Patte rn: f"₺{x:.2f}" -> format_currency(x)
        original_count = content.count('f"₺{')
        
        # Basit regex: f"₺{..} -> format_currency(...)
        pattern = r'f"₺\{([^}]+):\.[0-9]f\}"'
        replacement = r'format_currency(\1)'
        updated = re.sub(pattern, replacement, content)
        
        new_count = updated.count('format_currency(')
        
        if updated != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(updated)
            print(f'✓ {filepath}: {new_count} format_currency() eklendi')
        else:
            print(f'- {filepath}: değişiklik yok')
    except Exception as e:
        print(f'✗ {filepath}: {e}')
