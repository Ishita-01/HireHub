import os
import io
import re
import base64
from docx import Document
from googleapiclient.discovery import build
from .base import BaseScraper, ScrappedJob

class OnCampusScraper(BaseScraper):
    def __init__(self, service=None):
        # Assumes Gmail API service is authenticated elsewhere
        self.service = service 

    def fetch_jobs(self) -> list[ScrappedJob]:
        campus_jobs = []
        # 1. Search for emails from TIET Placement Cell
        query = "from:spr@thapar.edu has:attachment filename:.docx"
        results = self.service.users().messages().list(userId='me', q=query).execute()
        print(f"DEBUG: Found {len(results.get('messages', []))} messages matching query.")

        for msg in results.get('messages', []):
            print(f"DEBUG: Processing message ID: {msg['id']}")
            message = self.service.users().messages().get(userId='me', id=msg['id']).execute()
            for part in message['payload'].get('parts', []):
                if part['filename'].endswith('.docx'):
                    att_id = part['body']['attachmentId']
                    att = self.service.users().messages().attachments().get(
                        userId='me', messageId=msg['id'], id=att_id).execute()
                    
                    # 2. Extract text from the downloaded .docx
                    data_str = att['data']

                    # 1. Base64url uses '-' and '_' instead of '+' and '/'
                    # 2. Decode the string into bytes
                    file_bytes = base64.urlsafe_b64decode(data_str)
                    file_data = io.BytesIO(file_bytes)
                    text = self.extract_text_from_docx(file_data)
                    
                    # 3. Parse fields using Regex
                    job = self.parse_campus_data(text)
                    if job:
                        campus_jobs.append(job)
        return campus_jobs

    def parse_campus_data(self, text: str) -> ScrappedJob:
    # Use \s+ to handle tabs (\t) and multiple spaces
        company_match = re.search(r"Name of the Organization:\s*(.*)", text, re.IGNORECASE)
        # The profile is usually on the line after the organization
        profile_match = re.search(r"Organization:.*?\n\s*(.*)", text, re.DOTALL | re.IGNORECASE)
        link_match = re.search(r"https://forms.gle/\S+", text)
        location_match = re.search(r"Job location:\s*(.*)", text, re.IGNORECASE)
        deadline_match = re.search(r"Google link by\s*(.*?by.*?(?:AM|PM))", text, re.IGNORECASE)

        if company_match and profile_match and link_match:
            company = company_match.group(1).strip()
            # Clean up common artifacts from TIET notices
            profile = profile_match.group(1).split('(')[0].strip() 

            return ScrappedJob(
                title=profile,
                company=company,
                location=location_match.group(1).strip() if location_match else "Bengaluru",
                employment_type="Summer Internship",
                apply_link=link_match.group(0).strip(),
                source="onCampus",
                deadline=deadline_match.group(1).strip() if deadline_match else None

            )
        return None

    def extract_text_from_docx(self, file_stream):
        doc = Document(file_stream)
        return "\n".join([para.text for para in doc.paragraphs])