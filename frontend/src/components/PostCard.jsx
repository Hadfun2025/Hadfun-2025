import { useState } from 'react';
import { Card, CardContent, CardFooter, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { toast } from 'sonner';
import { Heart, MessageCircle, Trash2, Heart as HeartFilled, Share2 } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export function PostCard({ post, currentUser, onUpdate, onDelete }) {
  const [showComments, setShowComments] = useState(false);
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState('');
  const [liked, setLiked] = useState(false);
  const [likesCount, setLikesCount] = useState(post.likes_count || 0);
  const [commentsCount, setCommentsCount] = useState(post.comments_count || 0);
  const [loading, setLoading] = useState(false);
  const [loadingComments, setLoadingComments] = useState(false);

  const getInitials = (name) => {
    if (!name) return '?';
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    
    return date.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
  };

  const getYouTubeEmbedUrl = (url) => {
    // Extract YouTube video ID and return embed URL
    const patterns = [
      /(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\s?]+)/,
      /youtube\.com\/embed\/([^&\s?]+)/,
      /youtube\.com\/v\/([^&\s?]+)/,
      /youtube\.com\/shorts\/([^&\s?]+)/  // YouTube Shorts support
    ];
    
    for (const pattern of patterns) {
      const match = url.match(pattern);
      if (match && match[1]) {
        return `https://www.youtube.com/embed/${match[1]}`;
      }
    }
    return null;
  };

  const getVimeoEmbedUrl = (url) => {
    // Extract Vimeo video ID
    const match = url.match(/vimeo\.com\/(\d+)/);
    if (match && match[1]) {
      return `https://player.vimeo.com/video/${match[1]}`;
    }
    return null;
  };

  const getFacebookEmbedUrl = (url) => {
    // Facebook video embed - use the URL directly in Facebook's embed player
    if (url.includes('facebook.com/') && (url.includes('/videos/') || url.includes('/reel/'))) {
      // Encode the URL for Facebook's embed player
      return `https://www.facebook.com/plugins/video.php?href=${encodeURIComponent(url)}&show_text=false&width=560`;
    }
    return null;
  };

  const renderVideo = (videoUrl, index) => {
    const youtubeEmbed = getYouTubeEmbedUrl(videoUrl);
    const vimeoEmbed = getVimeoEmbedUrl(videoUrl);
    const facebookEmbed = getFacebookEmbedUrl(videoUrl);

    if (youtubeEmbed) {
      return (
        <div key={index} className="relative aspect-video bg-gray-100 rounded-lg overflow-hidden">
          <iframe
            src={youtubeEmbed}
            className="w-full h-full"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
            title={`Video ${index + 1}`}
          />
        </div>
      );
    }

    if (vimeoEmbed) {
      return (
        <div key={index} className="relative aspect-video bg-gray-100 rounded-lg overflow-hidden">
          <iframe
            src={vimeoEmbed}
            className="w-full h-full"
            allow="autoplay; fullscreen; picture-in-picture"
            allowFullScreen
            title={`Video ${index + 1}`}
          />
        </div>
      );
    }

    if (facebookEmbed) {
      return (
        <div key={index} className="relative aspect-video bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg overflow-hidden flex items-center justify-center">
          <a
            href={videoUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="flex flex-col items-center justify-center gap-4 text-white p-8 hover:scale-105 transition-transform"
          >
            <svg className="w-16 h-16" fill="currentColor" viewBox="0 0 24 24">
              <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
            </svg>
            <div className="text-center">
              <p className="font-semibold text-lg">View on Facebook</p>
              <p className="text-sm text-blue-100">Opens in new tab</p>
            </div>
          </a>
        </div>
      );
    }

    // Direct video URL (.mp4, .webm, etc.)
    // Handle relative URLs by prepending backend URL
    const fullVideoUrl = videoUrl.startsWith('http') ? videoUrl : `${BACKEND_URL}${videoUrl}`;
    
    return (
      <div key={index} className="relative aspect-video bg-gray-100 rounded-lg overflow-hidden">
        <video
          src={fullVideoUrl}
          controls
          className="w-full h-full object-cover"
          title={`Video ${index + 1}`}
        >
          Your browser does not support the video tag.
        </video>
      </div>
    );
  };

  const loadComments = async () => {
    if (comments.length > 0) {
      setShowComments(!showComments);
      return;
    }

    setLoadingComments(true);
    try {
      const response = await axios.get(`${API}/posts/${post.id}/comments`);
      setComments(response.data);
      setShowComments(true);
    } catch (error) {
      console.error('Load comments error:', error);
      toast.error('Failed to load comments');
    } finally {
      setLoadingComments(false);
    }
  };

  const handleLike = async () => {
    if (!currentUser) {
      toast.error('Please log in to like posts');
      return;
    }

    if (!currentUser.profile_completed) {
      toast.error('Please complete your profile to interact with posts');
      return;
    }

    setLoading(true);
    try {
      if (liked) {
        await axios.delete(`${API}/posts/${post.id}/like?user_id=${currentUser.id}`);
        setLiked(false);
        setLikesCount(prev => prev - 1);
        toast.success('Post unliked');
      } else {
        await axios.post(`${API}/posts/${post.id}/like?user_id=${currentUser.id}`);
        setLiked(true);
        setLikesCount(prev => prev + 1);
        toast.success('Post liked!');
      }
    } catch (error) {
      console.error('Like error:', error);
      if (error.response?.status === 400 && error.response?.data?.detail?.includes('already liked')) {
        setLiked(true);
      } else {
        toast.error(error.response?.data?.detail || 'Failed to like post');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleComment = async (e) => {
    e.preventDefault();

    if (!currentUser) {
      toast.error('Please log in to comment');
      return;
    }

    if (!currentUser.profile_completed) {
      toast.error('Please complete your profile to comment');
      return;
    }

    if (!newComment.trim()) {
      toast.error('Comment cannot be empty');
      return;
    }

    if (newComment.length > 1000) {
      toast.error('Comment exceeds 1000 character limit');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(
        `${API}/posts/${post.id}/comments?user_id=${currentUser.id}`,
        { content: newComment.trim() }
      );
      
      setComments([...comments, response.data]);
      setCommentsCount(prev => prev + 1);
      setNewComment('');
      toast.success('Comment posted!');
    } catch (error) {
      console.error('Comment error:', error);
      toast.error(error.response?.data?.detail || 'Failed to post comment');
    } finally {
      setLoading(false);
    }
  };

  const handleDeletePost = async () => {
    if (!confirm('Are you sure you want to delete this post?')) return;

    try {
      await axios.delete(`${API}/posts/${post.id}?user_id=${currentUser.id}`);
      toast.success('Post deleted successfully');
      if (onDelete) onDelete(post.id);
    } catch (error) {
      console.error('Delete post error:', error);
      toast.error(error.response?.data?.detail || 'Failed to delete post');
    }
  };

  const handleShareToFacebook = () => {
    // Build the share text
    let shareText = post.content;
    
    // Add charity info if present
    if (post.charity_name) {
      shareText += `\n\n💗 Supporting: ${post.charity_name}`;
      if (post.charity_description) {
        shareText += `\n${post.charity_description}`;
      }
    }
    
    // Add link back to HadFun
    shareText += `\n\n🔗 Join the conversation on HadFun: https://hadfun.co.uk`;
    
    // Build Facebook share URL
    const facebookShareUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent('https://hadfun.co.uk')}&quote=${encodeURIComponent(shareText)}`;
    
    // Use window.location for mobile Safari compatibility (avoids CORP issues)
    // This opens in same tab but is more reliable on mobile
    window.location.href = facebookShareUrl;
    
    toast.success('Opening Facebook to share...');
  };

  const isAuthor = currentUser && currentUser.id === post.author_id;

  return (
    <Card className="mb-4">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <Avatar>
              <AvatarFallback className="bg-gradient-to-br from-blue-500 to-purple-500 text-white">
                {getInitials(post.author_username)}
              </AvatarFallback>
            </Avatar>
            <div>
              <p className="font-semibold">{post.author_username}</p>
              <p className="text-xs text-gray-500">{formatDate(post.created_at)}</p>
            </div>
          </div>
          {isAuthor && (
            <Button
              variant="ghost"
              size="sm"
              onClick={handleDeletePost}
              className="text-red-500 hover:text-red-700 hover:bg-red-50"
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          )}
        </div>
      </CardHeader>

      <CardContent className="pb-3">
        {/* Charity Badge */}
        {post.charity_name && (
          <div className="mb-3 p-3 bg-gradient-to-r from-pink-50 to-purple-50 rounded-lg border border-pink-200">
            <div className="flex items-start gap-2">
              <Heart className="h-5 w-5 text-pink-500 mt-0.5 flex-shrink-0" />
              <div>
                <p className="font-semibold text-pink-700">{post.charity_name}</p>
                {post.charity_description && (
                  <p className="text-sm text-gray-600 mt-1">{post.charity_description}</p>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Post Content */}
        <p className="text-gray-800 whitespace-pre-wrap">{post.content}</p>

        {/* Images */}
        {post.images && post.images.length > 0 && (
          <div className="mt-3 grid grid-cols-2 gap-2">
            {post.images.slice(0, 4).map((img, index) => {
              // Handle relative URLs by prepending backend URL
              const imageUrl = img.startsWith('http') ? img : `${BACKEND_URL}${img}`;
              
              return (
                <div key={index} className="relative aspect-video bg-gray-100 rounded-lg overflow-hidden">
                  <img
                    src={imageUrl}
                    alt={`Post image ${index + 1}`}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      e.target.style.display = 'none';
                      e.target.parentElement.innerHTML = '<div class="w-full h-full bg-gray-200 flex items-center justify-center text-gray-500"><span>Image Not Available</span></div>';
                    }}
                  />
                  {index === 3 && post.images.length > 4 && (
                    <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center">
                      <p className="text-white font-semibold text-xl">+{post.images.length - 4}</p>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}

        {/* Videos */}
        {post.videos && post.videos.length > 0 && (
          <div className="mt-3 space-y-3">
            {post.videos.slice(0, 3).map((video, index) => renderVideo(video, index))}
            {post.videos.length > 3 && (
              <p className="text-sm text-gray-500 text-center">
                +{post.videos.length - 3} more video{post.videos.length - 3 > 1 ? 's' : ''}
              </p>
            )}
          </div>
        )}
      </CardContent>

      <CardFooter className="flex flex-col gap-3 pt-3">
        {/* Action Buttons */}
        <div className="flex items-center gap-2 w-full flex-wrap">
          <Button
            variant="ghost"
            size="sm"
            onClick={handleLike}
            disabled={loading}
            className={liked ? 'text-red-500' : ''}
          >
            {liked ? <HeartFilled className="h-5 w-5 mr-1 fill-current" /> : <Heart className="h-5 w-5 mr-1" />}
            {likesCount} {likesCount === 1 ? 'Like' : 'Likes'}
          </Button>

          <Button
            variant="ghost"
            size="sm"
            onClick={loadComments}
            disabled={loadingComments}
          >
            <MessageCircle className="h-5 w-5 mr-1" />
            {commentsCount} {commentsCount === 1 ? 'Comment' : 'Comments'}
          </Button>

          <Button
            variant="ghost"
            size="sm"
            onClick={handleShareToFacebook}
            className="text-blue-600 hover:text-blue-700 hover:bg-blue-50"
          >
            <svg className="h-5 w-5 mr-1" fill="currentColor" viewBox="0 0 24 24">
              <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
            </svg>
            Share
          </Button>
        </div>

        {/* Comments Section */}
        {showComments && (
          <div className="w-full space-y-3 border-t pt-3">
            {/* Existing Comments */}
            {comments.length > 0 && (
              <div className="space-y-2 max-h-60 overflow-y-auto">
                {comments.map((comment) => (
                  <div key={comment.id} className="flex gap-2">
                    <Avatar className="h-8 w-8">
                      <AvatarFallback className="bg-gray-300 text-xs">
                        {getInitials(comment.author_username)}
                      </AvatarFallback>
                    </Avatar>
                    <div className="flex-1 bg-gray-50 rounded-lg p-2">
                      <p className="text-sm font-semibold">{comment.author_username}</p>
                      <p className="text-sm text-gray-700">{comment.content}</p>
                      <p className="text-xs text-gray-500 mt-1">{formatDate(comment.created_at)}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Add Comment */}
            {currentUser ? (
              <form onSubmit={handleComment} className="flex gap-2">
                <Input
                  value={newComment}
                  onChange={(e) => setNewComment(e.target.value)}
                  placeholder="Write a comment..."
                  maxLength={1000}
                  disabled={loading}
                />
                <Button type="submit" disabled={loading || !newComment.trim()}>
                  Post
                </Button>
              </form>
            ) : (
              <p className="text-sm text-gray-500 text-center">Log in to comment</p>
            )}
          </div>
        )}
      </CardFooter>
    </Card>
  );
}
