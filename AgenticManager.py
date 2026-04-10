from FileExtracter import FileExtracter
from openai import OpenAI
from dotenv import load_dotenv
import json
import shutil
import os
import datetime


# Load the JSON configuration for the tool
with open("config.json", "r", encoding="utf-8") as f:
    extract_document_details_json = json.load(f)

tool = [{"type": "function", "function": extract_document_details_json}]

# Base folder for organized documents
# Underneath this folder, documents will be organized into subfolders.
MAIN_OUTPUT_FOLDER = "MPR_Legal_Documents" 
GLOBAL_LOG = "document_log.json"


class AgenticManager:
    def __init__(self):
        load_dotenv(override=True)
        self.openai = OpenAI()
        self.fileManager = FileExtracter() #create instance of FileExtracter

        
    def summarize(self, file_path):  
        '''
        Summarize a document using the OpenAI API.

        This function reads a file from the given path, extracts its text content,
        and generates a structured summary. The output includes:
        - A one-line blurb
        - A detailed summary
        - Bullet points highlighting key insights

        The response is formatted using Rich console markup.

        Args:
            file_path (str): Path to the input document.

        Returns:
            str: Formatted summary output.
        '''
        
        text = self.fileManager.extract_text(file_path) 

        system_message = f" You are a helpful assistant that summarizes text for the legal firm of Minnesota Public Radio. \
        You're job is to analyze {text} and create a one-line blurb, summary of the document, and a list of bullet points that\
        highlight key information/important insights from the document. \
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
                {"role": "user", "content": f"Extract details from this legal document and use the JSON schema provided in your tool:\n\n{text}. Ensure sure you give the document a name according to a standardized naming convention. "}
            ],
            tools=tool,
            tool_choice={"type": "function", "function": {"name": "extract_document_details"}}
        )  

        tool_call = response.choices[0].message.tool_calls[0]
        metadata = json.loads(tool_call.function.arguments)  

        #now just json dump into the global log file
        try:
            with open(GLOBAL_LOG, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
                logs = []  # file doesn't exist OR is empty, start fresh
    

        with open(GLOBAL_LOG, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=4)

        return metadata
    
    @staticmethod
    def determine_destination(metadata) -> str:
        #This function must read from the generated json and determine where to save the file based on the metadata. 
        #For example, if the document type is "contract", it should be saved in a "contracts" folder. If the parties include "John Doe", it should be saved in a "John Doe" folder. 
        # The function should return the destination path for the file.

        def sanitize(value):
            value = str(value or "").strip()
            cleaned = "".join(char if char.isalnum() or char in (" ", "-", "_") else "_" for char in value)
            return cleaned or "Unknown"
        
        raw_document_type = str(metadata.get("document_type", "documents")).strip().lower()
        normalized_types = {
            "nda": "ndas",
            "non-disclosure agreement": "ndas",
            "non-disclosure agreements": "ndas",
            "contract - non-disclosure agreement": "ndas",
            "contract - non-disclosure agreements": "ndas",
            "msa": "msas",
            "master services agreement": "msas",
            "master services agreements": "msas",
            "contract - master services agreement": "msas",
            "license agreement": "license agreements",
            "license agreements": "license agreements",
            "release agreement": "release agreements",
            "release agreements": "release agreements",
            "sponsorship agreement": "sponsorship agreements",
            "sponsorship agreements": "sponsorship agreements",
            "service agreement": "service agreements",
            "service agreements": "service agreements",
            "contract amendment": "contract amendments",
            "contract amendments": "contract amendments",
            "statement of work": "statement of works",
            "contract - statement of work": "statement of works",
            "contract - statement of works": "statement of works",
            "archive services agreement": "archive services agreements",
            "archive services agreements": "archive services agreements",
            "archive note": "archive notes",
            "archive notes": "archive notes",
            "letter": "letters",
            "letters": "letters",
        }

        document_type = normalized_types.get(raw_document_type, sanitize(raw_document_type).lower())
        if not document_type.endswith("s"):
            document_type = f"{document_type}s"

        parties = metadata.get("parties", [])
        if parties:
            return os.path.join(MAIN_OUTPUT_FOLDER, document_type, sanitize(parties[0]))

        return os.path.join(MAIN_OUTPUT_FOLDER, document_type)


    @staticmethod
    def place_file(file_path, metadata_path):
        #this function will move the file to the destination determined by the determine_destination function. It will also update the json with the new file path. 
        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)

        destination_folder = AgenticManager.determine_destination(metadata)
        os.makedirs(destination_folder, exist_ok=True)

        destination_path = os.path.join(destination_folder, os.path.basename(file_path))
        shutil.copy2(file_path, destination_path)

        metadata["new_file_path"] = destination_path

        try:
            with open(GLOBAL_LOG, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            logs = []

        logs.append({
            "file_path": destination_path,
            "metadata": metadata,
            "timestamp": datetime.datetime.now().isoformat()
        })

        with open(GLOBAL_LOG, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=4)

        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=4)

        return destination_path


    def search_for_file(self, file_path):
        if os.path.exists(file_path):
            return os.path.abspath(file_path)

        file_name = os.path.basename(file_path).lower()

        for root, _, files in os.walk("."):
            for current_file in files:
                if file_name == current_file.lower():
                    return os.path.abspath(os.path.join(root, current_file))

        return None
    
