# 📄 Automated Document Verification System using AI and Blockchain

This project is a smart, secure, and efficient document verification system that combines the power of **Generative AI (Gemini 1.5)** and **Blockchain** to authenticate documents—like participation certificates—uploaded as images. It uses **Google's Gemini AI** for intelligent text extraction and **blockchain hashing** for tamper-proof verification.

---

## 🚀 Key Features

- 🔍 **Text Extraction from Document Images** using Gemini 1.5 Flash.
- 🧠 **AI-Powered Data Parsing** (name, hackathon name, full text).
- 📦 **Document Hashing** using SHA-256.
- 🔐 **Blockchain-based Proof of Integrity** using NEOXT.
- 💾 **SQLite Storage** for participant and document metadata.
- ✅ **Verification Endpoint** to compare data hashes for authenticity.

---

## 🛠️ Tech Stack

| Layer       | Tech Used                     |
|-------------|-------------------------------|
| Backend     | Python, Flask, SQLite         |
| AI/ML       | Google Generative AI (Gemini) |
| Blockchain  | Web3.py, NEOXT Testnet        |
| Frontend    | HTML, CSS, Bootstrap (via templates) |
| Hosting     | Localhost / Flask Dev Server  |

---

## ⚙️ Installation Steps

1. Clone the Repository

```bash
git clone https://github.com/varshi-git/Automated-Document-Verification-System-using-AI.git
cd Automated-Document-Verification-System-using-AI

2. Setup Virtual Environment:
   
   python -m venv venv
   source venv/bin/activate        
  
3. Install Dependencies:

       pip install -r requirements.txt
   
4. Set up .env File:
   
       GOOGLE_API_KEY=your_google_generative_ai_api_key

5.Run the Flask Server:

        python app.py

---

## OUTPUT

Home Page






