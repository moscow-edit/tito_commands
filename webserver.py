from flask import Flask, jsonify, request
from threading import Thread
import time
import os
import json
from datetime import datetime

app = Flask(__name__)

start_time = time.time()

class BotController:
    outfit_pending = None
    item_pending = None
    command_queue = []
    
    @staticmethod
    def get_outfits():
        try:
            if os.path.exists("outfits.json"):
                with open("outfits.json", "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading outfits: {e}")
        return {}
    
    @staticmethod
    def set_pending_outfit(outfit_id):
        BotController.outfit_pending = outfit_id
        return True
    
    @staticmethod
    def get_pending_outfit():
        outfit = BotController.outfit_pending
        BotController.outfit_pending = None
        return outfit
    
    @staticmethod
    def set_pending_item(item_id):
        BotController.item_pending = item_id
        return True
    
    @staticmethod
    def get_pending_item():
        item = BotController.item_pending
        BotController.item_pending = None
        return item
    
    @staticmethod
    def queue_command(cmd):
        BotController.command_queue.append(cmd)
    
    @staticmethod
    def get_queued_command():
        if BotController.command_queue:
            return BotController.command_queue.pop(0)
        return None

def get_uptime():
    uptime = time.time() - start_time
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    seconds = int(uptime % 60)
    return f"{hours}h {minutes}m {seconds}s"

@app.route("/", methods=["GET"])
def home():
    outfits = BotController.get_outfits()
    outfit_options = "".join([f'<option value="{oid}">{oid}</option>' for oid in outfits.keys()])
    
    html = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Highrise Bot Dashboard</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        h1 {{ text-align: center; color: white; margin-bottom: 20px; }}
        .card {{ background: white; border-radius: 10px; padding: 20px; margin-bottom: 15px; }}
        .card h2 {{ color: #667eea; margin-bottom: 15px; font-size: 1.2em; }}
        .status {{ display: flex; justify-content: space-around; text-align: center; }}
        .status div {{ padding: 10px; }}
        .status .value {{ font-size: 1.5em; font-weight: bold; color: #333; }}
        .status .label {{ color: #666; font-size: 0.9em; }}
        input, select, button {{ padding: 10px; border: 1px solid #ddd; border-radius: 5px; margin: 5px; }}
        button {{ background: #667eea; color: white; cursor: pointer; border: none; }}
        button:hover {{ background: #764ba2; }}
        .flex {{ display: flex; gap: 10px; flex-wrap: wrap; }}
        #result {{ margin-top: 10px; padding: 10px; border-radius: 5px; }}
        .success {{ background: #d4edda; color: #155724; }}
        .error {{ background: #f8d7da; color: #721c24; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Highrise Bot</h1>
        
        <div class="card">
            <div class="status">
                <div><div class="value">🟢</div><div class="label">Online</div></div>
                <div><div class="value" id="uptime">{get_uptime()}</div><div class="label">Uptime</div></div>
            </div>
        </div>
        
        <div class="card">
            <h2>👗 تغيير الملابس</h2>
            <div class="flex">
                <select id="outfit"><option value="">-- اختر --</option>{outfit_options}</select>
                <button onclick="applyOutfit()">تطبيق</button>
            </div>
            <div class="flex" style="margin-top: 10px;">
                <input type="text" id="itemId" placeholder="أو اكتب Item ID مباشرة" style="flex: 1;">
                <button onclick="applyItem()">لبس</button>
            </div>
        </div>
        
        <div class="card">
            <h2>⚙️ تنفيذ أمر</h2>
            <div class="flex">
                <input type="text" id="cmd" placeholder="اكتب الأمر..." style="flex: 1;">
                <button onclick="runCmd()">تنفيذ</button>
            </div>
        </div>
        
        <div class="card">
            <h2>🎭 أوامر سريعة</h2>
            <div class="flex">
                <button onclick="quickCmd('ping')">Ping</button>
                <button onclick="quickCmd('uptime')">Uptime</button>
                <button onclick="quickCmd('wallet')">محفظة</button>
            </div>
        </div>
        
        <div id="result"></div>
    </div>
    
    <script>
        function showResult(msg, ok) {{
            const el = document.getElementById('result');
            el.textContent = msg;
            el.className = ok ? 'success' : 'error';
            setTimeout(() => el.textContent = '', 3000);
        }}
        
        async function applyOutfit() {{
            const id = document.getElementById('outfit').value;
            if (!id) return showResult('اختر ملابس', false);
            const res = await fetch('/api/outfit/apply', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{outfit_id: id}})
            }});
            const data = await res.json();
            showResult(data.message, data.status === 'success');
        }}
        
        async function applyItem() {{
            const id = document.getElementById('itemId').value.trim();
            if (!id) return showResult('اكتب Item ID', false);
            const res = await fetch('/api/outfit/apply-item', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{item_id: id}})
            }});
            const data = await res.json();
            showResult(data.message, data.status === 'success');
        }}
        
        async function runCmd() {{
            const cmd = document.getElementById('cmd').value.trim();
            if (!cmd) return showResult('اكتب أمر', false);
            await fetch('/api/command/execute', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{command: cmd}})
            }});
            showResult('تم: ' + cmd, true);
            document.getElementById('cmd').value = '';
        }}
        
        function quickCmd(cmd) {{
            fetch('/api/command/execute', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{command: cmd}})
            }});
            showResult('تم: ' + cmd, true);
        }}
        
        setInterval(() => {{
            fetch('/api/uptime').then(r => r.json()).then(d => {{
                document.getElementById('uptime').textContent = d.uptime;
            }});
        }}, 30000);
    </script>
</body>
</html>"""
    return html

@app.route("/api/outfit/apply", methods=["POST"])
def apply_outfit():
    try:
        data = request.get_json()
        outfit_id = data.get("outfit_id")
        if not outfit_id:
            return jsonify({"status": "error", "message": "لم تحدد ملابس"})
        BotController.set_pending_outfit(outfit_id)
        return jsonify({"status": "success", "message": f"تم تعيين: {outfit_id}"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route("/api/outfit/apply-item", methods=["POST"])
def apply_item():
    try:
        data = request.get_json()
        item_id = data.get("item_id")
        if not item_id:
            return jsonify({"status": "error", "message": "لم تحدد ID"})
        BotController.set_pending_item(item_id)
        return jsonify({"status": "success", "message": f"تم تعيين: {item_id}"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route("/api/command/execute", methods=["POST"])
def execute_command():
    try:
        data = request.get_json()
        command = data.get("command")
        if command:
            BotController.queue_command(command)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route("/api/outfits", methods=["GET"])
def get_outfits():
    return jsonify(BotController.get_outfits())

@app.route("/api/uptime", methods=["GET"])
def api_uptime():
    return jsonify({"uptime": get_uptime()})

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route("/api/items", methods=["GET"])
def get_items():
    try:
        if os.path.exists("outfit_items_database.json"):
            with open("outfit_items_database.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                items = data.get("outfit_items", [])
                return jsonify({"status": "success", "items": items[:100]})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
    return jsonify({"status": "error", "message": "no database"})

def keep_alive():
    port = int(os.environ.get("PORT", 5000))
    print(f"🌐 Dashboard: http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True, use_reloader=False)

if __name__ == "__main__":
    keep_alive()
