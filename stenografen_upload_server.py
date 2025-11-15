#!/usr/bin/env python3
"""
STENOGRAFEN Upload Server
Adds file upload functionality and folder creation to the HTML interface
"""

from flask import Flask, request, render_template_string, redirect, url_for, send_from_directory, jsonify
from pathlib import Path
import os
import yaml
import subprocess
import logging

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size

# Load config
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

INPUT_FOLDER = Path(config['folders']['input'])
ALLOWED_AUDIO = set(config['audio']['formats'])
ALLOWED_DOCS = {'pdf', 'docx', 'doc', 'txt', 'jpg', 'jpeg', 'png', 'msg', 'eml'}
ALL_ALLOWED = ALLOWED_AUDIO | ALLOWED_DOCS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALL_ALLOWED


@app.route('/')
def index():
    """Redirect to hovedindex"""
    return redirect('/browse/hovedindex.html')


@app.route('/browse/<path:filepath>')
def browse(filepath):
    """Serve files from input folder"""
    return send_from_directory(INPUT_FOLDER, filepath)


@app.route('/upload-ui/<path:folderpath>')
def upload_ui(folderpath=''):
    """Show upload interface for a specific folder"""
    folder = INPUT_FOLDER / folderpath
    
    # Get list of files in folder
    files = []
    if folder.exists() and folder.is_dir():
        for item in folder.iterdir():
            if item.is_file():
                files.append({
                    'name': item.name,
                    'size': item.stat().st_size,
                    'type': item.suffix[1:] if item.suffix else 'unknown'
                })
    
    return render_template_string(UPLOAD_TEMPLATE, 
                                 folderpath=folderpath,
                                 foldername=folder.name if folder.name else 'Root',
                                 files=files)


@app.route('/api/create-folder', methods=['POST'])
def create_folder():
    """Create a new folder"""
    data = request.json
    parent_path = data.get('parent', '')
    folder_name = data.get('name', '').strip()
    
    if not folder_name:
        return jsonify({'error': 'Folder name required'}), 400
    
    # Sanitize folder name
    folder_name = "".join(c for c in folder_name if c.isalnum() or c in (' ', '-', '_'))
    
    new_folder = INPUT_FOLDER / parent_path / folder_name
    
    try:
        new_folder.mkdir(parents=True, exist_ok=False)
        logger.info(f"Created folder: {new_folder}")
        return jsonify({'success': True, 'path': str(new_folder.relative_to(INPUT_FOLDER))})
    except FileExistsError:
        return jsonify({'error': 'Folder already exists'}), 400
    except Exception as e:
        logger.error(f"Error creating folder: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/upload-file', methods=['POST'])
def upload_file():
    """Handle file upload"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    folder_path = request.form.get('folder', '')
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': f'File type not allowed. Allowed: {", ".join(ALL_ALLOWED)}'}), 400
    
    target_folder = INPUT_FOLDER / folder_path
    target_folder.mkdir(parents=True, exist_ok=True)
    
    filepath = target_folder / file.filename
    
    try:
        file.save(filepath)
        logger.info(f"Uploaded file: {filepath}")
        
        # If it's an audio file, trigger transcription
        if filepath.suffix[1:].lower() in ALLOWED_AUDIO:
            logger.info(f"Audio file detected, triggering transcription...")
            # You can trigger your transcription script here
            # subprocess.Popen(['python', 'stenografen.py', str(filepath)])
        
        return jsonify({'success': True, 'filename': file.filename})
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/regenerate-html', methods=['POST'])
def regenerate_html():
    """Regenerate HTML after uploads"""
    try:
        result = subprocess.run(['python3', 'generate_index.py', '--both'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            logger.info("HTML regenerated successfully")
            return jsonify({'success': True})
        else:
            logger.error(f"HTML regeneration failed: {result.stderr}")
            return jsonify({'error': result.stderr}), 500
    except Exception as e:
        logger.error(f"Error regenerating HTML: {e}")
        return jsonify({'error': str(e)}), 500


UPLOAD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Upload - {{ foldername }} - STENOGRAFEN</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 900px;
            margin: 0 auto;
        }
        
        .card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }
        
        h1 {
            color: #2c3e50;
            margin-bottom: 10px;
        }
        
        h2 {
            color: #2c3e50;
            margin-bottom: 20px;
            font-size: 1.5em;
        }
        
        .breadcrumb {
            background: rgba(255, 255, 255, 0.9);
            padding: 15px 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
        }
        
        .breadcrumb a {
            color: #3498db;
            text-decoration: none;
            margin-right: 10px;
        }
        
        .upload-zone {
            border: 3px dashed #3498db;
            border-radius: 10px;
            padding: 40px;
            text-align: center;
            background: #f8f9fa;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .upload-zone:hover {
            border-color: #2980b9;
            background: #e9ecef;
        }
        
        .upload-zone.dragover {
            border-color: #2ecc71;
            background: #d4edda;
        }
        
        input[type="file"] {
            display: none;
        }
        
        .btn {
            background: #3498db;
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 5px;
            font-size: 1em;
            cursor: pointer;
            transition: background-color 0.3s;
            margin: 5px;
        }
        
        .btn:hover {
            background: #2980b9;
        }
        
        .btn-success {
            background: #2ecc71;
        }
        
        .btn-success:hover {
            background: #27ae60;
        }
        
        .btn-secondary {
            background: #95a5a6;
        }
        
        .btn-secondary:hover {
            background: #7f8c8d;
        }
        
        .file-list {
            list-style: none;
            margin-top: 20px;
        }
        
        .file-item {
            background: #f8f9fa;
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
            border-left: 4px solid #3498db;
        }
        
        .file-item.audio {
            border-left-color: #2ecc71;
        }
        
        .file-item.document {
            border-left-color: #e74c3c;
        }
        
        .progress {
            display: none;
            width: 100%;
            height: 30px;
            background: #e9ecef;
            border-radius: 5px;
            overflow: hidden;
            margin: 20px 0;
        }
        
        .progress-bar {
            height: 100%;
            background: linear-gradient(90deg, #3498db 0%, #2ecc71 100%);
            width: 0%;
            transition: width 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
        }
        
        .message {
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            display: none;
        }
        
        .message.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .message.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        .message.info {
            background: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }
        
        .folder-input {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 1em;
            margin: 10px 0;
        }
        
        .back-links {
            margin-top: 20px;
            text-align: center;
        }
        
        .back-links a {
            color: #3498db;
            text-decoration: none;
            margin: 0 15px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="breadcrumb">
            <a href="/browse/hovedindex.html">🏠 Home</a>
            {% if folderpath %}
            / <strong>{{ foldername }}</strong>
            {% endif %}
        </div>
        
        <div class="card">
            <h1>📤 Upload Files</h1>
            <p style="color: #7f8c8d; margin-bottom: 20px;">Folder: <strong>{{ foldername }}</strong></p>
            
            <div class="upload-zone" id="dropZone">
                <p style="font-size: 1.2em; margin-bottom: 10px;">📁 Drag & Drop Files Here</p>
                <p style="color: #7f8c8d;">or</p>
                <button class="btn" onclick="document.getElementById('fileInput').click()">
                    Choose Files
                </button>
                <input type="file" id="fileInput" multiple>
                <p style="margin-top: 15px; font-size: 0.9em; color: #95a5a6;">
                    Allowed: Audio (mp3, m4a, wav, etc.), Documents (pdf, docx, jpg, etc.)
                </p>
            </div>
            
            <div class="progress" id="progress">
                <div class="progress-bar" id="progressBar">0%</div>
            </div>
            
            <div class="message" id="message"></div>
        </div>
        
        <div class="card">
            <h2>📁 Create New Folder</h2>
            <input type="text" class="folder-input" id="folderName" placeholder="Enter folder name">
            <button class="btn btn-success" onclick="createFolder()">
                ➕ Create Folder
            </button>
        </div>
        
        {% if files %}
        <div class="card">
            <h2>📋 Files in This Folder ({{ files|length }})</h2>
            <ul class="file-list">
                {% for file in files %}
                <li class="file-item {% if file.type in ['mp3', 'm4a', 'wav', 'flac'] %}audio{% else %}document{% endif %}">
                    <strong>{{ file.name }}</strong>
                    <span style="color: #7f8c8d; float: right;">
                        {{ (file.size / 1024 / 1024)|round(2) }} MB
                    </span>
                </li>
                {% endfor %}
            </ul>
        </div>
        {% endif %}
        
        <div class="back-links">
            <a href="/browse/hovedindex.html">← Back to Main Index</a>
            <button class="btn btn-secondary" onclick="regenerateHTML()">
                🔄 Regenerate HTML
            </button>
        </div>
    </div>
    
    <script>
        const folderPath = "{{ folderpath }}";
        const dropZone = document.getElementById('dropZone');
        const fileInput = document.getElementById('fileInput');
        const progress = document.getElementById('progress');
        const progressBar = document.getElementById('progressBar');
        const message = document.getElementById('message');
        
        // Drag and drop handlers
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });
        
        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('dragover');
        });
        
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            const files = e.dataTransfer.files;
            uploadFiles(files);
        });
        
        fileInput.addEventListener('change', (e) => {
            uploadFiles(e.target.files);
        });
        
        function showMessage(text, type) {
            message.textContent = text;
            message.className = 'message ' + type;
            message.style.display = 'block';
            setTimeout(() => {
                message.style.display = 'none';
            }, 5000);
        }
        
        async function uploadFiles(files) {
            if (files.length === 0) return;
            
            progress.style.display = 'block';
            
            for (let i = 0; i < files.length; i++) {
                const file = files[i];
                const formData = new FormData();
                formData.append('file', file);
                formData.append('folder', folderPath);
                
                try {
                    const response = await fetch('/api/upload-file', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const result = await response.json();
                    
                    if (response.ok) {
                        const percent = Math.round(((i + 1) / files.length) * 100);
                        progressBar.style.width = percent + '%';
                        progressBar.textContent = percent + '%';
                        
                        showMessage(`✅ Uploaded: ${file.name}`, 'success');
                    } else {
                        showMessage(`❌ Error uploading ${file.name}: ${result.error}`, 'error');
                    }
                } catch (error) {
                    showMessage(`❌ Error: ${error.message}`, 'error');
                }
            }
            
            setTimeout(() => {
                progress.style.display = 'none';
                progressBar.style.width = '0%';
                fileInput.value = '';
                
                showMessage('✅ Upload complete! Refreshing...', 'success');
                setTimeout(() => location.reload(), 2000);
            }, 1000);
        }
        
        async function createFolder() {
            const folderName = document.getElementById('folderName').value.trim();
            
            if (!folderName) {
                showMessage('❌ Please enter a folder name', 'error');
                return;
            }
            
            try {
                const response = await fetch('/api/create-folder', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        parent: folderPath,
                        name: folderName
                    })
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    showMessage(`✅ Folder created: ${folderName}`, 'success');
                    document.getElementById('folderName').value = '';
                    setTimeout(() => location.reload(), 1500);
                } else {
                    showMessage(`❌ Error: ${result.error}`, 'error');
                }
            } catch (error) {
                showMessage(`❌ Error: ${error.message}`, 'error');
            }
        }
        
        async function regenerateHTML() {
            showMessage('🔄 Regenerating HTML pages...', 'info');
            
            try {
                const response = await fetch('/api/regenerate-html', {
                    method: 'POST'
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    showMessage('✅ HTML regenerated! Redirecting...', 'success');
                    setTimeout(() => {
                        window.location.href = '/browse/hovedindex.html';
                    }, 2000);
                } else {
                    showMessage(`❌ Error: ${result.error}`, 'error');
                }
            } catch (error) {
                showMessage(`❌ Error: ${error.message}`, 'error');
            }
        }
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    print("🚀 STENOGRAFEN Upload Server Starting...")
    print(f"📁 Serving from: {INPUT_FOLDER}")
    print(f"🌐 Open: http://localhost:5000")
    print(f"📤 Upload UI: http://localhost:5000/upload-ui/")
    app.run(host='0.0.0.0', port=5000, debug=True)
