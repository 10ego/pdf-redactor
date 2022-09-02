import fitz
import re
import json
import hashlib
import os
from unidecode import unidecode
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
    
    def __init__(self, filename, subdir, savesubdir):
        self.filename = filename
        self.subdir = subdir
        self.savesubdir = savesubdir
        self.path = subdir + '/' + self.filename
        self.lang = ''
        self.errorfactor = 0
        self.page1Chk = False
        self.page2Chk = False
        self.labeldict = {
                'footer':{
                    'en':'a program of med',
                    'fr':'un programme de med'
                },
                'A':{
                    'en':'reporter information',
                    'fr':'renseignements sur le'
                },
                'A2':{
                    'en':'reporter contact info',
                    'fr':'coordonnées du déclar'
                },
                'A6':{
                    'en':'date submit',
                    'fr':'date de '
                },
                'A7':{
                    'en':'name and address',
                    'fr':'nom et adresse'
                },
                'B':{
                    'en':'incident information',
#                   'fr':"renseignements sur l'incident"    
                    'fr':"renseignements sur l"
                },
                'B4':{
                    'en':'patient consequences',
                    'fr':'conséquences pour le patient'
                },
                'B5':{
                    'en':'details of incident',
#                   'fr':"détails sur l'incident"
                    'fr':"détails sur l"
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
#                   'fr':"nom de l'éstablissement de soins" # ' (U+0027) are getting caught as ’ (U+2019) sometimes and causing problems with identification 
                    'fr':"nom de l"
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
                    'en':'Investigative actions',
#                   'fr':"mesures d'enquê"
                    'fr':"mesures d"
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

    def get_area(self, key, only_alphabet=False, footer=False):
        if not only_alphabet:
            question_no = key[1:]
        elif footer:
            question_no = ''
        else:
            question_no = key
        p = self.page.get_textpage_ocr(dpi=300, full=True)
        joiners = [". ", ".", ", ", ","]
        A = None
        if not A:
            if self.lang == "fr":
                for joiner in joiners:
                    A = p.search(question_no + joiner + unidecode(self.labeldict[key][self.lang]))
                    if A:
                        break
        if not A:
            for joiner in joiners:
                A = p.search(question_no + joiner + self.labeldict[key][self.lang])
                if A:
                    break
        if A:
            return A[0]
        else:
            return None

    def get_pmaptext(self, area):
        pmap = self.page.get_pixmap(dpi=300, clip = area)
        tmppdf = pmap.pdfocr_tobytes()
        tmpdoc = fitz.open("pdf", tmppdf)
        return tmpdoc[0].get_text()

    def redaction(self):
        doc = fitz.open(self.path)
        pages_to_delete = []
        bounding = doc[0].bound()
        breaker = False
        for page in doc:
            # Quickly check if the page is ready to scan or requires OCR handling
            page_ocr = page.get_textpage_ocr(dpi=300, full=True)
            if page_ocr.search("A. "+self.labeldict["A"]["en"]):
                self.lang = 'en'
                break
            elif page_ocr.search("A. "+self.labeldict["A"]["fr"]):
                self.lang = 'fr'
                break
        if not self.lang:
            raise "NoLanguageFoundError"
#        print("Language:", self.lang)
        for page in doc:
            if breaker:
                pages_to_delete.append(page.number)
                continue
            self.page = page
            currentpage = 0
            breaker = False
            XL1 = page.bound()[2]/2 - 5
            XR0 = page.bound()[2]/2 + 5
            
            # Find reference points
            # page 1
            FOOTER = self.get_area('footer', True)
            A = self.get_area('A', True)
            B = self.get_area('B', True)
            D = self.get_area('D', True)
            E = self.get_area('E', True)
            if FOOTER:
                FOOTERY = FOOTER[1]
            if A:
                currentpage = 1
            elif D:
                currentpage = 2
#            print("Page:", currentpage)
            if currentpage == 1:
                YFactor = A[3][1] - A[1][1]
                YFactor_small = YFactor / bounding[3] * 200
#                print(YFactor, YFactor_small)
                A2 = self.get_area('A2')
                A6 = self.get_area('A6')
                A7 = self.get_area('A7')
                B4 = self.get_area('B4')
                B5 = self.get_area('B5')

                try:
                    XL0 = A[0][0] - 5
                    XL1 = bounding[2]/2 - 5
                    XR0 = bounding[2]/2 + 5
                    XR1 = bounding[2] - XL0
                    if A2:
                        A2_Y0 = A2[3][1] + YFactor_small
                    else: print("A2 not found")
                    if A7:
                        A2_Y1 = A7[1][1] - YFactor * 2.5
                    else:
                        A2_Y1 = A6[3][1] + YFactor
                    if B4:
                        B4_Y0 = B4[3][1] + YFactor_small
                    else: print("A4 not found")
                    if FOOTER:
                        B4_Y1 = FOOTERY - YFactor
                    else:
                        B4_Y1 = B4_Y0 + (A2_Y1 - A2_Y0) * 2
                    if B5:
                        B5_Y0 = B5[3][1] + YFactor_small
                    else:
                        B5_Y0 = B[3][1] + YFactor * 2.5
                    B5_Y1 = B4_Y1
                    
                    area_A2 = fitz.Rect(XL0, A2_Y0, XL1, A2_Y1)
                    area_B4 = fitz.Rect(XL0, B4_Y0, XL1, B4_Y1)
                    area_B5 = fitz.Rect(XR0, B5_Y0, XR1, B5_Y1)
                    areas_page1 = [area_A2, area_B4, area_B5]
                    text_A2 = self.get_pmaptext(area_A2)
                    text_B4 = self.get_pmaptext(area_B4)
                    text_B5 = self.get_pmaptext(area_B5)
                    text_page1 = [text_A2, text_B4, text_B5]
                    hash_page1 = [hashlib.md5(x.encode()).hexdigest() for x in text_page1]
                    assert len(areas_page1) == len(text_page1)
                    [page.add_redact_annot(x[0], text=x[1], fontsize=9, fill=(1,1,1)) for x in zip(areas_page1, hash_page1)]
                except Exception as e:
                    print(e.args)
                    
            elif currentpage == 2:
                breaker=True
                D2 = self.get_area('D2')
                D3 = self.get_area('D3')
                D4 = self.get_area('D4')
                D5 = self.get_area('D5')
                E1 = self.get_area('E1')
                E2 = self.get_area('E2')
                E3 = self.get_area('E3')
                try:
                    if D2:
                        D2_Y0 = D2[3][1] + YFactor_small
                    else: print("D2 not found")
                    if D3:
                        D2_Y1 = D3[1][1] - YFactor_small
                        D3_Y0 = D3[3][1] + YFactor_small
                    else: print("D3 not found")
                    if D4:
                        D3_Y1 = D4[1][1] - YFactor_small
                        D4_Y0 = D4[3][1] + YFactor_small
                    else: print("D4 not found")
                    if D5:
                        D4_Y1 = D5[1][1] - YFactor_small
                        D5_Y0 = D5[3][1] + YFactor_small
                        D5_Y1 = D5_Y0 + D4_Y1 - D4_Y0
                    else: print("D5 not found")
                    if E1:
                        E1_Y0 = E1[3][1] + YFactor_small
                        XR0 = E1[0][0]
                    else: print("E1 not found")
                    if E2:
                        E1_Y1 = E2[1][1] - YFactor * 2
                        E2_Y0 = E2[3][1] + YFactor_small
                    else: print("E2 not found")
                    if E3:
                        E2_Y1 = E3[1][1] - YFactor_small
                        E3_Y0 = E3[3][1] + YFactor_small
                        E3_Y1 = E3_Y0 + (D4_Y1 - D4_Y0) * 4
                    else: print("E3 not found")
                    
                    area_D2 = fitz.Rect(XL0, D2_Y0, XL1, D2_Y1)
                    area_D3 = fitz.Rect(XL0, D3_Y0, XL1, D3_Y1)
                    area_D4 = fitz.Rect(XL0, D4_Y0, XL1, D4_Y1)
                    area_D5 = fitz.Rect(XL0, D5_Y0, XL1, D5_Y1)
                    area_E1 = fitz.Rect(XR0, E1_Y0, XR1, E1_Y1)
                    area_E2 = fitz.Rect(XR0, E2_Y0, XR1, E2_Y1)
                    area_E3 = fitz.Rect(XR0, E3_Y0, XR1, E3_Y1)
                    areas_page2 = [area_D2, area_D3, area_D4, area_D5, area_E1, area_E2, area_E3]
                    text_D2 = self.get_pmaptext(area_D2)
                    text_D3 = self.get_pmaptext(area_D3)
                    text_D4 = self.get_pmaptext(area_D4)
                    text_D5 = self.get_pmaptext(area_D5)
                    text_E1 = self.get_pmaptext(area_E1)
                    text_E2 = self.get_pmaptext(area_E2)
                    text_E3 = self.get_pmaptext(area_E3)
                    text_page2 = [text_D2, text_D3, text_D4, text_D5, text_E1, text_E2, text_E3]
                    hash_page2 = [hashlib.md5(x.encode()).hexdigest() for x in text_page2]
                    assert len(areas_page2) == len(text_page2)
                    [page.add_redact_annot(x[0], text=x[1], fontsize=9, fill=(1,1,1)) for x in zip(areas_page2, hash_page2)]
                except Exception as e:
                    print(e.args)
            else:
                pages_to_delete.append(page.number)
                continue
            page.apply_redactions()

        quality_dir = self.savesubdir

        # saving it to a new pdf
        if not os.path.exists('data'):
            os.mkdir('data')
        if not os.path.exists(f'data/{quality_dir}'):
            os.mkdir(f'data/{quality_dir}')
        if not os.path.exists('redacted'):
            os.mkdir('redacted')
        if not os.path.exists(f'redacted/{quality_dir}'):
            os.mkdir(f'redacted/{quality_dir}')

        with open(f'data/{quality_dir}/{self.filename[:-4]}.json', 'w+') as f:
            data = dict({(x[0],x[1].encode().decode()) for x in zip(hash_page1+hash_page2, text_page1+text_page2)})
            json.dump(data, f)
        doc.delete_pages(pages_to_delete)
        doc.scrub()
        doc.save(f'redacted/{quality_dir}/{self.filename[:-4]}_REDACTED.pdf')
        print("Successfully redacted")
        doc.close()

if __name__ == "__main__":
    path = 'testing-fr.pdf'
    subdir = '.'
    subpath = 'other'
    redactor = Redactor(path, subdir, savesubdir)
    redactor.redaction()