#Sricharan Kotala 

'''
input a file, extract contents, give it a name, put it into a certain directory, log location, 


pip install openai pdfplumber python-docx pytesseract pillow\

    openAi -> the actual AI calls/agentic part of this project
    pdfplumber -> Reads text from PDFs
    python-docx -> reads text from docs
    pytesseract -> Optical Character Recognition (OCR) is a technology that 
    converts images of typed, handwritten, or printed text into machine-encoded, editable, and searchable digital text
    pillow -> Image processing library (needed for OCR)

'''
import datetime
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
import shutil
from PIL import Image

import pytesseract 


load_dotenv(override=True)
GLOBAL_LOG = "document_log.json"


extract_document_details_json = {
    "name": "extract_document_details",
    "description": "Extract structured metadata from a legal document including its name, type, parties, key terms, and date",
    "parameters": {
        "type": "object",
        "properties": {
            "name_of_document": {
                "type": "string",
                "description": "Name of file according to a standardized naming convention"
            },
            "document_type": {
                "type": "string",
                "description": "The type of document e.g. NDA, MSA, Agreement, Contract"
            },
            "parties": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of names of the parties involved in the document"
            },
            "key_terms": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of important terms or clauses found in the document"
            },
            "date": {
                "type": "string",
                "description": "The date of the document in YYYY-MM-DD format if possible"
            },
            "short_description": {
                "type": "string",
                "description": "A one line summary of what this document is about"
            },
            "confidence": {
                "type": "number",
                "description": "Confidence score between 0 and 1 on the accuracy of the extraction"
            }
        },
        "required": ["name_of_document", "document_type", "parties"],
        "additionalProperties": False
    }
}
tool = [{"type": "function", "function": extract_document_details_json}]


class FileManager:
    def __init__(self): #don't init anything because the folder is different for each user
        pass

    def get_files(self, folder):
        SUPPORTED = (
            ".pdf", ".docx", ".txt", ".md", ".rst",   # documents
            ".png", ".jpg", ".jpeg", ".tiff", ".bmp",  # images
            ".eml",                                     # emails
            ".csv",                                     # spreadsheets
            ".py", ".ipynb"                             # code
        )
        files = []
        # for file in os.listdir(folder): #for each file in a folder
        #     if file.endswith((SUPPORTED)): #there are probably more combinations...?
        #         files.append(os.path.join(folder, file)) #puts every file in the folder into a list (files)
        for root, dirs, filenames in os.walk(folder):  # os.walk goes into subfolders
            for file in filenames:
                if file.endswith(SUPPORTED):
                    files.append(os.path.join(root, file))
        return files


    def extract_text(self, file_path):
        if file_path.endswith(".pdf"):
            with pdfplumber.open(file_path) as pdf:
                return "\n".join(page.extract_text() or "" for page in pdf.pages)

        elif file_path.endswith(".docx"):
            doc = Document(file_path)
            return "\n".join(p.text for p in doc.paragraphs)

        elif file_path.endswith(".txt"):
            with open(file_path, "r") as f:
                return f.read()
            
        elif file_path.endswith((".txt", ".md", ".rst")):
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
            
        # elif file_path.endswith((".png", ".jpg", ".jpeg", ".tiff", ".bmp")):
        #     img = Image.open(file_path)
        #     return pytesseract.image_to_string(img)
        
        elif file_path.endswith(".csv"):
            import csv
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                return "\n".join([", ".join(row) for row in reader])
        
        return ""


class AgenticManager:
    def __init__(self):  #now I don't need to initialize the OpenAI client in the main function, I can just do it here and it will be available for all methods in this class
        load_dotenv(override=True)
        self.openai = OpenAI()
        self.fileManager = FileManager() #create instance of FileManager
        # os.makedirs(self.base_folder, exist_ok=True)

        
    def summarize(self, file_path):  # accept file path as argument
        #text that comes from the FileManager class
        text = self.fileManager.extract_text(file_path)

        system_message = f" You are a helpful assistant that summarizes text for the legal firm of Minnesota Public Radio. \
        You're job is to analyze {text} and create a one-line blurb, summary of the document, and a list of bullet points that highlight key information/important insights from the document. \
        Provide your solution in Rich console markup. \
        "
        response = self.openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": text}
            ] 
        )
        return response.choices[0].message.content.strip()
    
    
    def json_creator(self, text):
        response = self.openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": f"Extract details from this legal document:\n\n{text}"}
            ],
            tools=tool,
            tool_choice={"type": "function", "function": {"name": "extract_document_details"}}
        )  

        tool_call = response.choices[0].message.tool_calls[0]
        metadata = json.loads(tool_call.function.arguments)  
        #now just json dump into json file

        try:
            with open(GLOBAL_LOG, "r") as f:
                logs = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
                logs = []  # file doesn't exist OR is empty, start fresh
        
        logs.append({
            "file_path": "path/to/file",  # You can replace this with the actual
            "metadata": metadata,
            "timestamp": datetime.datetime.now().isoformat()
        })
        with open(GLOBAL_LOG, "w") as f:
            json.dump(logs, f, indent=4)

        return metadata
    
    def generate_directory(self, file_path, save_folder):
        pass

    def log_location(self, file_path, json_data):
        pass

    def email_summary(self, file_path):
        pass

# TODO
    '''
    1. extract date from a document to add to json 
        - can do this in the json_creator function by adding a date field to the tool and asking the model to extract it
        - also can use the date to splice directory structure by date (
    2. implelemtn reading from emails
    3. Clean up how the output looks 
    4. Add confidence score to the json output ALWAYS
    5. Create email sender
        - is it possible to add those documents in the email?
    
    '''

    
    
if __name__ == "__main__":
    TEST_FOLDER = "/Users/koala07/Documents/Job App Materials"
    TEST_FILE_INDEX = 14  # change this one number to test a different file

    f = FileManager()
    a = AgenticManager()

    # ── TEST 1: FileManager.get_files() ─────────────────────────
    print("\n── TEST 1: get_files()")
    files = f.get_files(TEST_FOLDER)
    assert len(files) > 0, "❌ No files found"

    print("\n\n")

    for i, file in enumerate(files):
        print(f"{i}: {file}")

    print("\n\n")

    print(f"✅ Found {len(files)} files")

    print("\n\n")

    # pin to one file for all tests below
    test_file = files[TEST_FILE_INDEX]
    print(f"🎯 Testing with: {test_file}")
    # ── TEST 2: FileManager.extract_text() ──────────────────────
    print("\n── TEST 2: extract_text()")
    text = f.extract_text(test_file)
    assert isinstance(text, str), "❌ Text is not a string"
    assert len(text) > 0, "❌ Extracted text is empty"
    print(f"✅ Extracted {len(text)} characters")
    print(f"  {text}")

    # ── TEST 3: AgenticManager.summarize() ──────────────────────
    print("\n── TEST 3: summarize()")
    summary = a.summarize(test_file)
    assert isinstance(summary, str), "❌ Summary is not a string"
    assert len(summary) > 0, "❌ Summary is empty"
    print(f"✅ Summary generated:")
    print(f"   {summary}") 

    # ── TEST 4: AgenticManager.json_creator() ───────────────────
    print("\n── TEST 4: json_creator()")
    metadata = a.json_creator(text)
    assert isinstance(metadata, dict), "❌ Metadata is not a dict"
    assert "name_of_document" in metadata, "❌ Missing name_of_document"
    assert "document_type" in metadata, "❌ Missing document_type"
    print(f"✅ Metadata extracted:")
    for key, value in metadata.items():
        print(f"   {key}: {value}")

    print("\n── ALL TESTS PASSED ✅")