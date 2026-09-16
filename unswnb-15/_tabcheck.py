import re
for fn in ['paper1-generalisasi.tex','paper1-en-ijisa.tex']:
    t=open(fn,encoding='utf-8').read()
    print('====',fn,'====')
    found=False
    for m in re.finditer(r'\\begin\{tabular\}(\{[^}]*\})(.*?)\\end\{tabular\}', t, re.S):
        body=m.group(2)
        for line in body.split('\\\\'):
            s=line.strip()
            if not s or 'rule' in s or 'multicolumn' in s or 'cmidrule' in s:
                continue
            cells=[c.strip() for c in s.split('&')]
            empties=[i for i,c in enumerate(cells) if c=='']
            if empties and len(cells)>1:
                found=True
                print('  EMPTY at col',empties,'::', s[:90])
    if not found:
        print('  OK - tidak ada sel data kosong tak-terduga')
