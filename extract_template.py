import pdfplumber

all_text = []
with pdfplumber.open(r'CV/NXSTEP_CV_Format ATS 2 - Copy.pdf') as pdf:
    print(f'Total pages: {len(pdf.pages)}')
    for i, page in enumerate(pdf.pages):
        text = page.extract_text()
        all_text.append(f'=== PAGE {i+1} ===\n{text if text else "(empty)"}\n')

full = '\n'.join(all_text)
with open('cv_template_content.txt', 'w', encoding='utf-8') as f:
    f.write(full)

print('Written to cv_template_content.txt')
print(f'Total chars: {len(full)}')
print()
print(full[:3000])
