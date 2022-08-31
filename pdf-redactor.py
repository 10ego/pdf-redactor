import fitz
import re
import json
import hashlib
class Redactor:
# Fields to redact:
#* A.2. Reporter Contact Information
#* B.4. Patient Consequences
#* B.5. Details of Incident
#* D.2. Name of Complainant
#* D.3. Name of Health Care Facility (if applicable)
#* D.4. Address
#* D.5. Telephone No. and/or E-mail Address
#* E.1. Investigative Actions and Timeline
#* E.2. Root Cause of Problem
#* E.3. Corrective Actions taken as a result of the investigation
	
	# @staticmethod
	# def get_sensitive_data(lines):
	#	  # EMAIL_REG = r"([\w\.\d]+\@[\w\d]+\.[\w\d]+)"
	#	  TARGET_REG = r"Reporter Contact Information"
	#	  for line in lines:
		   
	#		  # matching the regex to each line
	#		  if re.search(TARGET_REG, line, re.IGNORECASE):
	#			  search = re.search(TARGET_REG, line, re.IGNORECASE)
				 
	#			  # yields creates a generator
	#			  # generator is used to return
	#			  # values in between function iterations
	#			  yield search.group()
 
	def __init__(self, path):
		self.path = path

	def redaction(self):
		# opening the pdf
		doc = fitz.open(self.path)
		data = {}
		# iterating through pages
		for page in doc:
			currentpage = 0 
			
			# _wrapContents is needed for fixing
			# alignment issues with rect boxes in some
			# cases where there is alignment issue
			page.wrap_contents()
			 
			# align box area to match different PDF formats
			# using a few reference points that are known to exist

			# First page of form (real) detection
			# Also finds left edge reference point
			
			# Coordinates variables naming conventions
			# XL0 = x-axis left edge, left panel
			# XL1 = x-axis right edge, left panel
			# XR0 = x-axis left edge, right panel
			# XR1 = x-axis right edge, right panel
			# AREA_Y0 = y-axis top edge
			# AREA_Y1 = y-axis bottom edge
			# Page 1
		

			footer_area = page.search_for('a program of medeffect')
			if footer_area:
				found = footer_area
				YFOOTER = found[0][1] - 30
			
			Q_A2 = page.search_for('2. reporter contact information')
			if Q_A2:
				found = Q_A2
				XL0 = found[0][0]
				A2_Y0 = found[0][3] + 2
				currentpage = 1
			else:
				Q_D2 = page.search_for('2. Name of complainant')
				if Q_D2:
					found = Q_D2
					D2_Y0 = found[0][3] + 2
					currentpage = 2
			
			if currentpage == 1:
				Q_B5 = page.search_for('5. details of incident')
				if Q_B5:
					found = Q_B5
					XR0 = found[0][0]
					B5_Y0 = found[0][3] + 2
					XL1 = found[0][0] - 10
					XR1 = page.bound()[2]-XL0

				Q_A7 = page.search_for('7. Name and address') # Reference for Reporter Contact Information Y1
				if Q_A7:
					found = Q_A7
					A2_Y1 = found[0][1] - 17
			   
				Q_B4 = page.search_for('4. Patient consequences')
				if Q_B4:
					found = Q_B4
					B4_Y0 = found[0][3] + 2
				for Q in [Q_A2, Q_A7, Q_B4, Q_B5]:
					if Q is None: print(Q,'i')
				area_A2 = fitz.IRect(XL0, A2_Y0, XL1, A2_Y1)
				area_B4 = fitz.IRect(XL0, B4_Y0, XL1, YFOOTER)
				area_B5 = fitz.IRect(XR0, B5_Y0, XR1, YFOOTER)
				areas_page1 = [area_A2, area_B4, area_B5]

				text_A2 = page.get_text(clip=area_A2)
				text_B4 = page.get_text(clip=area_B4)
				text_B5 = page.get_text(clip=area_B5)
				hash_A2 = hashlib.md5(text_A2.encode()).hexdigest()
				hash_B4 = hashlib.md5(text_B4.encode()).hexdigest()
				hash_B5 = hashlib.md5(text_B5.encode()).hexdigest()
				data["A2"] = {"raw": text_A2, "hash":hash_A2}
				data["B4"] = {"raw": text_B4, "hash":hash_B4}
				data["B5"] = {"raw": text_B5, "hash":hash_B5}
				
				# [page.add_redact_annot(area, fill = (0, 0, 0)) for area in areas_page1]
				[page.add_redact_annot(x[0], text=x[1]) for x in zip(areas_page1,[data[x]['hash'] for x in {k:v for k,v in data.items() if 'A' in k or 'B' in k}])] #this code is unreadable..should fix

			elif currentpage == 2:
				Q_D3 = page.search_for('3. Name of health care facility')
				if Q_D3:
					found = Q_D3
					D2_Y1 = found[0][1] - 3
					D3_Y0 = found[0][3] + 2
				
				Q_D4 = page.search_for('4. Address')
				if Q_D4:
					found = Q_D4
					D3_Y1 = found[0][1] - 3
					D4_Y0 = found[0][3] + 2

				Q_D5 = page.search_for('5. Telephone No. and/or E-mail Address')
				if Q_D5:
					found = Q_D5
					D4_Y1 = found[0][1] -3
					D5_Y0 = found[0][3] + 2
					D5_Y1 = D4_Y1-D4_Y0 + D5_Y0

				Q_E1 = page.search_for('1. Investigative actions and timeline')
				if Q_E1:
					found = Q_E1
					XR0 = found[0][0]
					E1_Y0 = found[0][3] + 2

				Q_E2 = page.search_for('2. Root cause of problem')
				if Q_E2:
					found = Q_E2
					E1_Y1 = found[0][1] - 20
					E2_Y0 = found[0][3] + 2
				
				Q_E3 = page.search_for('3. corrective actions taken as a result of the investigation')
				if Q_E3:
					found = Q_E3
					E2_Y1 = found[0][1] - 3
					E3_Y0 = found[0][3] + 2
				for Q in [Q_D2, Q_D3, Q_D4, Q_D5, Q_E1, Q_E2, Q_E3]:
					if Q is None: print(Q,'i')
				area_D2 = fitz.IRect(XL0, D2_Y0, XL1, D2_Y1)
				area_D3 = fitz.IRect(XL0, D3_Y0, XL1, D3_Y1)
				area_D4 = fitz.IRect(XL0, D4_Y0, XL1, D4_Y1)
				area_D5 = fitz.IRect(XL0, D5_Y0, XL1, D5_Y1)
				area_E1 = fitz.IRect(XR0, E1_Y0, XR1, E1_Y1)
				area_E2 = fitz.IRect(XR0, E2_Y0, XR1, E2_Y1)
				area_E3 = fitz.IRect(XR0, E3_Y0, XR1, YFOOTER)
				areas_page2 = [
					area_D2, area_D3, area_D4, area_E1, area_E2, area_E3
				]

				text_D2 = page.get_text(clip=area_D2)
				text_D3 = page.get_text(clip=area_D3)
				text_D4 = page.get_text(clip=area_D4)
				text_D5 = page.get_text(clip=area_D5)
				text_E1 = page.get_text(clip=area_E1)
				text_E2 = page.get_text(clip=area_E2)
				text_E3 = page.get_text(clip=area_E3)
				hash_D2 = hashlib.md5(text_D2.encode()).hexdigest()
				hash_D3 = hashlib.md5(text_D3.encode()).hexdigest()
				hash_D4 = hashlib.md5(text_D4.encode()).hexdigest()
				hash_D5 = hashlib.md5(text_D5.encode()).hexdigest()
				hash_E1 = hashlib.md5(text_E1.encode()).hexdigest()
				hash_E2 = hashlib.md5(text_E2.encode()).hexdigest()
				hash_E3 = hashlib.md5(text_E3.encode()).hexdigest()
				data["D2"] = {"raw": text_D2, "hash":hash_D2}
				data["D3"] = {"raw": text_D3, "hash":hash_D3}
				data["D4"] = {"raw": text_D4, "hash":hash_D4}
				data["D5"] = {"raw": text_D5, "hash":hash_D5}
				data["E1"] = {"raw": text_E1, "hash":hash_E1}
				data["E2"] = {"raw": text_E2, "hash":hash_E2}
				data["E3"] = {"raw": text_E3, "hash":hash_E3}
				

				# [page.add_redact_annot(area, fill = (0, 0, 0)) for area in areas_page2]
				[page.add_redact_annot(x[0], text=x[1]) for x in zip(areas_page2,[data[x]['hash'] for x in {k:v for k,v in data.items() if 'D' in k or 'E' in k}])] #this code is unreadable..should fix
			# drawing outline over sensitive datas
			# [page.add_redact_annot(area, text='REDACTED_DATA') for area in areas]
			else:
				page.add_redact_annot(page.bound())
			
			# applying the redaction
			page.apply_redactions()
		# saving it to a new pdf
		with open('pdf/'+self.path[:-4]+'.json', 'w+') as f:
			json.dump(data, f)
		doc.save('redacted/'+self.path[:-4]+'_REDACTED.pdf')
		print("Successfully redacted")

if __name__ == "__main__":
	path = 'testing.pdf'
	# path = 'pdfs/000941728(F30)Attachment.pdf'
	
	redactor = Redactor(path)
	redactor.redaction() 
