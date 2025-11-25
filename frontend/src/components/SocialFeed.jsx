import { useState, useEffect } from 'react';
import { CreatePost } from './CreatePost';
import { PostCard } from './PostCard';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';
import { Users, RefreshCw, Heart, TrendingUp } from 'lucide-react';
import axios from 'axios';
import { useLanguage } from '@/LanguageContext';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export function SocialFeed({ currentUser, onTabChange }) {
  const { t } = useLanguage();
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadPosts();
  }, []);

  const loadPosts = async () => {
    try {
      const response = await axios.get(`${API}/posts?limit=50`);
      setPosts(response.data);
    } catch (error) {
      console.error('Load posts error:', error);
      toast.error('Failed to load posts');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleRefresh = () => {
    setRefreshing(true);
    loadPosts();
  };

  const handlePostCreated = () => {
    loadPosts();
  };

  const handlePostDeleted = (postId) => {
    setPosts(posts.filter(p => p.id !== postId));
  };

  if (loading) {
    return (
      <div className="max-w-3xl mx-auto p-4">
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto p-4 space-y-6">
      {/* Quick Navigation to Predictions */}
      <div className="bg-gradient-to-r from-blue-500 to-indigo-600 rounded-lg p-4 text-white shadow-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <TrendingUp className="h-6 w-6" />
            <div>
              <p className="font-semibold">{t.community?.predictionBanner || 'HadFun Football Predictions'}</p>
              <p className="text-xs text-blue-100">{t.community?.predictionSubtitle || 'Make predictions, win prizes, compete with friends'}</p>
            </div>
          </div>
          <Button
            variant="secondary"
            size="sm"
            onClick={() => onTabChange && onTabChange('predictions')}
            className="bg-white text-blue-600 hover:bg-blue-50"
          >
            {t.community?.goToPredictions || 'Go to Predictions →'}
          </Button>
        </div>
      </div>

      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Users className="h-8 w-8 text-blue-500" />
            {t.community?.title || 'Community'}
          </h1>
          <div className="flex items-center gap-2 mt-2">
            <img 
              src="/hadfun-logo.jpg" 
              alt="HadFun" 
              className="h-8 w-auto object-contain"
            />
            <p className="text-gray-600">{t.community?.subtitle || 'Share stories, support causes, connect with purpose'}</p>
          </div>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={handleRefresh}
          disabled={refreshing}
        >
          <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
          {refreshing ? (t.community?.refreshing || 'Refreshing...') : (t.community?.refresh || 'Refresh')}
        </Button>
      </div>

      {/* Create Post - Only for logged in users with completed profiles */}
      {currentUser && currentUser.profile_completed && (
        <CreatePost user={currentUser} onPostCreated={handlePostCreated} />
      )}

      {/* Profile Completion Prompt */}
      {currentUser && !currentUser.profile_completed && (
        <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6 border border-blue-200">
          <div className="flex items-start gap-4">
            <Heart className="h-8 w-8 text-purple-500 flex-shrink-0 mt-1" />
            <div className="flex-1">
              <h3 className="font-semibold text-lg mb-2">{t.community?.profileRequired || 'Complete Your Profile to Join the Conversation'}</h3>
              <p className="text-gray-700 mb-3">
                {t.community?.profileMessage || 'You can view posts, but to create your own posts and interact with the community, please complete your profile first.'}
              </p>
              <div className="flex gap-3">
                <Badge variant="outline" className="bg-white">
                  {t.community?.profileSetupRequired || 'Profile setup required for posting and commenting'}
                </Badge>
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => window.location.reload()}
                  className="ml-auto"
                >
                  {t.community?.refreshPage || 'Refresh Page'}
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Guest User Message */}
      {!currentUser && (
        <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-6 border border-green-200">
          <div className="flex items-start gap-4">
            <Users className="h-8 w-8 text-green-500 flex-shrink-0 mt-1" />
            <div>
              <h3 className="font-semibold text-lg mb-2">{t.community?.guestWelcome || 'Welcome to Football With Purpose'}</h3>
              <p className="text-gray-700 mb-3">
                {t.community?.guestMessage || "You're viewing as a guest. Join our community to share your stories, support causes, and make predictions!"}
              </p>
              <Badge variant="outline" className="bg-white">
                {t.community?.guestAction || 'Log in to create posts and join the conversation'}
              </Badge>
            </div>
          </div>
        </div>
      )}


      {/* Community Care Feature Banner */}
      <div className="bg-gradient-to-r from-pink-50 via-purple-50 to-pink-50 rounded-lg p-6 border-2 border-pink-300 shadow-sm">
        <div className="flex items-start gap-4">
          <Heart className="h-10 w-10 text-pink-600 flex-shrink-0 mt-1" />
          <div className="flex-1">
            <h3 className="font-bold text-xl text-pink-900 mb-2">
              ❤️ {t.community?.communityCareBanner || 'Charity Begins at Home - Community Care'}
            </h3>
            <p className="text-gray-700 leading-relaxed mb-3">
              {t.community?.communityCareDesc || 'HadFun isn\'t just about predictions - it\'s about building a caring community. Through our Community Care feature, team members can nominate teammates facing hardship. When someone wins, they can choose to share their winnings with those who need support.'}
            </p>
            <div className="grid md:grid-cols-2 gap-3 text-sm">
              <div className="bg-white/70 rounded p-3">
                <p className="font-semibold text-pink-900 mb-1">{t.community?.careHowItWorks || '🤝 How it works:'}</p>
                <p className="text-gray-600">{t.community?.careHowItWorksDesc || 'Nominate teammates in need. Winners see nominations and can choose to donate.'}</p>
              </div>
              <div className="bg-white/70 rounded p-3">
                <p className="font-semibold text-pink-900 mb-1">{t.community?.careOptional || '💝 Completely optional:'}</p>
                <p className="text-gray-600">{t.community?.careOptionalDesc || 'No pressure on anyone. Every act of kindness is celebrated.'}</p>
              </div>
            </div>
            <p className="text-xs text-pink-800 mt-3 italic">
              {t.community?.careFooter || 'Find Community Care in your team page to nominate someone or view donation history.'}
            </p>
          </div>
        </div>
      </div>


      {/* Posts List */}
      <div className="space-y-4">
        {posts.length === 0 ? (
          <div className="text-center py-16 bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50 rounded-lg border-2 border-dashed border-purple-200">
            <div className="max-w-2xl mx-auto px-4">
              {/* Icon */}
              <div className="mb-6">
                <Users className="h-20 w-20 text-purple-400 mx-auto mb-2" />
                <div className="flex justify-center gap-2">
                  <Heart className="h-6 w-6 text-pink-400 animate-pulse" />
                  <TrendingUp className="h-6 w-6 text-blue-400 animate-pulse" />
                </div>
              </div>
              
              {/* Heading */}
              <h3 className="text-3xl font-bold text-gray-800 mb-3">
                🎉 Start the Conversation!
              </h3>
              <p className="text-lg text-gray-600 mb-6">
                Be the first to share with the community!
              </p>
              
              {/* Quick Tips */}
              <div className="bg-white/80 rounded-lg p-6 mb-6 text-left">
                <h4 className="font-bold text-gray-800 mb-3 flex items-center gap-2">
                  <span className="text-2xl">💡</span>
                  What can you share?
                </h4>
                <ul className="space-y-2 text-gray-700">
                  <li className="flex items-start gap-2">
                    <span className="text-green-500 font-bold">✓</span>
                    <span><strong>Your predictions</strong> - Share your thoughts on upcoming matches</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-green-500 font-bold">✓</span>
                    <span><strong>Celebrate wins</strong> - Brag about your winning streak!</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-green-500 font-bold">✓</span>
                    <span><strong>Team banter</strong> - Connect with your teammates</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-green-500 font-bold">✓</span>
                    <span><strong>Match reactions</strong> - Did your team score? Share the excitement!</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-green-500 font-bold">✓</span>
                    <span><strong>Photos & videos</strong> - Add media links to make posts pop</span>
                  </li>
                </ul>
              </div>
              
              {/* CTA */}
              {currentUser && currentUser.profile_completed ? (
                <div>
                  <p className="text-gray-600 mb-4 text-sm">
                    👆 Scroll up to create your first post and get the community started!
                  </p>
                  <div className="inline-block px-6 py-2 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-full font-bold animate-pulse">
                    Your Community Awaits! 🚀
                  </div>
                </div>
              ) : (
                <p className="text-gray-500 text-sm">
                  Complete your profile to start posting!
                </p>
              )}
            </div>
          </div>
        ) : (
          posts.map((post) => (
            <PostCard
              key={post.id}
              post={post}
              currentUser={currentUser}
              onDelete={handlePostDeleted}
            />
          ))
        )}
      </div>

      {/* Load More Button (for future pagination) */}
      {posts.length >= 50 && (
        <div className="text-center py-4">
          <Button variant="outline" onClick={loadPosts}>
            Load More Posts
          </Button>
        </div>
      )}
    </div>
  );
}
