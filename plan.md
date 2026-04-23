## Comprehensive Fix Plan: Admin Access & Watermark Authentication

**Overall Goal:** Resolve critical Django startup block (missing storage settings), admin access block (FileDescriptor error), and underlying watermark authentication failures caused by Azure credential mismatches and hardcoded configuration.

---

## Phase -1: CRITICAL - Django Storage Settings Configuration (STARTUP BLOCKER)

**TL;DR:** Add missing Django storage settings that cause `AttributeError: 'Settings' object has no attribute 'PRIVATE_STORAGE_ROOT'` during URL loading. This prevents Django from starting entirely and must be fixed FIRST before any other work can proceed.

### Phase -1 Root Cause

**Error Location:** `dataroom/views.py` line 1100 and other watermark-related imports

**Investigation Findings:**
- Django attempts to import `dataroom/views.py` during URL configuration loading
- `dataroom/views.py` contains FileSystemStorage instantiations that reference missing Django settings
- Storage settings are undefined in `dms/settings.py`, causing AttributeError on import
- This blocks Django startup entirely before the dev server can start

**Missing Settings:**
- `PRIVATE_STORAGE_ROOT` - Directory for user uploads (dataroom logos, etc.)
- `PREVIEW_WATERMARK_ROOT` - Directory for watermark preview files
- `TEMP_WATERMARK_ROOT` - Directory for temporary watermark processing files

### Phase -1 Steps

1. **Add Storage Settings to `dms/settings.py`**
   - Add missing settings with configurable paths
   - Settings should use environment variables with sensible defaults
   - Create directories if they don't exist (auto-creation on startup)

2. **Update `pdf_watermarking.py` Hardcoded Paths**
   - Replace hardcoded `/home/cdms_backend/` paths with Django settings references
   - Use `TEMP_WATERMARK_ROOT` for temporary file storage
   - Use `PREVIEW_WATERMARK_ROOT` for preview files

3. **Verify Django Startup**
   - Ensure `python manage.py runserver` starts without AttributeError
   - Verify no Django startup errors during URL loading
   - Check all storage directories are created automatically

### Phase -1 Files to Modify

| File | Changes | Priority |
|------|---------|----------|
| `dms/settings.py` | Add PRIVATE_STORAGE_ROOT, PREVIEW_WATERMARK_ROOT, TEMP_WATERMARK_ROOT settings with auto-directory creation | CRITICAL |
| `watermark/pdf_watermarking.py` | Replace hardcoded `/home/cdms_backend/` paths with Django settings references | CRITICAL |
| `dataroom/views.py` | Verify storage settings are properly referenced (lines ~1100) | HIGH |

### Phase -1 Example Configuration

```python
# dms/settings.py
import os

# Storage directories for watermarking and uploads
BASE_STORAGE_DIR = os.path.join(BASE_DIR, 'storage')

PRIVATE_STORAGE_ROOT = os.getenv(
    'PRIVATE_STORAGE_ROOT',
    os.path.join(BASE_STORAGE_DIR, 'private')
)

PREVIEW_WATERMARK_ROOT = os.getenv(
    'PREVIEW_WATERMARK_ROOT',
    os.path.join(BASE_STORAGE_DIR, 'watermark_previews')
)

TEMP_WATERMARK_ROOT = os.getenv(
    'TEMP_WATERMARK_ROOT',
    os.path.join(BASE_STORAGE_DIR, 'temp_watermarks')
)

# Auto-create storage directories on startup
for storage_dir in [PRIVATE_STORAGE_ROOT, PREVIEW_WATERMARK_ROOT, TEMP_WATERMARK_ROOT]:
    os.makedirs(storage_dir, exist_ok=True)
```

### Phase -1 Verification

1. **Django Startup:**
   - `python manage.py runserver 8000` should start without errors
   - No AttributeError about missing storage settings
   - Storage directories created in `storage/` subdirectory

2. **Settings Verification:**
   - `python manage.py shell` then `from django.conf import settings; print(settings.PRIVATE_STORAGE_ROOT)` should return valid path
   - All three storage settings accessible
   - All directories exist after Django startup

3. **No Import Errors:**
   - `from dataroom import views` should work without error
   - URL loading (`urlpatterns`) should succeed
   - Admin panel should be accessible without import errors

### Phase -1 Critical Details

**Why This Blocks Everything:**
- Django's URL configuration (`urls.py`) imports view modules
- View modules instantiate storage classes that reference settings
- If settings are missing, import fails
- Django never finishes initialization
- Dev server cannot start
- Admin panel cannot load
- NO OTHER WORK CAN PROCEED

**Impact:**
- Phase 1 (FileDescriptor fix) cannot be tested without Django running
- Phase 2 (Azure auth fix) cannot be tested without Django running
- All watermark operations blocked
- Must resolve before any testing

---

## Phase 0: Environment Setup & Settings Verification

**TL;DR:** Configure initial environment with all required Django settings and verify baseline functionality.

### Phase 0 Steps

1. **Verify Phase -1 Completion**
   - Confirm Django starts without storage settings errors
   - All storage directories created
   - Settings accessible in Django shell

2. **Environment Configuration**
   - `.env` file setup with base configuration (not credentials yet)
   - Python environment verification
   - Database migration verification

3. **Django Admin Verification**
   - Admin panel accessible at `/projectName/admin/`
   - Database models visible in admin
   - No startup errors in console

### Phase 0 Dependencies
- **Must complete Phase -1 FIRST** - Django must start before any verification can occur

---

## Phase 1: CRITICAL - FileDescriptor AttributeError (Admin Access Blocker)

**TL;DR:** Fix the missing `__init__` method in FileDescriptor class that causes "'FileDescriptor' object has no attribute 'field'" error when accessing Django admin file fields. This must be completed first to unblock admin investigation and testing of watermark fixes.

### Phase 1 Steps
1. **Add `__init__` method to FileDescriptor class** - Insert missing constructor after line 207 in `data_documents/models.py` to store field reference
2. **Test admin access** - Verify admin URL loads without AttributeError
3. **Test file field operations** - Verify file upload/download works in admin interface

### Phase 1 Files
- **`C:\Project\cdms_backend\cdms2\data_documents\models.py`** (lines 193-263)
  - Add `__init__` method after docstring at line 207
  - Must store `self.field = field` to resolve AttributeError in `__set__` (line 262) and `__get__` (lines 233, 241, 251-252)

### Phase 1 Verification
1. Start Django dev server: `python manage.py runserver 8000`
2. Access: `http://127.0.0.1:8000/projectName/admin/data_documents/dataroomfolder/` (should load without error)
3. Verify file upload/download operations work
4. No FileDescriptor AttributeError in console output

### Phase 1 Critical Details
- **Error Location:** Line 262 in `__set__` method: `instance.__dict__[self.field.attname] = value`
- **Root Cause:** FileDescriptor inherits from DeferredAttribute but never calls/implements proper initialization
- **Field Reference:** Passed during instantiation at line 355 in `contribute_to_class()` but never stored
- **Affects:** Multiple methods using `self.field` at lines 233, 241, 251-252

### Phase 1 Dependencies
- **Blocker:** Must complete Phase 1 before any watermark testing can occur (admin inaccessible without this fix)

---

## Phase 2: Watermark Azure Authentication Fix

**TL;DR:** Resolve "AuthenticationFailedServer failed to authenticate the request" errors by:
- Moving hardcoded Azure credentials to environment variables
- Consolidating conflicting storage account references (docullystorage vs newdocullystorage)
- Fixing SAS token generation logic and credential mismatches
- Implementing proper credential hierarchy (env vars → fallback defaults)

### Phase 2 Root Cause Analysis

**Investigation Findings:**
- **Hardcoded Credentials:** Azure storage connection strings and credentials embedded in source code
- **Mixed Storage Accounts:** Two different Azure storage accounts referenced in watermark code:
  - `docullystorage` (account key: `***`) 
  - `newdocullystorage` (account key: `***`)
- **SAS Token Mismatch:** Generated tokens reference one account but actual storage calls use different account
- **Missing Configuration:** No environment-based credential management for production deployments

### Phase 2 Steps

#### Step 1: Identify All Credential References (Investigation)
Locate all hardcoded credentials and storage account references:

**Files to Audit:**
- `dms/settings.py` - Django/Azure configuration
- `dms/custom_azure.py` - Custom Azure storage backend
- `notifications/views.py` - Watermark notification handling (line-by-line audit needed)
- `watermark/` module - All watermark generation/application code
- Any files importing from above modules

**Search Patterns:**
- Hardcoded account names (docullystorage, newdocullystorage)
- Hardcoded connection strings or account keys
- Hardcoded SAS URIs or tokens

#### Step 2: Create Unified Environment Configuration
Create `.env` file template with consolidated Azure credentials:

```
# Azure Storage - Unified Configuration
AZURE_STORAGE_ACCOUNT_NAME=newdocullystorage  # Primary account for all operations
AZURE_STORAGE_ACCOUNT_KEY=<primary-key>
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=newdocullystorage;AccountKey=<primary-key>;EndpointSuffix=core.windows.net

# Legacy Account (if migration needed)
AZURE_STORAGE_LEGACY_ACCOUNT_NAME=docullystorage
AZURE_STORAGE_LEGACY_ACCOUNT_KEY=<legacy-key>
```

**Files to Modify:**
- Create/update `C:\Project\cdms_backend\cdms2\.env` with template above
- Update `.gitignore` to exclude `.env` file (verify already excluded)

#### Step 3: Consolidate Storage Account References
Standardize on single primary storage account (`newdocullystorage`) for all new operations:

**Files to Update:**

1. **`dms/settings.py`**
   - Replace hardcoded `docullystorage` references with `AZURE_STORAGE_ACCOUNT_NAME` env var
   - Update Azure backend configuration to use `newdocullystorage` as primary
   - Add fallback logic: `os.getenv('AZURE_STORAGE_ACCOUNT_NAME', 'newdocullystorage')`

2. **`dms/custom_azure.py` (Azure Storage Backend)**
   - Update connection string initialization to use env var: `os.getenv('AZURE_STORAGE_CONNECTION_STRING')`
   - Fix SAS token generation to use consolidated account
   - Ensure account name in token matches actual storage operations
   - Add validation: verify token account matches operation account

3. **`watermark/pdf_watermarking.py` (CRITICAL - Exact Issue Identified)**
   
   **CRITICAL: Line 170 - Hardcoded Credential Mismatch**
   ```python
   # CURRENT (Line 170) - BROKEN:
   block_blob_service = BlockBlobService(account_name='docullystorage', account_key='vyjT1gd5pbx4rlFFo+Q+5z5c3lZBENmF3yBFP9ZjohlWO4y1f1jic39sHatukVPL8dqP4OERbWFQ+AStzUWTnQ==')
   
   # REASON FOR FAILURE:
   # - Credentials reference 'docullystorage' account
   # - SAS URL in settings.py is signed for 'newdocullystorage'
   # - Authentication fails with "Signature did not match" error
   # - Error shows: "/blob/newdocullystorage/docullycontainer" but credentials are for docullystorage
   ```
   
   **Required Changes:**
   - Line 170: Remove hardcoded BlockBlobService instantiation
   - Replace with environment-based credentials using new azure_utils.py helper
   - New code structure:
     ```python
     from dms.azure_utils import get_azure_blob_client
     
     # Inside GeneratePDF function (around line 170):
     blob_client = get_azure_blob_client()
     ```
   - Lines 176-179: Update blob upload calls to use new blob_client
   - Current upload logic:
     ```python
     # Line 176-179 (approx):
     block_blob_service.create_blob_from_path(
         container_name='docullycontainer',
         blob_name=blob_name,
         file_path=local_file_path
     )
     ```
   - Update to use unified client that respects account from env vars
   
   **File Paths to Update:**
   - Line 170: Azure client initialization
   - Lines 176-179: Blob upload operations (GeneratePDF function)
   - Any local staging paths like `/home/cdms_backend/` (update to use Django settings or temp directory)
   - Add error handling for Azure authentication failures:
     ```python
     try:
         blob_client.upload_blob(...)
     except Exception as e:
         # Log specific error about account mismatch vs auth failure
         logger.error(f"Azure blob upload failed. Check AZURE_STORAGE_ACCOUNT_NAME matches SAS URL account: {str(e)}")
     ```

4. **Watermark Module Files** (all files in watermark directory)
   - Search for any hardcoded storage references
   - Replace with env-var based configuration
   - Update SAS URI generation to use primary account

5. **`notifications/views.py`** (Watermark operations, lines ~TBD)
   - Audit all watermark-related Azure calls
   - Verify using consolidated credentials
   - Update SAS token generation logic
   - Add debug logging for credential/account mismatch detection

#### Step 4: Fix SAS Token Generation Logic

**Issue:** Token generated from one account but applied to another

**Solution:**
- Create centralized SAS token generation function:
  ```
  Location: dms/azure_utils.py (new file)
  Function: generate_watermark_sas_token(blob_name)
  - Uses AZURE_STORAGE_ACCOUNT_NAME
  - Uses AZURE_STORAGE_ACCOUNT_KEY
  - Generates token scoped to blob_name with specific permissions
  - Returns full SAS URI with correct account name
  ```

- Update all watermark code to use this function instead of inline token generation
- Verify token account name matches AZURE_STORAGE_ACCOUNT_NAME

#### Step 5: Implement Credential Fallback Hierarchy

Create consistent credential loading across codebase:

**Priority Order:**
1. Environment variables (`AZURE_STORAGE_*`)
2. `.env` file (if loaded by Django)
3. Hardcoded defaults (logged as warnings for production)
4. Exception on missing credentials (fail-fast with clear error message)

**Implementation:** Add utility function in `dms/azure_utils.py`:
```
get_azure_credentials():
  - Check env vars first
  - Fall back to .env if using python-dotenv
  - Log warnings for hardcoded fallbacks in production
  - Raise clear exception if all missing
```

### Phase 2 Files to Modify

| File | Changes | Lines |
|------|---------|-------|
| `dms/settings.py` | Use env vars for Azure config, consolidate to newdocullystorage | TBD (audit needed) |
| `dms/custom_azure.py` | Update connection string, SAS token generation, account consolidation | TBD (audit needed) |
| `dms/azure_utils.py` | **NEW** - Centralized credential management and SAS token generation | N/A |
| **`watermark/pdf_watermarking.py`** | **CRITICAL** - Remove hardcoded credentials (line 170), update blob upload calls (lines 176-179), use new azure_utils helper | 170, 176-179 |
| `notifications/views.py` | Update watermark operations to use consolidated credentials | TBD (audit needed) |
| `watermark/*` | Update all watermark files for credential consolidation | TBD (per file) |
| `.env` | **NEW** - Configuration template with consolidated credentials | N/A |
| `.gitignore` | Verify .env is excluded (should already be) | Verify only |

### Phase 2 Verification

1. **Credential Loading:**
   - Start dev server with `.env` containing credentials
   - Verify no hardcoded credentials in console output
   - Check logs show env-var loading, not defaults

2. **Storage Account Consolidation:**
   - Trace all Azure calls: should reference `newdocullystorage` account
   - No calls to `docullystorage` in new code paths
   - Mixed account references should log warnings if unavoidable

3. **SAS Token Generation:**
   - Generate test watermark in admin
   - Verify SAS token account matches AZURE_STORAGE_ACCOUNT_NAME
   - Test token works without "AuthenticationFailed" errors
   - Verify watermark applies successfully to document

4. **Watermark Operations:**
   - Upload document to admin → apply watermark → should succeed
   - Check watermarked document downloads correctly
   - Verify no auth errors in server logs
   - Test with different document types (PDF, DOCX, etc.)

5. **Error Handling:**
   - Stop dev server, remove credentials from `.env`
   - Restart should fail with clear error about missing credentials (not auth mismatch)
   - Verify helpful error message guides credential setup

### Phase 2 Critical Details

**Azure Auth Error Root Causes:**
1. **SAS Account Mismatch:** Token created with account A, but blob call uses account B
2. **Expired/Invalid Token:** Token generation uses wrong account key
3. **Hardcoded Wrong Credentials:** Wrong account key embedded in code
4. **Missing Credentials:** No credentials provided for blob operation
5. **Permission Mismatch:** Token permissions don't match required blob operations

**Why This Happens:**
- Multiple developers → multiple storage accounts (docullystorage, newdocullystorage)
- Gradual migration between accounts left mixed references
- Hardcoded values prevent proper credential rotation
- No centralized credential management

**Migration Strategy:**
- Phase 2 implements centralized management via `.env`
- All new operations use `newdocullystorage` (newdocullystorage)
- Legacy docullystorage references marked for deprecation (logged as warnings)
- SAS token generation ensures account consistency

**SPECIFIC BUG IN pdf_watermarking.py (Line 170):**
- **Problem:** BlockBlobService hardcoded with `docullystorage` credentials
- **Impact:** Credentials for wrong account used in GeneratePDF function
- **Evidence:** Error shows SAS URL references `/blob/newdocullystorage/docullycontainer` but credentials are for `docullystorage`
- **Result:** Authentication fails with "Signature did not match" because:
  - SAS URL was signed for `newdocullystorage` account
  - BlockBlobService instantiated with `docullystorage` account key
  - Azure rejects mismatched credential/URL combination
- **Fix:** Replace line 170 BlockBlobService with environment-based credential from azure_utils.py helper function
- **Scope:** Also affects lines 176-179 (blob upload calls in GeneratePDF) - must use new blob_client

---

## Execution Order & Dependencies

### Dependency Chain:
```
Phase 1: FileDescriptor Fix (CRITICAL BLOCKER)
  ↓
  (Must complete before Phase 2 testing can begin)
  ↓
Phase 2: Azure Authentication Fix
  ├─ Step 1: Audit & document all credential references
  ├─ Step 2: Create .env configuration
  ├─ Step 3: Consolidate storage accounts (newdocullystorage primary)
  ├─ Step 4: Centralize SAS token generation (azure_utils.py)
  ├─ Step 5: Implement credential fallback hierarchy
  └─ Verify: Test end-to-end watermark generation
```

### Why Phase 1 Blocks Phase 2:
- Admin interface is primary tool for watermark testing
- FileDescriptor error prevents admin access
- Cannot test Phase 2 fixes without admin panel working
- Phase 1 fix has zero dependencies and takes ~5 min

---

## Success Criteria

### Phase 1 Success:
- [ ] Admin page loads without AttributeError
- [ ] File fields display correctly in admin forms
- [ ] File upload/download operations work
- [ ] No FileDescriptor errors in console

### Phase 2 Success:
- [ ] No "AuthenticationFailed" errors when applying watermarks
- [ ] Watermark SAS tokens generated with correct account
- [ ] All hardcoded credentials moved to `.env` (or logged as warnings)
- [ ] Storage account references consolidated to `newdocullystorage`
- [ ] End-to-end watermark test passes (upload → apply → download)
- [ ] Production deployment works with environment-based credentials
- [ ] Clear error messages if credentials missing
