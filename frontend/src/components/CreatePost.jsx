import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';
import { Heart, Image, Video, X, Facebook } from 'lucide-react';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export function CreatePost({ user, onPostCreated }) {
  const [content, setContent] = useState('');
  const [images, setImages] = useState([]);
  const [videos, setVideos] = useState([]);
  const [charityName, setCharityName] = useState('');
  const [charityDescription, setCharityDescription] = useState('');
  const [showCharityFields, setShowCharityFields] = useState(false);
  const [newImageUrl, setNewImageUrl] = useState('');
  const [newVideoUrl, setNewVideoUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [showImportDialog, setShowImportDialog] = useState(false);
  const [facebookUrl, setFacebookUrl] = useState('');
  const [importing, setImporting] = useState(false);
  const [uploadingFile, setUploadingFile] = useState(false);
  const [uploadProgress, setUploadProgress] = useState('');

  const handleAddImage = () => {
    if (!newImageUrl.trim()) {
      toast.error('Please enter an image URL');
      return;
    }

    if (images.length >= 5) {
      toast.error('Maximum 5 images allowed per post');
      return;
    }

    // Basic URL validation
    try {
      new URL(newImageUrl);
      setImages([...images, newImageUrl]);
      setNewImageUrl('');
    } catch (e) {
      toast.error('Please enter a valid URL');
    }
  };

  const handleRemoveImage = (index) => {
    setImages(images.filter((_, i) => i !== index));
  };

  const handleAddVideo = () => {
    if (!newVideoUrl.trim()) {
      toast.error('Please enter a video URL');
      return;
    }

    if (videos.length >= 5) {
      toast.error('Maximum 5 videos allowed per post');
      return;
    }

    // Basic URL validation
    try {
      new URL(newVideoUrl);
      setVideos([...videos, newVideoUrl]);
      setNewVideoUrl('');
    } catch (e) {
      toast.error('Please enter a valid URL');
    }
  };

  const handleRemoveVideo = (index) => {
    setVideos(videos.filter((_, i) => i !== index));
  };



  const handleFileUpload = async (event, type) => {
    const file = event.target.files[0];
    if (!file) return;

    console.log('File upload started:', { name: file.name, type: file.type, size: file.size });

    // Check file size (50MB limit)
    const maxSize = 50 * 1024 * 1024; // 50MB in bytes
    if (file.size > maxSize) {
      toast.error(`File too large (${(file.size / (1024 * 1024)).toFixed(1)}MB). Maximum size is 50MB`);
      return;
    }

    // Check file type
    const validImageTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp', 'image/heic', 'image/heif'];
    const validVideoTypes = ['video/mp4', 'video/quicktime', 'video/x-msvideo', 'video/avi'];
    
    // Mobile browsers sometimes don't set proper MIME types, so also check file extension
    const fileName = file.name.toLowerCase();
    const isImageByExtension = fileName.endsWith('.jpg') || fileName.endsWith('.jpeg') || 
                                fileName.endsWith('.png') || fileName.endsWith('.gif') || 
                                fileName.endsWith('.webp') || fileName.endsWith('.heic') || 
                                fileName.endsWith('.heif');
    const isVideoByExtension = fileName.endsWith('.mp4') || fileName.endsWith('.mov') || 
                                fileName.endsWith('.avi');
    
    if (type === 'image' && !validImageTypes.includes(file.type) && !isImageByExtension) {
      toast.error('Please upload a valid image (JPG, PNG, GIF, WEBP, HEIC)');
      console.error('Invalid image type:', file.type, fileName);
      return;
    }
    
    if (type === 'video' && !validVideoTypes.includes(file.type) && !isVideoByExtension) {
      toast.error('Please upload a valid video (MP4, MOV, AVI)');
      console.error('Invalid video type:', file.type, fileName);
      return;
    }

    setUploadingFile(true);
    setUploadProgress(`Uploading ${type}...`);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await axios.post(`${API}/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 60000, // 60 second timeout
      });

      if (!response.data || !response.data.url) {
        throw new Error('Upload succeeded but no file URL received');
      }

      const fileUrl = `${BACKEND_URL}${response.data.url}`;

      if (type === 'image') {
        if (images.length >= 5) {
          toast.error('Maximum 5 images allowed per post');
          return;
        }
        setImages([...images, fileUrl]);
        toast.success('✅ Photo uploaded and attached!');
      } else {
        if (videos.length >= 2) {
          toast.error('Maximum 2 videos allowed per post');
          return;
        }
        setVideos([...videos, fileUrl]);
        toast.success('✅ Video uploaded and attached!');
      }

      // Reset file input
      event.target.value = '';
    } catch (error) {
      console.error('Upload error:', error);
      console.error('Error details:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
        code: error.code
      });
      
      // Enhanced error messages
      if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
        toast.error('Upload timeout - file may be too large or connection is slow. Please try a smaller file or check your connection.');
      } else if (error.response?.status === 413) {
        toast.error('File too large for server. Please compress your image or use a smaller file.');
      } else if (error.response?.status === 500) {
        toast.error('Server error during upload. Please try again or use a different image format (JPG or PNG work best).');
      } else if (error.response?.status === 400) {
        toast.error(error.response?.data?.detail || 'File type not supported. Please try JPG or PNG format.');
      } else if (!navigator.onLine) {
        toast.error('No internet connection. Please check your network.');
      } else {
        toast.error(error.response?.data?.detail || error.message || 'Error uploading file. Try converting to JPG/PNG first.');
      }
    } finally {
      setUploadingFile(false);
      setUploadProgress('');
    }
  };

  const handleImportFromFacebook = async () => {
    if (!facebookUrl.trim()) {
      toast.error('Please enter a Facebook post URL');
      return;
    }

    // Validate Facebook URL
    if (!facebookUrl.includes('facebook.com')) {
      toast.error('Please enter a valid Facebook URL');
      return;
    }

    setImporting(true);

    try {
      // Try to extract content from Facebook URL
      // Note: This is a simplified version - Facebook's real content requires OAuth
      // For now, we'll provide a helpful prompt for manual paste
      
      toast.info('Please copy your post text from Facebook and paste it below');
      
      // Store the Facebook URL reference
      setContent(content + '\n\n📱 Originally posted on Facebook');
      setShowImportDialog(false);
      setFacebookUrl('');
      
      toast.success('Ready to paste your Facebook content!');
    } catch (error) {
      console.error('Import error:', error);
      toast.error('Unable to import. Please copy and paste your content manually.');
    } finally {
      setImporting(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!content.trim()) {
      toast.error('Please write something before posting');
      return;
    }

    if (content.length > 5000) {
      toast.error('Post content exceeds 5000 character limit');
      return;
    }

    if (showCharityFields && charityDescription.length > 500) {
      toast.error('Charity description exceeds 500 character limit');
      return;
    }

    // Confirm submission if user has uploaded media
    if ((images.length > 0 || videos.length > 0) && content.trim().length < 10) {
      if (!window.confirm('Your post has media but very little text. Continue posting?')) {
        return;
      }
    }

    setLoading(true);
    toast.loading('Creating your post...', { id: 'post-submit' });

    try {
      const postData = {
        content: content.trim(),
        images: images,
        videos: videos,
      };

      if (showCharityFields && charityName.trim()) {
        postData.charity_name = charityName.trim();
        if (charityDescription.trim()) {
          postData.charity_description = charityDescription.trim();
        }
      }

      const response = await axios.post(`${API}/posts?user_id=${user.id}`, postData, {
        timeout: 30000, // 30 second timeout
      });

      if (!response.data) {
        throw new Error('Post created but no confirmation received');
      }

      toast.success('🎉 Post created successfully!', { id: 'post-submit' });
      
      // Reset form
      setContent('');
      setImages([]);
      setVideos([]);
      setCharityName('');
      setCharityDescription('');
      setShowCharityFields(false);
      
      // Notify parent to refresh posts
      if (onPostCreated) {
        onPostCreated();
      }
    } catch (error) {
      console.error('Create post error:', error);
      
      // Enhanced error messages
      toast.dismiss('post-submit');
      
      if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
        toast.error('Post submission timeout. Your post may not have been saved. Please check and try again.');
      } else if (error.response?.status === 400) {
        toast.error(error.response?.data?.detail || 'Invalid post data. Please check your content and try again.');
      } else if (error.response?.status === 401 || error.response?.status === 403) {
        toast.error('You are not authorized to post. Please log in again.');
      } else if (error.response?.status === 500) {
        toast.error('Server error. Your post was not saved. Please try again.');
      } else if (!navigator.onLine) {
        toast.error('No internet connection. Please check your network and try again.');
      } else {
        toast.error(error.response?.data?.detail || 'Failed to create post. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <span>Share Your Story</span>
          <Badge variant="outline" className="ml-auto">
            Football With Purpose
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Import from Facebook Button */}
          <div className="flex justify-end">
            <Button
              type="button"
              onClick={() => setShowImportDialog(true)}
              variant="outline"
              size="sm"
              className="text-blue-600 border-blue-300 hover:bg-blue-50"
            >
              <svg className="h-4 w-4 mr-2" fill="currentColor" viewBox="0 0 24 24">
                <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
              </svg>
              Import from Facebook
            </Button>
          </div>

          {/* Main Content */}
          <div>
            <Textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Share your story, support a cause, or connect with the community..."
              rows={4}
              maxLength={5000}
              className="resize-none"
            />
            <p className="text-xs text-gray-500 text-right mt-1">
              {content.length}/5000 characters
            </p>
          </div>

          {/* Image URLs */}
          <div className="space-y-2">
            <Label className="flex items-center gap-2">
              <Image className="h-4 w-4" />
              Add Images (Optional)
            </Label>
            
            {images.length > 0 && (
              <div className="flex flex-wrap gap-2 mb-2">
                {images.map((img, index) => (
                  <Badge key={index} variant="secondary" className="pr-1 bg-green-100 border-green-300">
                    <span className="max-w-[150px] truncate">✓ Image {index + 1}</span>
                    <button
                      type="button"
                      onClick={() => handleRemoveImage(index)}
                      className="ml-1 hover:text-red-500"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </Badge>
                ))}
              </div>
            )}
            
            {/* Upload from Phone/Computer */}
            <div className="bg-green-50 border border-green-200 rounded-lg p-3 mb-2">
              <p className="text-sm font-semibold text-green-900 mb-2">📸 Option 1: Upload from your device</p>
              <Label 
                htmlFor="image-upload" 
                className="flex items-center justify-center gap-2 bg-white border-2 border-dashed border-green-400 rounded-lg p-4 cursor-pointer hover:bg-green-50 transition-colors"
              >
                <Image className="h-5 w-5 text-green-600" />
                <span className="text-sm font-medium text-green-700">
                  {uploadingFile ? uploadProgress : 'Tap to select or take photo'}
                </span>
              </Label>
              <input
                type="file"
                accept="image/*"
                capture="environment"
                onChange={(e) => handleFileUpload(e, 'image')}
                disabled={images.length >= 5 || uploadingFile}
                className="hidden"
                id="image-upload"
              />
              <p className="text-xs text-gray-600 mt-2">
                {uploadingFile && uploadProgress ? (
                  <span className="text-green-700 font-semibold">⏳ {uploadProgress}</span>
                ) : (
                  '📱 Works with phone camera, photo library, or computer files • JPG, PNG, GIF, WEBP, HEIC • Max 50MB'
                )}
              </p>
            </div>
            
            {/* Or paste URL */}
            <div className="space-y-2">
              <p className="text-sm font-medium text-gray-700">Option 2: Paste image URL</p>
              <div className="flex gap-2">
                <Input
                  value={newImageUrl}
                  onChange={(e) => setNewImageUrl(e.target.value)}
                  placeholder="Paste image link here..."
                  disabled={images.length >= 5}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      handleAddImage();
                    }
                  }}
                />
                <Button
                  type="button"
                  onClick={handleAddImage}
                  variant="outline"
                  disabled={images.length >= 5 || !newImageUrl.trim()}
                  className="whitespace-nowrap"
                >
                  Add Image
                </Button>
              </div>
              <p className="text-xs text-gray-500">
                💡 {images.length === 0 ? 'Choose ONE method: Upload a file OR paste a link, then click "Add Image"' : `${images.length}/5 images added`}
              </p>
            </div>
          </div>

          {/* Video URLs */}
          <div className="space-y-2">
            <Label className="flex items-center gap-2">
              <Video className="h-4 w-4" />
              Add Videos (Optional)
            </Label>
            
            {videos.length > 0 && (
              <div className="flex flex-wrap gap-2 mb-2">
                {videos.map((vid, index) => (
                  <Badge key={index} variant="secondary" className="pr-1 bg-green-100 border-green-300">
                    <span className="max-w-[150px] truncate">✓ Video {index + 1}</span>
                    <button
                      type="button"
                      onClick={() => handleRemoveVideo(index)}
                      className="ml-1 hover:text-red-500"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </Badge>
                ))}
              </div>
            )}
            
            {/* Upload from Phone/Computer */}
            <div className="bg-purple-50 border border-purple-200 rounded-lg p-3 mb-2">
              <p className="text-sm font-semibold text-purple-900 mb-2">🎥 Option 1: Upload from your device</p>
              <input
                type="file"
                accept="video/*"
                onChange={(e) => handleFileUpload(e, 'video')}
                disabled={videos.length >= 2 || uploadingFile}
                className="text-sm"
                id="video-upload"
              />
              <p className="text-xs text-gray-600 mt-1">
                {uploadingFile && uploadProgress ? (
                  <span className="text-purple-700 font-semibold">⏳ {uploadProgress}</span>
                ) : (
                  'MP4, MOV, AVI • Max 50MB'
                )}
              </p>
            </div>
            
            {/* Or paste URL */}
            <div className="space-y-2">
              <p className="text-sm font-medium text-gray-700">Option 2: Paste video URL</p>
              <div className="flex gap-2">
                <Input
                  value={newVideoUrl}
                  onChange={(e) => setNewVideoUrl(e.target.value)}
                  placeholder="Paste YouTube, Facebook, or Vimeo link here..."
                  disabled={videos.length >= 2}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      handleAddVideo();
                    }
                  }}
                />
                <Button
                  type="button"
                  onClick={handleAddVideo}
                  variant="outline"
                  disabled={videos.length >= 2 || !newVideoUrl.trim()}
                  className="whitespace-nowrap"
                >
                  Add Video
                </Button>
              </div>
              <p className="text-xs text-gray-500">
                💡 {videos.length === 0 ? 'Choose ONE method: Upload a file OR paste a link, then click "Add Video"' : `${videos.length}/2 videos added`}
              </p>
            </div>
          </div>

          {/* Charity Fields Toggle */}
          <div>
            <Button
              type="button"
              onClick={() => setShowCharityFields(!showCharityFields)}
              variant={showCharityFields ? 'default' : 'outline'}
              className="w-full"
            >
              <Heart className={`h-4 w-4 mr-2 ${showCharityFields ? 'fill-current' : ''}`} />
              {showCharityFields ? 'Remove Charity Tag' : 'Support a Cause'}
            </Button>
          </div>

          {/* Charity Fields */}
          {showCharityFields && (
            <div className="space-y-3 p-4 bg-pink-50 rounded-lg border border-pink-200">
              <div>
                <Label htmlFor="charity_name">Charity or Cause Name</Label>
                <Input
                  id="charity_name"
                  value={charityName}
                  onChange={(e) => setCharityName(e.target.value)}
                  placeholder="e.g., Local Food Bank, Youth Football Fund"
                  maxLength={100}
                />
              </div>
              <div>
                <Label htmlFor="charity_description">About This Cause (Optional)</Label>
                <Textarea
                  id="charity_description"
                  value={charityDescription}
                  onChange={(e) => setCharityDescription(e.target.value)}
                  placeholder="Tell us about the cause and how people can help..."
                  rows={2}
                  maxLength={500}
                />
                <p className="text-xs text-gray-500 text-right mt-1">
                  {charityDescription.length}/500 characters
                </p>
              </div>
            </div>
          )}

          {/* Submit Button */}
          <Button
            type="submit"
            disabled={loading || uploadingFile || !content.trim()}
            className="w-full"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Creating Post...
              </span>
            ) : uploadingFile ? (
              'Please wait - uploading...'
            ) : (
              'Share Post'
            )}
          </Button>
        </form>
      </CardContent>

      {/* Import from Facebook Dialog */}
      <Dialog open={showImportDialog} onOpenChange={setShowImportDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <svg className="h-6 w-6 text-blue-600" fill="currentColor" viewBox="0 0 24 24">
                <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
              </svg>
              Import from Facebook
            </DialogTitle>
            <DialogDescription>
              Paste your Facebook post URL and we'll help you create a HadFun post with the content.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 mt-4">
            <div>
              <Label htmlFor="fb-url">Facebook Post URL</Label>
              <Input
                id="fb-url"
                value={facebookUrl}
                onChange={(e) => setFacebookUrl(e.target.value)}
                placeholder="https://www.facebook.com/yourpost/12345"
                className="mt-1"
              />
            </div>

            <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
              <p className="text-sm text-gray-700">
                <strong>How to use:</strong>
              </p>
              <ol className="text-sm text-gray-600 mt-2 space-y-1 list-decimal list-inside">
                <li>Paste your Facebook post URL above</li>
                <li>Click "Import"</li>
                <li>Copy your post text from Facebook</li>
                <li>Paste it into the content area</li>
                <li>Add YouTube video link if you have one</li>
                <li>Share to HadFun!</li>
              </ol>
            </div>

            <div className="flex gap-3">
              <Button
                onClick={handleImportFromFacebook}
                disabled={importing || !facebookUrl.trim()}
                className="flex-1"
              >
                {importing ? 'Importing...' : 'Import'}
              </Button>
              <Button
                onClick={() => {
                  setShowImportDialog(false);
                  setFacebookUrl('');
                }}
                variant="outline"
              >
                Cancel
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </Card>
  );
}
