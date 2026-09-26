from pypdf import PdfReader

reader = PdfReader("Engineering.pdf")

# print("Pages", len(reader.pages))

char_count = 0

for page in reader.pages:
    text = page.extract_text()
    char_count += len(text)
    print(text)

    if char_count > 1000:
        break
