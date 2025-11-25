# Video Support Guide for HadFun Community

## Supported Video Platforms

### ✅ Embedded Players (Play Directly in Feed)

1. **YouTube**
   - Format: `https://www.youtube.com/watch?v=...` or `https://youtu.be/...`
   - Example: Andrew Henderson freestyle videos
   - **Works perfectly with embedded player**

2. **Vimeo**
   - Format: `https://vimeo.com/123456789`
   - Professional quality videos
   - **Works perfectly with embedded player**

3. **Direct Video Files**
   - Format: `.mp4`, `.webm`, `.ogg`
   - Direct links to video files
   - **Works with HTML5 player**

### 🔗 Link-Based (Opens on Original Platform)

4. **Facebook Videos & Reels**
   - Format: `https://www.facebook.com/reel/...` or `https://www.facebook.com/videos/...`
   - Shows as blue "View on Facebook" button
   - Opens video on Facebook in new tab
   - **Why?** Facebook restricts embedding for privacy/login reasons

---

## How It Works for Users

### Posting a Video:

1. Go to Community tab
2. In the "Add Videos" section, paste your video URL
3. Click "Add" button
4. Write your text content
5. Click "Share Post"

### Viewing Videos:

**YouTube/Vimeo Videos:**
- Play directly in the feed
- Full player controls (play, pause, volume, fullscreen)
- Responsive design

**Facebook Videos:**
- Shows blue button: "View on Facebook"
- Click to open video on Facebook
- Requires Facebook login to view

---

## Technical Details

**Limits:**
- Maximum 5 videos per post
- Maximum 5 images per post
- Videos + images can be combined

**Video Detection:**
- YouTube: Auto-detects various YouTube URL formats
- Vimeo: Extracts video ID from URL
- Facebook: Detects `/videos/` or `/reel/` in URL
- Direct: Checks file extension (.mp4, .webm)

**User Experience:**
- Embedded videos load lazily
- First 3 videos shown, "+X more" indicator for additional
- Mobile responsive players

---

## Recommendation for Users

**Best Practice:**
- **Use YouTube** for best embedding experience
- Andrew Henderson has official YouTube presence
- YouTube videos work perfectly across all devices
- No login required to view

**Facebook Alternative:**
- If video is exclusive to Facebook, share the link
- Users will see "View on Facebook" button
- Still trackable (likes, comments work on your post)

---

## Future Enhancements (Optional)

Potential additions:
- Instagram video embeds
- TikTok video embeds
- Twitter/X video embeds
- Download option for direct video files
