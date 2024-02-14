import pdf_redactor3 as pdf_redactor
from datetime import datetime
from multiprocessing import Pool

pdfs = []
today = datetime.strftime(datetime.now(), '%Y-%m-%d_%H%M%S')
datalist = 'pdfs.txt'
worklog = 'worked_synthdata.log'
errorlog = 'error_synthdata.log'
INPUT_DIR = 'emails/pdfs'
OUTPUT_DIR = 'emails/redacted'

with open(datalist) as f:
    for line in f:
        pdfs.append(line.rstrip())
with open(worklog) as f:
    worked = [x[21:].strip() for x in f.readlines()]

total = len(pdfs)
count = 0
POOL_SIZE = 5


def pdfproc(pdf, worked=worked, count=0):
    count += POOL_SIZE

    if pdf not in worked:
        print(f'{count}/{total}:', pdf)
        try:
            Redactor = pdf_redactor.Redactor(pdf, INPUT_DIR, OUTPUT_DIR)
            Redactor.redaction()
            with open(worklog, 'a+') as f:
                f.write(
                    f'[{datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")}]{pdf}\n'
                )
        except Exception as e:
            print("Error. Skipping.")
            with open(errorlog, 'a+') as f:
                f.write(
                    f'[{datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")}]{pdf}, {e.args}\n'
                )
            if not Redactor.lang:
                with open('pertinence_synthdata.log', 'a+') as f:
                    f.write(
                        f'[{datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")}]{pdf}, IMPERTINENT\n'
                    )
    else:
        pass


if __name__ == '__main__':
    with Pool(POOL_SIZE) as p:
        p.map(pdfproc, pdfs)
