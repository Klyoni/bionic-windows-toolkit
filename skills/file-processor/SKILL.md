---
name: file-processor
description: Rules for reading, analyzing, and creating Excel (.xlsx), Word (.docx), PDF (.pdf), and chart files using installed local Python libraries.
---
When the user asks to read, analyze, or generate structured documents or charts via the local Windows terminal, ALWAYS write a `.py` script using the pre-installed libraries instead of reading binary files directly:

1. Excel & CSV (`.xlsx`, `.xls`, `.csv`): Use `pandas` (`pd.read_excel`, `pd.read_csv`) and `openpyxl`.
2. Word Documents (`.docx`): Use `python-docx` (`import docx`) to extract paragraphs and tables or create formatted reports.
3. PDF Files (`.pdf`): Use `pypdf` (`from pypdf import PdfReader`) to extract text page by page.
4. Charts & Plots: Use `matplotlib` (`plt.savefig('chart.png', dpi=150, bbox_inches='tight')`) to save high-quality PNG images when running in the local terminal.

