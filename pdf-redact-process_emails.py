import pdf_redactor3 as pdf_redactor
import os
from datetime import datetime
from multiprocessing import Pool

pdfs = []
with open('emails/pdfs.txt') as f:
	for line in f:
		pdfs.append(line.rstrip())
with open('worked_emails.log') as f:
	worked = [x[21:].strip() for x in f.readlines()]
with open('error_emails(pertinence).log') as f:
	errl = [x[21:].strip().split(',')[0] for x in f.readlines()]
worked = worked + errl
total = len(pdfs)
count=0
#for pdf in pdfs:
def pdfproc(pdf, worked = worked, count=0):
	count+=5
	if not pdf in worked:
		print(f'{count}/{total}:', pdf)
		try:
			Redactor = pdf_redactor.Redactor(pdf, 'emails/pdfs', 'emails/redacted')
			Redactor.redaction()
			with open('worked_emails.log', 'a+') as f:
				f.write(f'[{datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")}]{pdf}\n')
#		except Exception as e:
		except Exception as e:
			print("Error. Skipping.")
			with open('error_emails.log', 'a+') as f:
				f.write(f'[{datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")}]{pdf}, {e.args}\n')
			if not Redactor.lang:
				with open('error_emails(pertinence).log', 'a+') as f:
					f.write(f'[{datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")}]{pdf}, IMPERTINENT\n')
	else:
		pass
#		print(f'\t{pdf} already worked on')

if __name__=='__main__':
	with Pool(5) as p:
		p.map(pdfproc, pdfs)
