# Let's attempt to extract text from the uploaded PDF file "UTS GKV.pdf".
# We will use PyPDF2 if it's available.
import PyPDF2

file_path = "/mnt/data/UTS GKV.pdf"
text = ""
try:
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        num_pages = len(reader.pages)
        text_list = []
        for i in range(num_pages):
            page = reader.pages[i]
            page_text = page.extract_text()
            text_list.append(page_text)
        text = "\n".join(text_list)
except Exception as e:
    text = str(e)

text[:1000]  # Print first 1000 characters for preview

