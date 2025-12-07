# Overview

Highrise bot application (Python-based) with ZERO DOWNTIME that manages automated dancing in room zones, features an advanced Dashboard Pro for real-time bot control with custom outfit creation, and supports comprehensive command execution through both in-game chat and web interface.

# User Preferences

Preferred communication style: Simple, everyday language (Arabic).
Goal: ZERO DOWNTIME - NO DISCONNECTIONS AT ALL
Feature Request: Custom outfit creation system - users create and apply outfits by selecting items by ID directly from Dashboard

**Latest Implementation (Dec 02, 2025 - PRODUCTION READY - FULLY TESTED):**
- ⚡ **ZERO DOWNTIME MODE**: Production Hardened ✓
  - Heartbeat: 30 seconds with 10s timeout (was 5s) - prevents false disconnects
  - Reconnect: 0.5s instant reconnection with retry counter
  - Connection stability: Failure tracking (3-strike system)
  - Error Resilience: Graceful degradation on all loops
  - Loop Stability: Try-except with async.CancelledError handling
  - Dashboard Server: Runs in daemon thread (separate from bot thread)
  - Clothing Items: Direct ID support + dropdown + custom outfit creator ✓ (FIXED)
- 🌐 **Dashboard Pro Advanced Features**:
  - Port 5000 - Real-time control interface
  - Live outfit changing by ID - NO restart needed
  - Command execution from web interface
  - Quick command buttons (dance enable/disable, ping, uptime, wallet)
  - Real-time metrics display (uptime, memory, request count)
  - **🎨 NEW: Custom Outfit Creator**:
    - Browse 1000+ clothing items from database
    - Checkboxes to select multiple items
    - Save custom outfits with custom names (e.g., "tilj")
    - Apply created outfits immediately with no restart
- 📡 **BotController Integration System**:
  - `dashboard_integration_loop()` - checks for pending outfit/command changes every second
  - API endpoints: `/api/outfit/apply`, `/api/command/execute`, `/api/outfits`, `/api/items`, `/api/outfit/create`
  - Two-way communication: Dashboard → Bot via BotController
  - Outfit system: JSON-based storage with custom name-based indexing
- **Web Framework**: Flask - Lightweight framework (chosen for compatibility with highrise-bot-sdk)
- **Emotes Management**: Extracted to separate `emotes.py` file (179 emotes)

# System Architecture

## Core Bot Framework

The bot is built upon the official `highrise-bot-sdk` (v24.1.0), extending its `BaseBot` class to manage events, user interactions, and room logistics.

## Configuration and State Management

JSON-based system for managing bot configurations and states:
- **User Roles & Permissions**: `admins.json`, `vip_users.json`, `allowed_vip_users.json`, `allowed_swms.json`, `owners.json`, `banned_users.json`
- **Feature Settings**: `room_commands.json`, `settings.json`, `teleports.json`
- **Customizations**: `special_welcomes.json`, `outfits.json`
- **State Tracking**: `contact_list.json`, `dance_settings.json`
- **Items Database**: `outfit_items_database.json` (1000+ items for outfit creation)

## Dashboard & API Integration (ADVANCED)

**webserver.py** - FastAPI server running on port 5000:
- `BotController` class manages outfit/command queuing
- Dashboard HTML interface with Arabic RTL support
- Real-time metrics: uptime, memory usage, request counts
- **API Endpoints**:
  - `GET /` - Dashboard main interface
  - `POST /api/outfit/apply` - Apply existing outfit by ID
  - `POST /api/command/execute` - Queue command for execution
  - `POST /api/outfit/create` - Create new outfit from selected items
  - `GET /api/outfits` - Retrieve all saved outfits
  - `GET /api/items` - Retrieve available items for outfit creation (1000+ items)
  - `GET /health` - Health check with metrics
  - `GET /api/status` - Bot status information
  - `GET /api/metrics` - Performance metrics

**dashboard_integration_loop()** - Bot integration loop:
- Runs every 1 second to check BotController queues
- Applies pending outfits using `highrise.set_outfit()`
- Executes queued commands via `on_chat()` method
- Enables real-time outfit/command management without restart

## Custom Outfit Creator Workflow

1. **User selects items** from Dashboard checklist (100 items available for quick browsing)
2. **User enters outfit name** (e.g., "tilj", "cool_style", etc.)
3. **User clicks "Create Outfit"** → `/api/outfit/create` API call
4. **Outfit saved** to `outfits.json` with custom name as key
5. **Outfit appears** in outfit dropdown
6. **User can apply outfit** immediately - no restart needed
7. **Bot wears outfit** in Highrise room instantly via dashboard_integration_loop

## Connection Stability & Uptime (ZERO DOWNTIME FOCUS)

Ultra-aggressive connection strategy:
- **Aggressive Heartbeat**: Every 30 seconds with 5-second timeout
- **Instant Reconnection**: 0.5-second reconnect delay (no exponential backoff)
- **Smart Caching**: 2-second cache on room user queries with 8-second timeouts
- **Dashboard Keep-Alive**: FastAPI server provides continuous health monitoring
- **Connection Resilience**: Multiple check loops ensure bot presence

## Multi-Language Support

`settings.json` includes `welcome_lang` parameter - supports Arabic content

## Position and Teleportation System

- `bot_position.json`: Bot spawn coordinates and facing direction
- `teleports.json`: Named, role-based teleport destinations
- `room_commands.json`: Text command to position mappings

## Customization System

- `special_welcomes.json`: Custom welcome messages for individual users
- `outfits.json`: Bot appearance configuration with ID/name-based indexing

## Key Features and Commands

### Owner Commands
- `addowner`, `removeowner`, `listowners`: Manage bot owners
- `add @username mod`: Add room moderator
- `rem @username mod`: Remove room moderator

### Admin/Mod Commands
- `add @username des`: Add designer (Owner/Mod only)
- `rem @username des`: Remove designer (Owner/Mod only)
- `/modlist`: View tracked mod members (Owner/Mod only)
- `/roommods`, `admin`, `ادمن`: View active mods in room (Public)
- `invite [message]`: Send invitations
- `say <message>`: Bot speaks in room
- `spam <message>`, `stop`: Message spamming control
- `follow @username`, `الحق @username`: Bot follows user
- `equip @username`, `equip [number]`: Manage outfits
- `tip @username amount`: Distribute gold
- `dance enable`, `dance disable`: Auto-dancing control

### Public Commands
- `ping`, `بينج`: Bot response time
- `uptime`, `وقت_التشغيل`: Operational duration
- `info @username`: User information

### Dashboard Features
- **Outfit Management**: 
  - Browse saved outfits
  - Apply by ID with one click
  - Create custom outfits by selecting items
  - No restart required
- **Command Execution**: 
  - Text input for any command
  - Quick buttons for common commands
  - Real-time execution
- **Real-time Metrics**:
  - Live uptime display
  - Memory usage monitoring
  - Request count tracking

### Automatic Features
- **Contact List Tracking**: DM and tipping track users
- **API Rate Limiting & Caching**: Reduces API load
- **Startup Dance**: Visual readiness confirmation
- **Dashboard Integration**: Real-time outfit/command polling

# External Dependencies

- **highrise-bot-sdk** (v24.1.0): Official Highrise SDK
- **FastAPI**: High-performance async web framework
- **Uvicorn**: ASGI server for FastAPI
- **psutil**: System monitoring (memory, CPU)
- **python-dotenv**: Environment variable management
- **requests**: HTTP client library
- **aiohttp**: Async HTTP client/server

# Architecture Decisions

- **Flask instead of FastAPI**: Flask is stable and compatible with highrise-bot-sdk (v24.1.0) - no dependency conflicts
- **JSON Files over Database**: Simple, portable, sufficient for state management
- **Dashboard Integration Loop**: Real-time polling (1-second) for instant changes
- **BotController as Message Queue**: Decouples Dashboard from Bot
- **Port 5000**: Replit compatibility and web preview access
- **Custom Outfit Creator**: User-friendly item selection for outfit creation
- **Item Database**: Pre-loaded 1000+ items for flexible outfit creation
- **Two-Method Outfit Application**: (1) Saved outfits from dropdown, (2) Direct item ID input for single items

# Latest Updates (Dec 02, 2025 - PRODUCTION HARDENED)

## Stability Fixes:
1. **Heartbeat Timeout**: 5s → 10s (prevents false disconnects)
2. **Error Tracking**: 3-strike failure counter for all loops
3. **Thread Safety**: Dashboard runs in separate daemon thread
4. **Graceful Degradation**: All loops handle errors without crashing
5. **CancelledError Handling**: Proper async task cleanup

## Dashboard Features:
1. **Dashboard Pro**: Advanced HTML with RTL Arabic support
2. **Outfit Methods**: 
   - Method 1️⃣: Saved outfits from dropdown
   - Method 2️⃣: Direct item ID input (e.g., "body-flesh")
3. **Custom Outfit Creator**: Select items + create custom named outfits
4. **API Endpoints**: `/api/outfit/apply`, `/api/outfit/apply-item`, `/api/outfit/create`, `/api/command/execute`
5. **Real-time Metrics**: Live uptime, memory, request count
6. **Quick Buttons**: Dance enable/disable, ping, uptime, wallet

## Connection Resilience:
- Heartbeat: Every 30 seconds (10s timeout)
- Reconnect: 0.5s instant retry with exponential backoff after failures
- Error Recovery: 5 consecutive errors = reinitialize bot
- Keep-Alive: Heartbeat checks connection stability
- Dashboard: Runs async without blocking bot connection
