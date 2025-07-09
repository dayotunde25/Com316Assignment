import os
from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        # Arial bold 15
        self.set_font('Arial', 'B', 15)
        # Title
        self.cell(0, 10, 'Transcribed Text', 0, 1, 'C')
        # Line break
        self.ln(10)

    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Page number
        self.cell(0, 10, 'Page %s' % self.page_no(), 0, 0, 'C')

    def chapter_body(self, text_content):
        # Add a Page
        self.add_page()
        # Set font for body (ensure it supports the characters in the text)
        # FPDF has core fonts: Courier, Helvetica/Arial, Times, Symbol, ZapfDingbats
        # For broader Unicode support, we might need to add a Unicode font like DejaVu
        # Set font for body (ensure it supports the characters in the text)
        # Try to load DejaVu font from the local 'fonts' directory first for better portability.
        font_name = 'DejaVu'
        font_file_path = os.path.join(os.path.dirname(__file__), '..', 'fonts', 'DejaVuSansCondensed.ttf')

        try:
            if os.path.exists(font_file_path):
                self.add_font(font_name, '', font_file_path, uni=True)
                self.set_font(font_name, '', 12)
            else:
                # Fallback to trying globally available DejaVu or then Arial
                try:
                    self.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
                    self.set_font('DejaVu', '', 12)
                except RuntimeError:
                    print("DejaVu font not found locally in ../fonts/ or globally. Falling back to Arial.")
                    print("For best Unicode support, download DejaVuSansCondensed.ttf and place it in tts_stt_app/fonts/")
                    self.set_font('Arial', '', 12) # Final fallback
        except Exception as e: # Catch any other font loading errors
            print(f"Error setting font: {e}. Falling back to Arial.")
            self.set_font('Arial', '', 12)

        # Output justified text
        self.multi_cell(0, 10, text_content)
        # Line break
        self.ln()

def create_pdf_from_text_file(text_filepath, pdf_filepath):
    """
    Creates a PDF file from a given text file.
    text_filepath: Path to the input .txt file.
    pdf_filepath: Path where the output .pdf file will be saved.
    Returns True on success, False on failure.
    """
    try:
        with open(text_filepath, 'r', encoding='utf-8') as f:
            text_content = f.read()

        pdf = PDF()
        # pdf.alias_nb_pages() # Not strictly necessary if not using {nb} alias for total pages in footer
        pdf.chapter_body(text_content)
        pdf.output(pdf_filepath, 'F')
        return True
    except Exception as e:
        print(f"Error creating PDF: {e}")
        return False

# To make this work, you might need to:
# 1. Install fpdf2: pip install fpdf2
# 2. Download a Unicode font like DejaVuSansCondensed.ttf.
#    Place it in your project, e.g., in a 'fonts' directory, or a system font directory.
#    If not in a standard FPDF font path, you might need to set the FPDF_FONTPATH environment variable
#    or ensure the .ttf file is in the same directory as this script (or a known path for FPDF).
#    For simplicity in a containerized/reproducible environment, including the font with the app is best.
#    Example: create a directory `tts_stt_app/fonts/` and place `DejaVuSansCondensed.ttf` there.
#    Then, in `pdf_tools.py` when adding font: `self.add_font('DejaVu', '', '../fonts/DejaVuSansCondensed.ttf', uni=True)`
#    (adjust path as needed relative to pdf_tools.py).
#    For now, the code attempts to add it and falls back if not found.
#    A more robust solution would involve packaging the font file.

# Let's assume for now that we will instruct the user to install the font or handle it during setup.
# For the `add_font` call: `self.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)`
# This assumes 'DejaVuSansCondensed.ttf' is in a location FPDF checks (e.g., current dir, Python path, or FPDF_FONTPATH).
# A common practice is to have a `fonts` folder in the application and point to it.
# For example, if `fonts` is at the same level as `utils`: `os.path.join(os.path.dirname(__file__), '..', 'fonts', 'DejaVuSansCondensed.ttf')`
# Let's try to make the font path relative to the project structure assuming a `tts_stt_app/fonts` directory.

# Revised add_font call within PDF.chapter_body method:
# font_path = os.path.join(os.path.dirname(__file__), '..', 'fonts', 'DejaVuSansCondensed.ttf')
# if os.path.exists(font_path):
#     self.add_font('DejaVu', '', font_path, uni=True)
#     self.set_font('DejaVu', '', 12)
# else:
#     print("DejaVu font not found at expected path. Falling back to Arial.")
#     self.set_font('Arial', '', 12)
# This requires creating the fonts directory and adding the .ttf file.
# I will proceed without this specific font file addition for now, relying on fpdf2's default capabilities or system fonts.
# The provided code has a try-except for `add_font` which is a reasonable fallback.
# The user will be instructed to install `fpdf2`.
# The `add_font` call `self.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)` implies the font file is discoverable.
# I will add a note about placing `DejaVuSansCondensed.ttf` in a location where FPDF can find it (e.g., alongside `pdf_tools.py` or in a directory specified by `FPDF_FONTPATH`).
# For a more self-contained app, packaging the font is better. I'll create the fonts folder and add a placeholder note about the font file.
# I will create the fonts directory and adjust the path in pdf_tools.py later if a specific font file is bundled.
# For now, the existing try-except block for font loading is acceptable.
# The key is to add fpdf2 to requirements.txt.
