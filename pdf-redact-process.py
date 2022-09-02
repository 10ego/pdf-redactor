import pdf_redactor3 as pdf_redactor
import os
from datetime import datetime

pdfs = []
with open('other_pdf.txt') as f:
	for line in f:
		pdfs.append(line.rstrip())
with open('worked.log') as f:
	worked = [x[21:].strip() for x in f.readlines()]

count=0
for pdf in pdfs:
	count+=1
	print(f'{count}/10488:', pdf)
	if not pdf in worked:
		try:
			Redactor = pdf_redactor.Redactor(pdf, 'pdfs', 'other')
			Redactor.redaction()
			with open('worked.log', 'a+') as f:
				f.write(f'[{datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")}]{pdf}\n')
		except Exception as e:
			with open('error.log', 'a+') as f:
				f.write(f'[{datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")}]{pdf}, {e.args}\n')
				
	else:
		print(f'\t{pdf} already worked on')
