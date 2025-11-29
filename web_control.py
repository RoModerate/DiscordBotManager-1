
from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from flask_cors import CORS
from functools import wraps
import subprocess
import signal
import os
import psutil
import time
import requests
from database import Database

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'change-this-in-production')
CORS(app)
bot_process = None
db = Database()

# Discord OAuth Config
DISCORD_CLIENT_ID = os.getenv('DISCORD_CLIENT_ID')
DISCORD_CLIENT_SECRET = os.getenv('DISCORD_CLIENT_SECRET')
DISCORD_REDIRECT_URI = os.getenv('DISCORD_REDIRECT_URI', 'http://localhost:5000/api/auth/discord/callback')
DISCORD_OAUTH_URL = 'https://discord.com/api/oauth2/authorize'
DISCORD_TOKEN_URL = 'https://discord.com/api/oauth2/token'
DISCORD_API_URL = 'https://discord.com/api/users/@me'
DISCORD_GUILD_ID = os.getenv('GUILD_ID')
OWNER_IDS = ['YOUR_DISCORD_USER_ID']  # Add owner Discord user IDs here

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'discord_user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def owner_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'discord_user' not in session:
            return redirect(url_for('login'))
        if session['discord_user']['id'] not in OWNER_IDS:
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

def is_bot_running():
    global bot_process
    if bot_process and bot_process.poll() is None:
        return True
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info.get('cmdline')
            if cmdline and len(cmdline) > 1:
                cmdline_str = ' '.join(cmdline)
                if 'python' in cmdline[0].lower() and 'main.py' in cmdline_str:
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    
    return False

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login')
def login():
    if 'discord_user' in session:
        return redirect(url_for('dashboard'))
    
    oauth_url = f"{DISCORD_OAUTH_URL}?client_id={DISCORD_CLIENT_ID}&redirect_uri={DISCORD_REDIRECT_URI}&response_type=code&scope=identify%20guilds"
    return render_template('login.html', oauth_url=oauth_url)

@app.route('/api/auth/discord/callback')
def discord_callback():
    code = request.args.get('code')
    
    if not code:
        return redirect(url_for('login'))
    
    # Exchange code for access token
    data = {
        'client_id': DISCORD_CLIENT_ID,
        'client_secret': DISCORD_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': DISCORD_REDIRECT_URI
    }
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    r = requests.post(DISCORD_TOKEN_URL, data=data, headers=headers)
    r.raise_for_status()
    token_data = r.json()
    
    # Get user info
    headers = {
        'Authorization': f"Bearer {token_data['access_token']}"
    }
    
    r = requests.get(DISCORD_API_URL, headers=headers)
    r.raise_for_status()
    user_data = r.json()
    
    session['discord_user'] = user_data
    session['access_token'] = token_data['access_token']
    
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/owner-portal')
@owner_required
def owner_portal():
    return render_template('owner_portal.html')

@app.route('/status')
def status():
    running = is_bot_running()
    ai_ops = db.get_ai_ops_status()
    return jsonify({
        'running': running,
        'bot_status': 'Online' if running else 'Offline',
        'ai_ops_enabled': ai_ops
    })

@app.route('/memory_stats')
def memory_stats():
    memory_data = db.data.get('ai_memory', {})
    messages = memory_data.get('messages', [])
    return jsonify({
        'total_messages': len(messages),
        'recent_messages': messages[-50:] if messages else []
    })

@app.route('/ai/start', methods=['POST'])
@owner_required
def ai_start():
    try:
        db.set_ai_ops_status(True)
        return jsonify({'success': True, 'message': 'AI operations started successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/ai/stop', methods=['POST'])
@owner_required
def ai_stop():
    try:
        db.set_ai_ops_status(False)
        return jsonify({'success': True, 'message': 'AI operations stopped successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/ai/status')
def ai_status():
    return jsonify({'ai_ops_enabled': db.get_ai_ops_status()})

@app.route('/start')
@owner_required
def start_bot():
    global bot_process
    
    if is_bot_running():
        return jsonify({'success': False, 'message': 'Bot is already running'})
    
    try:
        bot_process = subprocess.Popen(
            ['python3', 'main.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.PIPE,
            preexec_fn=os.setsid
        )
        
        time.sleep(2)
        
        if bot_process.poll() is None:
            return jsonify({'success': True, 'message': 'Bot started successfully'})
        else:
            return jsonify({'success': False, 'message': 'Bot failed to start'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Failed to start bot: {str(e)}'})

@app.route('/stop')
@owner_required
def stop_bot():
    global bot_process
    
    if not is_bot_running():
        return jsonify({'success': False, 'message': 'Bot is not running'})
    
    try:
        killed = False
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info.get('cmdline')
                if cmdline and len(cmdline) > 1:
                    cmdline_str = ' '.join(cmdline)
                    if 'python' in cmdline[0].lower() and 'main.py' in cmdline_str:
                        proc.terminate()
                        try:
                            proc.wait(timeout=5)
                        except psutil.TimeoutExpired:
                            proc.kill()
                        killed = True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        bot_process = None
        
        if killed:
            return jsonify({'success': True, 'message': 'Bot stopped successfully'})
        else:
            return jsonify({'success': False, 'message': 'No bot process found to stop'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Failed to stop bot: {str(e)}'})

@app.route('/restart')
@owner_required
def restart_bot():
    stop_bot()
    time.sleep(3)
    return start_bot()

@app.route('/teaches')
def get_teaches():
    try:
        teaches = db.get_all_teaches()
        return jsonify({'success': True, 'teaches': teaches})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/add_teach', methods=['POST'])
@owner_required
def add_teach():
    try:
        data = request.get_json()
        trigger = data.get('trigger', '').strip()
        response = data.get('response', '').strip()
        
        if not trigger or not response:
            return jsonify({'success': False, 'message': 'Trigger and response are required'})
        
        teach_id = db.add_teach_advanced(trigger, response, 0, 'response')
        
        from datetime import datetime
        timestamp = datetime.now().strftime('%I:%M %p')
        
        return jsonify({
            'success': True,
            'message': f'Successfully taught: "{trigger}" at {timestamp}',
            'teach_id': teach_id
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/remove_teach', methods=['POST'])
@owner_required
def remove_teach():
    try:
        data = request.get_json()
        identifier = data.get('identifier', '').strip()
        
        if not identifier:
            return jsonify({'success': False, 'message': 'Identifier is required'})
        
        success = db.remove_teach(identifier)
        
        if not success:
            success = db.remove_teach_by_trigger(identifier)
        
        from datetime import datetime
        timestamp = datetime.now().strftime('%I:%M %p')
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Response removed at {timestamp}'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No taught response found with that identifier'
            })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
