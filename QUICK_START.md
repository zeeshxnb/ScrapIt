# Quick Start Guide - Enhanced Gmail Sync

## 🚀 Starting the Server

### Option 1: Regular Start (with logs)
```bash
cd backend
python start.py
```

### Option 2: Quiet Start (minimal output)
```bash
cd backend
python start_quiet.py
```

## 🔐 Authentication

1. **Test server is running:**
   ```bash
   python test_server.py
   ```

2. **Authenticate with Gmail:**
   ```bash
   python test_auth.py
   ```
   - This will open your browser
   - Login with Gmail
   - Copy the code from callback URL
   - Paste it back in terminal

## 📧 Using the Enhanced Gmail Sync

### 1. Sync ALL Emails (No Limits)
```bash
curl -X POST "http://localhost:8000/gmail/full-sync" \
  -H "Content-Type: application/json" \
  -d '{"batch_size": 100}'
```

### 2. Incremental Sync (New emails only)
```bash
curl -X POST "http://localhost:8000/gmail/sync" \
  -H "Content-Type: application/json" \
  -d '{"incremental": true, "batch_size": 50}'
```

### 3. Check Gmail Folders
```bash
curl -X GET "http://localhost:8000/gmail/folders"
```

### 4. Get Sync Statistics
```bash
curl -X GET "http://localhost:8000/gmail/stats"
```

### 5. Sync Specific Folders
```bash
curl -X POST "http://localhost:8000/gmail/sync-folders" \
  -H "Content-Type: application/json" \
  -d '{
    "labels": ["INBOX", "SENT"],
    "batch_size": 100,
    "incremental": false
  }'
```

## 🎯 Key Features

- ✅ **No email limits** - syncs ALL your emails
- ✅ **All folders** - inbox, sent, drafts, spam, trash, custom labels
- ✅ **Batch processing** - handles large volumes efficiently
- ✅ **Progress tracking** - see sync progress in real-time
- ✅ **Flexible targeting** - sync all or specific folders

## 🔧 Troubleshooting

### Server not starting?
- Check if port 8000 is available
- Make sure you're in the backend directory
- Check your .env file has required variables

### Authentication failing?
- Verify GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env
- Make sure redirect URI is configured in Google Console
- Try the test_auth.py script

### Gmail sync not working?
- Ensure you're authenticated first
- Check Gmail API is enabled in Google Console
- Verify your Gmail account has emails to sync

## 📊 Monitoring Progress

The enhanced sync provides detailed progress information:

```json
{
  "success": true,
  "message": "Sync completed: 1,247 new, 23 updated (processed in 12 batches)",
  "new_emails": 1247,
  "updated_emails": 23,
  "total_batches": 12,
  "all_folders_synced": true,
  "no_limits_applied": true
}
```

## 🎉 Ready to Go!

Your Gmail sync now has unlimited access to ALL your emails from ALL folders. Start with authentication, then run a full sync to get everything!