# 📌 **EmailAssist**

### **AI-Powered Email Automation & Smart Response System**

---

## 📝 **Overview**

**EmailAssist (Environment A)** is an AI-driven email automation system designed to draft, analyze, categorize, and respond to emails intelligently. It reduces manual effort, improves response quality, and accelerates communication workflows for individuals, teams, and organizations.

EmailAssist is optimized for **speed, accuracy, and reliability**, providing context-aware email generation across multiple scenarios.

---

## 🎯 **Key Capabilities**

### ✔ **AI-Generated Emails**

* Professional emails
* Formal, semi-formal, and casual tones
* Customizable by purpose (request, follow-up, apology, inquiry, complaint, etc.)

### ✔ **Smart Categorization**

* Auto-sorts emails into categories such as:

  * Priority
  * Work
  * Academic
  * Finance
  * Spam
  * Follow-up required

### ✔ **Intent Detection**

Understands user input to generate the most suitable email format.

### ✔ **Template Engine (Environment A: Extended Mode)**

* Reusable templates
* Dynamic placeholders
* One-click insertion

### ✔ **Grammar & Tone Optimization**

* Polishes text
* Adjusts tone
* Enhances clarity & structure

---

## 🛠️ **Tech Stack (Environment A)**

### **Backend**

* Node.js
* Express.js
* Python (GPT Model Handler)
* Flask API (optional)

### **AI Layer**

* GPT-based LLM
* Fine-tuned prompt-engine
* Context memory controller

### **Frontend**

* React.js
* Tailwind CSS
* ShadCN components

---

## 📂 **Project Structure**

```
emailassist/
│
├── env_emailassist/
│   ├── __init__.py
│   ├── env.py
│   ├── models.py
│   ├── openenv.yaml
│   ├── tasks/
│   │   ├── task1_classify.py
│   │   ├── task2_priority.py
│   │   └── task3_drafting.py
│   └── graders/
│       ├── classify_grader.py
│       ├── priority_grader.py
│       └── drafting_grader.py
│
├── app.py                 ← FastAPI server (HF Space)
├── inference.py           ← Baseline (MANDATORY)
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## 🚀 Installation & Setup

### **1. Clone the Repository**

```bash
git clone https://github.com/your-repo/emailassist-A.git
cd emailassist-A
```

### **2. Backend Setup**

```bash
cd backend
npm install
node server.js
```

### **3. Frontend Setup**

```bash
cd frontend
npm install
npm run dev
```

### **4. AI Engine Setup (Optional)**

```bash
python emailAssistEngine.py
```

---

## 🧠 **How EmailAssist Works (Environment A Logic)**

```
User Input → Intent Analyzer → Template Selector → Tone Modifier → AI Engine → Final Email Output
```

### **Modes in Environment A**

1. **Neutral Mode** – Balanced tone
2. **Professional Mode** – Corporate & formal
3. **Human Mode** – Conversational, empathetic
4. **Condensed Mode** – Short & crisp
5. **Extended Mode** – Detailed, structured emails

---

## 📌 Example Use Cases

* Writing official requests
* Creating follow-up emails
* Fixing grammar and tone in drafts
* Automated reply generation
* Academic and internship emails
* HR communication templates
* Complaint and escalation emails

---

## 🧪 API Endpoints

### **POST /generate**

Generate an AI-powered email.

### **POST /categorize**

Analyze and categorize incoming text/email.

### **POST /optimize**

Improve grammar, tone, and clarity.

### **POST /template**

Return a structured template based on purpose.

---

## 🔐 Security (Environment A)

* No data stored or logged
* In-memory processing only
* Optional local-only mode
* Sanitization of input and output

---

## 📜 License

MIT License

---

## 👤 **Maintainer**

**Kirti Sharma**
Solo developer – AI engine, frontend, backend, documentation, and UX design.

---

## 🙏 Acknowledgments

Thanks to open-source libraries, AI frameworks, and community tools that support EmailAssist’s development.

---



