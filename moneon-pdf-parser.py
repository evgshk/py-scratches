import io, re, json, csv

from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage

def extract_text_by_page(pdf_path):
    with open(pdf_path, 'rb') as fh:
        transactions = []
        page_number = 0;
        for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
            resource_manager = PDFResourceManager()
            fake_file_handle = io.StringIO()
            converter = TextConverter(resource_manager, fake_file_handle)
            page_interpreter = PDFPageInterpreter(resource_manager, converter)
            page_interpreter.process_page(page)

            page_text = fake_file_handle.getvalue()

            # retrieve all transaction dates (e.g., 20 September 2018) from page text
            dates = re.findall(r'\d{1,2}\s[A-Z][a-z]{2,8}\s\d{4}', page_text)
            # split page text by these dates on a list
            text_splitted = re.split(r'\d{1,2}\s[A-Z][a-z]{2,8}\s\d{4}', page_text)
            text_splitted_count = len(text_splitted)

            if text_splitted_count > 1:
                last = text_splitted[text_splitted_count-1]
                text_splitted = text_splitted[1:-1]
                text_splitted.extend(last.split('−', 1))

            text_splitted_count = len(text_splitted)

            # retrieve all amounts (e.g., 3 000 RUB) from last item of the list
            prices = re.findall(r'\d{1,3}(?:\s\d{3})*(?:[,]\d{2})\sRUB', text_splitted[text_splitted_count-1])
            if text_splitted_count > 1:
                text_splitted.pop()

            i = 0
            for date in dates:
                transaction = Transaction()
                transaction.date = date
                transaction.price = float(prices[i].replace(' RUB', '').replace(' ', '').replace(',','.'))
                transaction.category = text_splitted[i]
                transactions.append(transaction)
                i = i + 1

            yield page_number
            page_number = page_number + 1

            # close open handles
            converter.close()
            fake_file_handle.close()

        # serialize a given list of transactions to json
        result_json = json.dumps([ob.__dict__ for ob in transactions])
        result_json_file = open("C:/result.txt", "w")
        result_json_file.write(result_json)

        result_csv_file = open("C:/result.csv", "w")
        csv_data = json.load(result_json_file)
        result_json_file.close()

        output = csv.writer(result_csv_file)
        for row in csv_data:
            output.writerow(row.values())

def extract_text(pdf_path):
    for page in extract_text_by_page(pdf_path):
        print(page)
        print()

class Transaction:
    date = ''
    category = ''
    price = 0

if __name__ == '__main__':
    print(extract_text('C:/report.pdf'))