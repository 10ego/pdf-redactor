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
	
    def __init__(self, filename, subdir):
        self.filename = filename
		self.path = subdir+'/'+self.filename
		self.OCR_TRIGGER = True
		self.lang = ''
        self.errorfactor = 0
        self.labeldict = {
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

    def search(self, phrase):
        if self.OCR_TRIGGER:
            self.page_ocr
        else:
            do()
        return

    def reference_search(self, phrase):
        try:
            p = self.page_ocr.get_textpage_ocr(dpi=300, full=True)
            A = p.search(phrase)
            RECT = A[0].rect
        except:
            p = self.page
            A = p.search_for(phrase)
            RECT = A[0]
        return RECT

    def redaction(self):
        
        doc = fitz.open(self.path)
        for page in doc:
            # Quickly check if the page is ready to scan or requires OCR handling
            XL1_1 = page.bound()[2]/2 - 5
            XR0_1 = page.bound()[2]/2 + 5
            if page.search_for(labeldict["A"]["en"]):
                self.lang = 'en'
                self.OCR_TRIGGER = False
                break
            elif page.search_for(labeldict["A"]["fr"]):
                self.lang = 'fr'
                self.OCR_TRIGGER = False
                break
            else:
                self.OCR_TRIGGER = True
                print("OCR triggered..")
                page_ocr = page.get_textpage_ocr(dpi=300, full=True)
                self.page_ocr = page_ocr
                if page_ocr.search(labeldict["A"]["en"]):
                    self.lang = 'en'
                elif page_ocr.search(labeldict["A"]["fr"]):
                    self.lang = 'fr'

        for page in doc:
            try:
                page.wrap_contents()
            except:
                pass
            
            # Find reference points

            A = self.reference_search(f'A. {self.labeldict["A"][self.lang]}')
            XL0_1 = A[0] - 5
            B = self.reference_search(f'B. {self.labeldict["B"][self.lang]}')
            # C = self.reference_search(f'C. {self.labeldict["C"][self.lang]}')
            D = self.reference_search(f'D. {self.labeldict["D"][self.lang]}')
            E = self.reference_search(f'E. {self.labeldict["E"][self.lang]}')
            if E:
                XR0_1 = E[0] - 5


            

            Q_A2 = self.search(f'2. {labeldict["A2"][self.lang]}')
            if Q_A2: