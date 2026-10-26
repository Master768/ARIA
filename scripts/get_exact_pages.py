import os
import win32com.client

path = os.path.abspath(r'C:\Users\Ravin\OneDrive\Desktop\Test 1\ARIA_Dissertation_MSc_Data_Science edit.docx')
word = win32com.client.Dispatch('Word.Application')
word.Visible = False
try:
    doc = word.Documents.Open(path, ReadOnly=True)
    total_pages = doc.ComputeStatistics(2)
    print(f'TOTAL_PAGES: {total_pages}')
    
    items = []
    prefixes = (
        'CHAPTER', 'DECLARATION', 'CERTIFICATE', 'ACKNOWLEDGEMENTS', 'ABSTRACT',
        'TABLE OF CONTENTS', 'LIST OF FIGURES', 'LIST OF TABLES', 'LIST OF ABBREVIATIONS',
        'REFERENCES', 'APPENDIX',
        '1.1', '1.2', '1.3', '1.4', '1.5',
        '2.1', '2.2', '2.3', '2.4', '2.5', '2.6',
        '3.1', '3.2', '3.3', '3.4', '3.5', '3.6',
        '4.1', '4.2', '4.3', '4.4',
        'Figure 2.', 'Figure 3.', 'Table 1.', 'Table 2.', 'Table 3.'
    )
    for p in doc.Paragraphs:
        text = p.Range.Text.strip()
        for pref in prefixes:
            if text.startswith(pref):
                page = p.Range.Information(3) # wdActiveEndPageNumber
                clean_text = text.encode('ascii', errors='replace').decode('ascii')
                items.append((page, clean_text[:80]))
                break
    
    for page, t in items:
        print(f"P.{page:02d} | {t}")
        
    doc.Close(False)
finally:
    word.Quit()
