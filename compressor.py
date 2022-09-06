import fitz

#with open('other_pdf.txt') as f:
#	l = [x.strip() for x in f.readlines()]
#
#ll = l[6576:9943]
with open('redacted/tocompress.txt') as f:
	l = [x.strip()[2:] for x in f.readlines()]
ll = l
for pdf in ll:
	doc = fitz.open(f'redacted/other/{pdf}')
	doc.save(f'redacted/other/compressed2/{pdf}', deflate_images=True, deflate_fonts=True)
