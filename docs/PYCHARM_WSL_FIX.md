# PyCharm WSL Configuration Fix ✅

## Problem Resolved

**Error:** 
```
Cannot run program "C:\WORK\idrissimart\.venv\Scripts\python.exe" 
(in directory "\\wsl.localhost\Ubuntu-24.04\opt\WORK\idrissimart"): 
CreateProcess error=2, The system cannot find the file specified
```

**Root Cause:**
PyCharm run configurations were set to use a hardcoded Python interpreter path instead of using the project's WSL Python interpreter.

---

## What Was Fixed

### Changed in All Run Configurations:

1. ✅ **Django_Runserver.xml**
2. ✅ **Daphne_ASGI_Server.xml**
3. ✅ **Django_Q_Cluster.xml**

### Changes Made:

**Before (Incorrect):**
```xml
<option name="SDK_HOME" value="$PROJECT_DIR$/.venv/bin/python" />
<option name="SDK_NAME" value="Python 3.11 (idrissimart)" />
<option name="IS_MODULE_SDK" value="false" />
```

**After (Correct):**
```xml
<option name="SDK_HOME" value="" />
<option name="IS_MODULE_SDK" value="true" />
```

### What This Does:

- `IS_MODULE_SDK="true"` → Use the project's configured Python interpreter
- `SDK_HOME=""` → Don't hardcode the interpreter path
- The project interpreter is already configured in `misc.xml` as WSL Python:
  ```
  3.12 WSL (Ubuntu-24.04): (/opt/WORK/idrissimart/.venv/bin/python)
  ```

---

## Compound Configurations

These configurations remain unchanged (they reference the fixed configs):
- ✅ **All Services (Compound)** - runs Daphne + Django Q
- ✅ **Full Dev Stack (Runserver + Q)** - runs Django Runserver + Django Q

---

## How to Use Now

### 1️⃣ No Restart Needed (But Recommended)
PyCharm will pick up the changes automatically, but restarting PyCharm ensures clean state.

### 2️⃣ Select and Run
- Top-right dropdown: Select any configuration
- Click green play button ▶️
- Should now work without errors!

### 3️⃣ Verify Python Interpreter
**File → Settings → Project: idrissimart → Python Interpreter**

Should show:
```
3.12 WSL (Ubuntu-24.04): (/opt/WORK/idrissimart/.venv/bin/python)
```

---

## Testing

### Quick Test:
1. Select **"Django Runserver"** from dropdown
2. Click Run ▶️
3. Should start Django server on port 8000
4. Check output - no path errors!

### Full Test:
1. Select **"All Services (Compound)"**
2. Click Run ▶️
3. Both Daphne and Django Q should start
4. No Python path errors

---

## Why This Happened

The original run configurations were created with hardcoded paths. When you:
- Work in WSL (Linux filesystem: `/opt/WORK/idrissimart/`)
- PyCharm on Windows tries to use: `C:\WORK\idrissimart\.venv\Scripts\python.exe`
- These are two different locations!

The fix makes PyCharm use the **project's interpreter** which is already correctly configured for WSL.

---

## Configuration Files Updated

```
.idea/runConfigurations/
├── Django_Runserver.xml          ✅ Fixed
├── Daphne_ASGI_Server.xml        ✅ Fixed
├── Django_Q_Cluster.xml          ✅ Fixed
├── All_Services__Compound_.xml   ✅ Uses fixed configs
└── Full_Dev_Stack__Runserver___Q_.xml  ✅ Uses fixed configs
```

---

## Additional Notes

### If You Still Have Issues:

1. **Check Python Interpreter:**
   - File → Settings → Project → Python Interpreter
   - Should be WSL Python (not Windows Python)

2. **Invalidate Caches:**
   - File → Invalidate Caches / Restart
   - Select "Invalidate and Restart"

3. **Verify Virtual Environment:**
   ```bash
   # In WSL terminal
   cd /opt/WORK/idrissimart
   source .venv/bin/activate
   which python  # Should show: /opt/WORK/idrissimart/.venv/bin/python
   ```

4. **Check WSL Access:**
   - Make sure `\\wsl.localhost\Ubuntu-24.04\` is accessible from Windows
   - Try opening the path in Windows Explorer

---

## Related Documentation

- **PYCHARM_SETUP_COMPLETE.md** - Original setup guide
- **PYCHARM_QUICKSTART.md** - Quick reference
- **PYCHARM_RUN_CONFIGURATIONS.md** - Detailed configuration docs

---

## Summary

✅ Fixed Python interpreter path issue in PyCharm run configurations  
✅ Changed from hardcoded path to project interpreter  
✅ All 3 base configurations updated  
✅ Compound configurations will work automatically  
✅ Compatible with **Poetry 2.3.2** + in-project virtual environment  
✅ Compatible with **WSL (Ubuntu-24.04)** + Python 3.12.3  
✅ No manual steps required - just run your configurations!

**Status: Ready to run! 🚀**

### Your Environment:
- 🐧 **WSL:** Ubuntu-24.04
- 📦 **Poetry:** 2.3.2
- 🐍 **Python:** 3.12.3
- 📁 **VirtualEnv:** `/opt/WORK/idrissimart/.venv/` (in-project)

---

## Date Fixed
February 16, 2026

