import fitz
import re

class Redactor:
'''
 Fields to redact:
* A.2. Reporter Contact Information
* B.4. Patient Consequences
* B.5. Details of Incident
* D.2. Name of Complainant
* D.3. Name of Health Care Facility (if applicable)
* D.4. Address
* D.5. Telephone No. and/or E-mail Address
* E.1. Investigative Actions and Timeline
* E.2. Root Cause of Problem
* E.3. Corrective Actions taken as a result of the investigation
'''
    # @staticmethod
    # def get_sensitive_data(lines):
    #     # EMAIL_REG = r"([\w\.\d]+\@[\w\d]+\.[\w\d]+)"
    #     TARGET_REG = r"Reporter Contact Information"
    #     for line in lines:
           
    #         # matching the regex to each line
    #         if re.search(TARGET_REG, line, re.IGNORECASE):
    #             search = re.search(TARGET_REG, line, re.IGNORECASE)
                 
    #             # yields creates a generator
    #             # generator is used to return
    #             # values in between function iterations
    #             yield search.group()
 
    def __init__(self, path):
        self.path = path

    def redaction(self):
        # opening the pdf
        doc = fitz.open(self.path)
         
        # iterating through pages
        for page in doc:
           
            # _wrapContents is needed for fixing
            # alignment issues with rect boxes in some
            # cases where there is alignment issue
            page.wrap_contents()
             
            # align box area to match different PDF formats
            # using a few reference points that are known to exist

            # First page of form (real) detection
            # Also finds left edge reference point
            area_A2 = page.search_for('2. reporter contact information')
            if area_A2:
                found = area_A2
                XL0 = found[0][0]
                YL0 = found[0][3] + 2
            area_B5 = page.search_for('5. details of incident')
            if area_B5:
                found = area_B5
                XR0 = found[0][0]
                YR0 = found[0][3] + 2
                XL1 = found[0][0] - 10
            area_B7 = page.search_for('7. Name and address') # Reference for Reporter Contact Information Y1
            if area_B7:
                found = area_B7
                YL1 = found[0][1] - 17
            area_B4 = page.search_for('4. Patient consequences')
            if area_B4:
                found = area_B4
                YL2
            footer_area = page.search_for('a program of medeffect canada')
            if footer_area:
                found = footer_area
                YFOOTER = found[0][1]

            areas_page1 = [fitz.IRect(XL0, YL0, XL1, YL1), fitz.IRect()] #, fitz.IRect(35, 565, 300, 585)

            # drawing outline over sensitive datas
            # page.get_text(clip=area)
            [page.add_redact_annot(area, fill = (0, 0, 0)) for area in areas_page1]
            # [page.add_redact_annot(area, text='REDACTED_DATA') for area in areas]
                
            # applying the redaction
            page.apply_redactions()
            break
        # saving it to a new pdf
        doc.save('replaced5.pdf')
        print("Successfully redacted")

if __name__ == "__main__":
    path = 'testing.pdf'
    path = 'pdfs/000922866.pdf'
    
    redactor = Redactor(path)
    redactor.redaction() 
