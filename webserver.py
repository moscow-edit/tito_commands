from flask import Flask, render_template_string, jsonify, request
from threading import Thread
import time
import os
import json
from datetime import datetime
import psutil

app = Flask(__name__)

# ==================== نظام المراقبة ====================

class BotMetrics:
    """نظام جمع metrics"""
    def __init__(self):
        self.metrics = {
            "requests_count": 0,
            "errors_count": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "last_error": None,
            "peak_memory": 0,
            "current_memory": 0,
        }
    
    def add_request(self):
        self.metrics["requests_count"] += 1
    
    def add_error(self, error_msg):
        self.metrics["errors_count"] += 1
        self.metrics["last_error"] = {"message": error_msg, "timestamp": datetime.now().isoformat()}
    
    def update_memory(self):
        process = psutil.Process(os.getpid())
        memory_mb = process.memory_info().rss / 1024 / 1024
        self.metrics["current_memory"] = memory_mb
        if memory_mb > self.metrics["peak_memory"]:
            self.metrics["peak_memory"] = memory_mb

metrics = BotMetrics()
start_time = time.time()
server_started = datetime.now()

# ==================== نظام التحكم العام ====================

class BotController:
    """التحكم الموحد بالبوت"""
    outfit_pending = None
    item_pending = None  # 🔧 لـ direct item IDs
    command_queue = []
    
    @staticmethod
    def get_outfits():
        """جلب قائمة الملابس"""
        try:
            if os.path.exists("outfits.json"):
                with open("outfits.json", "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading outfits: {e}")
        return {}
    
    @staticmethod
    def set_pending_outfit(outfit_id):
        """تعيين ملابس للتطبيق"""
        BotController.outfit_pending = outfit_id
        print(f"📍 Outfit pending: {outfit_id}")
        return True
    
    @staticmethod
    def get_pending_outfit():
        """الحصول على الملابس المعلقة"""
        outfit = BotController.outfit_pending
        BotController.outfit_pending = None
        return outfit
    
    @staticmethod
    def set_pending_item(item_id):
        """تعيين item ID للتطبيق المباشر"""
        BotController.item_pending = item_id
        print(f"📍 Item pending: {item_id}")
        return True
    
    @staticmethod
    def get_pending_item():
        """الحصول على item ID المعلق"""
        item = BotController.item_pending
        BotController.item_pending = None
        return item
    
    @staticmethod
    def queue_command(cmd):
        """إضافة أمر للطابور"""
        BotController.command_queue.append(cmd)
        print(f"📢 Command queued: {cmd}")
    
    @staticmethod
    def get_queued_command():
        """جلب أمر من الطابور"""
        if BotController.command_queue:
            return BotController.command_queue.pop(0)
        return None

def get_bot_status():
    """الحصول على حالة البوت"""
    uptime = time.time() - start_time
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    seconds = int(uptime % 60)
    
    return {
        "status": "running",
        "uptime_seconds": int(uptime),
        "uptime_formatted": f"{hours}h {minutes}m {seconds}s",
        "timestamp": time.time(),
        "server_start": server_started.isoformat()
    }

# ==================== المسارات ====================

@app.route("/", methods=["GET"])
def home():
    """Dashboard متطور متصل بالبوت"""
    metrics.add_request()
    bot_status = get_bot_status()
    outfits = BotController.get_outfits()
    
    outfit_options = "".join([f'<option value="{oid}">{oid}</option>' for oid in outfits.keys()])
    
    html = f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Highrise Bot - Dashboard Pro</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #333; min-height: 100vh; padding: 20px; }}
            .container {{ max-width: 1400px; margin: 0 auto; }}
            h1 {{ text-align: center; color: white; margin-bottom: 30px; font-size: 2.5em; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }}
            .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }}
            .stat-card {{ background: white; border-radius: 10px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
            .stat-card h3 {{ color: #667eea; font-size: 0.9em; text-transform: uppercase; margin-bottom: 10px; }}
            .stat-card .value {{ font-size: 2em; font-weight: bold; color: #333; }}
            .section {{ background: white; border-radius: 10px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
            .section h2 {{ color: #667eea; margin-bottom: 15px; font-size: 1.5em; border-bottom: 2px solid #667eea; padding-bottom: 10px; }}
            input, select, button {{ padding: 10px; border: 1px solid #ddd; border-radius: 5px; font-size: 1em; }}
            button {{ background: #667eea; color: white; cursor: pointer; margin: 5px; }}
            button:hover {{ background: #764ba2; }}
            .success {{ color: #4caf50; }}
            .error {{ color: #f44336; }}
            .info-row {{ display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #eee; }}
            .cmd-list {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 10px; }}
            .cmd-btn {{ padding: 8px; font-size: 0.9em; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 Highrise Bot Dashboard Pro</h1>
            
            <div class="grid">
                <div class="stat-card">
                    <h3>🟢 حالة البوت</h3>
                    <div class="value">Online</div>
                </div>
                <div class="stat-card">
                    <h3>⏱️ وقت التشغيل</h3>
                    <div class="value">{bot_status['uptime_formatted']}</div>
                </div>
                <div class="stat-card">
                    <h3>💾 الذاكرة</h3>
                    <div class="value">{metrics.metrics['current_memory']:.1f} MB</div>
                </div>
                <div class="stat-card">
                    <h3>📊 الطلبات</h3>
                    <div class="value">{metrics.metrics['requests_count']}</div>
                </div>
            </div>
            
            <div class="section">
                <h2>👗 تغيير ملابس البوت</h2>
                
                <div style="margin: 10px 0;">
                    <h4 style="color: #667eea; margin-bottom: 8px;">الطريقة 1️⃣: من القائمة المحفوظة</h4>
                    <div style="display: flex; gap: 10px;">
                        <select id="outfitSelect">
                            <option value="">-- اختر ملابس --</option>
                            {outfit_options}
                        </select>
                        <button onclick="changeOutfit()">✅ تطبيق</button>
                    </div>
                    <p id="outfitStatus"></p>
                </div>
                
                <div style="margin: 15px 0; padding: 10px; background: #f0f0f0; border-radius: 5px;">
                    <h4 style="color: #667eea; margin-bottom: 8px;">الطريقة 2️⃣: حط ID مباشرة</h4>
                    <div style="display: flex; gap: 10px; align-items: center;">
                        <input type="text" id="itemIdInput" placeholder="مثل: body-flesh أو watch-gold-room12019watch" style="flex: 1;">
                        <button onclick="applyItemId()" style="background: #ff9800;">🎯 لبس ID</button>
                    </div>
                    <p id="itemStatus"></p>
                </div>
            </div>
            
            <div class="section">
                <h2>⚙️ تنفيذ الأوامر</h2>
                <div style="display: flex; gap: 10px; margin: 10px 0;">
                    <input type="text" id="commandInput" placeholder="اكتب الأمر..." style="flex: 1;">
                    <button onclick="executeCommand()">🚀 تنفيذ</button>
                </div>
                <p id="commandStatus"></p>
            </div>
            
            <div class="section">
                <h2>🎨 إنشاء لبسة جديدة</h2>
                <div style="margin: 10px 0;">
                    <input type="text" id="outfitNameInput" placeholder="اسم اللبسة (مثل: tilj)" style="width: 200px;">
                    <button onclick="toggleItemsPanel()" style="margin: 5px;">📋 اختر Items</button>
                </div>
                <div id="itemsPanel" style="display: none; background: #f9f9f9; padding: 10px; border-radius: 5px; max-height: 300px; overflow-y: auto; margin: 10px 0;">
                    <div id="itemsList">جاري التحميل...</div>
                </div>
                <button onclick="createOutfit()" style="margin-top: 10px; background: #4caf50;">✨ إنشاء اللبسة</button>
                <p id="createStatus" style="margin-top: 10px;"></p>
            </div>
            
            <div class="section">
                <h2>🎭 الأوامر السريعة</h2>
                <div class="cmd-list">
                    <button class="cmd-btn" onclick="quickCmd('dance enable')">✅ تفعيل رقص</button>
                    <button class="cmd-btn" onclick="quickCmd('dance disable')">❌ تعطيل رقص</button>
                    <button class="cmd-btn" onclick="quickCmd('ping')">🏓 Ping</button>
                    <button class="cmd-btn" onclick="quickCmd('uptime')">⏰ Uptime</button>
                    <button class="cmd-btn" onclick="quickCmd('wallet')">💰 محفظة</button>
                </div>
            </div>
            
            <footer style="text-align: center; color: white; margin-top: 30px;">
                <p>🚀 Highrise Bot - ZERO DOWNTIME MODE</p>
            </footer>
        </div>
        
        <script>
            let availableItems = [];
            let selectedItems = [];
            
            async function loadItems() {{
                try {{
                    const res = await fetch('/api/items');
                    const data = await res.json();
                    if (data.status === 'success') {{
                        availableItems = data.items;
                        renderItems();
                    }}
                }} catch(e) {{
                    console.error('خطأ:', e);
                }}
            }}
            
            function renderItems() {{
                const panel = document.getElementById('itemsList');
                panel.innerHTML = availableItems.map((item, idx) => `
                    <div style="display: flex; align-items: center; padding: 5px; border-bottom: 1px solid #eee;">
                        <input type="checkbox" id="item-${{idx}}" value="${{item.id}}" onchange="toggleItem(this)">
                        <label for="item-${{idx}}" style="margin-right: 10px; flex: 1;">
                            <strong>${{item.name}}</strong> - <span style="color: #999;">${{item.id}}</span>
                        </label>
                    </div>
                `).join('');
            }}
            
            function toggleItemsPanel() {{
                const panel = document.getElementById('itemsPanel');
                if (panel.style.display === 'none') {{
                    panel.style.display = 'block';
                    if (availableItems.length === 0) {{
                        loadItems();
                    }}
                }} else {{
                    panel.style.display = 'none';
                }}
            }}
            
            function toggleItem(checkbox) {{
                if (checkbox.checked) {{
                    selectedItems.push(checkbox.value);
                }} else {{
                    selectedItems = selectedItems.filter(id => id !== checkbox.value);
                }}
            }}
            
            async function createOutfit() {{
                const name = document.getElementById('outfitNameInput').value;
                if (!name) {{
                    showStatus('createStatus', 'اكتب اسم اللبسة أولاً!', 'error');
                    return;
                }}
                if (selectedItems.length === 0) {{
                    showStatus('createStatus', 'اختر items من القائمة!', 'error');
                    return;
                }}
                
                try {{
                    const res = await fetch('/api/outfit/create', {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify({{
                            name: name,
                            items: selectedItems
                        }})
                    }});
                    const data = await res.json();
                    showStatus('createStatus', data.message, data.status === 'success' ? 'success' : 'error');
                    
                    if (data.status === 'success') {{
                        // أعد تحميل قائمة الملابس
                        setTimeout(() => {{
                            location.reload();
                        }}, 1000);
                    }}
                }} catch(e) {{
                    showStatus('createStatus', 'خطأ: ' + e.message, 'error');
                }}
            }}
            
            // تحميل الـ items عند فتح الصفحة
            window.onload = function() {{
                loadItems();
            }};
            
            async function changeOutfit() {{
                const outfitId = document.getElementById('outfitSelect').value;
                if (!outfitId) {{
                    showStatus('outfitStatus', 'اختر ملابس أولاً', 'error');
                    return;
                }}
                
                try {{
                    const res = await fetch('/api/outfit/apply', {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify({{outfit_id: outfitId}})
                    }});
                    const data = await res.json();
                    showStatus('outfitStatus', data.message, data.status === 'success' ? 'success' : 'error');
                }} catch(e) {{
                    showStatus('outfitStatus', 'خطأ: ' + e.message, 'error');
                }}
            }}
            
            async function applyItemId() {{
                const itemId = document.getElementById('itemIdInput').value.trim();
                if (!itemId) {{
                    showStatus('itemStatus', 'اكتب ID item أولاً', 'error');
                    return;
                }}
                
                try {{
                    const res = await fetch('/api/outfit/apply-item', {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify({{item_id: itemId}})
                    }});
                    const data = await res.json();
                    showStatus('itemStatus', data.message, data.status === 'success' ? 'success' : 'error');
                }} catch(e) {{
                    showStatus('itemStatus', 'خطأ: ' + e.message, 'error');
                }}
            }}
            
            async function executeCommand() {{
                const cmd = document.getElementById('commandInput').value;
                if (!cmd) {{
                    showStatus('commandStatus', 'اكتب أمر أولاً', 'error');
                    return;
                }}
                
                try {{
                    const res = await fetch('/api/command/execute', {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify({{command: cmd}})
                    }});
                    const data = await res.json();
                    showStatus('commandStatus', '✅ تم: ' + cmd, 'success');
                    document.getElementById('commandInput').value = '';
                }} catch(e) {{
                    showStatus('commandStatus', 'خطأ: ' + e.message, 'error');
                }}
            }}
            
            async function quickCmd(cmd) {{
                try {{
                    const res = await fetch('/api/command/execute', {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify({{command: cmd}})
                    }});
                    const data = await res.json();
                    showStatus('commandStatus', '✅ ' + cmd, 'success');
                }} catch(e) {{
                    showStatus('commandStatus', '❌ خطأ', 'error');
                }}
            }}
            
            function showStatus(id, msg, type) {{
                const el = document.getElementById(id);
                el.textContent = msg;
                el.className = type;
            }}
        </script>
    </body>
    </html>
    """
    return html

@app.route("/api/outfit/apply", methods=["POST"])
def apply_outfit():
    """تطبيق ملابس البوت"""
    metrics.add_request()
    try:
        data = request.get_json()
        outfit_id = data.get("outfit_id")
        if not outfit_id:
            return jsonify({"status": "error", "message": "❌ لم تحدد ملابس"})
        
        BotController.set_pending_outfit(outfit_id)
        return jsonify({"status": "success", "message": f"✅ تم تعيين الملابس: {outfit_id}"})
    except Exception as e:
        return jsonify({"status": "error", "message": f"❌ خطأ: {str(e)}"})

@app.route("/api/outfit/apply-item", methods=["POST"])
def apply_item():
    """تطبيق item واحد مباشرة"""
    metrics.add_request()
    try:
        data = request.get_json()
        item_id = data.get("item_id")
        if not item_id:
            return jsonify({"status": "error", "message": "❌ لم تحدد ID"})
        
        # تعيين item مباشر للبوت
        BotController.set_pending_item(item_id)
        
        return jsonify({"status": "success", "message": f"✅ تم تعيين: {item_id}"})
    except Exception as e:
        return jsonify({"status": "error", "message": f"❌ خطأ: {str(e)}"})

@app.route("/api/command/execute", methods=["POST"])
def execute_command():
    """تنفيذ أمر"""
    metrics.add_request()
    try:
        data = request.get_json()
        command = data.get("command")
        if not command:
            return jsonify({"status": "error", "message": "❌ لم تحدد أمر"})
        
        BotController.queue_command(command)
        return jsonify({"status": "success", "message": f"✅ تم قائمة الأمر"})
    except Exception as e:
        return jsonify({"status": "error", "message": f"❌ خطأ: {str(e)}"})

@app.route("/api/items", methods=["GET"])
def get_items():
    """جلب قائمة كل الـ items المتوفرة"""
    metrics.add_request()
    try:
        if os.path.exists("outfit_items_database.json"):
            with open("outfit_items_database.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                items = data.get("outfit_items", [])
                return jsonify({"status": "success", "items": items[:100]})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
    return jsonify({"status": "error", "message": "لا توجد قاعدة بيانات"})

@app.route("/api/outfit/create", methods=["POST"])
def create_outfit():
    """إنشاء لبسة جديدة بـ items معينة وحفظها"""
    metrics.add_request()
    try:
        data = request.get_json()
        outfit_name = data.get("name", "new_outfit")
        items_ids = data.get("items", [])
        
        if not items_ids or not outfit_name:
            return jsonify({"status": "error", "message": "❌ حدد اسم واختر items"})
        
        # تحويل IDs إلى Item objects
        items_data = []
        for item_id in items_ids:
            items_data.append({
                "id": item_id,
                "type": "clothing",
                "amount": 1
            })
        
        # حفظ في outfits.json
        try:
            if os.path.exists("outfits.json"):
                with open("outfits.json", "r", encoding="utf-8") as f:
                    outfits = json.load(f)
            else:
                outfits = {}
            
            outfits[outfit_name] = items_data
            with open("outfits.json", "w", encoding="utf-8") as f:
                json.dump(outfits, f, ensure_ascii=False, indent=2)
            
            return jsonify({"status": "success", "message": f"✅ تم إنشاء لبسة '{outfit_name}' بـ {len(items_ids)} items"})
        except Exception as e:
            return jsonify({"status": "error", "message": f"❌ خطأ في الحفظ: {str(e)}"})
    except Exception as e:
        return jsonify({"status": "error", "message": f"❌ خطأ: {str(e)}"})

@app.route("/api/outfits", methods=["GET"])
def get_outfits():
    """جلب قائمة الملابس"""
    metrics.add_request()
    return jsonify(BotController.get_outfits())

@app.route("/health", methods=["GET"])
def health():
    """فحص صحة النظام"""
    metrics.update_memory()
    metrics.add_request()
    status = get_bot_status()
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime": status,
        "memory_mb": metrics.metrics["current_memory"],
        "peak_memory_mb": metrics.metrics["peak_memory"]
    })

@app.route("/api/status", methods=["GET"])
def api_status():
    """معلومات البوت"""
    metrics.add_request()
    return jsonify({
        "status": "running",
        "bot_info": get_bot_status(),
        "metrics": metrics.metrics
    })

@app.route("/api/metrics", methods=["GET"])
def api_metrics():
    """معلومات الأداء"""
    metrics.add_request()
    metrics.update_memory()
    return jsonify(metrics.metrics)

@app.route("/api/alive", methods=["GET"])
def api_alive():
    """تأكيد الحياة"""
    metrics.add_request()
    return jsonify({"alive": True, "timestamp": datetime.now().isoformat()})

def keep_alive():
    """تشغيل السيرفر في خيط منفصل"""
    port = int(os.environ.get("PORT", 5000))
    print("🚀 Dashboard is starting...")
    print(f"🌐 URL: http://0.0.0.0:{port}")
    print("🚀 Features: Live outfit control, command execution, real-time metrics")
    print("🔌 Endpoints: /api/outfit/apply, /api/command/execute, /api/outfits")
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)

if __name__ == "__main__":
    keep_alive()
