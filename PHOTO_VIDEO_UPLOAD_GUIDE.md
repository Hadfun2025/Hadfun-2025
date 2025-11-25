# 📸🎥 Photo & Video Upload Feature - User Guide

## Overview
Users can now upload photos and videos directly from their phones or computers when creating Community posts!

---

## ✨ What's New

### **Direct Upload from Your Device**
- 📸 **Photos**: Upload directly from your phone's camera roll or computer
- 🎥 **Videos**: Upload video files from your device
- 🌐 **URL Support**: Still supports pasting image/video URLs as before

---

## 📱 How to Use (From Phone)

### **Uploading a Photo:**

1. Go to **Community** tab
2. Click **"Create Post"**
3. Scroll to **"Add Images (Optional)"** section
4. Look for the green box: **"📸 Upload from your device"**
5. Tap the file input
6. **Choose**:
   - **"Take Photo"** → Opens camera
   - **"Photo Library"** → Browse existing photos
7. Select your photo
8. Wait for upload (shows "Uploading...")
9. ✅ See "Photo uploaded successfully!"
10. Photo appears in your post

### **Uploading a Video:**

1. Same steps as photo
2. Look for the purple box: **"🎥 Upload from your device"**
3. Tap the file input
4. **Choose**:
   - **"Take Video"** → Record new video
   - **"Video Library"** → Browse existing videos
5. Select your video
6. Wait for upload (may take longer for videos)
7. ✅ See "Video uploaded successfully!"
8. Video appears in your post

---

## 💻 How to Use (From Computer)

### **Uploading Files:**

1. Go to **Community** tab
2. Click **"Create Post"**
3. In the **"Add Images"** or **"Add Videos"** section
4. Click the **file input button**
5. Browse your computer files
6. Select photo(s) or video(s)
7. Click **"Open"**
8. Wait for upload
9. ✅ File added to your post!

---

## 📋 Technical Specs

### **Supported File Types:**

**Images:**
- JPG/JPEG
- PNG
- GIF
- WEBP
- HEIC (iPhone photos)

**Videos:**
- MP4
- MOV (iPhone/Mac videos)
- AVI

### **File Size Limits:**
- **Maximum per file**: 50MB
- **Images**: Up to 5 images per post
- **Videos**: Up to 2 videos per post

### **Upload Speed:**
- **Photos**: Usually 2-10 seconds
- **Videos**: 10-60 seconds (depends on size)

---

## 🎨 UI Features

### **Photo Upload Section (Green Box):**
```
📸 Upload from your device:
[File Upload Button]
JPG, PNG, GIF, WEBP • Max 50MB
```

### **Video Upload Section (Purple Box):**
```
🎥 Upload from your device:
[File Upload Button]
MP4, MOV, AVI • Max 50MB
```

### **Upload Progress:**
- Shows "Uploading..." while processing
- Disables upload button during upload
- Shows success toast notification when complete

---

## 🔄 Still Works: Paste URLs

**You can still paste image/video URLs:**
- Below the upload box, there's an input field
- Paste any public image/video URL
- Works for YouTube, Facebook, Vimeo, direct links
- Click "Add" button

---

## 📸 Example Use Cases

### **Perfect for:**
✅ **Match day photos** - Upload selfies from the stadium  
✅ **Team celebrations** - Share victory photos instantly  
✅ **Action shots** - Capture amazing goals on video  
✅ **Behind the scenes** - Show training or team events  
✅ **Memes & reactions** - Quick uploads from your phone  

---

## 🔒 Storage & Security

### **Where Files Are Stored:**
- Files stored on your server in `/backend/uploads/`
- Each file gets a unique name (prevents conflicts)
- Files accessible via `/uploads/[filename]` URL

### **File Validation:**
- Only allowed file types accepted
- Maximum file size enforced (50MB)
- Malicious files rejected automatically

### **Privacy:**
- Files are public (anyone can view)
- No personal data stored in filenames
- Files associated with your posts only

---

## ⚠️ Limitations & Tips

### **Current Limitations:**
- Files stored locally (not cloud storage yet)
- No automatic image compression
- 50MB max per file

### **Tips for Best Experience:**

**For Photos:**
- Use phone camera at normal quality (not RAW)
- Compress large images before upload if possible
- Portrait photos work best for posts

**For Videos:**
- Keep videos under 30 seconds for faster upload
- Record at 720p or 1080p (not 4K)
- Trim videos before upload to save time

**General:**
- Upload over WiFi for faster speeds
- Wait for "Upload successful" before posting
- Check file size if upload fails

---

## 🐛 Troubleshooting

### **"File too large" error:**
→ Your file exceeds 50MB. Compress or trim it.

### **"File type not allowed" error:**
→ Use supported formats (JPG, PNG, MP4, MOV, etc.)

### **Upload stuck at "Uploading...":**
→ Check your internet connection
→ Try a smaller file
→ Refresh page and try again

### **File uploaded but not showing:**
→ Refresh the page
→ Check if you clicked "Share Post"
→ Contact support if issue persists

---

## 🎯 Quick Reference

| Feature | Limit | File Types |
|---------|-------|------------|
| **Photos** | 5 per post | JPG, PNG, GIF, WEBP |
| **Videos** | 2 per post | MP4, MOV, AVI |
| **File Size** | 50MB max | All types |
| **Upload Location** | Green (photos), Purple (videos) | - |

---

## 🚀 Getting Started

### **Try It Now:**

1. **Open your phone**
2. **Go to hadfun.co.uk** (after deployment)
3. **Tap Community tab**
4. **Create a new post**
5. **Scroll to "Add Images"**
6. **Tap the upload button**
7. **Take a selfie or select a photo**
8. **Wait for upload**
9. **Add caption and share!**

---

## 📱 Mobile-Optimized

The upload feature is fully optimized for mobile:
- ✅ Native camera integration
- ✅ Photo library access
- ✅ Touch-friendly buttons
- ✅ Responsive design
- ✅ Fast upload feedback

---

## 🎉 Benefits

### **For Users:**
✅ **No more URL hunting** - Upload directly  
✅ **Easy mobile sharing** - Tap and upload  
✅ **Rich content** - Share authentic moments  
✅ **Professional look** - High-quality posts  

### **For Community:**
✅ **More engagement** - Visual content  
✅ **Authentic connections** - Real photos/videos  
✅ **Active community** - Easy to participate  
✅ **Better experience** - Modern social features  

---

## 🔜 Future Enhancements

**Planned improvements:**
- Cloud storage integration (AWS S3/Cloudinary)
- Automatic image compression
- Image editing (crop, rotate, filters)
- Multiple file uploads at once
- Drag & drop support
- Progress bar for uploads

---

## 📞 Need Help?

If you encounter any issues:
1. Check this guide for troubleshooting
2. Try refreshing the page
3. Make sure file meets requirements
4. Contact support if problem persists

---

## ✅ Summary

**NEW: Upload photos/videos from your phone or computer!**

**Quick Steps:**
1. Tap Community → Create Post
2. Find green (photos) or purple (videos) upload box
3. Tap file input → Select file
4. Wait for "Upload successful"
5. Write caption → Share post!

**It's that easy! Start sharing your football moments today!** ⚽📸
