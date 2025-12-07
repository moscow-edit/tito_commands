import time
import random
import json
import os
import re
import traceback
import asyncio
from datetime import datetime
from typing import cast, Literal
import warnings

# 🔇 كتم تحذير pkg_resources من مكتبة Setuptools (لا يؤثر على الأداء)
warnings.filterwarnings("ignore", category=UserWarning, message=".*pkg_resources is deprecated.*")

# 🏗️ مكتبة Highrise الرسمية (v24.1.0+)
from highrise import BaseBot, User, Position, AnchorPosition
from highrise.models import Item, CurrencyItem, SessionMetadata, RoomPermissions
from highrise.webapi import WebAPI

# Helper function لتحويل amount لـ gold_bar format
def amount_to_gold_bar(amount: int) -> Literal["gold_bar_1", "gold_bar_5", "gold_bar_10", "gold_bar_50", "gold_bar_100", "gold_bar_500", "gold_bar_1k", "gold_bar_5000", "gold_bar_10k"]:
    """تحويل رقم الذهب إلى الـ format المطلوب"""
    valid_amounts = [1, 5, 10, 50, 100, 500, 1000, 5000, 10000]
    if amount not in valid_amounts:
        # إيجاد أقرب قيمة صحيحة
        amount = min(valid_amounts, key=lambda x: abs(x - amount))
    
    amount_map = {
        1: "gold_bar_1",
        5: "gold_bar_5",
        10: "gold_bar_10",
        50: "gold_bar_50",
        100: "gold_bar_100",
        500: "gold_bar_500",
        1000: "gold_bar_1k",
        5000: "gold_bar_5000",
        10000: "gold_bar_10k"
    }
    return cast(Literal["gold_bar_1", "gold_bar_5", "gold_bar_10", "gold_bar_50", "gold_bar_100", "gold_bar_500", "gold_bar_1k", "gold_bar_5000", "gold_bar_10k"], amount_map[amount])


# ⏰ تتبع وقت تشغيل البوت
bot_start_time = datetime.now()
auto_tip_enabled = False
auto_tip_amount = 1
auto_tip_delay = 5

# 💾 نظام الاسترجاع والنسخ الاحتياطية المتقدم

# 📞 قائمة المستخدمين الذين تواصلوا مع البوت
contact_list_file = "contact_list.json"
def load_contact_list():
    if os.path.exists(contact_list_file):
        with open(contact_list_file, "r", encoding="utf-8") as f:
            try:
                return set(json.load(f))
            except Exception:
                return set()
    return set()

def save_contact_list(contacts):
    with open(contact_list_file, "w", encoding="utf-8") as f:
        json.dump(list(contacts), f, ensure_ascii=False, indent=2)

contact_list = load_contact_list()

# 🔄 نظام أوامر من الواجهة البرمجية
command_queue = []
command_lock = asyncio.Lock()

async def add_command(command_type, **kwargs):
    """إضافة أمر للـ queue"""
    global command_queue
    async with command_lock:
        command_queue.append({"type": command_type, **kwargs})

async def get_next_command():
    """أخذ الأمر التالي من الـ queue"""
    global command_queue
    async with command_lock:
        if command_queue:
            return command_queue.pop(0)
    return None

def get_saved_outfits():
    """جلب قائمة اللبسات المحفوظة"""
    try:
        if os.path.exists(OUTFITS_FILE):
            data = load_all_outfits()
            return [{"name": k, "items": v} for k, v in data.items()]
    except:
        pass
    return []













OUTFITS_FILE = "outfits.json"

def load_all_outfits():
    if os.path.exists(OUTFITS_FILE):
        with open(OUTFITS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_all_outfits(data):
    with open(OUTFITS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def save_named_outfit(username, outfit):
    data = load_all_outfits()
    data[username.lower()] = [
        {"id": item.id, "type": item.type, "amount": getattr(item, "amount", 1)}
        for item in outfit
    ]
    save_all_outfits(data)






def save_bot_position(position: dict):
    with open("bot_position.json", "w", encoding="utf-8") as f:
        json.dump(position, f)

def load_bot_position():
    if os.path.exists("bot_position.json"):
        with open("bot_position.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return None


    

# ⬅️ فوق في الكود (global variable)
allowed_vip_users = ["q.xx"]  # صاحب البوت الأساسي

def save_allowed_vip_users():
    with open("allowed_vip_users.json", "w", encoding="utf-8") as f:
        json.dump(allowed_vip_users, f)

def load_allowed_vip_users():
    global allowed_vip_users
    try:
        with open("allowed_vip_users.json", "r", encoding="utf-8") as f:
            allowed_vip_users = json.load(f)
    except:
        allowed_vip_users = ["q.xx"]



# 📌 ملف نخزن فيه المستخدمين المسموح لهم
ALLOWED_SWMS_FILE = "allowed_swms.json"

# نحاول نقرأ الملف لو موجود
if os.path.exists(ALLOWED_SWMS_FILE):
    with open(ALLOWED_SWMS_FILE, "r") as f:
        allowed_addswm_users = json.load(f)
        if not isinstance(allowed_addswm_users, list):  # 👈 حماية
            allowed_addswm_users = ["q.xx"]
else:
    allowed_addswm_users = ["q.xx"]



# 🛠️ دوال الحفظ
def save_allowed_swms():
    with open(ALLOWED_SWMS_FILE, "w") as f:
        json.dump(allowed_addswm_users, f, indent=4)




special_welcomes = {}
def load_custom_welcomes():
    try:
        with open("special_welcomes.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_custom_welcomes():
    with open("special_welcomes.json", "w", encoding="utf-8") as f:
        json.dump(special_welcomes, f, ensure_ascii=False, indent=2)


room_commands_file = "room_commands.json"
room_commands = {}
def load_room_commands():
    global room_commands
    if os.path.exists(room_commands_file):
        with open(room_commands_file, "r", encoding="utf-8") as f:
            try:
                room_commands = json.load(f)
            except json.JSONDecodeError:
                room_commands = {}

def save_room_commands():
    with open(room_commands_file, "w", encoding="utf-8") as f:
        json.dump(room_commands, f, ensure_ascii=False, indent=2)


banned_users = {}  # لتخزين المستخدمين المحظورين
def save_banned_users():
    with open("banned_users.json", "w", encoding="utf-8") as f:
        json.dump(banned_users, f)
def load_banned_users():
    global banned_users
    try:
        with open("banned_users.json", "r", encoding="utf-8") as f:
            banned_users = json.load(f)
    except FileNotFoundError:
        banned_users = {}

# 👑 نظام المالكين (أعلى من الأدمنز)
owners = set()

def is_owner(username):
    return username.lower() in owners

def load_owners():
    global owners
    if os.path.exists("owners.json"):
        with open("owners.json", "r", encoding="utf-8") as f:
            try:
                data = json.load(f)

                if isinstance(data, list):
                    owners = set(o.lower().lstrip("@") for o in data)

                elif isinstance(data, dict):
                    # لو لقيت الملف {} أو أي شيء غلط
                    owners = {"q.xx"}

                else:
                    owners = {"q.xx"}

            except Exception:
                owners = {"q.xx"}
    else:
        owners = {"q.xx"}

    # التأكد من وجود المالك الأساسي
    owners.add("q.xx")
    save_owners()
    return owners


def save_owners():
    with open("owners.json", "w", encoding="utf-8") as f:
        json.dump(list(owners), f, ensure_ascii=False, indent=2)


vip_users = set()

def load_vip_users():
    global vip_users
    if os.path.exists("vip_users.json"):
        with open("vip_users.json", "r", encoding="utf-8") as f:
            try:
                vip_users.update(json.load(f))
            except json.JSONDecodeError:
                vip_users.clear()

def save_vip_users():
    with open("vip_users.json", "w", encoding="utf-8") as f:
        json.dump(list(vip_users), f, ensure_ascii=False)

# تحميل الترحيبات من الملف
special_welcomes = load_custom_welcomes()

# 🔧 تعريف دالة التحويل
def migrate_old_welcomes():
    updated = False
    for username, data in special_welcomes.items():
        if isinstance(data, str):
            special_welcomes[username] = {
                "welcome": data,
                "added_by": "q.xx"  # ← غيرها لو تحب
            }
            updated = True
    if updated:
        save_custom_welcomes()
        print("✅ تم تحويل الترحيبات القديمة.")

migrate_old_welcomes()

def split_message(text, max_length=200):
    lines = text.split('\n')
    chunks = []
    current = ""

    for line in lines:
        if len(current) + len(line) + 1 > max_length:
            chunks.append(current)
            current = line
        else:
            current += ("\n" if current else "") + line

    if current:
        chunks.append(current)

    return chunks






# 🎭 استيراد قائمة الرقصات من ملف خارجي
from emotes import emote_list






class MyBot(BaseBot):
    

    def save_teleports(self):
        try:
            with open(self.teleport_file, "w") as f:
                json.dump({
                    role: {
                        "x": pos.x,
                        "y": pos.y,
                        "z": pos.z,
                        "facing": pos.facing
                    } for role, pos in self.teleport_roles.items()
                }, f)
        except Exception as e:
            print("Error saving teleport positions:", e)

    def load_dance_zone(self, silent=False):
        """تحميل منطقة الرقص من الملف"""
        if os.path.exists(self.dance_zone_file):
            try:
                with open(self.dance_zone_file, "r") as f:
                    data = json.load(f)
                    if "start" in data and "end" in data:
                        self.dance_zone_start = data["start"]
                        self.dance_zone_end = data["end"]
                        if not silent:
                            print(f"✅ تم تحميل منطقة الرقص (مستطيل): {data}")
                    else:
                        from highrise.models import Position
                        self.dance_zone = Position(**data)
                        if not silent:
                            print(f"✅ تم تحميل منطقة الرقص (نقطة): {data}")
            except Exception as e:
                if not silent:
                    print(f"⚠️ خطأ في تحميل منطقة الرقص: {e}")

    def save_dance_zone(self, position):
        """حفظ منطقة الفلور بأكملها من موقع واحد"""
        try:
            # تحديد حدود الفلور تلقائياً حول الموقع الحالي (±4.5 وحدات) - فقط الفلور الملون بدون أي هوامش
            range_val = 3.0
            data = {
                "start": {
                    "x": float(position.x) - range_val,
                    "y": float(position.y),
                    "z": float(position.z) - range_val
                },
                "end": {
                    "x": float(position.x) + range_val,
                    "y": float(position.y),
                    "z": float(position.z) + range_val
                }
            }
            with open(self.dance_zone_file, "w") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.dance_zone_start = data["start"]
            self.dance_zone_end = data["end"]
            print(f"✅ منطقة الرقص محفوظة تلقائياً: X[{data['start']['x']:.1f}-{data['end']['x']:.1f}], Z[{data['start']['z']:.1f}-{data['end']['z']:.1f}]")
            return "saved"
        except Exception as e:
            print(f"❌ خطأ: {e}")

    def load_teleports(self):
        if not os.path.exists(self.teleport_file):
            return
        try:
            with open(self.teleport_file, "r") as f:
                data = json.load(f)
                from highrise.models import Position
                self.teleport_roles = {
                    role: Position(**pos) for role, pos in data.items()
                }
        except Exception as e:
            print("Error loading teleport positions:", e)



    
    
    def __init__(self):
       
        self.mod_users = set()  # Track all mod users (online/offline)
        self.designer_users = set()  # Track designer users

        # 📌 متغير اللغة الافتراضي
        # 👔 الملابس الثابتة الافتراضية
        self.FIXED_OUTFIT = [
            Item(type='clothing',
                 amount=1,
                 id='body-flesh',
                 account_bound=False,
                 active_palette=27),
            Item(type='clothing',
                 amount=1,
                 id='eyes-n_virgo2019virgoamythesteyes',
                 account_bound=False,
                 active_palette=7),
            Item(type='clothing',
                 amount=1,
                 id='eyebrow-n_06',
                 account_bound=False,
                 active_palette=0),
            Item(type='clothing',
                 amount=1,
                 id='nose-n_01',
                 account_bound=False,
                 active_palette=0),
            Item(type='clothing',
                 amount=1,
                 id='mouth-n_amethystdailyrewards2020chainmouth',
                 account_bound=False,
                 active_palette=-1),
            Item(type='clothing',
                 amount=1,
                 id='hair_front-n_malenew23',
                 account_bound=False,
                 active_palette=-1),
            Item(type='clothing',
                 amount=1,
                 id='shirt-m_suit_black',
                 account_bound=False,
                 active_palette=-1),
            Item(type='clothing',
                 amount=1,
                 id='pants-n_starteritems2019cuffedjeansblack',
                 account_bound=False,
                 active_palette=-1),
            Item(type='clothing',
                 amount=1,
                 id='shoes-n_room12019bootsblack',
                 account_bound=False,
                 active_palette=-1),
            Item(type='clothing',
                 amount=1,
                 id='bag-n_amethystdailyrewards2020amethystwings',
                 account_bound=False,
                 active_palette=-1),
            Item(type='clothing',
                 amount=1,
                 id='earrings-n_amethystdailyrewards2020amethystearrings',
                 account_bound=False,
                 active_palette=-1),
        ]

        # 📋 الترحيبات العربية
        self.welcomes_ar = [
            "خش يبن قلبي {user} 😍",
            "يخربيت جمالك دوبتني {user} 🤤❤️",
            "ابتعد 100 متر جميلنا وصل {user} 🙈🤚",
            "اللي جاب الحلاويات هنا {user} 🌚",
            "هتعمي من جمالك نورتنا {user} 🙆🔥",
            "المز دخل الروم ولعها {user} 🔥❤️",
            "اررحب دخل الصاروخ {user} 💋",
            "صلي على النبي {user} ❤️",
            
        ]

        # ⚙️ تحميل الإعدادات والبيانات
        self.load_settings()
        self.owner_username = "q.xx"  # ← غيرها لاسمك
        self.saved_position = None
        self.teleport_roles = {}
        self.teleport_file = "teleports.json"
        self.dance_zone_file = "dance_zone.json"
        self.dance_zone = None

        self.load_teleports()
        self.load_dance_zone()
        load_room_commands()
        load_banned_users()  # تحميل قائمة المحظورين عند بداية التشغيل
        self.autotip_task = None
        self.spam_task = None  # 📢 متغير لتتبع مهمة السبام
        self.is_spamming = False  # 📢 حالة السبام
        self.follow_task = None  # 📍 متغير لتتبع مهمة التتبع
        self.is_following = False  # 📍 حالة التتبع
        self.follow_target = None  # 📍 الشخص المستهدف للتتبع
        load_vip_users()
        self.position_tasks = {}
        self.haricler = set()
        self.is_teleporting_dict = {}  # لتتبع حالة التليبورت للمستخدمين
        self.saved_position = load_bot_position()
        self.last_ping_time = None  # ⏱️ لتتبع آخر اتصال
        self.dance_task = None  # 🎭 مهمة الرقص المستمرة
        self.room_owner = None  # 👑 مالك الروم
        
        # 🛡️ Rate limiting لحماية من الانقطاع في الغرف المزدحمة
        self.last_room_users_check = None
        self.room_users_cache = None
        self.room_users_cache_duration = 2.0  # ثانيتين cache
        
        # 👮 إدارة المشرفين
        self.admins = []
        self.filename = "admins.json"
        self.load_admins()
        
        # 💰 إعداد صلاحيات الأوتو تيب
        self.auto_tip_enabled = False
        self.file_path = "allowed_autotip_users.json"
        self.allowed_autotip_users = self.load_allowed_users()
       
        # 🎭 نظام حلقات الرقص التلقائي
        self.user_emote_loops = {}
        
        # 🌐 تهيئة WebAPI
        try:
            self.webapi = WebAPI()
            print("✅ WebAPI initialized successfully")
        except Exception as e:
            print(f"⚠️ WebAPI initialization failed: {e}")
            self.webapi = WebAPI()  # استخدام الكلاس البديل
        # 👑 تحميل المالكين
        global owners
        owners = load_owners()
        print(f"👑 Loaded owners: {owners}")


        # 🗂️ تحميل المشرفين من ملف
    def load_admins(self):
            if os.path.exists(self.filename):
                with open(self.filename, "r") as f:
                    try:
                        data = json.load(f)
                        if isinstance(data, list):
                            self.admins = data
                        else:
                            self.admins = []
                    except:
                        self.admins = []
            else:
                self.admins = []
            print(f"📂 Loaded admins: {self.admins}")  # Debug


    def save_admins(self):
            with open(self.filename, "w") as f:
                json.dump(self.admins, f, indent=4)
            print(f"💾 Saved admins: {self.admins} → {os.path.abspath(self.filename)}")  # Debug

    def load_user_cache(self):
            """📦 تحميل cache الـ usernames → user_ids"""
            cache_file = "user_cache.json"
            if os.path.exists(cache_file):
                try:
                    with open(cache_file, "r", encoding="utf-8") as f:
                        return json.load(f)
                except:
                    return {}
            return {}

    def save_to_user_cache(self, username, user_id):
            """💾 حفظ username و user_id في الـ cache"""
            cache_file = "user_cache.json"
            cache = self.load_user_cache()
            cache[username.lower()] = user_id
            try:
                with open(cache_file, "w", encoding="utf-8") as f:
                    json.dump(cache, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"⚠️ Error saving user cache: {e}")

    async def get_user_id_by_username(self, username: str) -> str | None:
            """🔍 جلب user_id من username باستخدام GraphQL API"""
            import requests
            
            graphql_url = "https://webapi.highrise.game/graphql"
            query = """
            query GetUserByUsername($username: String!) {
                userByUsername(username: $username) {
                    id
                    username
                }
            }
            """
            
            try:
                response = requests.post(
                    graphql_url,
                    json={
                        "query": query,
                        "variables": {"username": username}
                    },
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("data") and data["data"].get("userByUsername"):
                        user_data = data["data"]["userByUsername"]
                        user_id = user_data.get("id")
                        real_username = user_data.get("username", username)
                        if user_id:
                            self.save_to_user_cache(real_username, user_id)
                            print(f"✅ GraphQL: Found {real_username} → {user_id}")
                            return user_id
                    else:
                        print(f"⚠️ GraphQL: User '{username}' not found")
                else:
                    print(f"⚠️ GraphQL error: {response.status_code}")
            except Exception as e:
                print(f"⚠️ GraphQL request failed: {e}")
            
            return None

        # ⚙️ تحميل الإعدادات العامة
    def load_settings(self):
            try:
                path = os.path.join(os.getcwd(), "settings.json")

                if os.path.exists(path):
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    self.bot_auto_dance = data.get("bot_auto_dance", False)
                    print(f"📂 تم تحميل الإعدادات")
                    print(f"🎭 رقصة البوت التلقائية: {'مفعلة' if self.bot_auto_dance else 'معطلة'}")
                else:
                    self.bot_auto_dance = False
                    self.save_settings()
                    print("⚙️ تم إنشاء ملف إعدادات جديد")

            except Exception as e:
                print(f"⚠️ خطأ أثناء تحميل الإعدادات: {e}")
                self.bot_auto_dance = False


    def save_settings(self):
            try:
                data = {"bot_auto_dance": getattr(self, "bot_auto_dance", False)}
                with open("settings.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                print(f"💾 تم حفظ الإعدادات بنجاح")
            except Exception as e:
                print(f"⚠️ خطأ أثناء حفظ الإعدادات: {e}")


    def load_allowed_users(self):
            """💰 تحميل قائمة المستخدمين المسموح ليهم بالأوتو تيب"""
            file_path = getattr(self, 'file_path', 'allowed_autotip_users.json')
            if os.path.exists(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            return set(data)
                except Exception as e:
                    print(f"⚠️ خطأ في قراءة الملف: {e}")
            return {"q.xx"}


    def save_allowed_users(self):
            """💾 حفظ الصلاحيات في الملف"""
            try:
                file_path = getattr(self, 'file_path', 'allowed_autotip_users.json')
                allowed_users = getattr(self, 'allowed_autotip_users', {"q.xx"})
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(list(allowed_users), f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"⚠️ خطأ في حفظ الملف: {e}")

        
      
        
    def is_owner(self, user):
        return user.username.lower() in owners
    
    # ✅ دالة التحقق من صلاحيات المستخدم (تلقائي + دعم WebAPI)
    async def is_user_allowed(self, user: User):
        try:
            # 👑 أولًا: لو هو من المالكين
            if self.is_owner(user):
                return True
            
            # 👑 ثانياً: لو هو المالك المسجل للروم
            if hasattr(self, "room_owner") and self.room_owner:
                if user.username.lower() == self.room_owner.lower():
                    return True

            # 👮‍♂️ ثالثاً: لو هو من الأدمنز المخزنين
            if user.username.lower() in [a.lower() for a in getattr(self, "admins", [])]:
                return True

            # 🧰 رابعاً: تحقق مباشر من صلاحياته بالغرفة (مشرف أو كوهوست أو هوست)
            try:
                privilege = await self.highrise.get_room_privilege(user.id)
                if privilege and (
                    getattr(privilege, "moderator", False)
                    or getattr(privilege, "co_host", False)
                    or getattr(privilege, "host", False)
                ):
                    return True
            except Exception:
                pass

            return False

        except Exception as e:
            print(f"⚠️ خطأ أثناء التحقق من صلاحيات {user.username}: {e}")
            return False


    # 🧩 دالة: تحديث المشرفين تلقائيًا عند دخول البوت للروم
    async def update_room_admins(self):
        try:
            users_data_response = await self.highrise.get_room_users()
            users_data = users_data_response.content
            self.admins = []

            for user, _ in users_data:
                try:
                    privilege = await self.highrise.get_room_privilege(user.id)
                    if privilege and (
                        getattr(privilege, "moderator", False)
                        or getattr(privilege, "co_host", False)
                        or getattr(privilege, "host", False)
                    ):
                        self.admins.append(user.username)
                except Exception:
                    continue

            print(f"👑 تم اكتشاف {len(self.admins)} مشرف في الروم: {self.admins}")

            # 💬 إرسال إشعار داخل الروم
            if len(self.admins) > 0:
                admins_list = ", ".join([f"@{a}" for a in self.admins])
                 
            else:
                await self.highrise.chat("ℹ️ لا يوجد مشرفين في هذه الغرفة حالياً.")

        except Exception as e:
            print(f"⚠️ فشل في تحديث قائمة المشرفين: {e}")



    

   
    
    
    
    
   

    
    
    
    
    
    async def get_bot_gold(self):
        try:
            wallet = (await self.highrise.get_wallet()).content
            if wallet and len(wallet) > 0:
                return wallet[0].amount
            return 0
        except Exception as e:
            print(f"❌ خطأ في قراءة المحفظة: {e}")
            return 0

   
    async def auto_tip_loop(self):
        global auto_tip_enabled, auto_tip_amount, auto_tip_delay
        
        error_count = 0

        while auto_tip_enabled:
            try:
                # 💰 التحقق من الجولد المتبقي
                current_gold = await self.get_bot_gold()
                if current_gold < auto_tip_amount:
                    print(f"❌ انتهى الجولد! المتبقي: {current_gold}, المطلوب: {auto_tip_amount}")
                    auto_tip_enabled = False
                    await self.highrise.chat(f"⛔ تم إيقاف أوتو تيب - انتهى الجولد! (المتبقي: {current_gold})")
                    break
                
                # 👥 جلب جميع اللاعبين في الروم
                try:
                    room_users_response = await self.highrise.get_room_users()
                    room_users = room_users_response.content
                except Exception as room_err:
                    await asyncio.sleep(auto_tip_delay)
                    continue
                
                if not room_users:
                    await asyncio.sleep(auto_tip_delay)
                    continue
                
                # 🎲 اختيار لاعب عشوائي (ليس البوت نفسه)
                available_users = [(u, pos) for u, pos in room_users if u.id != self.my_user_id]
                
                if not available_users:
                    await asyncio.sleep(auto_tip_delay)
                    continue
                
                target_user, _ = random.choice(available_users)
                
                # 💰 إرسال الجولد
                try:
                    await self.highrise.tip_user(target_user.id, amount_to_gold_bar(auto_tip_amount))
                    print(f"💸 تم إرسال {auto_tip_amount} جولد إلى @{target_user.username}")
                    error_count = 0
                except Exception as tip_err:
                    error_msg = str(tip_err).lower()
                    if "insufficient" in error_msg or "not enough" in error_msg:
                        print(f"❌ جولد غير كافي، توقف auto_tip")
                        auto_tip_enabled = False
                        await self.highrise.chat(f"⛔ توقف أوتو تيب - جولد غير كافي!")
                        break
                    elif "cannot write to closing transport" in error_msg or "connection" in error_msg:
                        error_count += 1
                        if error_count > 3:
                            print("❌ الاتصال متقطع")
                            await asyncio.sleep(10)
                            error_count = 0
                        else:
                            await asyncio.sleep(5)
                    else:
                        await asyncio.sleep(auto_tip_delay)
                
            except asyncio.CancelledError:
                print("🛑 auto_tip_loop cancelled")
                break
            except Exception as e:
                pass

            await asyncio.sleep(auto_tip_delay)


    
    
    async def add_owner(self, name, requester):
        global owners
        clean = name.lower().lstrip("@")

        if clean in owners:
            await self.highrise.chat(f"ℹ️ @{clean} مسجل بالفعل كمالك.")
            return

        owners.add(clean)
        save_owners()   # ← لازم
        await self.highrise.chat(f"👑 تمت إضافة @{clean} إلى قائمة المالكين بواسطة @{requester.username}.")


    async def remove_owner(self, name, requester):
        global owners
        clean = name.lower().lstrip("@")

        if clean not in owners:
            await self.highrise.chat(f"ℹ️ @{clean} غير موجود في قائمة المالكين.")
            return

        owners.remove(clean)
        save_owners()   # ← لازم
        await self.highrise.chat(f"❌ تمت إزالة @{clean} من المالكين بواسطة @{requester.username}.")


    
       
    

    
    
    
    

    

    
    
    
    
    
    async def add_admin(self, username, user):
        if username not in self.admins:
            self.admins.append(username)
            self.save_admins()
            await self.highrise.chat(f"✅ تم إضافة {username} كأدمن")
        else:
            await self.highrise.chat(f"❌ {username} هو بالفعل أدمن")

    async def remove_admin(self, username, user):
        if username in self.admins:
            self.admins.remove(username)
            self.save_admins()
            await self.highrise.chat(f"❌ تم إزالة {username} من الأدمن")
        else:
            await self.highrise.chat(f"❌ {username} مش موجود كأدمن")
    


        
   
        

    
        

        

               
    
   
    

       


        
        
   

    async def switch_users(self, user, target_username):
        room_users_response = await self.highrise.get_room_users()
        room_users = room_users_response.content

        user_pos = None
        target_user = None
        target_pos = None

        for u, pos in room_users:
            if u.id == user.id:
                user_pos = pos
            elif u.username.lower() == target_username.lower():
                target_user = u
                target_pos = pos

        if not target_user or not user_pos or not target_pos:
            await self.highrise.send_whisper(user.id, "❌ لم يتم العثور على أحد المستخدمين أو مواقعهما.")
            return

        try:
            if isinstance(target_pos, Position):
                await self.highrise.teleport(user.id, target_pos)
            if isinstance(user_pos, Position):
                await self.highrise.teleport(target_user.id, user_pos)
            await self.highrise.send_whisper(user.id, f"🔄 تم تبديلك مع @{target_user.username}.")
            await self.highrise.send_whisper(target_user.id, f"🔄 تم تبديلك مع @{user.username}.")
        except Exception as e:
            await self.highrise.send_whisper(user.id, f"❌ فشل التبديل: {str(e)}")
            print(f"Switch users error: {e}")

    async def get_user_by_username(self, highrise, username: str):
        room_users_response = await highrise.get_room_users()
        for user_obj, _ in room_users_response.content:
            if user_obj.username.lower() == username.lower():
                return user_obj
        return None

    # دالة لمساعدة البوت في إرسال تفاعل معين لكل المستخدمين بالغرفة
    async def react_all(self, command: str, count: int):
        room_users_response = await self.highrise.get_room_users()
        for user_obj, _ in room_users_response.content:
            if user_obj.id == self.my_user_id:
                continue  # تجاهل البوت نفسه
            try:
                for _ in range(count):
                    await self.highrise.react(cast(Literal["clap", "heart", "thumbs", "wave", "wink"], command), user_obj.id)
                    await asyncio.sleep(0.1)
            except Exception as e:
                print(f"⚠️ فشل إرسال {command} إلى {user_obj.username}: {e}")


    async def reset_target_position(self, target_user, fixed_position):
        try:
            while True:
                try:
                    await self.highrise.teleport(target_user.id, fixed_position)
                except Exception as e:
                    print(f"Reset position error: {e}")
                await asyncio.sleep(1.2)  # ← كل ثانية يرجّعه مكانه
        except asyncio.CancelledError:
            pass

    async def get_room_users_cached(self):
        """🛡️ الحصول على مستخدمي الغرفة مع caching قوي"""
        import time
        current_time = time.time()
        
        if (self.room_users_cache is not None and 
            self.last_room_users_check is not None and 
            (current_time - self.last_room_users_check) < 2.0):  # cache لمدة ثانيتين فقط
            return self.room_users_cache
        
        try:
            room_users_response = await asyncio.wait_for(
                self.highrise.get_room_users(),
                timeout=8.0
            )
            self.room_users_cache = room_users_response
            self.last_room_users_check = current_time
            return room_users_response
        except asyncio.TimeoutError:
            print("⚠️ get_room_users timeout")
            if self.room_users_cache is not None:
                return self.room_users_cache
            raise
        except Exception as e:
            print(f"⚠️ get_room_users error: {str(e)[:40]}")
            if self.room_users_cache is not None:
                return self.room_users_cache
            raise
    
    async def teleport_to_user(self, requester: User, target_username: str):
        room_users_response = await self.get_room_users_cached()
        room_users = room_users_response.content
        target_user = next((u for u, _ in room_users if u.username.lower() == target_username), None)

        if not target_user:
            await self.highrise.send_whisper(requester.id, f"❌ @{target_username} مش موجود في الروم.")
            return

        target_pos = next((pos for u, pos in room_users if u.username.lower() == target_username and isinstance(pos, Position)), None)

        if not target_pos:
            await self.highrise.send_whisper(requester.id, "❌ لا يمكن تحديد موقع المستخدم (ربما واقف على أنكر أو كرسي).")
            return

        # تحويل إلى Position صريح
        pos = Position(
            x=target_pos.x,
            y=target_pos.y,
            z=target_pos.z,
            facing=target_pos.facing
        )

        try:
            await self.highrise.teleport(requester.id, pos)
            await self.highrise.send_whisper(requester.id, f"✅ تم نقلك إلى @{target_username}.")
        except Exception as e:
            await self.highrise.send_whisper(requester.id, f"❌ فشل النقل: {str(e)}")
            print(f"Teleport to user error: {e}")

   
    async def teleport_user_next_to(self, target_user_id: str, reference_user: User):
        room_users_response = await self.get_room_users_cached()
        room_users = room_users_response.content
        reference_pos = None

        for u, pos in room_users:
            if u.id == reference_user.id:
                reference_pos = pos
                break

        if not reference_pos:
            await self.highrise.send_whisper(reference_user.id, "❌ لم يتم العثور على موقعك.")
            return

        # تعديل الموقع لتفادي التراكب
        if isinstance(reference_pos, Position):
            new_pos = Position(
                x=reference_pos.x + 1,
                y=reference_pos.y,
                z=reference_pos.z,
                facing=reference_pos.facing
            )
        else:
            return

        new_pos_dict = Position(
            x=new_pos.x,
            y=new_pos.y,
            z=new_pos.z,
            facing=new_pos.facing
        )

        try:
            await self.highrise.teleport(target_user_id, new_pos)
        except Exception as e:
            print(f"Teleport user next to error: {e}")
    
    async def ad_loop(self):
        """📢 إرسال رسائل إعلان دورية"""
        MESSAGE = ["<#FF69B4>ارحبو حبايبي منورين روم ملتقي مصرين 🇪🇬 🦋"]
        
        try:
            while True:
                try:
                    await self.highrise.chat(f"{MESSAGE[0]}")
                except Exception as e:
                    pass
                
                await asyncio.sleep(180)
        except asyncio.CancelledError:
            print("🛑 تم إيقاف حلقة الإعلانات")

    async def check_dance_area(self):
        """📍 مراقبة منطقة الرقص - عندما يدخل شخص يرقص تلقائياً"""
        print("📍 نظام مراقبة منطقة الرقص نشط!")
        check_count = 0
        last_load = 0
        dance_zone_cache = None
        
        def is_dance_enabled():
            """تحقق من ملف الإعدادات - هل الرقص التلقائي مفعل؟"""
            try:
                if os.path.exists("dance_settings.json"):
                    with open("dance_settings.json", "r") as f:
                        settings = json.load(f)
                        return settings.get("dance_enabled", True)
            except Exception:
                pass
            return True
        
        try:
            while True:
                try:
                    # تحقق من الإعدادات
                    if not is_dance_enabled():
                        await asyncio.sleep(10)
                        continue
                    
                    check_count += 1
                    current_time = time.time()
                    
                    # تحميل الملف كل 30 ثانية فقط (تقليل ضخم للحمل)
                    if current_time - last_load > 30:
                        self.load_dance_zone(silent=True)
                        last_load = current_time
                    
                    if not (self.dance_zone or (hasattr(self, 'dance_zone_start') and self.dance_zone_start and hasattr(self, 'dance_zone_end') and self.dance_zone_end)):
                        await asyncio.sleep(10)
                        continue
                    
                    try:
                        room_users_response = await self.highrise.get_room_users()
                        if not hasattr(room_users_response, 'content'):
                            await asyncio.sleep(10)
                            continue
                        room_users = room_users_response.content
                    except Exception as api_err:
                        await asyncio.sleep(10)
                        continue
                    
                    for usr, pos in room_users:
                        if usr.id == self.my_user_id:
                            continue
                        
                        if pos and isinstance(pos, Position):
                            in_zone = False
                            
                            # التحقق من المنطقة المستطيلة (إذا كانت محفوظة)
                            if hasattr(self, 'dance_zone_start') and self.dance_zone_start and hasattr(self, 'dance_zone_end') and self.dance_zone_end:
                                x_min = min(self.dance_zone_start['x'], self.dance_zone_end['x'])
                                x_max = max(self.dance_zone_start['x'], self.dance_zone_end['x'])
                                z_min = min(self.dance_zone_start['z'], self.dance_zone_end['z'])
                                z_max = max(self.dance_zone_start['z'], self.dance_zone_end['z'])
                                
                                if x_min <= pos.x <= x_max and z_min <= pos.z <= z_max:
                                    in_zone = True
                                
                                if check_count % 30 == 0:
                                    print(f"🔍 @{usr.username}: pos=({pos.x:.1f},{pos.z:.1f}) bounds=X[{x_min:.1f}-{x_max:.1f}] Z[{z_min:.1f}-{z_max:.1f}] in_zone={in_zone}")
                            
                            # التحقق من نقطة واحدة (للعودة للخلف)
                            elif self.dance_zone:
                                dx = float(pos.x) - float(self.dance_zone.x)
                                dy = float(pos.y) - float(self.dance_zone.y)
                                dz = float(pos.z) - float(self.dance_zone.z)
                                distance = (dx**2 + dy**2 + dz**2) ** 0.5
                                if distance < 0.5:
                                    in_zone = True
                                
                                if check_count % 30 == 0:
                                    print(f"🔍 @{usr.username}: pos=({pos.x:.1f},{pos.y:.1f},{pos.z:.1f}) zone=({self.dance_zone.x:.1f},{self.dance_zone.y:.1f},{self.dance_zone.z:.1f}) distance={distance:.2f}")
                            
                            if in_zone:
                                if usr.id not in self.user_emote_loops:
                                    print(f"🎭 @{usr.username} دخل منطقة الرقص!")
                                    asyncio.create_task(self.start_random_emote_loop(usr.id))
                            else:
                                if usr.id in self.user_emote_loops:
                                    await self.stop_emote_loop(usr.id)
                
                except asyncio.CancelledError:
                    raise
                except Exception as e:
                    print(f"⚠️ خطأ في مراقب: {str(e)[:50]}")
                
                await asyncio.sleep(8)  # تقليل من 15 لأسرع استجابة
                    
        except asyncio.CancelledError:
            print("🛑 تم إيقاف مراقب منطقة الرقص")
        except Exception as e:
            await asyncio.sleep(2)
            pass

    async def start_random_emote_loop(self, user_id: str):
        """🎭 بدء حلقة رقصة عشوائية للمستخدم - استمرار بدون استسلام"""
        self.user_emote_loops[user_id] = "auto_dance"
        retry_count = 0
        failed_emotes = set()
        consecutive_errors = 0
        max_consecutive_errors = 5
        
        try:
            while self.user_emote_loops.get(user_id) == "auto_dance":
                try:
                    # اختار رقصة عشوائية
                    emote_name, emote_id, duration = random.choice(emote_list)
                    
                    # تخطي الرقصات التي فشلت
                    if emote_id in failed_emotes:
                        continue
                    
                    await self.highrise.send_emote(emote_id, user_id)
                    await asyncio.sleep(float(duration) + 0.2)
                    retry_count = 0
                    consecutive_errors = 0
                except Exception as e:
                    error_msg = str(e).lower()
                    if "not free" in error_msg or "not owned" in error_msg:
                        # تسجيل هذه الرقصة كمشكلة
                        if "emote_id" in locals():
                            failed_emotes.add(emote_id)
                            print(f"⚠️ تم تخطي الرقصة {emote_id} (غير مملوكة)")
                        await asyncio.sleep(0.5)
                        consecutive_errors = 0
                    elif "cannot write to closing transport" in error_msg or "connection" in error_msg or "closed" in error_msg:
                        retry_count += 1
                        consecutive_errors += 1
                        wait_time = min(5 + (retry_count * 3), 45)
                        print(f"⚠️ خطأ اتصال (المحاولة {retry_count}) - انتظار {wait_time}ثانية...")
                        await asyncio.sleep(wait_time)
                    else:
                        consecutive_errors += 1
                        if consecutive_errors >= max_consecutive_errors:
                            print(f"❌ توقفت حلقة المستخدم بعد {max_consecutive_errors} أخطاء")
                            break
                        print(f"⚠️ خطأ (محاولة {consecutive_errors}/{max_consecutive_errors}): {str(e)[:40]}")
                        await asyncio.sleep(0.5)
        except Exception as e:
            pass
        finally:
            if user_id in self.user_emote_loops:
                del self.user_emote_loops[user_id]

    async def stop_emote_loop(self, user_id: str):
        """⛔ إيقاف حلقة الرقص للمستخدم"""
        if user_id in self.user_emote_loops:
            del self.user_emote_loops[user_id]

    async def continuous_dance_loop(self):
        """حلقة مراقبة بسيطة - بدون رقص تلقائي"""
        try:
            while True:
                try:
                    # تحقق من أن البوت موجود في الروم
                    try:
                        room_users = await self.highrise.get_room_users()
                        bot_found = any(u.id == self.my_user_id for u, _ in room_users.content)
                        
                        if not bot_found:
                            print("❌ البوت محظور من الروم!")
                            await asyncio.sleep(5)
                        else:
                            await asyncio.sleep(15)  # مراقبة خفيفة كل 15 ثانية
                    except Exception as e:
                        await asyncio.sleep(5)
                    
                except asyncio.CancelledError:
                    print("🛑 توقفت حلقة المراقبة")
                    break
                        
        except Exception as e:
            print(f"❌ خطأ في حلقة المراقبة: {e}")

    async def on_start(self, session_metadata: SessionMetadata) -> None:
        self.my_user_id = session_metadata.user_id
        self.room_owner_id = session_metadata.room_info.owner_id if session_metadata.room_info else None
        
        print(f"🔍 SessionMetadata room_info: {session_metadata.room_info}")
        print(f"🔍 room_owner_id: {self.room_owner_id}")

        # نجيب اسم البوت من قائمة المستخدمين في الروم
        try:
            room_users_response = await self.highrise.get_room_users()
            for u, _ in room_users_response.content:
                if u.id == self.my_user_id:
                    self.bot_username = u.username.lower()
                    break
        except Exception as e:
            print(f"⚠️ خطأ في جلب اسم البوت: {e}")
            self.bot_username = "bot"

        # 👑 اكتشاف مالك الروم - محاولة متعددة (صامت)
        global owners
        room_owner_found = False
        
        try:
            room_users_response = await self.highrise.get_room_users()
            all_users = room_users_response.content
            
            # الطريقة 1: البحث عن صاحب الروم من room_owner_id (SessionMetadata)
            if self.room_owner_id:
                for u, _ in all_users:
                    if u.id == self.room_owner_id or str(u.id).lower() == str(self.room_owner_id).lower():
                        username_lower = u.username.lower()
                        if username_lower not in owners:
                            owners.add(username_lower)
                            save_owners()
                        room_owner_found = True
                        break
            
            # الطريقة 2: البحث عن صاحب الروم من get_room_privilege
            if not room_owner_found:
                for u, _ in all_users:
                    try:
                        privilege = await self.highrise.get_room_privilege(u.id)
                        if privilege and (getattr(privilege, 'host', False) or getattr(privilege, 'moderator', False)):
                            username_lower = u.username.lower()
                            if username_lower not in owners:
                                owners.add(username_lower)
                                save_owners()
                            self.room_owner_id = u.id
                            room_owner_found = True
                            break
                    except:
                        continue
            
            # الطريقة 3: اعتبار أول مستخدم غير البوت كمالك
            if not room_owner_found:
                for u, _ in all_users:
                    if u.id != self.my_user_id:
                        username_lower = u.username.lower()
                        owners.add(username_lower)
                        save_owners()
                        self.room_owner_id = u.id
                        room_owner_found = True
                        break
                
        except Exception as e:
            print(f"❌ خطأ في اكتشاف مالك الروم: {e}")
            import traceback
            traceback.print_exc()

        print(f"✅ تم الاتصال بالغرفة بنجاح. UserID: {self.my_user_id}")
        await self.highrise.chat("✅ البوت بدأ التشغيل!")
        
        # 🎭 حلقة المراقبة
        try:
            asyncio.create_task(self.continuous_dance_loop())
            print("🎭 Monitor loop started")
        except Exception as e:
            print(f"⚠️ Monitor error: {e}")
        
        # 📍 تشغيل نظام مراقبة منطقة الرقص
        try:
            asyncio.create_task(self.check_dance_area())
        except Exception as e:
            print(f"⚠️ خطأ في check_dance_area: {e}")
        
        # تشغيل auto_tip بشكل آمن
        try:
            asyncio.create_task(self.auto_tip_loop())
        except Exception as e:
            print(f"⚠️ خطأ في auto_tip_loop: {e}")
        
        # 📢 تشغيل حلقة الإعلانات
        try:
            asyncio.create_task(self.ad_loop())
        except Exception as e:
            print(f"⚠️ خطأ في ad_loop: {e}")




       



   

    

   

    
        

    





    








    

    


    


    


   

        




    


   


    async def on_user_join(self, user: User, position: Position | AnchorPosition):
        # 📦 حفظ username و user_id في الـ cache للاستخدام لاحقاً في -eq
        self.save_to_user_cache(user.username, user.id)
        
        # 👤 طباعة معلومات الصلاحيات عند دخول الاعب
        try:
            privileges = await self.highrise.get_room_privilege(user.id)
            print(f"👤 {user.username} joined the room with privileges: {privileges}")
        except Exception as e:
            print(f"⚠️ خطأ في جلب صلاحيات {user.username}: {e}")
        
        # 🔄 تحديث معرف مالك الروم إذا تغيرت الغرفة
        try:
            room_priv = await self.highrise.get_room_privilege(self.my_user_id)
            if room_priv and hasattr(room_priv, 'moderator'):
                print(f"👑 صلاحيات الروم: {room_priv}")
        except Exception:
            pass
        
        # 🔹 اختار رقصة عشوائية من القائمة
        emote_name, emote_id, duration = random.choice(emote_list)
        try:
            await self.highrise.send_emote(emote_id, user.id)
        except Exception as e:
            print(f"⚠️ فشل في تشغيل الرقصة {emote_name}: {e}")

        # 🔹 تحقق من الترحيب الخاص أولًا
        username = user.username.lower()
        if username in special_welcomes:
            welcome_template = special_welcomes[username]["welcome"]
            welcome = welcome_template.replace("{user}", user.username).replace("@{user}", f"@{user.username}")
        else:
            # 🔹 الترحيبات بالعربية
            welcomes_ar = [
                f"خش يبن قلبي @{user.username} 😍",
                f"يخربيت جمالك دوبتني @{user.username} 🤤❤️",
                f"ابتعد 100 متر جميلنا وصل @{user.username} 🙈🤚",
                f"اللي جاب الحلاويات هنا @{user.username} 🌚",
                f"هتعمي من جمالك نورتنا @{user.username} 🙆🔥",
                f"المز دخل الروم ولعها @{user.username} 🔥❤️",
                f"اررحب دخل الصاروخ @{user.username} 💋",
                f"صلي على النبي @{user.username} ❤️",
                f"أهلا وسهلا 👋 @{user.username}",
                f"تشرفت يا غالي 😊 @{user.username}",
                f"منور ياقمر 💕 @{user.username}",
                f"أهلا بأجمل إطلالة 🌟 @{user.username}",
                f"يا حلا 💫 @{user.username}",
                f"نورت الروم يا جميل 🌈 @{user.username}",
                f"مرحبا يا حبيبي ❤️ @{user.username}",
                f"سعدنا فيك يا رائع 🎉 @{user.username}",
                f"أهلا يا ملك 👑 @{user.username}",
                f"تشرفنا بحضورك يا غالي 🥰 @{user.username}",
                f"ياهلا وياأهلا 🎊 @{user.username}",
                f"رحبا يا جميل 😍 @{user.username}",
                f"أهلا يا جنتل 🎩 @{user.username}",
                f"منور يا قمر البيت 🌙 @{user.username}",
                f"تفضل يا حبيب القلب 💖 @{user.username}",
                f"أهلا وألف أهلا 🙌 @{user.username}",
                f"يا أجمل إطلالة اليوم ✨ @{user.username}",
                f"منور الروم يا ألماظ 💎 @{user.username}",
                f"سعدنا بك يا جميل 😊 @{user.username}",
                f"تفضل ياملك الروم 👸 @{user.username}",
                f"أهلا يا نجم ⭐ @{user.username}",
                f"يا حلا يا جميل 🌺 @{user.username}",
                f"منور يا زين 😎 @{user.username}",
                f"أهلا بأجمل عضو 🎯 @{user.username}",
                f"تشرفنا يا قمر 🌟 @{user.username}",
                f"يا مرحبا يا أهلا 🎪 @{user.username}",
                f"أهلا يا حبيب 💝 @{user.username}",
                f"منور ياغالي 🌸 @{user.username}",
                f"تفضل يا أجمل 👌 @{user.username}",
                f"سلام عليك يا جميل 🕊️ @{user.username}",
                f"أهلا يا زعيم 🦁 @{user.username}",
                f"منور يا ملاك 😇 @{user.username}",
                f"يا غالي أهلا وسهلا 🏰 @{user.username}",
            ]
            welcome = random.choice(welcomes_ar)

        # 🔹 إرسال رسالة الترحيب
        try:
            await self.highrise.chat(welcome)
            print(f"📢 ترحيب: {welcome}")
        except Exception as e:
            print(f"⚠️ خطأ في إرسال الترحيب: {e}")
        # ❤️ توزيع قلب تلقائي عند الدخول
        try:
            heart_count = 1  # ← عدد القلوب اللي يوزعها (غيره لو حبيت)
            for _ in range(heart_count):
                await self.highrise.react("heart", user.id)
                await asyncio.sleep(0.4)
            print(f"💖 تم إرسال {heart_count} قلوب إلى {user.username}")
        except Exception as e:
            print(f"⚠️ خطأ أثناء إرسال القلوب لـ {user.username}: {e}")





    async def loop_emote(self, user: User, emote_id: str, emote_name: str, duration: int):
        loop_count = 0
        connection_error_count = 0
        consecutive_errors = 0
        max_consecutive_errors = 5  # توقف بعد 5 أخطاء متتالية فقط
        
        try:
            try:
                await self.highrise.chat(f"🔁 @{user.username} is looping: {emote_name}")
            except Exception:
                pass
            
            while True:
                try:
                    try:
                        await self.highrise.send_emote(emote_id, user.id)
                        loop_count += 1
                        connection_error_count = 0
                        consecutive_errors = 0
                        print(f"🔁 Loop #{loop_count}: {emote_name} for @{user.username}")
                    except Exception as send_err:
                        error_str = str(send_err).lower()
                        if "closing transport" in error_str or "cannot write" in error_str or "connection" in error_str:
                            connection_error_count += 1
                            consecutive_errors += 1
                            wait_time = min(5 + (connection_error_count * 2), 30)
                            print(f"⚠️ خطأ اتصال ({connection_error_count}) - إعادة المحاولة خلال {wait_time}ثانية...")
                            await asyncio.sleep(wait_time)
                            continue
                        raise
                    
                    await asyncio.sleep(duration)
                    
                    # تحقق من وجود المستخدم لسه في الروم
                    try:
                        users_response = await self.highrise.get_room_users()
                        users = users_response.content
                        if not any(u.id == user.id for u, _ in users):
                            print(f"📍 @{user.username} left the room, stopping loop")
                            break
                    except:
                        pass
                        
                except asyncio.CancelledError:
                    print(f"🛑 Loop cancelled for @{user.username}")
                    break
                except Exception as e:
                    consecutive_errors += 1
                    print(f"⚠️ خطأ في loop_emote (محاولة {consecutive_errors}/{max_consecutive_errors}): {str(e)[:50]}")
                    
                    # حاول مجدداً بدلاً من التوقف
                    if consecutive_errors >= max_consecutive_errors:
                        print(f"❌ توقفت حلقة @{user.username} بعد {max_consecutive_errors} أخطاء")
                        break
                    
                    await asyncio.sleep(2)
                    consecutive_errors = 0  # إعادة تعيين عند نجاح جديد
        except asyncio.CancelledError:
            pass
        except Exception as e:
            pass
        finally:
            self.user_emote_loops.pop(user.id, None)

    async def spam_message(self, message: str, delay: float = 1.0):
        """دالة السبام المستمر - محسنة بإيقاف فوري صحيح"""
        spam_count = 0
        try:
            self.is_spamming = True
            
            while self.is_spamming:
                await self.highrise.chat(message)
                spam_count += 1
                await asyncio.sleep(delay)
                    
        except asyncio.CancelledError:
            print(f"🛑 تم إيقاف السبام بواسطة cancel - تم إرسال {spam_count} رسالة")
            raise
        except Exception as e:
            print(f"⚠️ خطأ في spam_message بعد {spam_count} رسالة: {e}")
        finally:
            self.is_spamming = False
            self.spam_task = None
            print(f"✅ انتهى السبام - تم إرسال {spam_count} رسالة إجمالاً")

    async def follow_user(self, target_username: str):
        """📍 متابعة مستخدم باستمرار"""
        try:
            self.is_following = True
            self.follow_target = target_username.lower()
            print(f"📍 بدء متابعة @{target_username}")
            
            while self.is_following:
                try:
                    room_users_response = await self.highrise.get_room_users()
                    room_users = room_users_response.content
                    target_user = None
                    target_position = None
                    
                    for u, pos in room_users:
                        if u.username.lower() == self.follow_target:
                            target_user = u
                            target_position = pos
                            break
                    
                    if target_user and target_position:
                        await self.highrise.walk_to(target_position)
                    else:
                        print(f"⚠️ لم يتم العثور على @{target_username} في الروم")
                        break
                    
                    await asyncio.sleep(0.5)  # تحديث كل نصف ثانية
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    print(f"⚠️ خطأ في متابعة المستخدم: {e}")
                    await asyncio.sleep(2)
        except Exception as e:
            print(f"❌ خطأ عام في follow_user: {e}")
        finally:
            self.is_following = False
            self.follow_target = None

    async def stop_loop(self, user: User):
        cancelled = False
        try:
            for task in list(self.highrise.tg._tasks):
                if task.get_name() == user.username:
                    task.cancel()
                    cancelled = True
                    await self.highrise.chat(f"🛑 تم إيقاف الحلقة @{user.username}")
                    return
        except Exception as e:
            print(f"⚠️ خطأ في إيقاف الحلقة: {e}")
        
        if not cancelled:
            # سكوت - لا نعرض رسالة إذا لم توجد حلقة نشطة
            print(f"📌 @{user.username} لا توجد حلقة نشطة")
    
    async def get_ping(self):
        """قياس سرعة الاستجابة"""
        try:
            start_time = time.time()
            await self.highrise.get_room_users()
            end_time = time.time()
            ping_ms = round((end_time - start_time) * 1000, 2)
            self.last_ping_time = datetime.now()
            return ping_ms
        except Exception as e:
            print(f"⚠️ خطأ في قياس البينج: {e}")
            return None
    
    async def get_uptime(self):
        """حساب مدة تشغيل البوت"""
        global bot_start_time
        uptime_delta = datetime.now() - bot_start_time
        days = uptime_delta.days
        hours, remainder = divmod(uptime_delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if days > 0:
            return f"{days} يوم، {hours} ساعة، {minutes} دقيقة"
        elif hours > 0:
            return f"{hours} ساعة، {minutes} دقيقة، {seconds} ثانية"
        elif minutes > 0:
            return f"{minutes} دقيقة، {seconds} ثانية"
        else:
            return f"{seconds} ثانية"
    
    async def get_user_info(self, username: str):
        """الحصول على معلومات المستخدم"""
        try:
            room_users_response = await self.highrise.get_room_users()
            room_users = room_users_response.content
            target_user = None
            target_position = None
            
            for u, pos in room_users:
                if u.username.lower() == username.lower():
                    target_user = u
                    target_position = pos
                    break
            
            if not target_user:
                return None
            
            info = {
                "username": target_user.username,
                "user_id": target_user.id,
                "position": f"X:{getattr(target_position, 'x', 0):.1f}, Y:{getattr(target_position, 'y', 0):.1f}, Z:{getattr(target_position, 'z', 0):.1f}" if target_position and hasattr(target_position, 'x') else "غير متاح"
            }
            
            try:
                privilege = await self.highrise.get_room_privilege(target_user.id)
                if privilege:
                    roles = []
                    if getattr(privilege, "host", False):
                        roles.append("Host")
                    if getattr(privilege, "co_host", False):
                        roles.append("Co-Host")
                    if getattr(privilege, "moderator", False):
                        roles.append("Moderator")
                    info["roles"] = ", ".join(roles) if roles else "User"
                else:
                    info["roles"] = "User"
            except Exception:
                info["roles"] = "User"
            
            return info
        except Exception as e:
            print(f"⚠️ خطأ في الحصول على معلومات المستخدم: {e}")
            return None
    
    
    async def on_join_room(self, room, user):
        try:
            self.current_room_id = room.id
            print(f"[✔] Room ID saved: {self.current_room_id}")
        except Exception as e:
            print("خطأ في on_join_room:", e)


    
    


    async def send_emote_list(self, user: User):
        lines = [f"{i+1}. {name} ({duration}s)" for i, (name, _, duration) in enumerate(emote_list)]
        chunk = ""
        for line in lines:
            if len(chunk) + len(line) + 1 < 250:
                chunk += line + "\n"
            else:
                await self.highrise.chat(chunk)
                chunk = line + "\n"
        if chunk:
            await self.highrise.chat(chunk)

    async def loop_all_users(self, message: str):
        parts = message.strip().split()
        if len(parts) < 2:
            await self.highrise.chat("❌ استخدم: /loopall <رقم أو اسم الرقصة>")
            return

        emote_input = parts[1]
        emote_id = None
        emote_name = None
        duration = None

        if emote_input.isdigit():
            index = int(emote_input) - 1
            if 0 <= index < len(emote_list):
                emote_name, emote_id, duration = emote_list[index]
        else:
            for name, eid, dur in emote_list:
                if name.lower() == emote_input.lower():
                    emote_name, emote_id, duration = name, eid, dur
                    break

        if not emote_id:
            await self.highrise.chat("❌ رقصة غير موجودة.")
            return

        users_response = await self.highrise.get_room_users()
        users = users_response.content if hasattr(users_response, 'content') else []
        for u, _ in users:
            await self.stop_loop(u)
            task = self.highrise.tg.create_task(self.loop_emote(u, emote_id, emote_name or "", int(duration) if duration else 0))
            task.set_name(u.username)

    async def on_chat(self, user: User, message: str) -> None:
        global auto_tip_enabled, auto_tip_amount, auto_tip_delay


        if message.startswith("-eq "):
            target = message.split(" ", 1)[1].strip()

            # إزالة @ لو مكتوبة
            if target.startswith("@"):
                target = target[1:]

            try:
                outfit = None
                found_username = target
                
                # 1️⃣ أولاً: البحث في الروم الحالية
                room_users = await self.highrise.get_room_users()
                users_list = room_users.content if hasattr(room_users, 'content') else room_users
                
                target_user = None
                for u, _ in users_list:
                    if u.username.lower() == target.lower():
                        target_user = u
                        found_username = u.username
                        break
                
                if target_user:
                    # المستخدم موجود في الروم - جلب الـ outfit مباشرة
                    outfit_response = await self.highrise.get_user_outfit(target_user.id)
                    outfit = outfit_response
                else:
                    # 2️⃣ محاولة الجلب من WebAPI باستخدام الـ cache
                    user_cache = self.load_user_cache()
                    
                    if target.lower() in user_cache:
                        user_id = user_cache[target.lower()]
                        try:
                            user_response = await self.webapi.get_user(user_id)
                            if hasattr(user_response, 'user') and user_response.user:
                                outfit = user_response.user.outfit
                                found_username = user_response.user.username
                        except Exception as e:
                            print(f"⚠️ Cache lookup failed: {e}")
                    
                    # 3️⃣ إذا لم يوجد في الـ cache، نستخدم GraphQL API
                    if not outfit:
                        try:
                            user_id = await self.get_user_id_by_username(target)
                            if user_id:
                                user_response = await self.webapi.get_user(user_id)
                                if hasattr(user_response, 'user') and user_response.user:
                                    outfit = user_response.user.outfit
                                    found_username = user_response.user.username
                        except Exception as e:
                            print(f"⚠️ GraphQL/WebAPI failed: {e}")
                
                if outfit:
                    await self.highrise.set_outfit(outfit)
                    await self.highrise.chat(f"✅ Outfit copied from @{found_username}!")
                else:
                    await self.highrise.chat(f"❌ User @{target} not found. Try when they're in the room first.")

            except Exception as e:
                print(f"❌ Error fetching outfit: {e}")
                await self.highrise.chat("❌ Failed to fetch outfit.")


        
        # 🔄 معالجة أوامر من الواجهة البرمجية
        cmd_obj = await get_next_command()
        if cmd_obj:
            cmd_type = cmd_obj.get("type")
            if cmd_type == "outfit_copy":
                message = "c"
            elif cmd_type == "outfit_equip":
                message = f"equip @{cmd_obj.get('username', '')}"
            elif cmd_type == "outfit_quick":
                message = cmd_obj.get('preset', 'q1')
            elif cmd_type == "outfit_save":
                message = "q-save"
            elif cmd_type == "outfit_load":
                message = "q-load"
            elif cmd_type == "outfit_save_named":
                # حفظ لبسة باسم من الواجهة
                name = cmd_obj.get('name', 'outfit')
                items = cmd_obj.get('items', [])
                if items:
                    try:
                        data = load_all_outfits()
                        data[name.lower()] = items
                        save_all_outfits(data)
                        await self.highrise.chat(f"💾 تم حفظ لبسة '{name}' بنجاح!")
                        return
                    except Exception as e:
                        await self.highrise.chat(f"❌ خطأ في الحفظ: {e}")
                        return
            elif cmd_type == "outfit_load_named":
                # تحميل لبسة محفوظة من الواجهة
                name = cmd_obj.get('name', '')
                if name:
                    try:
                        data = load_all_outfits()
                        if name.lower() in data:
                            items_data = data[name.lower()]
                            outfit_items = []
                            for item_data in items_data:
                                outfit_items.append(Item(
                                    id=item_data.get('id', ''),
                                    type=item_data.get('type', 'clothing'),
                                    amount=item_data.get('amount', 1)
                                ))
                            if outfit_items:
                                await self.highrise.set_outfit(outfit=outfit_items)
                                await self.highrise.chat(f"⚡ تم تطبيق لبسة '{name}'!")
                                return
                        await self.highrise.chat(f"❌ لبسة '{name}' غير موجودة!")
                        return
                    except Exception as e:
                        await self.highrise.chat(f"❌ خطأ: {e}")
                        return
            elif cmd_type == "outfit_custom":
                # تطبيق لبسة مخصصة
                items = cmd_obj.get('items', [])
                if items:
                    try:
                        await self.highrise.set_outfit(outfit=items)
                        await self.highrise.chat(f"🎭 تم تطبيق اللبسة المخصصة ({len(items)} عناصر)")
                        return
                    except Exception as e:
                        await self.highrise.chat(f"❌ خطأ: {e}")
                        return
            elif cmd_type == "direct_command":
                # أمر مباشر من الواجهة
                message = cmd_obj.get('command', '')
            elif cmd_type == "dance_start":
                message = f"dance {cmd_obj.get('dance', 'random')}"
            elif cmd_type == "dance_stop":
                message = "stop"

        msg = message.lower().strip()
        parts = msg.split()
        clean_message = msg
        cmd = parts[0] if parts else ""

        if message.lower().startswith("مرجح") and await self.is_user_allowed(user):
            target_username = message.split("@")[-1].strip().lower()

            if target_username not in self.haricler:
                room_users = (await self.highrise.get_room_users()).content
                target_user = next((u for u, _ in room_users if u.username.lower() == target_username), None)

                if target_user:
                    if target_user.id not in self.is_teleporting_dict:
                        self.is_teleporting_dict[target_user.id] = True

                        try:
                            while self.is_teleporting_dict.get(target_user.id, False):
                                kl = Position(random.randint(0, 39), random.randint(0, 29), random.randint(0, 39))
                                await self.highrise.teleport(target_user.id, kl)
                                await asyncio.sleep(1)
                        except Exception as e:
                            print(f"An error occurred while teleporting: {e}")

                        self.is_teleporting_dict.pop(target_user.id, None)
                        final_position = Position(1.0, 15, 14, "FrontRight")
                        await self.highrise.teleport(target_user.id, final_position)


        if message.lower().startswith("وقف") and await self.is_user_allowed(user):
            target_username = message.split("@")[-1].strip().lower()

            room_users = (await self.highrise.get_room_users()).content
            target_user = next((u for u, _ in room_users if u.username.lower() == target_username), None)

            if target_user:
                self.is_teleporting_dict.pop(target_user.id, None)

        # 👊 أمر كف - متاح للجميع
        if msg.startswith("كف"):
            parts = message.split()
            if len(parts) < 2:
                return
            if "@" not in parts[1]:
                username = parts[1]
            else:
                username = parts[1][1:]

            room_users = (await self.highrise.get_room_users()).content
            target_user_id = None
            for room_user, pos in room_users:
                if room_user.username.lower() == username.lower():
                    target_user_id = room_user.id
                    break

            if not target_user_id:
                return

            try:
                await self.highrise.send_emote("emote-judochop", user.id)
                await self.highrise.send_emote("emote-fail2", target_user_id)
                await self.highrise.chat(f"💥 @{user.username} كف @{username}!")
            except Exception as e:
                print(f"Error in punch command: {e}")
            return

        # 👮 أمر إضافة مود - add @username mod
        if message.lower().startswith("add") and message.lower().endswith("mod"):
            # Only owner can add mods
            if user.username not in ["q.xx", "T_I_T____O"]:
                await self.highrise.chat("❌ Only owner can add MODs!")
                return
            parts = message.split()
            if len(parts) < 3 or not parts[1].startswith("@"):
                await self.highrise.chat("Usage: add @username mod")
                return
            target_username = parts[1][1:].lower()
            
            try:
                room_users = (await self.highrise.get_room_users()).content
                target_user_id = None
                for room_user, pos in room_users:
                    if room_user.username.lower() == target_username:
                        target_user_id = room_user.id
                        break
                
                if not target_user_id:
                    await self.highrise.chat(f"❌ @{target_username} not found in room!")
                    return
                
                try:
                    # Try new method first
                    try:
                        await self.highrise.set_room_privilege(target_user_id, "moderator")
                    except AttributeError:
                        # Fallback to old method
                        new_priv = RoomPermissions(moderator=True)
                        await self.highrise.change_room_privilege(target_user_id, new_priv)
                    self.mod_users.add(target_username)
                    await self.highrise.chat(f"✅ @{target_username} is now a ROOM MODERATOR!")
                except Exception as e:
                    error_msg = str(e).lower()
                    if "cannot modify" in error_msg or "permission" in error_msg or "privilege" in error_msg:
                        await self.highrise.chat(f"⚠️ البوت مش مالك الروم! لازم تدي الصلاحية يدوي من التطبيق")
                        self.mod_users.add(target_username)
                        await self.highrise.chat(f"📝 تم تسجيل @{target_username} كمود في قائمة البوت")
                    else:
                        await self.highrise.chat(f"❌ Error adding mod: {str(e)}")
                    
            except Exception as e:
                await self.highrise.chat(f"❌ Error: {str(e)}")
            return

        # 👮 أمر إزالة مود - rem @username mod
        if message.lower().startswith("rem") and message.lower().endswith("mod"):
            # Only owner can remove mods
            if user.username not in ["q.xx", "T_I_T____O"]:
                await self.highrise.chat("❌ Only owner can remove MODs!")
                return
            parts = message.split()
            if len(parts) < 3 or not parts[1].startswith("@"):
                await self.highrise.chat("Usage: rem @username mod")
                return
            target_username = parts[1][1:].lower()
            
            try:
                room_users = (await self.highrise.get_room_users()).content
                target_user_id = None
                for room_user, pos in room_users:
                    if room_user.username.lower() == target_username:
                        target_user_id = room_user.id
                        break
                
                if not target_user_id:
                    await self.highrise.chat(f"❌ @{target_username} not found in room!")
                    return
                
                try:
                    # Try new method first
                    try:
                        await self.highrise.set_room_privilege(target_user_id, "none")
                    except AttributeError:
                        # Fallback to old method
                        new_priv = RoomPermissions(moderator=False)
                        await self.highrise.change_room_privilege(target_user_id, new_priv)
                    if target_username in self.mod_users:
                        self.mod_users.remove(target_username)
                    await self.highrise.chat(f"✅ @{target_username} has been removed from MOD!")
                except Exception as e:
                    error_msg = str(e).lower()
                    if "cannot modify" in error_msg or "permission" in error_msg or "privilege" in error_msg:
                        await self.highrise.chat(f"⚠️ البوت مش مالك الروم! لازم تشيل الصلاحية يدوي من التطبيق")
                        if target_username in self.mod_users:
                            self.mod_users.remove(target_username)
                        await self.highrise.chat(f"📝 تم شطب @{target_username} من قائمة المودز")
                    else:
                        await self.highrise.chat(f"❌ Error removing mod: {str(e)}")
            except Exception as e:
                await self.highrise.chat(f"❌ Error: {e}")
            return

        # 🎨 أمر إضافة مصمم - add @username des
        if message.lower().startswith("add") and message.lower().endswith("des"):
            is_owner = self.is_owner(user)
            is_mod = False
            
            if not is_owner:
                try:
                    user_privileges = await self.highrise.get_room_privilege(user.id)
                    if hasattr(user_privileges, 'moderator'):
                        is_mod = user_privileges.moderator
                except:
                    is_mod = False
            
            if is_owner or is_mod:
                parts = message.split()
                if len(parts) < 3 or not parts[1].startswith("@"):
                    await self.highrise.chat("Usage: add @username des")
                    return
                target_username = parts[1][1:].lower()
                
                try:
                    room_users = (await self.highrise.get_room_users()).content
                    target_user_id = None
                    for room_user, pos in room_users:
                        if room_user.username.lower() == target_username:
                            target_user_id = room_user.id
                            break
                    
                    if not target_user_id:
                        await self.highrise.chat(f"❌ @{target_username} not found in room!")
                        return
                    
                    # Try new method first
                    try:
                        await self.highrise.set_room_privilege(target_user_id, "designer")
                    except AttributeError:
                        # Fallback to old method
                        await self.highrise.change_room_privilege(target_user_id, RoomPermissions(designer=True))
                    self.designer_users.add(target_username)
                    await self.highrise.chat(f"✅ @{target_username} has been added to DESIGNER!")
                except Exception as e:
                    error_msg = str(e).lower()
                    if "cannot modify" in error_msg or "permission" in error_msg or "privilege" in error_msg:
                        await self.highrise.chat(f"⚠️ البوت مش مالك الروم! لازم تدي الصلاحية يدوي من التطبيق")
                        self.designer_users.add(target_username)
                        await self.highrise.chat(f"📝 تم تسجيل @{target_username} كمصمم في قائمة البوت")
                    else:
                        await self.highrise.chat(f"❌ Error: {str(e)}")
            else:
                await self.highrise.chat("❌ Only MOD/OWNER can add DESIGNER!")
            return

        # 🎨 أمر إزالة مصمم - rem @username des
        if message.lower().startswith("rem") and message.lower().endswith("des"):
            is_owner = self.is_owner(user)
            is_mod = False
            
            if not is_owner:
                try:
                    user_privileges = await self.highrise.get_room_privilege(user.id)
                    if hasattr(user_privileges, 'moderator'):
                        is_mod = user_privileges.moderator
                except:
                    is_mod = False
            
            if is_owner or is_mod:
                parts = message.split()
                if len(parts) < 3 or not parts[1].startswith("@"):
                    await self.highrise.chat("Usage: rem @username des")
                    return
                target_username = parts[1][1:].lower()
                
                try:
                    room_users = (await self.highrise.get_room_users()).content
                    target_user_id = None
                    for room_user, pos in room_users:
                        if room_user.username.lower() == target_username:
                            target_user_id = room_user.id
                            break
                    
                    if not target_user_id:
                        await self.highrise.chat(f"❌ @{target_username} not found in room!")
                        return
                    
                    # Try new method first
                    try:
                        await self.highrise.set_room_privilege(target_user_id, "none")
                    except AttributeError:
                        # Fallback to old method
                        await self.highrise.change_room_privilege(target_user_id, RoomPermissions(designer=False))
                    if target_username in self.designer_users:
                        self.designer_users.remove(target_username)
                    await self.highrise.chat(f"✅ @{target_username} has been removed from DESIGNER!")
                except Exception as e:
                    error_msg = str(e).lower()
                    if "cannot modify" in error_msg or "permission" in error_msg or "privilege" in error_msg:
                        await self.highrise.chat(f"⚠️ البوت مش مالك الروم! لازم تشيل الصلاحية يدوي من التطبيق")
                        if target_username in self.designer_users:
                            self.designer_users.remove(target_username)
                        await self.highrise.chat(f"📝 تم شطب @{target_username} من قائمة المصممين")
                    else:
                        await self.highrise.chat(f"❌ Error: {str(e)}")
            else:
                await self.highrise.chat("❌ Only MOD/OWNER can remove DESIGNER!")
            return

        # 📋 أمر عرض قائمة المودز - /modlist
        if message.lower() == "/modlist":
            is_owner = self.is_owner(user)
            is_mod = False
            
            if not is_owner:
                try:
                    user_privileges = await self.highrise.get_room_privilege(user.id)
                    if hasattr(user_privileges, 'moderator'):
                        is_mod = user_privileges.moderator
                except:
                    is_mod = False
            
            if is_owner or is_mod:
                if self.mod_users:
                    mods_display = ", ".join([f"@{mod}" for mod in sorted(self.mod_users)])
                    await self.highrise.chat(f"🛡️ MOD Members: {mods_display}")
                else:
                    await self.highrise.chat("🛡️ No MOD members yet!")
            else:
                await self.highrise.chat("❌ Only MOD/OWNER can view MOD list!")
            return

        # 📋 أمر عرض المودز في الروم - /roommods أو admin أو ادمن
        if message.lower() in ["/roommods", "admin", "ادمن"]:
            try:
                room_users = (await self.highrise.get_room_users()).content
                room_mods = []
                
                for room_user, pos in room_users:
                    try:
                        user_priv = await self.highrise.get_room_privilege(room_user.id)
                        if hasattr(user_priv, 'moderator') and user_priv.moderator:
                            room_mods.append(room_user.username)
                    except:
                        pass
                
                if room_mods:
                    mods_display = ", ".join([f"@{mod}" for mod in sorted(room_mods)])
                    await self.highrise.chat(f"🛡️ MODs in Room: {mods_display}")
                else:
                    await self.highrise.chat("🛡️ No MOD members in room!")
            except Exception as e:
                await self.highrise.chat(f"❌ Error: {str(e)}")
            return

        # 📍 أمر حفظ منطقة الرقص - نقطتان لتحديد منطقة مستطيلة
        if msg in ["set_dance_zone", "حفظ_منطقة", "save_dance_zone"]:
            if not await self.is_user_allowed(user):
                await self.highrise.chat(f"❌ عذراً @{user.username}، أنت لا تملك صلاحيات!")
                return
            
            try:
                # جلب موقع المستخدم الحالي من الروم
                room_users = await self.highrise.get_room_users()
                user_position = None
                
                for u, pos in room_users.content:
                    if u.id == user.id:
                        user_position = pos
                        break
                
                if not user_position:
                    await self.highrise.chat("❌ فشل في جلب موقعك!")
                    return
                
                # حفظ منطقة الفلور من موقع واحد فقط
                result = self.save_dance_zone(user_position)
                await self.highrise.chat(f"✅ تم حفظ منطقة الرقص! 🎭 أي شخص يدخل الفلور سيرقص تلقائياً!")
            except Exception as e:
                print(f"❌ خطأ في حفظ منطقة الرقص: {e}")
                await self.highrise.chat(f"❌ خطأ: {str(e)[:50]}")
            return

        # 💰 أمر محفظة - عرض جولد البوت
        if msg in ["محفظة", "wallet", "", ""]:
            bot_gold = await self.get_bot_gold()
            await self.highrise.chat(f"💰 محفظة البوت: {bot_gold} جولد 💎")
            return
        
        # 💃 أوامر التحكم بالرقص التلقائي
        if msg in ["dance enable", "رقص تفعيل", "تفعيل رقص"]:
            if not await self.is_user_allowed(user):
                await self.highrise.chat("❌ لا صلاحيات!")
                return
            try:
                with open("dance_settings.json", "r") as f:
                    settings = json.load(f)
                settings["dance_enabled"] = True
                with open("dance_settings.json", "w") as f:
                    json.dump(settings, f, ensure_ascii=False, indent=2)
                await self.highrise.chat("✅ تم تفعيل الرقص التلقائي في منطقة الرقص! 🎭")
            except Exception as e:
                await self.highrise.chat(f"❌ خطأ: {e}")
            return
        
        if msg in ["dance disable", "رقص تعطيل", "تعطيل رقص"]:
            if not await self.is_user_allowed(user):
                await self.highrise.chat("❌ لا صلاحيات!")
                return
            try:
                with open("dance_settings.json", "r") as f:
                    settings = json.load(f)
                settings["dance_enabled"] = False
                with open("dance_settings.json", "w") as f:
                    json.dump(settings, f, ensure_ascii=False, indent=2)
                await self.highrise.chat("🛑 تم تعطيل الرقص التلقائي. الأشخاص لن يرقصوا تلقائياً.")
            except Exception as e:
                await self.highrise.chat(f"❌ خطأ: {e}")
            return
        
        # 🗑️ أمر حذف منطقة الرقص
        if msg in ["delete_dance_zone", "حذف_منطقة", "remove_dance_zone", "الغي_منطقة"]:
            if not await self.is_user_allowed(user):
                await self.highrise.chat("❌ لا صلاحيات!")
                return
            try:
                # إيقاف جميع الرقص الجاري أولاً
                users_to_stop = list(self.user_emote_loops.keys())
                for usr_id in users_to_stop:
                    await self.stop_emote_loop(usr_id)
                
                # حذف ملف منطقة الرقص
                if os.path.exists(self.dance_zone_file):
                    os.remove(self.dance_zone_file)
                    self.dance_zone = None
                    self.dance_zone_start = None
                    self.dance_zone_end = None
                    await self.highrise.chat("🗑️ تم حذف منطقة الرقص! تم إيقاف جميع الرقص الجاري. ✅")
                else:
                    await self.highrise.chat("⚠️ لا توجد منطقة رقص محفوظة.")
            except Exception as e:
                await self.highrise.chat(f"❌ خطأ في حذف المنطقة: {str(e)[:50]}")
            return

        # 🔄 أمر changeoutfit - تغيير ملابس البوت بـ @username أو item ID
        if message.lower().startswith("fit"):
            if not await self.is_user_allowed(user):
                await self.highrise.chat(f"❌ عذراً @{user.username}، ليس لديك صلاحية تغيير الملابس")
                return
            
            try:
                # استخرج المعامل من الأمر
                parts = message.split()
                target_param = None
                
                if len(parts) > 1:
                    target_param = parts[1].lstrip("@").lower()
                
                # 🔍 تحقق: هل هو @username أم item ID؟
                if target_param:
                    # إذا كان يبدأ بـ @ أو كان بدون شرطة، حاول أنه شخص
                    if "@" in message.split()[1] or "-" not in target_param:
                        # 👤 معالجة اسم شخص
                        try:
                            if not hasattr(self, 'webapi') or not self.webapi:
                                await self.highrise.chat("❌ خدمة WebAPI غير متاحة")
                                return
                            
                            await self.highrise.chat(f"🌐 جاري جلب ملابس @{target_param} من خارج الروم... ⏳")
                            user_info = await self.webapi.get_users(username=target_param, limit=1)
                            if not user_info or not hasattr(user_info, 'users') or not user_info.users:
                                await self.highrise.chat(f"❌ المستخدم @{target_param} غير موجود!")
                                return
                            
                            target_user_id = user_info.users[0].user_id
                            target_outfit = await self.highrise.get_user_outfit(target_user_id)
                            if not target_outfit or not target_outfit.outfit:
                                await self.highrise.chat(f"⚠️ لا توجد ملابس محفوظة للمستخدم @{target_param}")
                                return
                            
                            await self.highrise.set_outfit(outfit=target_outfit.outfit)
                            await self.highrise.chat(f"🌐 البوت لبس ملابس @{target_param}! 🎭 ✨")
                            return
                        
                        except Exception as e:
                            error_msg = str(e).lower()
                            if "404" in error_msg or "not found" in error_msg:
                                await self.highrise.chat(f"⚠️ ملابس @{target_param} غير متاحة")
                            else:
                                await self.highrise.chat(f"❌ خطأ: {str(e)[:60]}")
                            return
                    else:
                        # 👕 معالجة item ID (يحتوي على شرطة)
                        try:
                            current_outfit = await self.highrise.get_user_outfit(self.my_user_id)
                            outfit_items = []
                            if current_outfit and current_outfit.outfit:
                                outfit_items = list(current_outfit.outfit)
                            
                            new_item = Item(id=target_param, type='clothing', amount=1)
                            outfit_items.append(new_item)
                            
                            await self.highrise.set_outfit(outfit=outfit_items)
                            await self.highrise.chat(f"✅ تم لبس: {target_param} 🎭")
                            return
                        except Exception as e:
                            await self.highrise.chat(f"❌ خطأ في تطبيق item: {str(e)[:50]}")
                            return
                
                # بدون معامل - استخدم الملابس الثابتة
                await self.highrise.set_outfit(outfit=self.FIXED_OUTFIT)
                await self.highrise.chat("✅ تم تغيير الملابس للزي الافتراضي! 🎭")
                
            except Exception as e:
                await self.highrise.chat(f"❌ خطأ: {str(e)[:80]}")
            return

        
        
        if re.search(r"\bم+ح+\b", clean_message):
            await self.highrise.send_emote("emote-kissing", user.id)
            return

        if re.search(r"\bت+ي+\b", clean_message):
            await self.highrise.send_emote("emote-curtsy", user.id)
            return

        if re.search(r"\bت+و+\b", clean_message):
            await self.highrise.send_emote("emote-curtsy", user.id)
            return

        if re.search(r"\bه+\b", clean_message):
            await self.highrise.send_emote("emote-laughing", user.id)
            return

        if re.search(r"\b(و+ل+ك+م+|و+ب+)\b", clean_message):
            await self.highrise.send_emote("emote-bow", user.id)
            return

        if re.search(r"\bشكرا\b", clean_message):
            await self.highrise.send_emote("emote-kiss", user.id)
            return

        
        
        if msg.lower() in ["emotes", "/emotes", "الرقصات"]:
            emote_names = [name for name, _, _ in emote_list]
            chunk_size = 10  # عدد الرقصات في كل رسالة

            await self.highrise.chat("🕺 قائمة الرقصات المتاحة:")

            for i in range(0, len(emote_names), chunk_size):
                chunk = emote_names[i:i+chunk_size]
                text = "\n".join(f"{i+j+1}. {name}" for j, name in enumerate(chunk))
                await self.highrise.chat(text)
                await asyncio.sleep(0.5)  # عشان ما يعملش سبام للـ API
            return


        # 🛑 أمر توقف - لأي شخص (إيقاف رقصتك الخاصة)
        if msg.lower() in ["توقف", "stop"] or (msg.startswith(("توقف", "stop")) and len(msg) == len(msg.split()[0])):
            await self.stop_loop(user)
            await self.highrise.chat(f"⛔ تم إيقاف رقصتك @{user.username}.")
            return

        # جلب المستخدمين - فقط للأوامر الإدارية
        users = []
        if cmd == "loopall":
            try:
                users_response = await self.highrise.get_room_users()
                users = users_response.content
            except Exception as e:
                print(f"⚠️ خطأ جلب المستخدمين: {e}")
                users = []

        # ------------------ 🛑 أوامر الأدمن فقط ------------------
        if cmd == "loopall":
            if not await self.is_user_allowed(user):
                await self.highrise.chat("🚫 هذا الأمر مخصص للأدمن فقط.")
                return

            # أمر /loopall
            if cmd == "loopall":
                if len(parts) < 2:
                    await self.highrise.chat(
                        "🕺 استخدم:\n"
                        "/loopall <رقم أو اسم الرقصة>\n"
                        "/loopall stop → إيقاف الجميع"
                    )
                    return

                if parts[1].lower() == "stop":
                    for target_user, _ in users:
                        
                        if "bot" in target_user.username.lower():
                            continue
                        await self.stop_loop(target_user)
                    await self.highrise.chat("⛔ تم إيقاف جميع الرقصات.")
                    return

                emote_input = " ".join(parts[1:])
                emote_id, emote_name, duration = None, None, None

                # 🎲 اختيار الرقصة
                if emote_input.isdigit():
                    index = int(emote_input) - 1
                    if 0 <= index < len(emote_list):
                        emote_name, emote_id, duration = emote_list[index]
                else:
                    for name, eid, dur in emote_list:
                        # ✅ دعم العربي والإنجليزي (تأمل | stargaze)
                        for alias in name.split("|"):
                            alias = alias.strip().lower()
                            if emote_input.lower() == alias or emote_input.lower() in alias:
                                emote_name, emote_id, duration = name, eid, dur
                                break
                        if emote_id:
                            break

                if not emote_id:
                    await self.highrise.chat("❌ الرقصة غير موجودة.")
                    return

                count = 0
                for target_user, _ in users:
                    
                    if "bot" in target_user.username.lower():
                        continue
                    if target_user.id == self.my_user_id:
                        continue

                    await self.stop_loop(target_user)
                    task = self.highrise.tg.create_task(
                        self.loop_emote(target_user, emote_id, emote_name or "", int(duration) if duration else 0)
                    )
                    task.set_name(target_user.username)
                    count += 1

                await self.highrise.chat(f"💃 تم تشغيل رقصة {emote_name} لـ {count} مستخدم (ماعدا البوتات).")
                return

        # ------------------ 💃 أوامر الرقص العامة (لكل المستخدمين) ------------------
        # التحقق من أن الأمر هو رقم أو اسم رقصة محدد بالكامل (ليس جزئي)
        is_dance_cmd = cmd in ["loop", "dance"] or cmd.isdigit()
        if not is_dance_cmd:
            # تحقق من تطابق كامل فقط مع اسم الرقصة
            for name, _, _ in emote_list:
                for alias in name.split("|"):
                    if cmd.lower() == alias.strip().lower():
                        is_dance_cmd = True
                        break
                if is_dance_cmd:
                    break
        
        if is_dance_cmd:

            # لو كتب رقم أو اسم الرقصة بدون "loop" نضيفها أوتوماتيك
            if cmd.isdigit():
                parts.insert(0, "loop")
                cmd = "loop"
            else:
                # تحقق من تطابق كامل فقط
                for name, _, _ in emote_list:
                    for alias in name.split("|"):
                        if cmd.lower() == alias.strip().lower():
                            parts.insert(0, "loop")
                            cmd = "loop"
                            break
                    if cmd == "loop":
                        break

            if len(parts) < 2 and cmd not in ["loop", "dance"]:
                await self.highrise.chat(
                    "🕺 استخدم:\n"
                    "/loop <رقم أو اسم الرقصة>\n"
                    "/dance <رقم أو اسم الرقصة> → مرة واحدة فقط\n"
                    "أو اكتب فقط /<رقم> أو /<اسم_رقصة>"
                )
                return

            targets = [p for p in parts[1:] if p.startswith("@")]
            emote_input = next((p for p in reversed(parts[1:]) if not p.startswith("@")), "") or cmd

            emote_id, emote_name, duration = None, None, None

            # 🎲 اختيار الرقصة
            if emote_input.isdigit():
                index = int(emote_input) - 1
                if 0 <= index < len(emote_list):
                    emote_name, emote_id, duration = emote_list[index]
            else:
                for name, eid, dur in emote_list:
                    # ✅ دعم العربي والإنجليزي - تطابق كامل فقط
                    for alias in name.split("|"):
                        alias = alias.strip().lower()
                        if emote_input.lower() == alias:
                            emote_name, emote_id, duration = name, eid, dur
                            break
                    if emote_id:
                        break

            if not emote_id:
                await self.highrise.chat("❌ الرقصة غير موجودة.")
                return

            def is_bot_user(u):
                return hasattr(u, "is_bot") and u.is_bot or "bot" in u.username.lower()

            # 🕺 تنفيذ الرقصة
            if not targets:
                if is_bot_user(user):
                    return

                await self.stop_loop(user)

                if cmd == "dance":
                    await self.highrise.send_emote(emote_id, user.id)
                    await self.highrise.chat(f"💫 تم تشغيل رقصة {emote_name} مرة واحدة لـ @{user.username}")
                else:
                    task = self.highrise.tg.create_task(
                        self.loop_emote(user, emote_id, emote_name or "", int(duration) if duration else 0)
                    )
                    task.set_name(user.username)
                    await self.highrise.chat(f"💫 تم تشغيل رقصة {emote_name} (loop) لـ @{user.username}")

            else:
                # 💃 رقصة جماعية - جلب البيانات الحالية من الروم
                try:
                    room_users_response = await self.get_room_users_cached()
                    current_users = room_users_response.content if room_users_response else []
                except Exception:
                    current_users = []
                
                found_count = 0
                not_found = []
                
                for target in targets:
                    username = target[1:].lower()
                    
                    # البحث عن المستخدم في قائمة الروم الحالية
                    target_user = next((u for u, _ in current_users if u.username.lower() == username), None)
                    
                    if not target_user:
                        not_found.append(username)
                        continue
                    
                    if is_bot_user(target_user) or target_user.id == self.my_user_id:
                        continue

                    await self.stop_loop(target_user)

                    try:
                        if cmd == "dance":
                            await self.highrise.send_emote(emote_id, target_user.id)
                        else:
                            task = self.highrise.tg.create_task(
                                self.loop_emote(target_user, emote_id, emote_name or "", int(duration) if duration else 0)
                            )
                            task.set_name(target_user.username)
                        found_count += 1
                    except Exception as e:
                        print(f"⚠️ خطأ في تشغيل رقصة {emote_name} لـ @{target_user.username}: {e}")

                # إرسال رسالة النتيجة
                if found_count > 0:
                    msg = f"💃 تم تشغيل رقصة {emote_name} {'مرة واحدة' if cmd == 'dance' else '(loop)'} لـ {found_count} مستخدم!"
                    if not_found:
                        msg += f"\n⚠️ لم يتم العثور على: {', '.join(not_found)}"
                    await self.highrise.chat(msg)
                else:
                    await self.highrise.chat(f"❌ لم يتم العثور على المستخدمين: {', '.join(not_found or ['Unknown'])}")
            return











        
      

        





       
        
        # 🚫 أمر التبديل - للمالكين والمشرفين فقط، معطّل للبوتات
        allowed_commands = ["switch", "بدل", "değiş", "değis", "degiş"]

        if any(message.lower().startswith(command) for command in allowed_commands):
            def is_bot_user(u):
                return hasattr(u, "is_bot") and u.is_bot or "bot" in u.username.lower()
            
            if is_bot_user(user):
                await self.highrise.send_whisper(user.id, "❌ أمر التبديل معطّل للبوتات!")
                return
            
            # التحقق من صلاحيات المالك/المشرف
            if not await self.is_user_allowed(user):
                await self.highrise.send_whisper(user.id, "❌ هذا الأمر متاح للمالكين والمشرفين فقط.")
                return
            
            # السماح للمالكين والمشرفين
            parts = message.split()
            target_username = None

            for word in parts:
                if word.startswith("@"):
                    target_username = word.lstrip("@").lower()
                    break

            if not target_username:
                await self.highrise.send_whisper(user.id, "❌ من فضلك حدد اسم الشخص اللي عايز تبدله (مثال: switch @username)")
                return

            if target_username not in self.haricler:
                await self.switch_users(user, target_username)
            else:
                await self.highrise.send_whisper(user.id, f"⚠️ لا يمكن تبديل @{target_username} لأنه في قائمة الاستثناء.")
            return



        # ✅ إضافة شخص للقائمة
        if msg.startswith("add swm "):
            if not self.is_owner(user):  # ← تعديل هنا
                await self.highrise.send_whisper(user.id, "❌ هذا الأمر متاح للمالكين فقط.")
                return

            parts = message.split()
            if len(parts) < 3:
                await self.highrise.send_whisper(user.id, "⚠️ الصيغة: add swm @username")
                return

            target_username = parts[2].lstrip("@").lower()
            if target_username not in allowed_addswm_users:
                allowed_addswm_users.append(target_username)
                save_allowed_swms()
                await self.highrise.chat(f"✅ @{target_username} أصبح عنده صلاحية استعمال أمر addswm.")
            else:
                await self.highrise.send_whisper(user.id, f"⚠️ @{target_username} عنده صلاحية بالفعل.")


        # 🗑️ إزالة شخص من القائمة
        if msg.startswith("remove swm "):
            if not self.is_owner(user):  # ← تعديل هنا
                await self.highrise.send_whisper(user.id, "❌ هذا الأمر متاح للمالكين فقط.")
                return

            parts = message.split()
            if len(parts) < 3:
                await self.highrise.send_whisper(user.id, "⚠️ الصيغة: remove swm @username")
                return

            target_username = parts[2].lstrip("@").lower()
            if target_username in allowed_addswm_users:
                allowed_addswm_users.remove(target_username)
                save_allowed_swms()
                await self.highrise.chat(f"🗑️ تم إزالة صلاحية addswm من @{target_username}.")
            else:
                await self.highrise.send_whisper(user.id, f"⚠️ @{target_username} مش عنده صلاحية أصلاً.")


        # 📋 عرض القائمة
        if msg == "swm list":
            if not self.is_owner(user):  # ← تعديل هنا
                await self.highrise.send_whisper(user.id, "❌ هذا الأمر متاح للمالكين فقط.")
                return

            if not allowed_addswm_users:
                await self.highrise.send_whisper(user.id, "⚠️ مفيش حد عنده صلاحية addswm.")
            else:
                await self.highrise.send_whisper(user.id, "📋 المصرح لهم:\n" + "\n".join(f"- @{u}" for u in allowed_addswm_users))


        # 📝 استخدام أمر addswm نفسه
        if msg.startswith("addswm "):
            if user.username.lower() not in allowed_addswm_users:
                await self.highrise.send_whisper(user.id, "❌ هذا الأمر متاح فقط للمصرح لهم.")
                return

            parts = message.split(" ", 2)
            if len(parts) < 3:
                await self.highrise.send_whisper(user.id, "⚠️ الصيغة: addswm @username رسالة الترحيب")
                return

            target_username = parts[1].lstrip("@").lower()
            custom_welcome = parts[2]

            special_welcomes[target_username] = {"welcome": custom_welcome}
            save_custom_welcomes()
            await self.highrise.chat(f"✅ تم إضافة ترحيب مخصص لـ @{target_username} بواسطة @{user.username}")


        # 🗑️ حذف ترحيب مخصص
        if msg.startswith("removeaddswm "):
            if not self.is_owner(user):  # ← تعديل هنا
                await self.highrise.send_whisper(user.id, "❌ هذا الأمر متاح للمالكين فقط.")
                return

            parts = message.split(" ", 1)
            if len(parts) < 2:
                await self.highrise.send_whisper(user.id, "⚠️ الصيغة: removeaddswm @username")
                return

            target_username = parts[1].lstrip("@").lower()
            if target_username in special_welcomes:
                del special_welcomes[target_username]
                save_custom_welcomes()
                await self.highrise.chat(f"🗑️ تم إزالة الترحيب المخصص لـ @{target_username}")
            else:
                await self.highrise.send_whisper(user.id, f"⚠️ لا يوجد ترحيب مخصص لـ @{target_username}")


        # 📋 عرض قائمة الترحيبات
        if msg == "listswm":
            if not self.is_owner(user):  # ← تعديل هنا
                await self.highrise.send_whisper(user.id, "❌ هذا الأمر متاح للمالكين فقط.")
                return

            if not special_welcomes:
                await self.highrise.send_whisper(user.id, "📭 لا توجد ترحيبات مخصصة حالياً.")
                return

            msg_lines = ["📋 قائمة الترحيبات المخصصة:"]
            for username, data in special_welcomes.items():
                if isinstance(data, dict):
                    line = f"🟢 @{username} ← \"{data['welcome']}\""
                else:
                    line = f"🟢 @{username} ← \"{data}\""
                msg_lines.append(line)

            message_text = "\n".join(msg_lines)
            chunks = split_message(message_text)
            for chunk in chunks:
                await self.highrise.send_whisper(user.id, chunk)




        if message.lower() == "add":
            if user.username.lower() != self.owner_username.lower():
                return

            room_users_response = await self.highrise.get_room_users()
            for u, pos in room_users_response.content:
                if u.id == user.id:
                    self.saved_position = {"x": pos.x, "y": pos.y, "z": pos.z, "facing": pos.facing}
                    save_bot_position(self.saved_position)  # ✅ حفظ في ملف
                    await self.highrise.chat("✅ تم حفظ مكان البوت.")
                    return

            await self.highrise.chat("❌ معرفتش مكانك.")
            return
        if message.lower() == "go":
            if user.username.lower() != self.owner_username.lower():
                return

            if not self.saved_position:
                self.saved_position = load_bot_position()  # ✅ تحميل من الملف لو موجود

            if not self.saved_position:
                await self.highrise.chat("❌ مفيش مكان محفوظ للبوت.")
                return

            pos = Position(
                x=self.saved_position["x"],
                y=self.saved_position["y"],
                z=self.saved_position["z"],
                facing=self.saved_position.get("facing", "Front")
            )
            await self.highrise.walk_to(pos)   # ✅ بدل teleport → walk_to
            await self.highrise.chat("🚶 البوت راح لمكانه المحفوظ بالمشي.")
            return


         
        
        if message.startswith(("add_admin")):
            parts = message.split()
            if len(parts) != 2:
                await self.highrise.chat("❌ اكتب add_admin @username")
                return

            username = parts[1].lstrip("@")
            await self.add_admin(username, user)
            return

        if message.startswith(("remove_admin")):
            parts = message.split()
            if len(parts) != 2:
                await self.highrise.chat("❌ اكتب remove_admin @username")
                return

            username = parts[1].lstrip("@")
            await self.remove_admin(username, user)
            return

  
        

        
        






        
        
        if msg.startswith("settele "):
            # السماح فقط لصاحب البوت
            if user.username.lower() != "q.xx":
                await self.highrise.send_whisper(user.id, "❌ هذا الأمر مخصص لصاحب البوت فقط.")
                return

            parts = message.strip().split()
            roles = parts[1:]  # باقي الكلام بعد !settele
            if not roles:
                await self.highrise.send_whisper(user.id, "❌ الصيغة: !settele [vip mod owner admin]")
                return

            valid_roles = ["vip", "admin", "owner", "mod"]
            roles = [r.lower() for r in roles if r.lower() in valid_roles]

            if not roles:
                await self.highrise.send_whisper(user.id, "❌ لم يتم تحديد أي رتبة صالحة.")
                return

            room_users_response = await self.highrise.get_room_users()
            for u, pos in room_users_response.content:
                if u.id == user.id:
                    for role in roles:
                         self.teleport_roles[role] = pos
                    self.save_teleports()  # ✅ نحفظ المواقع في ملف
                    await self.highrise.chat(f"✅ تم حفظ الموقع للرتب: {', '.join(roles)}.")
                    return

            await self.highrise.send_whisper(user.id, "❌ لم يتم العثور على موقعك.")
            return



        # 🟡 أمر التنقل إلى vip (أو غيره من الرُتب)
        if len(parts) >= 1 and parts[0] in self.teleport_roles:
            role = parts[0]

            # 👮 فقط المشرفين يقدروا يستخدموا vip
        if msg.startswith("vip") or msg.startswith("mod") or msg.startswith("admin") or msg.startswith("owner"):
            parts = msg.split()
            role = parts[0].lower()

            if role not in self.teleport_roles:
                await self.highrise.send_whisper(user.id, f"❌ لم يتم تحديد موقع لرتبة {role}.")
                return

            # تحقق من صلاحية المستخدم
            if not await self.is_user_allowed(user):
                await self.highrise.send_whisper(user.id, "❌ ليس لديك صلاحية استخدام هذا الأمر.")
                return

            # لو مفيش اسم مستخدم بعد الأمر، انقل المستخدم نفسه
            if len(parts) == 1:
                try:
                    await self.highrise.teleport(user.id, self.teleport_roles[role])
                    await self.highrise.chat(f"✅ تم نقلك إلى موقع {role}.")
                except Exception as e:
                    await self.highrise.send_whisper(user.id, f"❌ فشل النقل: {str(e)}")
                    print(f"Teleport error for {role}: {e}")
                return

            # لو في @اسم، نحاول ننقل الشخص
            target_name = parts[1].lstrip("@").lower()
            room_users_response = await self.highrise.get_room_users()
            for u, _ in room_users_response.content:
                if u.username.lower() == target_name:
                    try:
                        await self.highrise.teleport(u.id, self.teleport_roles[role])
                        await self.highrise.chat(f"✅ تم نقل @{target_name} إلى موقع {role}.")
                    except Exception as e:
                        await self.highrise.send_whisper(user.id, f"❌ فشل نقل @{target_name}: {str(e)}")
                        print(f"Teleport error for {target_name} to {role}: {e}")
                    return

            await self.highrise.send_whisper(user.id, f"❌ لم يتم العثور على المستخدم @{target_name} في الروم.")
            return

        # ✅ نقل نفسك إلى موقع محفوظ (أي اسم بمفرده)
        global room_commands
        if len(parts) == 1 and parts[0] in ["تحت", "وسط", "فوق", "vr"]:
            command = parts[0]
            info = room_commands.get(command)
            if not info:
                await self.highrise.send_whisper(user.id, f"❌ مكان '{command}' مش محفوظ.")
                return
            
            pos_data = info["position"]
            pos = Position(x=pos_data["x"], y=pos_data["y"], z=pos_data["z"], facing=pos_data.get("facing", "Front"))
            try:
                await self.highrise.teleport(user.id, pos)
                await self.highrise.chat(f"✅ تم نقلك إلى '{command}'.")
            except Exception as e:
                await self.highrise.send_whisper(user.id, f"❌ فشل النقل: {str(e)}")
                print(f"Custom location teleport error for {command}: {e}")
            return

        # ✅ نقل شخص آخر إلى f1 / f2 / f3 / f4 (فقط للمشرفين أو صاحب البوت)
        if len(parts) >= 2 and parts[0] in ["تحت", "وسط", "فوق", "vr"]:
            if not await self.is_user_allowed(user):
                await self.highrise.send_whisper(user.id, "❌ الأمر ده مخصص للمشرفين فقط.")
                return

            command = parts[0]
            target_name = parts[1].lstrip('@').lower()

            target_user = None
            room_users_response = await self.highrise.get_room_users()
            for u, pos in room_users_response.content:
                if u.username.lower() == target_name:
                    target_user = u
                    break

            if not target_user:
                await self.highrise.send_whisper(user.id, f"❌ @{target_name} مش موجود في الروم.")
                return

            info = room_commands.get(command)
            if not info:
                await self.highrise.send_whisper(user.id, f"❌ مكان '{command}' مش محفوظ.")
                return

            if info.get("admin_only") and not await self.is_user_allowed(target_user):
                await self.highrise.send_whisper(user.id, f"❌ لا يمكن نقل @{target_name} إلى مكان مخصص للمشرفين.")
                return

            pos_data = info["position"]
            pos = Position(x=pos_data["x"], y=pos_data["y"], z=pos_data["z"], facing=pos_data.get("facing", "Front"))
            try:
                await self.highrise.teleport(target_user.id, pos)
                await self.highrise.send_whisper(user.id, f"✅ تم نقل @{target_user.username} إلى '{command}'.")
            except Exception as e:
                await self.highrise.send_whisper(user.id, f"❌ فشل نقل @{target_user.username}: {str(e)}")
                print(f"Custom location teleport error for {command}: {e}")
            return

        # 📍 أمر حفظ موقع جديد (set تحت/فوق/نص/vr)
        if message.startswith("set "):
            if not await self.is_user_allowed(user):
                await self.highrise.send_whisper(user.id, "❌ هذا الأمر مخصص للمشرفين فقط")
                return
            
            parts = message.split()
            if len(parts) < 2:
                await self.highrise.send_whisper(user.id, "❌ الصيغة: set <اسم المكان>")
                return
            
            location_name = parts[1].lower()
            
            # الحصول على موقع المستخدم الحالي
            room_users_response = await self.highrise.get_room_users()
            user_position = None
            for u, pos in room_users_response.content:
                if u.id == user.id:
                    user_position = pos
                    break
            
            if not user_position:
                await self.highrise.send_whisper(user.id, "❌ معرفتش مكانك")
                return
            
            # حفظ الموقع
            room_commands[location_name] = {
                "enabled": True,
                "position": {
                    "x": user_position.x,
                    "y": user_position.y,
                    "z": user_position.z,
                    "facing": user_position.facing
                },
                "admin_only": False
            }
            save_room_commands()
            await self.highrise.send_whisper(user.id, f"✅ تم حفظ المكان '{location_name}' بنجاح!")
            return

        # 🗑️ أمر حذف موقع (del تحت/فوق/نص/vr)
        if message.startswith("del "):
            if not await self.is_user_allowed(user):
                await self.highrise.send_whisper(user.id, "❌ هذا الأمر مخصص للمشرفين فقط")
                return
            
            parts = message.split()
            if len(parts) < 2:
                await self.highrise.send_whisper(user.id, "❌ الصيغة: del <اسم المكان>")
                return
            
            location_name = parts[1].lower()
            
            if location_name not in room_commands:
                await self.highrise.send_whisper(user.id, f"❌ المكان '{location_name}' غير موجود")
                return
            
            del room_commands[location_name]
            save_room_commands()
            await self.highrise.send_whisper(user.id, f"✅ تم حذف المكان '{location_name}' بنجاح!")
            return

        # 📋 أمر عرض المواقع المحفوظة (list_locations)
        if message.lower() in ["list_locations", "listloc", "locations"]:
            if not room_commands:
                await self.highrise.send_whisper(user.id, "📭 لا توجد مواقع محفوظة حالياً")
                return
            
            msg_lines = ["📍 المواقع المحفوظة:"]
            for name, info in room_commands.items():
                pos = info.get("position", {})
                admin_flag = "🔐" if info.get("admin_only") else "🟢"
                msg_lines.append(f"{admin_flag} {name} → ({pos.get('x', 0)}, {pos.get('y', 0)}, {pos.get('z', 0)})")
            
            message_text = "\n".join(msg_lines)
            chunks = split_message(message_text)
            for chunk in chunks:
                await self.highrise.send_whisper(user.id, chunk)
            return

        # 🗑️ أمر إزالة مشرف (removemod @username)
        if message.lower().startswith("removemod "):
            if not await self.is_user_allowed(user):
                await self.highrise.send_whisper(user.id, "❌ هذا الأمر مخصص للمشرفين فقط")
                return
            
            target_name = message.split("removemod ", 1)[1].strip().lstrip("@").lower()
            
            try:
                room_users_response = await self.highrise.get_room_users()
                target_user = None
                for u, _ in room_users_response.content:
                    if u.username.lower() == target_name:
                        target_user = u
                        break
                
                if not target_user:
                    await self.highrise.send_whisper(user.id, f"❌ @{target_name} غير موجود في الروم")
                    return
                
                # إنشاء RoomPermissions جديد بدون صلاحيات
                permissions = RoomPermissions(
                    moderator=False,
                    designer=False
                )
                await self.highrise.change_room_privilege(target_user.id, permissions)
                await self.highrise.send_whisper(user.id, f"✅ تم إزالة @{target_user.username} من المشرفين")
            except Exception as e:
                print(f"removemod error: {e}")
                await self.highrise.send_whisper(user.id, f"⚠️ خطأ: {str(e)[:100]}")
            return

        # 🗑️ أمر إزالة مصمم (removedesigner @username)
        if message.lower().startswith("removedesigner "):
            if not await self.is_user_allowed(user):
                await self.highrise.send_whisper(user.id, "❌ هذا الأمر مخصص للمشرفين فقط")
                return
            
            target_name = message.split("removedesigner ", 1)[1].strip().lstrip("@").lower()
            
            try:
                room_users_response = await self.highrise.get_room_users()
                target_user = None
                for u, _ in room_users_response.content:
                    if u.username.lower() == target_name:
                        target_user = u
                        break
                
                if not target_user:
                    await self.highrise.send_whisper(user.id, f"❌ @{target_name} غير موجود في الروم")
                    return
                
                # إنشاء RoomPermissions جديد بدون صلاحيات
                permissions = RoomPermissions(
                    moderator=False,
                    designer=False
                )
                await self.highrise.change_room_privilege(target_user.id, permissions)
                await self.highrise.send_whisper(user.id, f"✅ تم إزالة @{target_user.username} من المصممين")
            except Exception as e:
                print(f"removedesigner error: {e}")
                await self.highrise.send_whisper(user.id, f"⚠️ خطأ: {str(e)[:100]}")
            return

        # 👑 أمر إضافة مالك (addowner @username)
        if message.lower().startswith("addowner "):
            if not is_owner(user.username):
                await self.highrise.send_whisper(user.id, "❌ هذا الأمر مخصص للمالكين فقط")
                return
            
            target_name = message.split("addowner ", 1)[1].strip().lstrip("@").lower()
            owners.add(target_name)
            save_owners()
            await self.highrise.chat(f"✅ تمت إضافة @{target_name} كمالك! 👑")
            return

        # 🗑️ أمر إزالة مالك (removeowner @username)
        if message.lower().startswith("removeowner "):
            if not is_owner(user.username):
                await self.highrise.send_whisper(user.id, "❌ هذا الأمر مخصص للمالكين فقط")
                return
            
            target_name = message.split("removeowner ", 1)[1].strip().lstrip("@").lower()
            if target_name in owners:
                owners.remove(target_name)
                save_owners()
                await self.highrise.chat(f"✅ تمت إزالة @{target_name} من المالكين")
            else:
                await self.highrise.send_whisper(user.id, f"⚠️ @{target_name} ليس مالكاً")
            return

        if msg.startswith(("kick ", "ban ", "mute ", "unmute ", "unban ")):
            parts = msg.strip().split()
            if not parts:
                return

            cmd = parts[0].lower()
            args = parts[1:]

            # تحقق من صلاحيات المستخدم
            if not await self.is_user_allowed(user):
                await self.highrise.send_whisper(user.id, "❌ لا تملك صلاحية استخدام هذا الأمر.")
                return

            # أوامر: kick / ban / mute / unmute
            if cmd in ["kick", "ban", "mute", "unmute"] and args:
                target_name = args[0].lstrip("@").lower()
                duration = int(args[1]) if len(args) > 1 and args[1].isdigit() else None

                room_info = await self.highrise.get_room_users()
                room_users = room_info.content

                for u, pos in room_users:
                    if u.username.lower() == target_name:

                        # ✅ تنفيذ الإجراء
                        try:
                            if cmd == "kick":
                                await self.highrise.moderate_room(user_id=u.id, action="kick")
                                await self.highrise.chat(f"✅ تم طرد {u.username}.")
                            elif cmd == "ban":
                                duration = duration or 60 * 60 * 24 * 365 * 100  # حظر دائم
                                await self.highrise.moderate_room(user_id=u.id, action="ban", action_length=duration)
                                banned_users[u.id] = u.username
                                save_banned_users()
                                await self.highrise.chat(f"✅ {u.username} تم حظره لمدة {duration} ثانية.")
                            elif cmd == "mute":
                                duration = duration or 3600
                                await self.highrise.moderate_room(user_id=u.id, action="mute", action_length=duration)
                                await self.highrise.chat(f"✅ {u.username} تم كتمه لمدة {duration} ثانية.")
                            elif cmd == "unmute":
                                await self.highrise.moderate_room(user_id=u.id, action="mute", action_length=1)
                                await self.highrise.chat(f"✅ تم فك كتم {u.username}.")
                            return

                        except Exception as e:
                            await self.highrise.send_whisper(user.id, f"⚠️ خطأ أثناء تنفيذ {cmd}: {e}")
                            return

                await self.highrise.chat("❌ لم يتم العثور على المستخدم في الروم.")
                return

            # أمر unban
            elif cmd == "unban" and args:
                target_name = args[0].lstrip("@").lower()
                user_id_to_unban = None

                for uid, uname in banned_users.items():
                    if uname.lower() == target_name:
                        user_id_to_unban = uid
                        break

                if user_id_to_unban:
                    await self.highrise.moderate_room(user_id=user_id_to_unban, action="unban")
                    del banned_users[user_id_to_unban]
                    save_banned_users()
                    await self.highrise.chat(f"✅ تم فك الحظر عن {target_name}.")
                else:
                    await self.highrise.chat("❌ لا يوجد مستخدم بهذا الاسم في قائمة الحظر.")
                return


       

        

        # 🎁 أمر rtip (يدّي جولد لشخص محدد)
        if msg.startswith("rtip "):
            if user.username.lower() not in self.allowed_autotip_users:
                await self.highrise.send_whisper(user.id, "❌ هذا الأمر خاص بالمصرّح لهم فقط.")
                return

            parts = msg.split()
            if len(parts) < 3:
                await self.highrise.send_whisper(user.id, "❌ الصيغة: rtip @username الكمية")
                return

            name = parts[1].lstrip("@")
            try:
                amount = int(parts[2])
                if amount <= 0:
                    raise ValueError()
            except ValueError:
                await self.highrise.send_whisper(user.id, "❌ الكمية غير صحيحة.")
                return

            # 🔍 محاولة إيجاد المستخدم بالاسم
            target_user = await self.get_user_by_username(self.highrise, name)
            if target_user:
                await self.highrise.tip_user(target_user.id, amount_to_gold_bar(amount))
                await self.highrise.chat(f"🎁 @{user.username} أرسل {amount} جولد إلى @{name}")
            else:
                await self.highrise.send_whisper(user.id, f"❌ المستخدم @{name} غير موجود.")
            return
        
        if msg.startswith("tipauto"):
            if not is_owner(user.username):
                await self.highrise.chat("❌ هذا الأمر مخصص للمالكين فقط.")
                return

            parts = msg.split()

            # tipauto on [amount] [delay]
            if len(parts) >= 4 and parts[1] == "on":
                global auto_tip_enabled, auto_tip_amount, auto_tip_delay
                try:
                    auto_tip_amount = int(parts[2])
                    auto_tip_delay = int(parts[3])
                except Exception:
                    await self.highrise.chat("❌ الصيغة الصحيحة: tipauto on [جولد] [ثواني]")
                    return

                # ✅ إذا كان يعمل بالفعل، لا تفعل شيء
                if auto_tip_enabled:
                    await self.highrise.chat(f"⚠️ أوتو تيب يعمل بالفعل! استخدم 'tipauto off' أولاً للإيقاف.")
                    return

                auto_tip_enabled = True
                
                # 🚀 إنشاء task جديد
                try:
                    if hasattr(self, 'auto_tip_task') and self.auto_tip_task and not self.auto_tip_task.done():
                        self.auto_tip_task.cancel()
                    
                    self.auto_tip_task = asyncio.create_task(self.auto_tip_loop())
                    print(f"✅ تم إنشاء auto_tip_task جديد")
                except Exception as e:
                    print(f"⚠️ خطأ في إنشاء task: {e}")
                
                await self.highrise.chat(f"🔁 تم تشغيل أوتو تيب — كل {auto_tip_delay}s مقدار {auto_tip_amount} جولد.")
                print(f"💸 تم تشغيل auto_tip: {auto_tip_amount} جولد كل {auto_tip_delay}ث")
                return

            # tipauto off
            if len(parts) >= 2 and parts[1] == "off":
                auto_tip_enabled = False
                
                # 🛑 إلغاء الـ task
                try:
                    if hasattr(self, 'auto_tip_task') and self.auto_tip_task and not self.auto_tip_task.done():
                        self.auto_tip_task.cancel()
                        print("✅ تم إلغاء auto_tip_task")
                except Exception as e:
                    print(f"⚠️ خطأ في إلغاء task: {e}")
                
                await self.highrise.chat("⛔ تم إيقاف أوتو تيب.")
                return



      
        


        # ----------------------------------------------------
        # 💰 أمر TIP — بجميع أنواعه
        # ----------------------------------------------------
        if msg.startswith("tip "):

            if not is_owner(user.username):
                await self.highrise.chat("❌ هذا الأمر مخصص للمالكين فقط.")
                return

            parts = msg.split()
            if len(parts) < 3:
                await self.highrise.chat(
                    "💵 طرق استخدام tip:\n"
                    "1️⃣ tip @user [amount]\n"
                    "2️⃣ tip [num_people] [amount]\n"
                    "3️⃣ tip all [amount]"
                )
                return

            # الحالة 3: tip all
            if parts[1] == "all":
                try:
                    amount = int(parts[2])
                except Exception:
                    await self.highrise.chat("❌ أدخل رقم صحيح.")
                    return

                room_users_response = await self.highrise.get_room_users()
                room_users = room_users_response.content
                sent = 0

                for u, _ in room_users:
                    if u.id == self.my_user_id: continue
                    if "bot" in u.username.lower(): continue

                    try:
                        await self.highrise.tip_user(u.id, amount_to_gold_bar(amount))
                        sent += 1
                    except Exception as e:
                        if "not enough" in str(e).lower():
                            await self.highrise.chat("❌ البوت لا يملك جولد كافي!")
                            return

                await self.highrise.chat(f"💰 تم إرسال {amount} جولد إلى {sent} شخص.")
                return

            # الحالة 1: tip @user amount
            if parts[1].startswith("@"):
                target = parts[1][1:]
                try:
                    amount = int(parts[2])
                except Exception:
                    await self.highrise.chat("❌ أدخل رقم صحيح.")
                    return

                target_user = await self.get_user_by_username(self.highrise, target)
                if not target_user:
                    await self.highrise.chat(f"❌ @{target} غير موجود.")
                    return

                try:
                    await self.highrise.tip_user(target_user.id, amount_to_gold_bar(amount))
                    await self.highrise.chat(f"💵 تم إرسال {amount} جولد إلى @{target}")
                except Exception as e:
                    if "not enough" in str(e).lower():
                        await self.highrise.chat("❌ البوت لا يملك جولد كافي!")
                    else:
                        await self.highrise.chat(f"⚠️ خطأ: {e}")
                return

            # الحالة 2: tip [num_people] [amount]
            try:
                num = int(parts[1])
                amount = int(parts[2])
            except Exception:
                await self.highrise.chat("❌ الصيغة غير صحيحة.")
                return

            room_users_response = await self.highrise.get_room_users()
            room_users = room_users_response.content
            users = [u for u, _ in room_users if u.id != self.my_user_id and "bot" not in u.username.lower()]

            if not users:
                await self.highrise.chat("❌ لا يوجد أشخاص في الروم.")
                return

            selected = random.sample(users, min(num, len(users)))
            sent = 0

            for u in selected:
                try:
                    await self.highrise.tip_user(u.id, amount_to_gold_bar(amount))
                    sent += 1
                except Exception:
                    await self.highrise.chat("❌ البوت لا يملك جولد كافي!")
                    return

            await self.highrise.chat(f"💰 تم توزيع {amount} جولد على {sent} شخص.")
            return

        
        
        

        # 🧾 users
        if msg == "users":
            users_response = await self.highrise.get_room_users()
            users = users_response.content
            names = [f"@{u.username}" for u, _ in users]
            await self.highrise.send_whisper(user.id, "👥 الموجودين الآن:\n" + ", ".join(names))
            return

      



       
        if msg.startswith("add vip "):
            # السماح فقط للأونرز
            if user.username.lower() not in owners:
                await self.highrise.send_whisper(user.id, "❌ هذا الأمر مخصص للأونرز فقط.")
                return

            parts = message.split()
            if len(parts) < 3:
                await self.highrise.send_whisper(user.id, "❌ الصيغة: add vip @username")
                return

            target_username = parts[2].lstrip("@").lower()

            users_response = await self.highrise.get_room_users()
            users = users_response.content
            target_user = next((u for u, _ in users if u.username.lower() == target_username), None)

            if not target_user:
                await self.highrise.send_whisper(user.id, f"❌ لم يتم العثور على @{target_username} في الروم.")
                return

            vip_users.add(target_username)
            save_vip_users()
            await self.highrise.chat(f"✅ تم إعطاء صلاحية VIP للمستخدم @{target_username}.")
            return


        # ✅ إضافة شخص لقائمة المصرح لهم باستخدام "allow vip"
        if msg.startswith("allow vip "):
            if not is_owner(user.username):
                await self.highrise.send_whisper(user.id, "❌ هذا الأمر مخصص للمالكين فقط.")
                return

            parts = msg.split()
            if len(parts) < 3:
                await self.highrise.send_whisper(user.id, "❌ الصيغة: allow vip @username")
                return

            new_user = parts[2].lstrip("@").lower()
            if new_user not in allowed_vip_users:
                allowed_vip_users.append(new_user)
                save_allowed_vip_users()
                await self.highrise.chat(f"✅ @{new_user} أصبح مصرح له باستخدام أمر add vip.")
            else:
                await self.highrise.send_whisper(user.id, f"⚠️ @{new_user} عنده الصلاحية بالفعل.")
            return


        # ✅ إزالة شخص من قائمة المصرح لهم باستخدام "remove allow vip"
        if msg.startswith("remove allow vip "):
            if not is_owner(user.username):
                await self.highrise.send_whisper(user.id, "❌ هذا الأمر مخصص للمالكين فقط.")
                return

            parts = msg.split()
            if len(parts) < 4:
                await self.highrise.send_whisper(user.id, "❌ الصيغة: remove allow vip @username")
                return

            remove_user = parts[3].lstrip("@").lower()
            if remove_user in allowed_vip_users:
                allowed_vip_users.remove(remove_user)
                save_allowed_vip_users()
                await self.highrise.chat(f"🗑️ @{remove_user} تم إزالة صلاحياته من استخدام add vip.")
            else:
                await self.highrise.send_whisper(user.id, f"⚠️ @{remove_user} مش موجود في قائمة المصرح لهم.")
            return


        # ✅ عرض قائمة المصرح لهم "list allow vip"
        if msg == "list allow vip":
            if not is_owner(user.username):
                await self.highrise.send_whisper(user.id, "❌ هذا الأمر مخصص للمالكين فقط.")
                return

            if not allowed_vip_users:
                await self.highrise.send_whisper(user.id, "📋 لا يوجد أي شخص لديه صلاحية add vip.")
                return

            users_list = "\n".join([f"- @{u}" for u in allowed_vip_users])
            await self.highrise.send_whisper(user.id, f"📋 قائمة المصرح لهم باستخدام add vip:\n{users_list}")
            return


        # ✅ أمر إزالة VIP
        if msg.startswith("remove vip "):
            if not is_owner(user.username):
                await self.highrise.send_whisper(user.id, "❌ هذا الأمر مخصص للمالكين فقط.")
                return

            parts = msg.split()
            if len(parts) < 3:
                await self.highrise.send_whisper(user.id, "❌ الصيغة: remove vip @username")
                return

            target_username = parts[2].lstrip("@").lower()
            if target_username not in vip_users:
                await self.highrise.send_whisper(user.id, f"⚠️ @{target_username} لا يملك VIP.")
                return

            vip_users.remove(target_username)
            save_vip_users()
            await self.highrise.chat(f"🗑️ تم إزالة صلاحية VIP من @{target_username}.")
            return

        # 🧹 مسح جميع VIP
        if msg == "clear vip":
            if not is_owner(user.username):
                await self.highrise.send_whisper(user.id, "❌ هذا الأمر مخصص للمالكين فقط.")
                return

            vip_users.clear()
            save_vip_users()
            await self.highrise.chat("🧹 تم مسح جميع مستخدمين VIP.")
            return
    

        if msg == "banlist":
            if not is_owner(user.username):  # 🔒 مخصص للمالكين فقط
                await self.highrise.send_whisper(user.id, "❌ هذا الأمر مخصص للمالكين فقط.")
                return

            if not banned_users:
                await self.highrise.send_whisper(user.id, "✅ لا يوجد أي شخص محظور حاليًا.")
                return

            ban_list = "\n".join(f"- @{uname}" for uname in banned_users.values())
            message_text = f"📛 قائمة المحظورين:\n{ban_list}"

            chunks = split_message(message_text)
            for chunk in chunks:
                await self.highrise.send_whisper(user.id, chunk)

            return


       
        

        

        if message.startswith(("هات ", "b ")):  # ← أضفت مسافة هنا!
            # ✅ تحقق من الصلاحية
            if not await self.is_user_allowed(user):
                await self.highrise.send_whisper(user.id, "❌ مالكش صلاحية تستعمل الأمر.")
                return

            parts = message.split()
            if len(parts) < 2:
                await self.highrise.send_whisper(user.id, "❌ اكتب: هات @user أو اسم مباشر.")
                return

            targets = [p.lstrip("@").lower() for p in parts[1:] if p.strip()]
            if not targets:
                await self.highrise.send_whisper(user.id, "❌ لم يتم تحديد أي اسم.")
                return

            room_users_response = await self.highrise.get_room_users()
            room_users = room_users_response.content
            found = False

            for name in targets:
                if name == user.username.lower():
                    continue  # ما يسحبش نفسه

                if name == self.bot_username:
                    await self.highrise.send_whisper(user.id, "❌ لا يمكن سحب البوت.")
                    continue

                target_user = next((u for u, _ in room_users if u.username.lower() == name), None)

                if target_user:
                    await self.teleport_user_next_to(target_user.id, user)
                    await self.highrise.send_whisper(user.id, f"✅ تم نقل @{target_user.username}")
                    found = True
                else:
                    await self.highrise.send_whisper(user.id, f"❌ @{name} مش موجود في الروم.")

            if not found:
                await self.highrise.send_whisper(user.id, "❌ لم يتم سحب أي شخص.")
            return
        if msg.startswith(("روح ", "go ")):
            # ✅ تحقق من الصلاحية
            if not await self.is_user_allowed(user):
                await self.highrise.send_whisper(user.id, "❌ مالكش صلاحية تستعمل الأمر.")
                return

            parts = msg.split('@')
            if len(parts) < 2 or not parts[1].strip():
                await self.highrise.send_whisper(user.id, "❌ اكتب: عند @username أو go @username")
                return

            target_username = parts[1].strip().lower()
            await self.teleport_to_user(user, target_username)
            return


        elif msg.startswith(("امسك", "fix", "اسمك")) and await self.is_user_allowed(user):
            if "@" not in msg:
                await self.highrise.send_whisper(user.id, "❌ استخدم الأمر بهذا الشكل: fix @username")
                return

            target_username = msg.split("@", 1)[-1].strip().lower()
            room_users_response = await self.highrise.get_room_users()
            room_users = room_users_response.content
            target_user_info = next(
                (info for info in room_users if info[0].username.lower() == target_username),
                None
            )

            if target_user_info:
                target_user, initial_position = target_user_info
                task = asyncio.create_task(self.reset_target_position(target_user, initial_position))

                if target_user.id not in self.position_tasks:
                    self.position_tasks[target_user.id] = []
                self.position_tasks[target_user.id].append(task)

                await self.highrise.send_whisper(user.id, f"✅ تم تثبيت @{target_username} في مكانه.")
            else:
                await self.highrise.send_whisper(user.id, f"❌ لم يتم العثور على المستخدم @{target_username} في الغرفة.")
            return

        elif msg.startswith(("فك", "unfix")) and await self.is_user_allowed(user):
            if "@" not in msg:
                await self.highrise.send_whisper(user.id, "❌ استخدم الأمر بهذا الشكل: unfix @username")
                return

            target_username = msg.split("@", 1)[-1].strip().lower()
            room_users_response = await self.highrise.get_room_users()
            room_users = room_users_response.content
            target_user_obj = next(
                (user_obj for user_obj, _ in room_users if user_obj.username.lower() == target_username),
                None
            )

            if target_user_obj and target_user_obj.id in self.position_tasks:
                for task in self.position_tasks[target_user_obj.id]:
                    task.cancel()
                del self.position_tasks[target_user_obj.id]
                await self.highrise.send_whisper(user.id, f"✅ تم تحرير @{target_username}")
            else:
                await self.highrise.send_whisper(user.id, f"❌ مفيش حد مثبت اسمه @{target_username}")
            return

        
        # 👑 addowner
        if msg.startswith("addowner "):
            if not self.is_owner(user):
                await self.highrise.chat("❌ هذا الأمر مخصص للمالكين فقط.")
                return

            parts = message.split()
            if len(parts) < 2:
                await self.highrise.chat("❌ استخدم: addowner اسم_المستخدم")
                return

            target_username = parts[1]
            await self.add_owner(target_username, user)
            return

        # 👑 listowners
        if msg == "listowners":
            if len(owners) == 0:
                await self.highrise.chat("📋 لا يوجد مالكين مسجلين حالياً")
            else:
                owners_list = ", ".join([f"@{o}" for o in owners])
                await self.highrise.chat(f"👑 قائمة المالكين: {owners_list}")
            return

        # 👑 removeowner
        if msg.startswith("removeowner "):
            if not self.is_owner(user):
                await self.highrise.chat("❌ هذا الأمر مخصص للمالكين فقط.")
                return

            parts = message.split()
            if len(parts) < 2:
                await self.highrise.chat("❌ استخدم: removeowner اسم_المستخدم")
                return

            target_username = parts[1]
            await self.remove_owner(target_username, user)
            return


        
        # 📡 أمر ping - اختبار سرعة الاتصال
        if msg in ["ping", "بينج"]:
            ping_ms = await self.get_ping()
            if ping_ms is not None:
                await self.highrise.chat(f"🏓 Ping: {ping_ms}ms")
            else:
                await self.highrise.chat("❌ فشل قياس البينج")
            return
        
        # ⏰ أمر uptime - عرض مدة تشغيل البوت
        if msg in ["uptime", "وقت_التشغيل", "runtime"]:
            uptime_str = await self.get_uptime()
            await self.highrise.chat(f"⏰ Bot uptime: {uptime_str}")
            return
        
        # 💰 أمر محفظة - عرض جولد البوت
        if msg in ["محفظة", "wallet", "gold", "جولد"]:
            bot_gold = await self.get_bot_gold()
            await self.highrise.chat(f"💰 محفظة البوت: {bot_gold} جولد 💎")
            return
        
        # 🔍 أمر info - معلومات عن مستخدم
        if msg.startswith(("info ", "معلومات ")):
            parts = message.split()
            if len(parts) < 2:
                await self.highrise.chat("❌ استخدم: info @username أو info اسم_المستخدم")
                return
            
            target_username = parts[1].lstrip("@")
            user_info = await self.get_user_info(target_username)
            
            if user_info:
                info_text = (
                    f"👤 معلومات @{user_info['username']}:\n"
                    f"🆔 User ID: {user_info['user_id']}\n"
                    f"📍 Position: {user_info['position']}\n"
                    f"⭐ Role: {user_info['roles']}"
                )
                await self.highrise.chat(info_text)
            else:
                await self.highrise.chat(f"❌ لم يتم العثور على @{target_username}")
            return
        
        # 💬 أمر say - البوت يتكلم بالهمس فقط
        if msg.startswith("say "):
            if not await self.is_user_allowed(user):
                await self.highrise.send_whisper(user.id, "❌ هذا الأمر مخصص للأدمن فقط.")
                return

            say_message = message[4:].strip()  # إزالة "say " من البداية

            if say_message:
                await self.highrise.send_whisper(user.id, say_message)
            else:
                await self.highrise.send_whisper(user.id, "❌ اكتب رسالة بعد say")
            return

        
        # 📧 أمر invite - إرسال دعوة انضمام للروم
        if msg.startswith("invite"):
            if not await self.is_user_allowed(user):
                await self.highrise.send_whisper(user.id, "❌ هذا الأمر مخصص للأدمن فقط.")
                return

            try:
                # إرسال دعوة لكل الأشخاص في contact_list (حتى لو خرجوا من الروم)
                global contact_list
                if len(contact_list) == 0:
                    await self.highrise.send_whisper(user.id, "❌ قائمة الاتصال فارغة.")
                    return

                sent_count = 0
                failed_count = 0
                
                # رسالة الدعوة المخصصة أو رسالة افتراضية
                custom_msg = msg[6:].strip() if len(msg) > 6 else "شارك دعوة الغرفة"
                
                # صيغة الرسالة الاحترافية
                invite_text = (
                    f"👋 شارك دعوة غرفة\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"💬 **الرسالة:** {custom_msg}\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"✨ تعال انضم إلينا الآن! ✨"
                )
                
                # جلب جميع المستخدمين لتجميع معرفاتهم
                try:
                    room_users_response = await self.highrise.get_room_users()
                    if not hasattr(room_users_response, 'content'):
                        await self.highrise.send_whisper(user.id, "❌ خطأ في جلب قائمة المستخدمين")
                        return
                    
                    # بناء قاموس بأسماء المستخدمين ومعرفاتهم
                    user_ids = {}
                    for u, pos in room_users_response.content:
                        user_ids[u.username.lower()] = u.id
                except Exception as e:
                    print(f"⚠️ خطأ في جلب معرفات المستخدمين: {e}")
                    user_ids = {}
                
                # إرسال الدعوات لجميع الأشخاص في contact_list
                for username in contact_list:
                    try:
                        username_lower = username.lower()
                        
                        # إذا كان لدينا معرفه المستخدم، أرسل دعوة مباشرة
                        if username_lower in user_ids:
                            user_id = user_ids[username_lower]
                            # محاولة إرسال دعوة انضمام للروم
                            if hasattr(self, 'current_room_id') and self.current_room_id:
                                await self.highrise.send_room_invite(user_id, self.current_room_id)
                            # أو إرسال رسالة
                            await self.highrise.send_message(user_id, invite_text)
                            sent_count += 1
                            await asyncio.sleep(0.3)
                        else:
                            # المستخدم لا يملك معرفه، لا يمكن الإرسال له
                            failed_count += 1
                    except Exception as e:
                        print(f"⚠️ فشل إرسال دعوة إلى {username}: {e}")
                        failed_count += 1
                
                # رسالة التأكيد في الروم
                await self.highrise.chat(f"📧 تم إرسال {sent_count} دعوة من أصل {len(contact_list)}")
                if failed_count > 0:
                    await self.highrise.send_whisper(user.id, f"⚠️ فشل إرسال {failed_count} دعوة")
                    
            except Exception as e:
                await self.highrise.send_whisper(user.id, f"❌ خطأ في إرسال الدعوات: {str(e)}")
                print(f"Error in invite command: {e}")
            return

        # 📢 أمر spam - تشغيل السبام
        if msg.startswith("spam "):
            if not await self.is_user_allowed(user):
                await self.highrise.send_whisper(user.id, "❌ هذا الأمر مخصص للأدمن فقط.")
                return

            spam_text = msg[5:].strip()
            if not spam_text:
                await self.highrise.send_whisper(user.id, "❌ اكتب رسالة بعد spam")
                return

            # إيقاف سبام قديم لو موجود
            if self.spam_task:
                self.is_spamming = False
                self.spam_task.cancel()
                self.spam_task = None

            # تشغيل سبام جديد
            self.is_spamming = True
            self.spam_task = asyncio.create_task(self.spam_message(spam_text, delay=1.5))
            await self.highrise.chat(f"📢 بدأ السبام: {spam_text}")
            return


        # 🛑 أمر stop - إيقاف السبام والمتابعة
        if msg.strip().lower() in ["stop", "ستوب", "توقف", "إيقاف"]:
            stopped_something = False
            
            if self.is_spamming:
                self.is_spamming = False
                if self.spam_task:
                    self.spam_task.cancel()
                    try:
                        await asyncio.sleep(0.1)
                    except:
                        pass
                    self.spam_task = None
                await self.highrise.chat("🛑 تم إيقاف السبام")
                stopped_something = True
            
            if self.is_following:
                self.is_following = False
                if self.follow_task:
                    self.follow_task.cancel()
                    try:
                        await asyncio.sleep(0.1)
                    except:
                        pass
                    self.follow_task = None
                await self.highrise.chat("🛑 تم إيقاف المتابعة")
                stopped_something = True
            
            if not stopped_something:
                await self.highrise.chat("⚠️ لا يوجد سبام أو متابعة شغالة الآن")
            return


        
       
        
       
        # 🧭 أمر follow - متابعة مستخدم أو إيقاف المتابعة
        if msg.startswith(("الحق", "اتبع", "follow")):
            if not await self.is_user_allowed(user):
                await self.highrise.send_whisper(user.id, "❌ هذا الأمر مخصص للأدمن فقط.")
                return

            parts = message.split()

            # لو كتب "follow stop" → يوقف المتابعة
            if len(parts) >= 2 and parts[1].lower() == "stop":
                if self.is_following:
                    self.is_following = False
                    if self.follow_task:
                        self.follow_task.cancel()
                        self.follow_task = None
                    await self.highrise.chat("🛑 تم إيقاف المتابعة")
                else:
                    await self.highrise.chat("⚠️ لا يوجد متابعة شغالة")
                return

            # لو مفيش مستخدم مستهدف
            if len(parts) < 2:
                await self.highrise.chat("❌ استخدم: follow @username أو follow stop")
                return

            target_username = parts[1].lstrip("@")

            # إلغاء أي متابعة سابقة
            if self.follow_task:
                self.follow_task.cancel()
                self.is_following = False

            # بدء متابعة جديدة
            self.follow_task = asyncio.create_task(self.follow_user(target_username))
            await self.highrise.chat(f"📍 بدء متابعة @{target_username}")
            return

        
        # ❤️ أوامر التفاعلات (أمر صريح فقط - يجب أن تكون الرسالة الكاملة الأمر نفسه)
        # التحقق من أن الرسالة تبدأ بالأمر وتكون كلمة واحدة أو متبوعة بـ @ أو رقم
        reaction_mapping = {
            "h": "heart", "heart": "heart",
            "w": "wave", "wave": "wave",
            "c": "clap", "clap": "clap",
            "k": "wink", "wink": "wink",
            "t": "thumbs", "thumbs": "thumbs"
        }
        
        first_word = msg.split()[0].lower()
        if first_word in reaction_mapping:
            parts = msg.split()
            
            # التأكد من أن هذا أمر صريح (ليس كلمة عادية مثل "hello" أو "can")
            # فقط إذا كانت الرسالة فقط الأمر أو الأمر + @user أو الأمر + رقم
            if len(parts) <= 3 and all(not p.isalpha() or p.lower() == first_word for i, p in enumerate(parts) if i > 0):
                command = reaction_mapping[first_word]
                target = None
                count = 10  # 💖 الافتراضي: قلوب كتيرة بدلاً من قلب واحد

                # 🧮 تحليل الرسالة
                if len(parts) >= 2:
                    # لو الثاني رقم → عدد
                    if parts[1].isdigit():
                        count = int(parts[1])
                    # لو الثاني اسم مستخدم
                    elif parts[1].startswith("@"):
                        target = parts[1][1:]
                        # لو الثالث رقم
                        if len(parts) >= 3 and parts[2].isdigit():
                            count = int(parts[2])

                # 🧍‍♂️ إرسال لشخص محدد
                if target:
                    # 🛡️ حد أقصى 300 قلب لشخص واحد
                    if count > 300:
                        await self.highrise.chat(f"⚠️ الحد الأقصى 300 {command}! تم تعديل العدد إلى 300.")
                        count = 300
                    target_user = await self.get_user_by_username(self.highrise, target)
                    if not target_user:
                        await self.highrise.send_whisper(user.id, f"❌ لم يتم العثور على المستخدم @{target}.")
                        return

                    for _ in range(count):
                        await self.highrise.react(cast(Literal["clap", "heart", "thumbs", "wave", "wink"], command), target_user.id)
                        await asyncio.sleep(0.1)

                    await self.highrise.chat(f"💖 تم إرسال {count} × {command} إلى @{target_user.username}")
                    return

                
                # 🌍 إرسال للجميع (بدون البوت نفسه) - قلب واحد لكل الناس في كل جولة
                users_response = await self.highrise.get_room_users()
                users = users_response.content
                
                # فلترة المستخدمين (حذف البوتات والبوت نفسه)
                valid_users = []
                for u, _ in users:
                    if "bot" in u.username.lower():
                        continue
                    if u.id == self.my_user_id:
                        continue
                    valid_users.append(u)
                
                # إرسال قلب واحد لكل المستخدمين في كل جولة
                for _ in range(count):  # 🔁 جولات متعددة
                    for u in valid_users:  # 👥 كل المستخدمين
                        try:
                            await self.highrise.react(cast(Literal["clap", "heart", "thumbs", "wave", "wink"], command), u.id)
                            await asyncio.sleep(0.1)
                        except Exception as e:
                            print(f"⚠️ فشل في إرسال {command} إلى {u.username}: {e}")

             
                return





    async def on_message(self, user_id: str, conversation_id: str, is_new_conversation: bool) -> None:
        try:
            response = await self.highrise.get_messages(conversation_id)

            if not (response and hasattr(response, 'messages') and len(response.messages) > 0):
                return
            
            message = response.messages[0].content.strip()
            message_lower = message.lower()
            
            # 📞 إضافة المرسل إلى قائمة الاتصال
            try:
                room_users_response = await self.highrise.get_room_users()
                room_users = room_users_response.content
                sender_user = None
                for u, _ in room_users:
                    if u.id == user_id:
                        sender_user = u
                        break
                
                if sender_user:
                    global contact_list
                    is_new_contact = sender_user.username.lower() not in contact_list
                    
                    if is_new_contact:
                        contact_list.add(sender_user.username.lower())
                        save_contact_list(contact_list)
                        print(f"📞 أضيف {sender_user.username} إلى قائمة الاتصال")
                        
                        # رسالة ترحيبية للمستخدم الجديد
                        welcome_dm = (
                            f"👋 مرحباً @{sender_user.username}!\n\n"
                            "🤖 أنا بوت الروم بذكاء اصطناعي، يمكنني مساعدتك في:\n\n"
                            "📜 اكتب 'commands' أو 'اوامر' → لعرض قائمة الأوامر\n"
                            "🤖 اكتب أي سؤال وسأرد عليك بذكاء!\n\n"
                            "💡 نصيحة: يمكنك إرسال أي سؤال وسأحاول مساعدتك!\n"
                        )
                        await self.highrise.send_message(conversation_id, welcome_dm)
                        
                        
            except Exception as e:
                print(f"⚠️ خطأ في تحديث قائمة الاتصال: {e}")
                sender_user = None

            # 🤖 تحقق من الأوامر المحددة
            # تحقق أولاً من الأوامر المحددة

            if message.startswith("say ") or message.startswith("1 "):
                try:
                    # التحقق أن المستخدم لديه صلاحيات
                    if sender_user is None:
                        return
                    if not await self.is_user_allowed(sender_user):
                        # ❌ صامت - لا نرسل أي رد
                        return

                    # استخراج النص
                    if message.startswith("say "):
                        say_text = message[4:].strip()
                    else:
                        say_text = message[2:].strip()

                    if not say_text:
                        # ❌ صامت - لا نرسل أي رد
                        return

                    # إرسال الرسالة في الروم العام لكل الناس فقط
                    await self.highrise.chat(say_text)
                    print(f"📢 @{sender_user.username} قال: {say_text}")
                    return

                except Exception as e:
                    print(f"⚠️ خطأ في أمر say: {e}")
                    return

            # 📢 أي همس من admin يرد في العام مباشرة (بدون كلمة say)
            if sender_user and message.strip():
                try:
                    if await self.is_user_allowed(sender_user):
                        # إرسال الرسالة مباشرة في العام
                        await self.highrise.chat(message.strip())
                        print(f"📢 @{sender_user.username} (همس→عام): {message.strip()}")
                    return
                except Exception as e:
                    print(f"⚠️ خطأ في إرسال الهمس للعام: {e}")
                    return



            
            
            
            

            if message.strip().lower() in ["اوامر", "commands"]:
                print(f"📋 استقبال طلب قائمة الأوامر من {sender_user.username if sender_user else 'unknown'}")
                # 🔹 القائمة العربية
                help_text_ar = (
                    "🎛️ **قائمة أوامر البوت المتكاملة** 🎛️\n"
                    "━━━━━━━━━━━━━━━━━━━\n\n"

                    "💃 **أوامر الرقص:**\n"
                    "🕺 الرقصات أو emotes → عرض جميع الرقصات\n"
                    "🔁 رقص <رقم أو اسم> → تشغيل رقصة متكررة\n"
                    "✨ رقصة <رقم أو اسم> → رقصة لمرة واحدة\n"
                    "🎲 loopall <رقصة> → رقصة جماعية للجميع\n"
                    "🛑 توقف أو stop → إيقاف الرقصة الحالية\n"
                    "📍 حفظ_منطقة → حفظ منطقة الرقص التلقائية\n\n"

                    "🌪️ **أوامر التمرجح:**\n"
                    "🌀 مرجح @user → تليبورت عشوائي للمستخدم\n"
                    "⛔ وقف @user → إيقاف التمرجح\n\n"

                    "🧭 **أوامر التنقل (Teleport):**\n"
                    "📍 add f1/f2/f3/f4 → حفظ موقعك الحالي\n"
                    "🚶 f1/f2/f3/f4 → الانتقال للموقع المحفوظ\n"
                    "🧍‍♂️ روح @user أو go @user → الذهاب لمكان مستخدم\n"
                    "🧲 هات @user → سحب المستخدم إليك\n"
                    "🔄 بدل @user أو switch @user → تبديل المكان مع مستخدم\n"
                    "⚙️ settele <rank> → حفظ موقع رتبة (vip/mod/admin/owner)\n"
                    "💫 vip / mod / admin / owner → الذهاب لمكان الرتبة\n"
                    "💫 vip/mod/admin/owner @user → نقل شخص للموقع\n\n"

                    "🧷 **أوامر التثبيت:**\n"
                    "📌 امسك @user أو fix @user → تثبيت مستخدم\n"
                    "🔓 فك @user أو unfix @user → فك التثبيت\n\n"

                    "💬 **أوامر الترحيب (Welcome):**\n"
                    "🎉 welcome → ترحيب عشوائي\n"
                    "🪄 addswm @user <رسالة> → إضافة ترحيب مخصص\n"
                    "❌ remove swm @user أو removeaddswm → حذف الترحيب\n"
                    "📜 swm list أو listswm → عرض الترحيبات\n\n"

                    "💸 **أوامر الجولد (Gold):**\n"
                    "💰 autotip <قيمة> <مدة> → توزيع تلقائي\n"
                    "⏹️ autotip stop → إيقاف التوزيع\n"
                    "📤 rtip @user <قيمة> → إرسال جولد لشخص\n"
                    "💎 tip @user <قيمة> → إرسال جولد\n"
                    "💎 محفظة أو wallet أو gold → عرض رصيدك\n\n"

                    "🎨 **أوامر الملابس:**\n"
                    "👗 changeoutfit → تغيير الملابس للزي الافتراضي\n"
                    "👕 outfit @user → عرض ملابس المستخدم\n"
                    "🧷 equip @user أو outfit_copy → نسخ ملابس المستخدم\n\n"

                    "🚫 **أوامر الإدارة (Moderation):**\n"
                    "⛔ kick @user → طرد مستخدم\n"
                    "🔨 ban @user → حظر مستخدم\n"
                    "♻️ unban @user → فك الحظر\n"
                    "🔇 mute @user → كتم المستخدم\n"
                    "🔊 unmute @user → فك الكتم\n"
                    "📋 banlist → قائمة المحظورين\n\n"

                    "⭐ **أوامر VIP:**\n"
                    "🌟 add vip @user → إضافة VIP\n"
                    "🚫 remove vip @user → إزالة VIP\n"
                    "🧹 clear vip → حذف جميع VIP\n"
                    "🔓 allow vip @user → السماح لـ VIP معين\n"
                    "🚫 remove allow vip @user → إزالة VIP المسموح\n"
                    "📜 list allow vip → عرض المسموحين\n\n"

                    "👑 **أوامر الأدمن:**\n"
                    "🧰 addowner @user → إضافة مالك\n"
                    "❌ removeowner @user → إزالة مالك\n"
                    "📜 listowners → عرض المالكين\n"
                    "👮 add_admin @user → إضافة أدمن\n"
                    "👮 remove_admin @user → إزالة أدمن\n\n"

                    "❤️ **تفاعلات سريعة:**\n"
                    "💓 h @user أو heart → قلب\n"
                    "👋 w @user أو wave → تلويحة\n"
                    "👏 c @user أو clap → تصفيق\n"
                    "😉 k @user أو wink → غمزة\n"
                    "👍 t @user أو thumbs → لايك\n"
                    "💬 invite → إرسال دعوة\n\n"

                    "🧠 **أوامر إضافية:**\n"
                    "💬 say <رسالة> أو 1 <رسالة> → البوت يتكلم في الروم\n"
                    "📢 spam <رسالة> → تكرار رسالة باستمرار\n"
                    "📍 follow @user أو اتبع → متابعة مستخدم\n"
                    "🛑 stop أو توقف → إيقاف السبام/المتابعة\n"
                    "ℹ️ info @user أو معلومات → معلومات عن مستخدم\n"
                    "👥 users → عرض الموجودين في الروم\n"
                    "🏓 ping أو بينج → اختبار الاتصال\n"
                    "⏰ uptime أو وقت_التشغيل أو runtime → مدة التشغيل\n"
                    "━━━━━━━━━━━━━━━━━━━\n"
                    "🤖 **تم تطوير البوت بواسطة:** @q.xx\n"
                )

                # 🔹 القائمة الإنجليزية
                help_text_en = (
                    "📋 **Bot Commands List:**\n"
                    "━━━━━━━━━━━━━━━━━━━\n\n"

                    "🕺 **Dance Commands:**\n"
                    "/emote → Show all dances\n"
                    "/loop <number or name> → Loop a dance\n"
                    "/dance <number or name> → Single dance\n"
                    "/random → Random dance\n"
                    "/loopall <dance> → Make everyone dance\n"
                    "/stop → Stop the current dance\n\n"

                    "👕 **Outfit Commands:**\n"
                    "equip @user → Copy user's outfit\n"
                    "equip goth/angel → Preset outfit\n"
                    "equip all → Apply bot outfit to all\n"
                    "delequip → Remove outfit\n"
                    "changeoutfit → Reset outfit\n\n"

                    "🧭 **Teleport Commands:**\n"
                    "add f1/f2/f3/f4 → Save position\n"
                    "go @user → Go to user\n"
                    "bring @user → Bring user to you\n"
                    "switch @user → Swap position\n"
                    "settele <rank> → Save rank spot\n"
                    "vip/mod/admin/owner → Go to rank spot\n"
                    "vip/mod/admin/owner @user → Move user to rank spot\n\n"

                    "🧷 **Fix Commands:**\n"
                    "fix @user → Fix user\n"
                    "unfix @user → Unfix user\n"
                    "fix all → Fix everyone\n"
                    "unfix all → Unfix everyone\n\n"

                    "💬 **Welcome Commands:**\n"
                    "/welcome → Random welcome\n"
                    "addswm @user <message> → Add custom welcome\n"
                    "removeaddswm @user → Remove welcome\n"
                    "listswm → Show welcomes\n\n"

                    "💸 **Gold Commands:**\n"
                    "autotip <amount> <delay> → Auto tipping\n"
                    "autotip stop → Stop tipping\n"
                    "rtip @user <amount> → Send gold\n"
                    "tipme <amount> → Tip the bot owner\n\n"

                    "🚫 **Moderation:**\n"
                    "kick @user → Kick user\n"
                    "ban @user → Ban user\n"
                    "unban @user → Unban user\n"
                    "mute @user → Mute user\n"
                    "unmute @user → Unmute user\n"
                    "banlist → Show banned users\n\n"

                    "⭐ **VIP Commands:**\n"
                    "add vip @user → Add VIP\n"
                    "remove vip @user → Remove VIP\n"
                    "clear vip → Clear all VIPs\n"
                    "allow vip @user → Allow VIP user\n"
                    "remove allow vip @user → Remove allowed VIP\n"
                    "list allow vip → Show allowed VIPs\n\n"

                    "👑 **Admins:**\n"
                    "add_admin @user → Add admin\n"
                    "remove_admin @user → Remove admin\n"
                    "list_admin → List admins\n\n"

                    "❤️ **Reactions:**\n"
                    "h/w/c/k/t @user → Heart, Wave, Clap, Wink, Like\n\n"

                    "🧠 **Extras:**\n"
                    "/refresh → Refresh room data\n"
                    "/refreshowner → Refresh owner\n"
                    "users → Show users\n"
                    "commands / اوامر → Show this list\n"
                    "━━━━━━━━━━━━━━━━━━━\n"
                    "🤖 **Developed by:** @q.xx\n"
                )

                # 🔹 اختيار اللغة
                help_text = help_text_ar if message_lower == "اوامر" else help_text_en

                # ✂️ تقسيم النص إلى أجزاء صغيرة لتفادي الخطأ
                try:
                    chunks = [help_text[i:i + 800] for i in range(0, len(help_text), 800)]
                    for chunk in chunks:
                        await self.highrise.send_message(conversation_id, chunk)
                except Exception as e:
                    print(f"⚠️ خطأ في إرسال قائمة الأوامر: {e}")
        except Exception as e:
            print(f"⚠️ خطأ في معالجة الرسالة: {e}")






   



        


           





    async def on_tip(self, sender: User, receiver: User, tip: CurrencyItem | Item) -> None:
        # 📞 إضافة المرسل إلى قائمة الاتصال
        try:
            global contact_list
            if sender.username.lower() not in contact_list:
                contact_list.add(sender.username.lower())
                save_contact_list(contact_list)
                print(f"📞 أضيف {sender.username} إلى قائمة الاتصال (عبر tip)")
        except Exception as e:
            print(f"⚠️ خطأ في تحديث قائمة الاتصال: {e}")
        
        if receiver.id == self.my_user_id:
            tip_amount = getattr(tip, "amount", 0)

            if tip_amount < 10:
                await self.highrise.send_whisper(sender.id, "❌ لتفعيل VIP يجب إرسال 10 جولد دفعة واحدة.")
                return

            # ❌ منع المشرفين من الحصول على VIP (هم بالفعل لديهم صلاحيات)
            try:
                room_priv = await self.highrise.get_room_privilege(sender.id)
                is_moderator = getattr(room_priv, "moderator", False)
                is_designer = getattr(room_priv, "designer", False)
                
                if is_moderator or is_designer:
                    await self.highrise.send_whisper(sender.id, "⚠️ أنت مشرف أو مصمم بالفعل، لا تحتاج VIP!")
                    return
            except Exception as e:
                print(f"⚠️ خطأ في التحقق من صلاحيات المستخدم: {e}")
            
            # تفعيل VIP إذا تم الدفع 10 جولد
            if "vip" not in self.teleport_roles:
                await self.highrise.send_whisper(sender.id, "❌ لم يتم تحديد موقع VIP بعد.")
                return

            # تفعيل VIP ونقل المستخدم
            try:
                await self.highrise.teleport(sender.id, self.teleport_roles["vip"])
            except Exception as e:
                print("❌ خطأ أثناء النقل:", e)
                await self.highrise.send_whisper(sender.id, "❌ حدث خطأ أثناء نقلك لموقع VIP.")
                return

            await self.highrise.chat(f"🎉 تم تفعيل VIP لـ {sender.username} بنجاح!")
        else:
            # تبرع عادي لشخص آخر
            tip_amount = getattr(tip, "amount", 0)
            msg = f"💸 {sender.username} أرسل {tip_amount} جولد إلى {receiver.username}."
            await self.highrise.chat(msg)
        

                
    

    async def run_bot(self, room_id: str, api_key: str) -> None:
        """🚀 نظام التشغيل المستقر - ZERO DOWNTIME"""
        from highrise.__main__ import BotDefinition, main as highrise_main
        
        backoff = 1
        connection_attempts = 0
        max_backoff = 30
        
        while True:
            try:
                connection_attempts += 1
                print(f"🔗 محاولة الاتصال #{connection_attempts}...")
                
                definitions = [BotDefinition(self, room_id, api_key)]
                await highrise_main(definitions)
                
            except asyncio.CancelledError:
                print("⚠️ تم إلغاء المهمة - إيقاف البوت...")
                raise
            except ConnectionError as e:
                print(f"❌ خطأ اتصال: {e}")
            except Exception as e:
                error_type = type(e).__name__
                print(f"❌ خطأ ({error_type}): {str(e)[:100]}")
            
            print(f"⏳ إعادة الاتصال بعد {backoff} ثانية...")
            await asyncio.sleep(backoff)
            
            backoff = min(backoff * 2, max_backoff)
            
            if connection_attempts >= 10:
                print("🔄 إعادة ضبط عداد المحاولات...")
                connection_attempts = 0
                backoff = 1


if __name__ == "__main__":
    import asyncio
    import traceback
    import signal
    import sys
    
    load_custom_welcomes()
    
    print("=" * 50)
    print("🚀 HIGHRISE BOT - ZERO DOWNTIME MODE")
    print("=" * 50)
    
    room_id = os.environ.get("HIGHRISE_ROOM_ID", "678a1472765cf0644e8bcb89")
    api_token = os.environ.get("HIGHRISE_API_TOKEN", "1b695780fdfb86aab003754aaf05f05d5f60e2549e5bef2fd2aa4bc8a5905c14")
    
    if not api_token:
        print("❌ ERROR: HIGHRISE_API_TOKEN not found!")
        sys.exit(1)
    
    print(f"📍 Room ID: {room_id}")
    print(f"🔑 API Token: {'✓ Found' if api_token else '✗ Missing'}")
    
    def signal_handler(sig, frame):
        print("\n⛔ إيقاف البوت...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    outer_retry = 0
    max_outer_retries = 100
    
    while outer_retry < max_outer_retries:
        try:
            outer_retry += 1
            print(f"\n🔄 الدورة #{outer_retry}")
            
            bot = MyBot()
            asyncio.run(bot.run_bot(room_id, api_token))
            
        except KeyboardInterrupt:
            print("\n⛔ تم إيقاف البوت بواسطة المستخدم")
            break
        except SystemExit:
            print("\n⛔ إيقاف النظام")
            break
        except Exception as e:
            error_type = type(e).__name__
            print(f"❌ خطأ خارجي ({error_type}): {str(e)[:150]}")
            
            wait_time = min(2 ** min(outer_retry, 5), 30)
            print(f"⏳ إعادة التشغيل بعد {wait_time} ثانية...")
            time.sleep(wait_time)
    
    print("🔚 انتهى تشغيل البوت")
