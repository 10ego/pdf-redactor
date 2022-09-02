import fitz
import re
import json
import hashlib
import os
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
 
	def __init__(self, filename, subdir):
		self.filename = filename
		self.path = subdir+'/'+self.filename
		self.OCR_TRIGGER = True
		self.lang = ''
	def search(self, phrase, obj, obj_ocr): # Not sure how PyMuPDF caches pages so just pass in both page objects manually for now
		if self.OCR_TRIGGER:
			return obj_ocr.search(phrase)
		else:
			return obj.search_for(phrase)
	def redaction(self):
		count = 0
		errorfactors = 0
		# opening the pdf
		doc = fitz.open(self.path)
		labeldict = {
			'footer':{
				'en':'a program of medeffect',
				'fr':'un programme de medeffect'
			},
			'A':{
				'en':'reporter information',
				'fr':'rensegnements sur le'
			},
			'A2':{
				'en':'reporter contact info',
				'fr':'coordonnées du déclar'
			},
			'A7':{
				'en':'name and address',
				'fr':'nom et adresse'
			},
			'B':{
				'en':'incident information',
				'fr':"renseignements sur l'incident"
			},
			'B4':{
				'en':'patient consequences',
				'fr':'conséquences pour le patient'
			},
			'B5':{
				'en':'details of incident',
				'fr':"détails sur l'incident"
			},
			'D':{
				'en':'complainant information',
				'fr':'renseignements sur le plaignant'
			},
			'D2':{
				'en':'Name of complainant',
				'fr':'Nom du plaignant'
			},
			'D3':{
				'en':'name of health care facility',
				'fr':"nom de l'éstablissement de soins"
			},
			'D4':{
				'en':'address',
				'fr':'adresse'
			},
			'D5':{
				'en':'telephone no',
				'fr':'numéro de téléphone'
			},
			'E':{
				'en':'investigation information',
				'fr':"renseignements sur"
			},
			'E1':{
				'en':'Investigative actions and timeline',
				'fr':"mesures d'enquê"
			},
			'E2':{
				'en':'root cause of problem',
				'fr':'source du problème'
			},
			'E3':{
				'en':'corrective actions taken as',
				'fr':'mesures correctives prises'
			}
		}

		data = {}
		# iterating through pages
		for page in doc:
			# Quick check
			if page.search_for(f"{labeldict['A']['en']}"):
				self.lang = 'en'
				self.OCR_TRIGGER = False
				break
			elif page.search_for(f"{labeldict['A']['fr']}"):
				self.lang = 'fr'
				self.OCR_TRIGGER = False
				break
			else:
				self.OCR_TRIGGER = True
		print("OCR Trigger:", self.OCR_TRIGGER)
		for page in doc:
			self.page = page
			page_ocr = None
			if self.OCR_TRIGGER:
				page_ocr = page.get_textpage_ocr(dpi=300, full=True)
				if page_ocr.search(labeldict['A2']['en']):
					self.lang = 'en'
				elif page_ocr.search(labeldict['A2']['fr']):
					self.lang = 'fr'
				self.page_ocr = page_ocr

			currentpage = 0
			
			# _wrapContents is needed for fixing
			# alignment issues with rect boxes in some
			# cases where there is alignment issue
			page.wrap_contents()
			
			# align box area to match different PDF formats
			# using a few reference points that are known to exist
			# Page 1
			
			Q_A2 = self.search(f"2. {labeldict['A2'][self.lang]}", page, page_ocr)
			if Q_A2:
				print(type(Q_A2))
				if not type(Q_A2)== fitz.fitz.Rect:
					Q_A2[0] = Q_A2[0].rect
				found = Q_A2
				XL0 = found[0][0]
				A2_Y0 = found[0][3]
				currentpage = 1
				
			else:
				Q_D2 = self.search(f"2. {labeldict['D2'][self.lang]}", page, page_ocr)
				if Q_D2:
					if not type(Q_D2)== fitz.fitz.Rect:
						Q_D2[0] = Q_D2[0].rect
					found = Q_D2
					D2_Y0 = found[0][3]
					currentpage = 2

			if currentpage == 1:

				footer_area = self.search(f"{labeldict['footer'][self.lang]}", page, page_ocr)
				if footer_area:
					if not type(footer_area)== fitz.fitz.Rect:
						footer_area[0] = footer_area[0].rect
					found = footer_area
					YFOOTER = found[0][1] - 30

				Q_B5 = self.search(f"5. {labeldict['B5'][self.lang]}", page, page_ocr)
				if Q_B5:
					if not type(Q_B5)== fitz.fitz.Rect:
						Q_B5[0] = Q_B5[0].rect
					found = Q_B5
					XR0 = found[0][0]
					B5_Y0 = found[0][3]
					XL1 = found[0][0] - 10
					XR1 = page.bound()[2] - XL0

				Q_A7 = self.search(f"7. {labeldict['A7'][self.lang]}", page, page_ocr) # Reference for Reporter Contact Information Y1
				if Q_A7:
					if not type(Q_A7)== fitz.fitz.Rect:
						Q_A7[0] = Q_A7[0].rect
					found = Q_A7
					A2_Y1 = found[0][1] - 17
			   
				Q_B4 = self.search(f"4. {labeldict['B4'][self.lang]}", page, page_ocr)
				if Q_B4:
					if not type(Q_B4)== fitz.fitz.Rect:
						Q_B4[0] = Q_B4[0].rect
					found = Q_B4
					B4_Y0 = found[0][3]
				
				# Look at variance in string match
				A = self.search(f"A. {labeldict['A'][self.lang]}", page, page_ocr)
				if not type(A)== fitz.fitz.Rect:
					A[0] = A[0].rect
				AY0 = A[0][3]
				Afactor = A[0][3] - A[0][1]
				
				B = self.search(f"B. {labeldict['B'][self.lang]}", page, page_ocr)
				if not type(B)== fitz.fitz.Rect:
					B[0] = B[0].rect
				BY0 = B[0][3]
				Bfactor = B[0][3] - B[0][1]
				if not 'XL0' in locals() or 'A2_Y0' in locals():
					# print("couldnt find XL0 or A2_Y0")
					errorfactors += 1
					Q_A2 = self.search(f"2.{labeldict['A2'][self.lang]}", page, page_ocr)
					if Q_A2:
						if not type(Q_A2)== fitz.fitz.Rect:
							Q_A2[0] = Q_A2[0].rect
						found = Q_A2
						XL0 = found[0][0]
						A2_Y0 = found[0][3]
						currentpage = 1
					else:
						errorfactors += 1
						# print("using Afactor")
						XL0 = A[0][0]-5
						A2_Y0 = AY0 + Afactor * 8
				if not 'A2_Y1' in locals():
					# print("couldnt find A2_Y1")
					errorfactors += 1
					Q_A7 = self.search(f"7.{labeldict['A7'][self.lang]}", page, page_ocr)
					if Q_A7:
						if not type(Q_A7)== fitz.fitz.Rect:
							Q_A7[0] = Q_A7[0].rect
						found = Q_A7
						A2_Y1 = found[0][1] - 17
					else:
						errorfactors += 1
						A2_Y1 = AY0 + Afactor * 16.5
				if not 'B4_Y0' in locals():
					# print("couldnt find B4_Y0")
					errorfactors += 1
					Q_B4 = self.search(f"4.{labeldict['B4'][self.lang]}", page, page_ocr)
					if Q_B4:
						if not type(Q_B4)== fitz.fitz.Rect:
							Q_B4[0] = Q_B4[0].rect
						found = Q_B4
						B4_Y0 = found[0][3]
					else:
						errorfactors += 1
						B4_Y0 = BY0 + Bfactor * 9
				if not 'XR0' in locals() or 'B5_Y0' in locals() or 'XL1' in locals() or 'XR1' in locals():
					# print("couldnt find XR0 or B5_Y0 or XL1 or XR1")
					errorfactors += 1
					Q_B5 = self.search(f"5.{labeldict['B5'][self.lang]}", page, page_ocr)
					if Q_B5:
						if not type(Q_B5)== fitz.fitz.Rect:
							Q_B5[0] = Q_B5[0].rect
						found = Q_B5
						XR0 = found[0][0]
						B5_Y0 = found[0][3]
						XL1 = found[0][0] - 10
						XR1 = page.bound()[2]-XL0
					else:
						errorfactors += 1
						XR0 = page.bound()[2]/2 + 5
						B5_Y0 = BY0 + Bfactor * 2
						XL1 = page.bound()[2]/2 - 5
						XR1 = page.bound()[2]-XL0
				if not 'YFOOTER' in locals():
					YFOOTER = page.bound()[3]-A2_Y1-A2_Y1
					errorfactors += 1
				

				area_A2 = fitz.Rect(XL0, A2_Y0, XL1, A2_Y1)
				area_B4 = fitz.Rect(XL0, B4_Y0, XL1, YFOOTER)
				area_B5 = fitz.Rect(XR0, B5_Y0, XR1, YFOOTER)
				areas_page1 = [area_A2, area_B4, area_B5]
				for a in areas_page1: print(a)
				if self.OCR_TRIGGER:
					pmap_A2 = page.get_pixmap(clip = area_A2)
					tmppdf = pmap_A2.pdfocr_tobytes()
					tmpdoc = fitz.open("pdf", tmppdf)
					text_A2 = tmpdoc[0].get_text()

					pmap_B4 = page.get_pixmap(clip = area_B4)
					tmppdf = pmap_B4.pdfocr_tobytes()
					tmpdoc = fitz.open("pdf", tmppdf)
					text_B4 = tmpdoc[0].get_text()

					pmap_B5 = page.get_pixmap(clip = area_B5)
					tmppdf = pmap_B5.pdfocr_tobytes()
					tmpdoc = fitz.open("pdf", tmppdf)
					text_B5 = tmpdoc[0].get_text()
					# text_B4 = page.get_text(clip=area_B4)
					# text_B5 = page.get_text(clip=area_B5)
				else:
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
			
			# Page 2
			elif currentpage == 2:
				Q_D3 = self.search(f"3. {labeldict['D3'][self.lang]}", page, page_ocr)
				if Q_D3:
					if not type(Q_D3)== fitz.fitz.Rect:
						Q_D3[0] = Q_D3[0].rect
					found = Q_D3
					D2_Y1 = found[0][1]
					D3_Y0 = found[0][3]
				
				Q_D4 = self.search(f"4. {labeldict['D4'][self.lang]}", page, page_ocr)
				if Q_D4:
					if not type(Q_D4)== fitz.fitz.Rect:
						Q_D4[0] = Q_D4[0].rect
					found = Q_D4
					D3_Y1 = found[0][1]
					D4_Y0 = found[0][3]

				Q_D5 = self.search(f"5. {labeldict['D5'][self.lang]}", page, page_ocr)
				if Q_D5:
					if not type(Q_D5)== fitz.fitz.Rect:
						Q_D5[0] = Q_D5[0].rect
					found = Q_D5
					D4_Y1 = found[0][1]
					D5_Y0 = found[0][3]
					D5_Y1 = D5_Y0 + (D5_Y0 - D4_Y1) * 3.5

				Q_E1 = self.search(f"1. {labeldict['E1'][self.lang]}", page, page_ocr)
				if Q_E1:
					if not type(Q_E1)== fitz.fitz.Rect:
						Q_E1[0] = Q_E1[0].rect
					found = Q_E1
					XR0_2 = found[0][0]
					E1_Y0 = found[0][3]

				Q_E2 = self.search(f"2. {labeldict['E2'][self.lang]}", page, page_ocr)
				if Q_E2:
					if not type(Q_E2)== fitz.fitz.Rect:
						Q_E2[0] = Q_E2[0].rect
					found = Q_E2
					E1_Y1 = found[0][1] - 20
					E2_Y0 = found[0][3]
				
				Q_E3 = self.search(f"3. {labeldict['E3'][self.lang]}", page, page_ocr)
				if Q_E3:
					if not type(Q_E3)== fitz.fitz.Rect:
						Q_E3[0] = Q_E3[0].rect
					found = Q_E3
					E2_Y1 = found[0][1]
					E3_Y0 = found[0][3]
				
				# Look at variance in string match
				D = self.search(f"D. {labeldict['D'][self.lang]}", page, page_ocr)
				if not type(D)== fitz.fitz.Rect:
					D[0] = D[0].rect
				DY0 = D[0][3]
				Dfactor = max(D[0][3] - D[0][1], 11.6)
				print('Dfactor', Dfactor)
				E = self.search(f"E. {labeldict['E'][self.lang]}", page, page_ocr)
				if not type(E)== fitz.fitz.Rect:
					E[0] = E[0].rect
				EY0 = E[0][3]
				Efactor = E[0][3] - E[0][1]
				if not 'D2_Y0' in locals():
					errorfactors += 1
					# print("couldnt find D2_Y0")
					Q_D2 = self.search(f"2.{labeldict['D2'][self.lang]}", page, page_ocr)
					if Q_D2:
						if not type(Q_D2)== fitz.fitz.Rect:
							Q_D2[0] = Q_D2[0].rect
						found = Q_D2
						D2_Y0 = found[0][3]
						currentpage = 2
					else:
						errorfactors += 1
						print("using dfactor D2_Y0")
						D2_Y0 = DY0 + (Dfactor * 3)
				if not 'D2_Y1' in locals() or 'D3_Y0' in locals():
					errorfactors += 1
					# print("couldnt find D2_Y1 or D3_Y0")
					Q_D3 = self.search(f"3.{labeldict['D3'][self.lang]}", page, page_ocr)
					if Q_D3:
						if not type(Q_D3)== fitz.fitz.Rect:
							Q_D3[0] = Q_D3[0].rect
						found = Q_D3
						D2_Y1 = found[0][1] 
						D3_Y0 = found[0][3] 
					else:
						errorfactors += 1
						print("using dfactor D2_Y1, D3_Y0")
						D2_Y1 = D2_Y0 + Dfactor 
						D3_Y0 = D2_Y1 + Dfactor
				if not 'D3_Y1' in locals() or 'D4_Y0' in locals():
					errorfactors += 1
					# print("couldnt find D3_Y1 or D4_Y0")
					Q_D4 = self.search(f"4.{labeldict['D4'][self.lang]}", page, page_ocr)
					if Q_D4:
						if not type(Q_D4)== fitz.fitz.Rect:
							Q_D4[0] = Q_D4[0].rect
						found = Q_D4
						D3_Y1 = found[0][1] 
						D4_Y0 = found[0][3] 
					else:
						errorfactors += 1
						print("using dfactor D3_Y1, D4_Y0")
						D3_Y1 = D3_Y0 + Dfactor
						D4_Y0 = D3_Y1 + Dfactor
				if not 'D4_Y1' in locals() or 'D5_Y0' in locals() or 'D5_Y1' in locals():
					errorfactors += 1
					# print("couldnt find D4_Y1 or D5_Y0 or D5_Y1")
					Q_D5 = self.search(f"5.{labeldict['D5'][self.lang]}", page, page_ocr)
					if Q_D5:
						if not type(Q_D5)== fitz.fitz.Rect:
							Q_D5[0] = Q_D5[0].rect
						found = Q_D5
						D4_Y1 = found[0][1]
						D5_Y0 = found[0][3]
						D5_Y1 = D5_Y0 + D4_Y1 - D4_Y0
						print(D5_Y0, D5_Y1)
					else:
						errorfactors += 1
						print("using dfactor D5_Y1")
						D4_Y1 = D4_Y0 + Dfactor * 3
						D5_Y0 = D4_Y1 + Dfactor
						D5_Y1 = D5_Y0 + Dfactor * 3

				if not 'XR0_2' in locals() or 'E1_Y0' in locals():
					errorfactors += 1
					# print("couldnt find XR0_2 or E1_Y0")
					Q_E1 = self.search(f"1.{labeldict['E1'][self.lang]}", page, page_ocr)
					if Q_E1:
						if not type(Q_E1)== fitz.fitz.Rect:
							Q_E1[0] = Q_E1[0].rect
						found = Q_E1
						XR0_2 = found[0][0]
						E1_Y0 = found[0][3]
					else:
						print("efactor used on e1_y0, xr0_2")
						errorfactors += 1
						E1_Y0 = EY0 + Efactor*2
						XRO_2 = page.bound()[2]/2 + 5
				if not 'E1_Y1' in locals() or 'E2_Y0' in locals():
					errorfactors += 1
					# print("couldnt find E1_Y1 or E2_Y0")
					Q_E2 = self.search(f"2.{labeldict['E2'][self.lang]}", page, page_ocr)
					if Q_E2:
						if not type(Q_E2)== fitz.fitz.Rect:
							Q_E2[0] = Q_E2[0].rect
						found = Q_E2
						E1_Y1 = found[0][1] - 20
						E2_Y0 = found[0][3]
					else:
						print("efactor used on e1_y1, e2_y0")
						errorfactors += 1
						E1_Y1 = EY0 + (Efactor * 15.5)
						E2_Y0 = EY0 + (Efactor * 17)
				if not 'E2_Y1' in locals() or 'E3_Y0' in locals():
					errorfactors += 1
					# print("couldnt find E2_Y1 or E3_Y0")
					Q_E3 = self.search(f"3.{labeldict['E3'][self.lang]}", page, page_ocr)
					if Q_E3:
						if not type(Q_E3)== fitz.fitz.Rect:
							Q_E3[0] = Q_E3[0].rect
						found = Q_E3
						E2_Y1 = found[0][1]
						E3_Y0 = found[0][3]
					else:
						print("efactor used on e2_y1, e3_y0")
						errorfactors += 1
						E2_Y1 = EY0 + Efactor * 29.5
						E3_Y0 = EY0 + Efactor * 30.5
				area_D2 = fitz.Rect(XL0, D2_Y0, XL1, D2_Y1)
				area_D3 = fitz.Rect(XL0, D3_Y0, XL1, D3_Y1)
				area_D4 = fitz.Rect(XL0, D4_Y0, XL1, D4_Y1)
				area_D5 = fitz.Rect(XL0, D5_Y0, XL1, D5_Y1)
				area_E1 = fitz.Rect(XR0_2, E1_Y0, XR1, E1_Y1)
				area_E2 = fitz.Rect(XR0_2, E2_Y0, XR1, E2_Y1)
				area_E3 = fitz.Rect(XR0_2, E3_Y0, XR1, YFOOTER)
				areas_page2 = [
					area_D2, area_D3, area_D4, area_D5, area_E1, area_E2, area_E3
				]


				if self.OCR_TRIGGER:
					pmap_D2 = page.get_pixmap(clip = area_D2)
					tmppdf = pmap_D2.pdfocr_tobytes()
					tmpdoc = fitz.open("pdf", tmppdf)
					text_D2 = tmpdoc[0].get_text()

					pmap_D3 = page.get_pixmap(clip = area_D3)
					tmppdf = pmap_D3.pdfocr_tobytes()
					tmpdoc = fitz.open("pdf", tmppdf)
					text_D3 = tmpdoc[0].get_text()

					pmap_D4 = page.get_pixmap(clip = area_D4)
					tmppdf = pmap_D4.pdfocr_tobytes()
					tmpdoc = fitz.open("pdf", tmppdf)
					text_D4 = tmpdoc[0].get_text()

					pmap_D5 = page.get_pixmap(clip = area_D5)
					tmppdf = pmap_D5.pdfocr_tobytes()
					tmpdoc = fitz.open("pdf", tmppdf)
					text_D5 = tmpdoc[0].get_text()

					pmap_E1 = page.get_pixmap(clip = area_E1)
					tmppdf = pmap_E1.pdfocr_tobytes()
					tmpdoc = fitz.open("pdf", tmppdf)
					text_E1 = tmpdoc[0].get_text()

					pmap_E2 = page.get_pixmap(clip = area_E2)
					tmppdf = pmap_E2.pdfocr_tobytes()
					tmpdoc = fitz.open("pdf", tmppdf)
					text_E2 = tmpdoc[0].get_text()

					pmap_E3 = page.get_pixmap(clip = area_E3)
					tmppdf = pmap_E3.pdfocr_tobytes()
					tmpdoc = fitz.open("pdf", tmppdf)
					text_E3 = tmpdoc[0].get_text()
				else:
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
		if not os.path.exists('data'):
			os.mkdir('data')
		if not os.path.exists('data/hq'):
			os.mkdir('data/hq')
		if not os.path.exists('data/mq'):
			os.mkdir('data/mq')
		if not os.path.exists('data/lq'):
			os.mkdir('data/lq')
		if not os.path.exists('redacted'):
			os.mkdir('redacted')
		if not os.path.exists('redacted/hq'):
			os.mkdir('redacted/hq')
		if not os.path.exists('redacted/mq'):
			os.mkdir('redacted/mq')
		if not os.path.exists('redacted/lq'):
			os.mkdir('redacted/lq')
		
		if errorfactors < 1:
			quality_dir = 'hq'
		elif 0 < errorfactors < 6:
			quality_dir = 'mq'
		else:
			quality_dir = 'lq'

		with open(f'data/{quality_dir}/{self.filename[:-4]}.json', 'w+') as f:
			json.dump(data, f)
		doc.save(f'redacted/{quality_dir}/{self.filename[:-4]}_REDACTED.pdf')
		print("Successfully redacted")

if __name__ == "__main__":
	path = 'testing.pdf'
	subdir = '.'
	# path = '000865165 5947-2018-1625.pdf'
	# subdir = 'pdfs'
	redactor = Redactor(path, subdir)
	redactor.redaction() 
