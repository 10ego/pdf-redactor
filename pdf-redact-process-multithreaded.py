import pdf_redactor3 as pdf_redactor
from datetime import datetime
from multiprocessing import Pool, Value, Lock

pdfs = []
today = datetime.strftime(datetime.now(), '%Y-%m-%d_%H%M%S')
datalist = 'pdfs.txt'
worklog = 'worked_synthdata.log'
errorlog = 'error_synthdata.log'
INPUT_DIR = 'pdfs'
OUTPUT_DIR = 'synthetic'

with open(datalist) as f:
    for line in f:
        pdfs.append(line.rstrip())
with open(worklog) as f:
    worked = [x[21:].strip() for x in f.readlines()]

total = len(pdfs) - len(worked)
counter = Value ('i', 0)
lock = Lock()


def pdfproc(pdf, worked=worked):
    global counter, lock

    with lock:
        counter.value += 1
        print(f"{counter}/{total}:", pdf)
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

if __name__ == '__main__':
    POOL_SIZE = 5
    INPUT_LIST = list(set(pdfs)-set(worked))
    with Pool(POOL_SIZE) as p:
        p.map(pdfproc, INPUT_LIST)
