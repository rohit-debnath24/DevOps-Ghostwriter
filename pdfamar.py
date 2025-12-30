from fpdf import FPDF

class ProjectPDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 16)
        self.cell(0, 10, 'AI & Productivity Project Descriptions', ln=True, align='C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

    def add_project(self, title, description):
        # Set Title style
        self.set_font('helvetica', 'B', 12)
        self.multi_cell(0, 8, title)
        
        # Set Description style
        self.set_font('helvetica', '', 11)
        self.multi_cell(0, 6, description)
        self.ln(6) # Add space between projects

# --- Data Preparation ---
projects = [
    ("1. AI-Powered Mental Well-Being Platform (Privacy-First)", 
     "This project focuses on building a privacy-first mental well-being platform that helps users become more aware of their emotional health. By analyzing opt-in digital behavior, the system looks for early signs of stress, burnout, or depression. All user data is processed and stored locally, so privacy is never compromised."),
    
    ("2. AI-Powered Image Editing Platform (Nano Banana / Pro)", 
     "A professional image editing platform where users can freely edit images using manual controls or AI assistance. Users can apply Nano Banana or Nano Banana Pro to specific regions to enhance, modify, or refine areas like background cleanup and lighting correction."),
    
    ("3. Real-Time Malicious Link Detection Chrome Extension", 
     "This Chrome extension scans all links on a webpage in real time and checks for phishing behavior before users click. It visually marks URLs with check marks or warning icons directly on the page without interrupting browsing flow."),
    
    ("4. Reimagined Retro Games with an AI Twist", 
     "Brings classic retro games to life by adding an AI layer that adapts gameplay based on player style. Difficulty, enemy behavior, and level structure change dynamically, ensuring each playthrough feels fresh."),

    ("5. Real-Time AI Threat Detection for Digital Fraud", 
     "A real-time defense system that detects deepfake videos, phishing, and unusual transaction behavior. It combines video, text, and behavioral data to generate risk scores before fraud causes damage."),

    ("6. Neurodivergent-Friendly Reading Chrome Extension", 
     "Built for users with ADHD and dyslexia, this extension transforms webpages into easier-to-read formats using simplified text and structured checklists. All processing happens locally on-device."),

    ("7. Offline Webpage Memory Chrome Extension", 
     "Securely saves visited webpages locally, preserving structure and content for access without an internet connection. Ideal for research and travel in low-connectivity areas."),

    ("8. Privacy-First Sensitive Data Detection Toolkit", 
     "Runs locally to detect passwords, API keys, and tokens in real time. It masks or flags sensitive info to reduce security risks without ever uploading data to the cloud."),

    ("9. Multi-Agent AI Platform for Collaborative Research", 
     "Uses specialized AI agents to find papers, summarize content, and validate claims. It combines these outputs into traceable insights to assist human researchers."),

    ("10. AI-Powered Personal Fashion Assistant", 
     "Learns a user’s style from their device gallery (with consent) to recommend outfits and assist with shopping. Focuses on personalization while keeping the user in full control."),

    ("11. AI-Powered Pitch Assistant", 
     "Offers real-time factual support and adaptive coaching for presentations. It suggests clearer phrasing and validates claims to help users deliver confident, structured pitches."),

    ("12. Agentic Platform for ID-Based Auto Form Filling", 
     "Simplifies form filling by extracting info from ID documents (Aadhaar/PAN) and storing it in an encrypted local environment. It fills online forms only with user approval.")
]

# --- Generate PDF ---
pdf = ProjectPDF()
pdf.add_page()
pdf.set_auto_page_break(auto=True, margin=15)

for title, desc in projects:
    pdf.add_project(title, desc)

pdf.output("Project_Descriptions.pdf")
print("PDF created successfully: Project_Descriptions.pdf")