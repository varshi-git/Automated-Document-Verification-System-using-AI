import os
import time
import re
import json
import hashlib
import sqlite3
from web3 import Web3
from dotenv import load_dotenv
import google.generativeai as genai
from flask import Flask, request, jsonify, render_template

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)


neoxt_url = "https://neoxt4seed1.ngd.network"
web3 = Web3(Web3.HTTPProvider(neoxt_url))

# Check if the connection is successful
if web3.is_connected():
    print("Connected to blockchain")
else:
    print("Failed to connect to blockchain")

# Define your wallet address, private key and chain ID
from_address = "0x8883bFFa42A7f5B509D0929c6fFa041e46E18e2f"
private_key = "9b63cd445ab8312da178e90693290d0d2c98a334f77634013f5d8cfce60f644f"
chain_id = 12227332

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

dictionary = {}

# SQLite database connection
conn = sqlite3.connect('document_verification.db')
c = conn.cursor()

# Create a table if it doesn't exist
c.execute('''
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        participant_name TEXT,
        hackathon_name TEXT,
        extracted_text TEXT,
        document_hash TEXT,
        txn_hash TEXT,
        timestamp TEXT
    )
''')
conn.commit()
conn.close()

# Function to add document hash to the database
# Function to add extracted data + blockchain details to the database
def store_in_db(participant_name, document_hash, txn_hash):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    conn = sqlite3.connect('document_verification.db')
    c = conn.cursor()
    c.execute('INSERT INTO documents (participant_name, document_hash, txn_hash, timestamp) VALUES (?, ?, ?, ?)',
              (participant_name, document_hash, txn_hash, timestamp))
    conn.commit()
    conn.close()


@app.route('/')
def home():
    return render_template('index.html')



def verify_data(participant_name, json_data):
    # Calculate the hash of the provided JSON data
    json_string = json.dumps(json_data, sort_keys=True)
    calculated_hash = hashlib.sha256(json_string.encode()).hexdigest()

    conn = sqlite3.connect('document_verification.db')
    c = conn.cursor()

    # Retrieve the most recent valid hash
    c.execute('''
        SELECT document_hash FROM documents 
        WHERE participant_name = ? AND document_hash IS NOT NULL
        ORDER BY timestamp DESC LIMIT 1
    ''', (participant_name,))
    
    result = c.fetchone()
    conn.close()

    if result:
        stored_hash = result[0]
        print(f"🔍 Stored Hash: {stored_hash}")  # Debugging output
        print(f"🔍 Calculated Hash: {calculated_hash}")
        
        if calculated_hash == stored_hash:
            return "✅ Verification successful! Data is authentic."
        else:
            return "❌ Verification failed! Data has been altered."
    else:
        return "❌ Verification failed! No valid record found."





@app.route('/verify')
def verify():
    return render_template('verify.html')


@app.route('/upload_details')
def upload_details():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload():
    global dictionary   
    if 'image' not in request.files:
        return "No file part", 400
    image = request.files['image']
    if image.filename == '':
        return "No selected file", 400
    save = os.path.join('uploads', image.filename)
    image.save(save)

    sample_file = genai.upload_file(path="uploads/" + image.filename,
                            display_name="PASS IMAGE")

    file = genai.get_file(name=sample_file.name)

    model = genai.GenerativeModel("gemini-1.5-flash")
    result = model.generate_content(
        [file, "\n\n", "Extract the text content from this image. Organise the text into paragraph format, and extract the name, hackathon name from the text. respond with json containing the text, hackathon_name and name extracted."],
    )
    
    raw_response = result.text
    print(f"🔍 Gemini API raw response: {raw_response}")  # Debugging print

    clean_json = re.search(r'```json\n(.*?)\n```', raw_response, re.DOTALL)
    if clean_json:
        json_text = clean_json.group(1)  # Extract only the JSON part
        try:
            result_data = json.loads(json_text)
        except json.JSONDecodeError as e:
            print(f"🚨 JSON Decode Error: {e}")
            return "Error: Invalid response from Gemini API", 500
    else:
        print("🚨 No valid JSON found in Gemini response!")
        return "Error: No valid JSON detected", 500

    text = result_data.get("text", "Text not found")
    hackathon_name = result_data.get("hackathon_name", "Hackathon name not found")
    name = result_data.get("name", "Name not found")
    dictionary = {"hackathon_name": hackathon_name, "name": name}
    return render_template('result.html', dictionary=dictionary, verify_result=verify_data( dictionary["name"], dictionary))

@app.route('/upload_data', methods=['POST'])
def upload_data():
    if 'image' not in request.files:
        return "No file part", 400
    image = request.files['image']
    if image.filename == '':
        return "No selected file", 400
    save_path = os.path.abspath(os.path.join(UPLOAD_FOLDER, image.filename.replace(" ", "_")))  # Get full path
    image.save(save_path)

# Ensure the file is fully saved before processing
    time.sleep(1)

# Debug print to verify path
    print(f"✅ File saved at: {save_path}")

# Upload to Google Gemini
    if os.path.exists(save_path):  # Check if file exists
        sample_file = genai.upload_file(path=save_path, display_name="PASS IMAGE")
    else:
        print("🚨 File not found before uploading to Gemini!")
        return "File upload error. Please try again.", 500

    file = genai.get_file(name=sample_file.name)

    model = genai.GenerativeModel("gemini-1.5-flash")
    result = model.generate_content(
        [file, "\n\n", "Extract the text content from this image. Organise the text into paragraph format, and extract the name, hackathon name from the text. respond with json containing the text, hackathon_name and name extracted."],
    )
    raw_response = result.text
    clean_json = re.search(r'```json\n(.*?)\n```', raw_response, re.DOTALL)

    if clean_json:
       json_text = clean_json.group(1)  # Extracts only the JSON part
       print(f"🔍 Extracted JSON: {json_text}")  # Debugging print
       try:
          result_data = json.loads(json_text)
       except json.JSONDecodeError as e:
          print(f"🚨 JSON Decode Error: {e}")
          return "Error: Invalid response from Gemini API", 500
    else:
       print("🚨 No valid JSON found in Gemini response!")
       return "Error: No valid JSON detected", 500

    text = result_data.get("text", "Text not found")
    hackathon_name = result_data.get("hackathon_name", "Hackathon name not found")
    name = result_data.get("name", "Name not found")
    # Store extracted data in SQLite
    conn = sqlite3.connect('document_verification.db')
    c = conn.cursor()

    c.execute('''
    INSERT INTO documents (participant_name, hackathon_name, extracted_text, document_hash, txn_hash, timestamp)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, hackathon_name, text, None, None, time.strftime('%Y-%m-%d %H:%M:%S')))

    conn.commit()
    conn.close()

    print("Extracted data stored in SQLite")

    data = {"hackathon_name": hackathon_name, "name": name}
    # Convert JSON to string and then create a hash (SHA-256)
    data_string = json.dumps(data, sort_keys=True)
    data_hash = hashlib.sha256(data_string.encode()).hexdigest()
    
    account = web3.eth.account.from_key(private_key)
    nonce = web3.eth.get_transaction_count(account.address)
    conn = sqlite3.connect('document_verification.db')
    c = conn.cursor()
    # lenth of the data
    c.execute('SELECT COUNT(*) FROM documents')
    result = c.fetchone()
    conn.close()
    if result:
        length = result[0]
    else:
        length = 0
    to_address = from_address  # Send transaction to your own wallet address

    
    
    transaction = {
        'to': to_address,  # Use a smart contract address if interacting with one
        'value': web3.to_wei(0, 'ether'),  # We are not sending ETH, just a transaction with data
        'gas': 2000000,
        'gasPrice': web3.to_wei('50', 'gwei'),
        'nonce': nonce,
        'chainId': chain_id,  # Include the chain ID for replay protection
        'data': web3.to_bytes(hexstr=data_hash)
    }
    # Sign and send the transaction
    signed_txn = web3.eth.account.sign_transaction(transaction, private_key)
    txn_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)

    # Store the document hash and transaction hash in the database
    
    store_in_db(data["name"], data_hash, web3.to_hex(txn_hash))

    

    return web3.to_hex(txn_hash)

@app.route('/result')
def result():
    global dictionary
    return render_template('result.html', dictionary=dictionary, verify_result=verify_data( dictionary["name"], dictionary))

if __name__ == '__main__':
    app.run(debug=True)