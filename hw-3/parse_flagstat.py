#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import re

def parse_flagstat(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Ошибка при чтении файла {filename}: {e}")
        return None
    
    match = re.search(r'mapped\s+\((\d+(?:\.\d+)?)%', content)
    if match:
        return float(match.group(1))
    
    match = re.search(r'(\d+(?:\.\d+)?)%\s+:\s+N/A', content)
    if match:
        return float(match.group(1))
        
    return None

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Использование: python parse_flagstat.py <путь_к_flagstat.txt>")
        sys.exit(1)
        
    flagstat_file = sys.argv[1]
    percent = parse_flagstat(flagstat_file)
    
    if percent is None:
        print("Ошибка: не удалось извлечь процент картирования из файла.")
        sys.exit(2)
        
    print(f"Процент картированных ридов: {percent}%")
    
    if percent > 90.0:
        print("OK")
        sys.exit(0)
    else:
        print("not OK")
        sys.exit(3)
