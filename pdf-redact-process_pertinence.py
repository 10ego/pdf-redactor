import pdf_redactor3 as pdf_redactor
import os
import fitz
from datetime import datetime

pdfs = []
with open('other_pdf.txt') as f:
	for line in f:
		pdfs.append(line.rstrip())
with open('worked.log') as f:
	worked = [x[21:].strip() for x in f.readlines()]
with open('worked_2.log') as f:
	worked2 = [x[21:].strip() for x in f.readlines()]
with open('error.log') as f:
	errl = [x[21:].strip().split(',')[0] for x in f.readlines()]
with open('error_2.log') as f:
	errl2 = [x[21:].strip().split(',')[0] for x in f.readlines()]
worked = worked + worked2
#worked = worked + errl
count=0
total = len(errl2)
for pdf in errl2:
	count+=1
	if not pdf in worked:
		print(f'{count}/{total}:', pdf)
		try:
			Redactor = pdf_redactor.Redactor(pdf, 'pdfs', '.')
			Redactor.preredaction(fitz.open(Redactor.path))
			if redacted.path:
				with open('worked_3(pertinent).log', 'a+') as f:
					f.write(f'[{datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")}]{pdf}\n')
			else:
				with open('error_3(impertinent).log', 'a+') as f:
					f.write(f'[{datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")}]{pdf}, {e}, No Language Found\n')
		except Exception as e:
			print("Error. Skipping.")
			with open('error_3(impertinent).log', 'a+') as f:
				f.write(f'[{datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")}]{pdf}, {e}, {Redactor.errorlog}\n')
	else:
		pass
#		print(f'\t{pdf} already worked on')
