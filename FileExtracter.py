from email.mime import text
from http import client
import os
from tkinter import Image
from urllib import response
import pdfplumber
from docx import Document
from openai import OpenAI
from dotenv import load_dotenv
import json
from PIL import Image
import email
import csv
import pytesseract 


load_dotenv(override=True)

class FileExtracter:
    def __init__(self): #don't init anything because the folder is different for each user
        pass

    def get_files(self, folder):
        SUPPORTED = (
            ".pdf", ".docx", ".txt", ".md", ".rst",   # documents
            ".png", ".jpg", ".jpeg", ".tiff", ".bmp",  # images
            ".eml", ".pst",                              # emails
            ".csv", ".msg"                                # spreadsheets
        )
        files = []
        for root, dirs, filenames in os.walk(folder):  # os.walk goes into subfolders
            for file in filenames:
                if file.endswith(SUPPORTED):
                    files.append(os.path.join(root, file))
        return files


    def extract_text(self, file_path):
        def extract_text_from_image(file_path):
            '''
            This is called when images are uploaded. Example use case is if someone uploads a scanned document, 
            we can use OCR to extract the text from the image and then feed that text into the model for summarization and metadata extraction.
            '''
            img = Image.open(file_path)

            text = pytesseract.image_to_string(img)
            
            return text

        if file_path.endswith(".pdf"):
            with pdfplumber.open(file_path) as pdf:
                return "\n".join(page.extract_text() or "" for page in pdf.pages)

        elif file_path.endswith(".docx"):
            doc = Document(file_path)
            return "\n".join(p.text for p in doc.paragraphs)

        elif file_path.endswith((".txt", ".md", ".rst")):
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        
        elif file_path.endswith(".csv"):
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                return "\n".join([", ".join(row) for row in reader])
            
        #for now just extracting text from the email, not attachments
        elif file_path.endswith((".eml")): 
            with open(file_path, "r", encoding="utf-8") as f:
                msg = email.message_from_file(f)
                parts = []
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            parts.append(part.get_payload(decode=True).decode("utf-8", errors="ignore"))
                else:
                    parts.append(msg.get_payload(decode=True).decode("utf-8", errors="ignore"))
                return "\n".join(parts)
        
       #this will extract attachments from the emails
        elif file_path.endswith((".eml")):
            with open(file_path, "r", encoding="utf-8") as f:
                msg = email.message_from_file(f)
                attachments = []
                for part in msg.walk():
                    if part.get_content_disposition() == "attachment":
                        filename = part.get_filename()
                        if filename:
                            attachments.append(filename)
                            with open(os.path.join("attachments", filename), "wb") as att_file:
                                att_file.write(part.get_payload(decode=True))
                return "\n".join(attachments)   
            
        elif file_path.endswith((".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff")):
            return extract_text_from_image(file_path)
                
        return ""
    
