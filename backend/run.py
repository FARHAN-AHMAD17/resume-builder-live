# ==============================================================================
# FINAL, DEFINITIVE v5 of run.py (OpenAI Edition with 2-Step Anti-Hallucination)
# ==============================================================================

import os
import re
import sys
import hashlib
sys.path.append(os.path.join(os.path.dirname(__file__), 'templates'))
from templates import *
import traceback
from flask import Flask, jsonify, request, send_file
# ... (all other imports are correct and unchanged)
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
import PyPDF2
import docx
import json
import importlib
import copy
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate
from io import BytesIO
from sentence_transformers import SentenceTransformer, util
from json_repair import repair_json
from openai import OpenAI
import smtplib

print("--- Backend Script Initializing (OpenAI API Mode) ---")
load_dotenv()

app = Flask(__name__)
# Allow all origins temporarily so your live frontend works immediately
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.init_app(app)

try:
    openai_client = OpenAI()
    print("✅ OpenAI client initialized successfully.")
except Exception as e:
    print(f"FATAL ERROR: Could not initialize OpenAI client. Is OPENAI_API_KEY set in .env? Error: {e}")
    sys.exit(1)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Use PostgreSQL if available (Live), else fall back to SQLite (Local)
database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///' + os.path.join(BASE_DIR, 'site.db')
app.config['SECRET_KEY'] = 'a_very_secret_key_change_this_later'
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
db = SQLAlchemy(app)

@app.route("/api")
def api_root(): return jsonify({"message": "API is running!"})

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(60), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    with app.app_context(): return User.query.get(int(user_id))

bert_model = None
# Global cache for generated resume data (in-memory cache per user session)
resume_data_cache = {}
last_resume_cache = {}  # per-user last successful resume_data with its cache_key

def ensure_models_ready():
    """Lazily load models if not already loaded."""
    global bert_model
    if bert_model is None:
        configure_ai_and_models()

def configure_ai_and_models():
    global bert_model; print("Configuring AI models...")
    try:
        bert_model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ BERT model loaded successfully.")
    except Exception as e: print(f"FATAL ERROR: Could not load BERT model. Error: {e}"); sys.exit(1)
    print("✅ Generative AI is now accessed via the OpenAI API.")

def extract_text_from_file(file_stream, file_name):
    # This function is unchanged
    text = ""
    if file_name.endswith('.pdf'):
        pdf_reader = PyPDF2.PdfReader(file_stream); text = "".join(page.extract_text() or "" for page in pdf_reader.pages)
    elif file_name.endswith('.docx'):
        doc = docx.Document(file_stream); text = "\n".join(para.text for para in doc.paragraphs)
    else: raise ValueError("Unsupported file type")
    return text

def calculate_match_score_bert(resume_text, job_description, is_raw_resume=False):
    # Scoring function with different logic for raw vs optimized resumes
    import nltk; from nltk.tokenize import sent_tokenize; global bert_model, DOMAIN_KEYWORDS
    ensure_models_ready()
    if not resume_text or not job_description: return 0.0
    try: nltk.data.find("tokenizers/punkt")
    except LookupError: nltk.download("punkt", quiet=True)
    if 'DOMAIN_KEYWORDS' not in globals(): DOMAIN_KEYWORDS = {"Software Engineering": ["software", "development"], "Data Science": ["data analysis", "python"], "Machine Learning": ["machine learning"], "Cloud Computing": ["cloud", "aws"]}
    resume_sentences, jd_sentences = sent_tokenize(str(resume_text)), sent_tokenize(str(job_description))
    try: base_score = sum(util.cos_sim(bert_model.encode(resume_sentences, convert_to_tensor=True), bert_model.encode(jd_sentences, convert_to_tensor=True)).max(dim=1).values.cpu().tolist()) / max(len(resume_sentences), 1)
    except: base_score = float(util.cos_sim(bert_model.encode(str(resume_text), convert_to_tensor=True), bert_model.encode(str(job_description), convert_to_tensor=True)).item())
    jd_lower, resume_lower = str(job_description).lower(), str(resume_text).lower()
    detected_domain, max_hits = None, 0;
    for domain, kws in DOMAIN_KEYWORDS.items():
        if (hits := sum(1 for kw in kws if kw in jd_lower)) > max_hits: max_hits, detected_domain = hits, domain
    matched_keywords = [kw for kw in DOMAIN_KEYWORDS.get(detected_domain, []) if kw in resume_lower and kw in jd_lower]
    keyword_boost = (len(matched_keywords) / max(len(DOMAIN_KEYWORDS.get(detected_domain, [])), 1)) * 25
    final_score = (base_score * 100 * 0.75) + keyword_boost
    if final_score < 50: final_score = 50 + (final_score / 2)
    elif final_score > 95: final_score = 95 - ((final_score - 95) / 2)
    
    # Different logic based on resume type
    if is_raw_resume:
        # For raw/original resume: set scores between 66-77% to 65% for display in 'before' section
        if 66 <= final_score <= 77:
            final_score = 65.0
            print("[SCORE ADJUSTMENT] Raw Resume Score SET to 65.0% for 66-77% range")
        # (Optional: keep previous logic for 70-77% if needed, or remove if replaced by above)
    else:
        # For optimized resume: keep the buff zone (70-77% boosted to 78%)
        if 69 < final_score < 78: final_score = 78.0; print("[SCORE ADJUSTMENT] Optimized Resume Score BOOSTED to 78.0%")
    
    final_score = round(min(100, final_score), 2)
    print(f"[MATCH DEBUG] Domain={detected_domain}, Base={base_score:.3f}, Matched={matched_keywords}, Final={final_score}%, Type={'RAW' if is_raw_resume else 'OPTIMIZED'}")
    return final_score


def normalize_resume_for_template(template_id, data):
    """Best-effort adapter so one canonical resume payload can render in all templates."""
    safe = copy.deepcopy(data) if isinstance(data, dict) else {}

    # Canonical fields from template1
    name = safe.get('name', '')
    summary = safe.get('summary') or safe.get('profile') or safe.get('profile_summary') or ''
    experience = safe.get('experience', []) or safe.get('work_experience', [])
    education = safe.get('education', [])
    skills_raw = safe.get('skills', [])
    contact_raw = safe.get('contact', [])
    
    # Flatten skills if it's a dict like {"Technical Skills": [...], "Soft Skills": [...]}
    def flatten_skills(skills_input):
        if isinstance(skills_input, dict):
            flat = []
            for category, items in skills_input.items():
                if isinstance(items, list):
                    flat.extend(items)
                else:
                    flat.append(str(items))
            return flat
        elif isinstance(skills_input, list):
            return skills_input
        else:
            return [str(skills_input)] if skills_input else []
    
    skills_flat = flatten_skills(skills_raw)

    # Helper: map contact list -> dict
    def contact_list_to_dict(lst, keys):
        if not isinstance(lst, list):
            return lst if isinstance(lst, dict) else {}
        out = {}
        for idx, key in enumerate(keys):
            if idx < len(lst):
                out[key] = lst[idx]
        return out

    if template_id == 'template2':
        # Expect: contact dict, skills list, software list[dict], languages list[dict]
        safe['contact'] = contact_list_to_dict(safe.get('contact', []), ["Address", "Phone", "E-mail", "LinkedIn"])
        # Use flattened skills
        safe['skills'] = skills_flat
        # Coerce lists
        for key in ['software', 'languages', 'experience', 'education', 'certifications', 'interests']:
            if not isinstance(safe.get(key), list):
                if safe.get(key):
                    safe[key] = [safe[key]]
                else:
                    safe[key] = []
        # Ensure dict items for experience/education
        def ensure_dict_list(items):
            out = []
            for item in items:
                if isinstance(item, dict):
                    out.append(item)
                else:
                    out.append({'role': str(item), 'duties': []})
            return out
        safe['experience'] = ensure_dict_list(safe.get('experience', []))
        safe['education'] = ensure_dict_list(safe.get('education', []))
        # Fill summary into first experience/company if needed
        if summary and not safe['experience']:
            safe['experience'] = [{'role': '', 'company': '', 'duties': [summary]}]

    elif template_id == 'template3':
        # Expect: contact dict with Phone, Website, Email
        safe['contact'] = contact_list_to_dict(safe.get('contact', []), ["Phone", "Website", "Email"])
        # Normalize work_experience list
        work = safe.get('work_experience') or safe.get('experience') or []
        if not isinstance(work, list):
            work = [work]
        norm_work = []
        for item in work:
            if isinstance(item, dict):
                # duties can be list or str; keep str
                duties = item.get('duties')
                if isinstance(duties, list):
                    item = {**item, 'duties': "\n".join(duties)}
                norm_work.append(item)
            else:
                norm_work.append({'company': str(item), 'duties': str(item)})
        safe['work_experience'] = norm_work
        # Education list
        edu = safe.get('education', [])
        if not isinstance(edu, list): edu = [edu]
        norm_edu = []
        for item in edu:
            if isinstance(item, dict):
                # details might be list -> join
                det = item.get('details')
                if isinstance(det, list):
                    item = {**item, 'details': "\n".join(det)}
                norm_edu.append(item)
            else:
                norm_edu.append({'university': str(item), 'details': str(item)})
        safe['education'] = norm_edu
        # Skills/hobbies - use flattened skills
        safe['skills'] = skills_flat
        hobbies = safe.get('hobbies', [])
        if not isinstance(hobbies, list):
            safe['hobbies'] = [hobbies] if hobbies else []
        # Profile
        safe['profile'] = summary

    elif template_id == 'template4':
        # Expect: contact dict with lower-case keys
        contact_dict = contact_list_to_dict(safe.get('contact', []), ["Phone", "Email", "Location", "LinkedIn"])
        # Map to lowercase keys expected by template4
        safe['contact'] = {
            'phone': contact_dict.get('Phone', ''),
            'email': contact_dict.get('Email', ''),
            'address': contact_dict.get('Location', ''),
            'website': contact_dict.get('LinkedIn', '')
        }
        # work_experience duties list - limit to top 2 experiences for space
        work = safe.get('work_experience') or safe.get('experience') or []
        if not isinstance(work, list): work = [work]
        norm_work = []
        for item in work[:2]:  # Limit to first 2 experiences to prevent layout overflow
            if isinstance(item, dict):
                duties = item.get('duties')
                if isinstance(duties, str): duties = [duties]
                if duties is None: duties = []
                # Limit duties to first 3 for space
                item = {**item, 'duties': duties[:3]}
                norm_work.append(item)
            else:
                norm_work.append({'company': str(item), 'duties': [str(item)]})
        safe['work_experience'] = norm_work
        # education details list - limit to top 2 for space
        edu = safe.get('education', [])
        if not isinstance(edu, list): edu = [edu]
        norm_edu = []
        for item in edu[:2]:  # Limit to first 2 education entries
            if isinstance(item, dict):
                details = item.get('details')
                if isinstance(details, str): details = [details]
                if details is None: details = []
                item = {**item, 'details': details[:2]}  # Limit details
                norm_edu.append(item)
            else:
                norm_edu.append({'degree': str(item), 'details': [str(item)]})
        safe['education'] = norm_edu
        # skills list - use flattened skills (limit to first 10 for space)
        safe['skills'] = skills_flat[:10]
        # languages list of dicts
        langs = safe.get('languages', [])
        if not isinstance(langs, list): langs = [langs]
        norm_langs = []
        for l in langs:
            if isinstance(l, dict):
                norm_langs.append(l)
            else:
                norm_langs.append({'language': str(l), 'level': 'Fluent'})
        safe['languages'] = norm_langs
        # profile summary
        safe['profile_summary'] = summary

    return safe

def generate_with_openai(messages, json_mode=False):
    # This function is unchanged and correct
    print("Sending request to OpenAI API...")
    try:
        api_params = {"model": "gpt-4o", "messages": messages, "temperature": 0.3, "max_tokens": 4096}
        if json_mode:
            api_params["response_format"] = {"type": "json_object"}
        completion = openai_client.chat.completions.create(**api_params)
        if not completion.choices:
            raise RuntimeError("No choices returned from OpenAI")
        response_text = completion.choices[0].message.content or ""
        print("--- OpenAI Raw Response ---"); print(response_text); print("---------------------------")
        return response_text
    except Exception as e:
        print(f"FATAL ERROR: OpenAI API call failed. Error: {e}")
        return '{"name": "Error", "summary": "Failed to connect to OpenAI API."}' if json_mode else "Error: Failed to connect to OpenAI API."

# ✅ THIS IS THE NEW, ROBUST, 2-STEP FUNCTION
def generate_full_resume_text(resume_text, job_description, ai_suggestions, template_id):
    print("--- Starting 2-Step Resume Generation Process ---")
    
    # --- STEP 1: TRUTHFUL DATA EXTRACTION ---
    print("\n[STEP 1/2] Extracting truthful data from original resume...")
    try:
        json_structure = importlib.import_module(f"templates.{template_id}").get_json_prompt()
    except:
        print(f"⚠️ WARNING: Could not load prompt from {template_id}.py."); json_structure = "{}"
    
    extraction_system_message = "You are a data extraction bot. Your only task is to read the user's resume text and populate the JSON structure with the information found. Do not rewrite, invent, or change any information. Extract the data exactly as it appears."
    extraction_user_prompt = f"Extract all information from the 'Original Resume Text' below and place it into the following JSON structure. Do not add any information that is not in the original text. \n\nJSON STRUCTURE:\n```json\n{json_structure}\n```\n\nOriginal Resume Text:\n{resume_text}"
    extraction_messages = [{"role": "system", "content": extraction_system_message}, {"role": "user", "content": extraction_user_prompt}]
    
    truthful_json_str = generate_with_openai(extraction_messages, json_mode=True)
    try:
        truthful_data = json.loads(repair_json(truthful_json_str))
        print("✅ Step 1 Successful: Truthful data extracted.")
    except Exception as e:
        print(f"FATAL ERROR in Step 1 (Extraction): {e}")
        return {"name": "Error", "summary": f"Failed to extract initial data. Raw response: {truthful_json_str}"}

    # --- STEP 2: FOCUSED REWRITING AND OPTIMIZATION ---
    print("\n[STEP 2/2] Rewriting and optimizing the extracted data...")
    rewriting_system_message = "You are an expert resume writer. Your task is to take a JSON object and rewrite its string fields to be more professional, action-oriented, and tailored to the provided job description. You must not add new entries or change the structure of the JSON."
    rewriting_user_prompt = f"""
    Please rewrite the string values (like 'summary', 'duties', 'role') in the following JSON object to be more professional and better aligned with the 'Target Job Description'.
    
    CRITICAL RULES:
    1.  Rewrite the text to be impactful and start duties with action verbs.
    2.  Incorporate keywords from the job description naturally.
    3.  DO NOT add, remove, or change any keys in the JSON structure.
    4.  DO NOT invent new jobs, projects, or skills. Only improve the text that is already there.
    5.  Your final output MUST be only the rewritten JSON object and nothing else.

    **TARGET JOB DESCRIPTION:**
    {job_description}

    **ORIGINAL JSON DATA TO REWRITE:**
    ```json
    {json.dumps(truthful_data, indent=2)}
    ```
    """
    rewriting_messages = [{"role": "system", "content": rewriting_system_message}, {"role": "user", "content": rewriting_user_prompt}]
    
    final_json_str = generate_with_openai(rewriting_messages, json_mode=True)
    try:
        final_data = json.loads(repair_json(final_json_str))
        print("✅ Step 2 Successful: Resume data rewritten and optimized.")
        return final_data
    except Exception as e:
        print(f"FATAL ERROR in Step 2 (Rewriting): {e}")
        print("⚠️ Falling back to truthfully extracted data without rewrite.")
        return truthful_data # As a fallback, return the original, non-rewritten data.

# ✅ THIS ROUTE IS NOW SIMPLER
@app.route('/api/optimize', methods=['POST', 'OPTIONS'])
@login_required
def optimize_resume_route():
    if request.method == 'OPTIONS': return jsonify(ok=True)
    try:
        file, job_description = request.files.get('resumeFile'), request.form.get('jobDescription')
        if not file or not job_description:
            return jsonify({'error': 'Missing data'}), 400

        # Always rewind the stream before reading
        try:
            file.stream.seek(0)
        except Exception:
            pass

        try:
            resume_text = extract_text_from_file(file.stream, file.filename)
        except Exception as parse_err:
            print(f"❌ Failed to parse resume file: {parse_err}")
            traceback.print_exc()
            return jsonify({'error': f'Could not read resume file: {parse_err}'}), 400

        # Ensure models are loaded
        ensure_models_ready()
        score_before = calculate_match_score_bert(resume_text, job_description, is_raw_resume=True)
        print(f"📊 Unoptimized Resume Score: {score_before}%")
        
        suggestion_messages = [
            {"role": "system", "content": "You are an expert AI career coach."},
            {"role": "user", "content": f"Analyze this resume based on this job description. Provide 3-5 short, actionable bullet-point suggestions for improvement. Output ONLY the bullet points.\n\nRESUME:\n{resume_text}\n\nJOB:\n{job_description}"}
        ]
        ai_suggestions = generate_with_openai(suggestion_messages)
        if (not ai_suggestions) or ai_suggestions.startswith("Error"):
            print(f"❌ AI suggestion generation failed. Response: {ai_suggestions}")
            return jsonify({'error': 'AI suggestion generation failed'}), 502
        
        # We now pass the original text and new suggestions to the next step.
        # The score calculation is now a simple preview.
        preview_text = resume_text + "\n\n" + ai_suggestions
        score_after = calculate_match_score_bert(preview_text, job_description, is_raw_resume=False)
        print(f"🤖 Preview Optimized Score: {score_after}%")
        
        return jsonify({
            'match_score': f"{round(score_before, 2)}%",
            'optimized_resume': ai_suggestions.strip(),
            'optimized_resume_full': resume_text, # Send original text
            'optimized_score': f"{round(score_after, 2)}%"
        })
    except Exception as e:
        print(f"❌ FATAL ERROR in /api/optimize: {e}")
        traceback.print_exc()
        return jsonify({'error': f'Server error: {e}'}), 500

# ✅ THIS ROUTE IS NOW THE MAIN WORKHORSE
@app.route('/api/generate-pdf', methods=['POST', 'OPTIONS'])
@login_required
def generate_pdf_route():
    if request.method == 'OPTIONS': return jsonify(ok=True)
    try:
        file = request.files.get('resumeFile'); data = request.form.to_dict()
        if not file or not all(k in data for k in ['jobDescription', 'aiSuggestions', 'templateId']):
            return jsonify({'error': 'Missing data'}), 400
        
        # Create a stable cache key (user + file bytes + jobDescription + aiSuggestions)
        file.stream.seek(0)
        file_content = file.stream.read()
        file.stream.seek(0)  # Reset for extraction
        cache_hasher = hashlib.sha256()
        cache_hasher.update(str(current_user.id).encode())
        cache_hasher.update(file_content)
        cache_hasher.update(data['jobDescription'].encode())
        cache_hasher.update(data.get('aiSuggestions', '').encode())
        cache_key = cache_hasher.hexdigest()
        print(f"🧮 cache_key (first12): {cache_key[:12]} for user {current_user.id}")
        
        # Check if we have cached resume data for this user and file
        if cache_key in resume_data_cache:
            print(f"✅ Using CACHED resume data for template: {data['templateId']}")
            resume_data = resume_data_cache[cache_key]
        else:
            # Fallback: reuse last resume for this user if same cache_key matches
            user_last = last_resume_cache.get(current_user.id)
            if user_last and user_last.get('cache_key') == cache_key:
                print(f"♻️ Using LAST resume cache for user {current_user.id}")
                resume_data = user_last.get('data', {})
            else:
                # Generate new resume data only if not cached
                original_resume_text = extract_text_from_file(file.stream, file.filename)
                print(f"📄 Generating NEW resume data using canonical schema: template1")
                resume_data = generate_full_resume_text(original_resume_text, data['jobDescription'], data['aiSuggestions'], 'template1')
                
                # Check if resume_data is valid
                if not resume_data or not isinstance(resume_data, dict):
                    print(f"❌ ERROR: Invalid resume data generated: {resume_data}")
                    return jsonify({'error': 'Failed to generate valid resume data'}), 500
                
                # Cache the generated data (canonical)
                resume_data_cache[cache_key] = resume_data
                last_resume_cache[current_user.id] = {'cache_key': cache_key, 'data': resume_data}
                print(f"💾 Cached resume data for future use (cache key: {cache_key[:20]}...)")

        # Ensure models are loaded before any downstream scoring (belt-and-suspenders)
        ensure_models_ready()
        
        print(f"📋 Building PDF with template: {data['templateId']}")

        # Normalize cached data for the specific template to avoid schema mismatches
        resume_data_for_template = normalize_resume_for_template(data['templateId'], resume_data)

        buffer = BytesIO()
        try:
            template_module = importlib.import_module(f"templates.{data['templateId']}")
            print(f"✅ Template module loaded: {data['templateId']}")
            build_result = template_module.build(resume_data_for_template)
            print(f"✅ Story generated successfully for {data['templateId']}")
        except Exception as template_error:
            print(f"❌ ERROR building template {data['templateId']}: {template_error}")
            traceback.print_exc()
            return jsonify({'error': f'Template error: {str(template_error)}'}), 500

        if data['templateId'] == 'template2' and callable(build_result):
            # For template2, build_result is a function: call it with buffer
            build_result(buffer)
        else:
            # For other templates, build_result is the story list
            from reportlab.platypus import SimpleDocTemplate
            from reportlab.lib.pagesizes import letter
            # Reduce top and bottom margins for template3 to avoid blank first page
            if data['templateId'] == 'template3':
                doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=24, bottomMargin=24)
            else:
                doc = SimpleDocTemplate(buffer, pagesize=letter)
            doc.build(build_result)
        buffer.seek(0)
        print(f"✅ PDF generated successfully for {data['templateId']}")
        return send_file(buffer, as_attachment=True, download_name=f"Optimized_Resume_{data['templateId']}.pdf", mimetype='application/pdf')
    except Exception as e:
        print(f"❌ FATAL ERROR in generate_pdf_route: {e}")
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/clear-cache', methods=['POST'])
@login_required
def clear_cache():
    """Clear cached resume data for the current user"""
    global resume_data_cache
    user_keys = [k for k in resume_data_cache.keys() if k.startswith(f"{current_user.id}_")]
    for key in user_keys:
        del resume_data_cache[key]
    print(f"🧹 Cleared {len(user_keys)} cached items for user {current_user.id}")
    return jsonify({'message': 'Cache cleared successfully'}), 200

# --- All other routes are unchanged ---
@app.route('/api/register', methods=['POST', 'OPTIONS'])
def register():
    # ... code is unchanged ...
    if request.method == 'OPTIONS': return jsonify({'message': 'CORS preflight successful'}), 200
    try:
        data = request.get_json()
        if User.query.filter_by(username=data.get('username')).first(): return jsonify({'error': 'Username already exists'}), 409
        user = User(username=data.get('username'), password_hash=bcrypt.generate_password_hash(data.get('password')).decode('utf-8'))
        db.session.add(user); db.session.commit(); return jsonify({'message': 'User registered successfully'}), 201
    except: traceback.print_exc(); return jsonify({'error': 'Server error'}), 500
@app.route('/api/login', methods=['POST', 'OPTIONS'])
def login():
    # ... code is unchanged ...
    if request.method == 'OPTIONS': return jsonify({'message': 'CORS preflight successful'}), 200
    try:
        data = request.get_json()
        user = User.query.filter_by(username=data.get('username')).first()
        if user and bcrypt.check_password_hash(user.password_hash, data.get('password')): login_user(user); return jsonify({'message': 'Login successful', 'username': user.username}), 200
        return jsonify({'error': 'Invalid credentials'}), 401
    except: traceback.print_exc(); return jsonify({'error': 'Server error'}), 500
@app.route('/api/logout', methods=['POST'])
@login_required
def logout(): logout_user(); return jsonify({'message': 'Logout successful'}), 200
@app.route('/api/status', methods=['GET'])
def status():
    if current_user.is_authenticated: return jsonify({'logged_in': True, 'username': current_user.username})
    return jsonify({'logged_in': False})
@app.route('/api/contact', methods=['POST', 'OPTIONS'])
@login_required
def handle_contact_form():
    # ... code is unchanged ...
    if request.method == 'OPTIONS': return jsonify(ok=True)
    try:
        data = request.get_json()
        name, from_email, message = data.get('name'), data.get('email'), data.get('message')
        if not all([name, from_email, message]): return jsonify({'error': 'All fields are required.'}), 400
        sender_email, sender_password = os.environ.get('EMAIL_USER'), os.environ.get('EMAIL_PASSWORD')
        if not sender_email or not sender_password: return jsonify({'error': 'Server not configured for email.'}), 500
        email_text = f"Subject: New Feedback from SR Builder: {name}\n\nFrom: {name}\nEmail: {from_email}\n\nMessage:\n{message}"
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls(); server.login(sender_email, sender_password); server.sendmail(sender_email, sender_email, email_text.encode('utf-8'))
        return jsonify({'message': 'Feedback sent!'}), 200
    except Exception as e:
        traceback.print_exc(); return jsonify({'error': 'Could not send email.'}), 500

if __name__ == '__main__':
    with app.app_context(): db.create_all()
    configure_ai_and_models()
    print("🚀 Starting Flask server on http://127.0.0.1:5001")
    app.run(debug=False, host='127.0.0.1', port=5001)