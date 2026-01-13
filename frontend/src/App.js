import { useState, useEffect } from 'react';
import '@/App.css';
import '@/football-bg.css';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';
import { Toaster } from '@/components/ui/sonner';
import { Trophy, Calendar, TrendingUp, Users, BarChart3 } from 'lucide-react';
import { AboutPage } from '@/components/AboutPage';
import { TermsPage } from '@/components/TermsPage';
import { RulesPage } from '@/components/RulesPage';
import { TwitterFeed } from '@/components/TwitterFeed';
import { Navbar } from '@/components/Navbar';
import { TeamManagement } from '@/components/TeamManagement';
import { PaymentModal } from '@/components/PaymentModal';
import { ProfileSetup } from '@/components/ProfileSetup';
import { SocialFeed } from '@/components/SocialFeed';
import { WorldCupGroups } from '@/components/WorldCupGroups';
import { AdminDashboard } from '@/components/AdminDashboard';
import { useLanguage } from '@/LanguageContext';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Admin usernames who can access the dashboard
const ADMIN_USERS = ['aysin', 'admin'];

function App() {
  const { t } = useLanguage();
  const [currentUser, setCurrentUser] = useState(null);
  const [leagues, setLeagues] = useState([]);
  const [fixtures, setFixtures] = useState([]);
  const [showAdminDashboard, setShowAdminDashboard] = useState(false);
  const [selectedLeagues, setSelectedLeagues] = useState([]); // No leagues selected by default - user must click to select
  const [predictions, setPredictions] = useState([]);
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(false);
  
  // Set default tab based on user profile completion
  const getDefaultTab = () => {
    const storedUser = localStorage.getItem('currentUser');
    if (storedUser) {
      const user = JSON.parse(storedUser);
      // If user has completed profile, land on Community, otherwise Fixtures
      return user.profile_completed ? 'community' : 'fixtures';
    }
    return 'fixtures';
  };
  
  const [activeTab, setActiveTab] = useState(getDefaultTab());
  const [showAbout, setShowAbout] = useState(false);
  const [showTerms, setShowTerms] = useState(false);
  const [showRules, setShowRules] = useState(false);
  const [showTwitter, setShowTwitter] = useState(false);
  const [showTeam, setShowTeam] = useState(false);
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [showProfileSetup, setShowProfileSetup] = useState(false);
  const [userPayment, setUserPayment] = useState(null);
  const [checkingPayment, setCheckingPayment] = useState(false);
  const [userTeams, setUserTeams] = useState([]); // All teams user is in
  const [selectedTeam, setSelectedTeam] = useState(null); // Currently selected team
  const [standings, setStandings] = useState({}); // League standings
  const [selectedMatchday, setSelectedMatchday] = useState(null); // Matchday filter
  const [daysAhead, setDaysAhead] = useState(28); // Days ahead for fixtures (4 weeks of upcoming matches)
  
  // Community Welcome Banner
  const [showCommunityBanner, setShowCommunityBanner] = useState(() => {
    return localStorage.getItem('communityBannerDismissed') !== 'true';
  });

  // Auth form
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');

  const dismissCommunityBanner = () => {
    setShowCommunityBanner(false);
    localStorage.setItem('communityBannerDismissed', 'true');
  };

  const goToCommunity = () => {
    setActiveTab('community');
    dismissCommunityBanner();
  };

  useEffect(() => {
    loadLeagues();
    // Check for saved user
    const savedUser = localStorage.getItem('currentUser');
    if (savedUser) {
      setCurrentUser(JSON.parse(savedUser));
    }
    
    // Check for payment callback
    checkPaymentCallback();
  }, []);

  useEffect(() => {
    if (currentUser) {
      loadFixtures();
      loadUserPredictions();
      checkUserPaymentStatus();
      loadUserTeams(); // Load all teams user is in
    }
  }, [currentUser, selectedLeagues, selectedMatchday, daysAhead]);

  useEffect(() => {
    if (currentUser && activeTab === 'standings') {
      loadStandings();
    }
  }, [currentUser, activeTab, selectedLeagues]);

  useEffect(() => {
    if (currentUser && selectedTeam) {
      // loadLeaderboard(); // Removed - now only in My Team section
    }
  }, [currentUser, selectedTeam]);

  const checkPaymentCallback = () => {
    const urlParams = new URLSearchParams(window.location.search);
    const sessionId = urlParams.get('session_id');
    const paymentStatus = urlParams.get('payment');

    if (sessionId && paymentStatus === 'success') {
      // Poll for payment status
      pollPaymentStatus(sessionId);
    } else if (paymentStatus === 'cancel') {
      toast.error('Payment cancelled');
      // Clean up URL
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  };

  const pollPaymentStatus = async (sessionId, attempts = 0) => {
    const maxAttempts = 5;
    const pollInterval = 2000; // 2 seconds

    if (attempts >= maxAttempts) {
      toast.error('Payment status check timed out. Please refresh the page.');
      setCheckingPayment(false);
      return;
    }

    setCheckingPayment(true);

    try {
      const response = await axios.get(`${API}/stripe/checkout-status/${sessionId}`);
      
      if (response.data.payment_status === 'paid') {
        toast.success('Payment successful! You\'re in this week\'s pot! 🎉');
        setCheckingPayment(false);
        // Clean up URL
        window.history.replaceState({}, document.title, window.location.pathname);
        // Refresh user payment status
        if (currentUser) {
          checkUserPaymentStatus();
        }
        return;
      } else if (response.data.status === 'expired') {
        toast.error('Payment session expired. Please try again.');
        setCheckingPayment(false);
        window.history.replaceState({}, document.title, window.location.pathname);
        return;
      }

      // Continue polling
      setTimeout(() => pollPaymentStatus(sessionId, attempts + 1), pollInterval);
    } catch (error) {
      console.error('Error checking payment status:', error);
      toast.error('Error checking payment status');
      setCheckingPayment(false);
    }
  };

  const checkUserPaymentStatus = async () => {
    if (!currentUser) return;
    
    try {
      const response = await axios.get(`${API}/pot/current`);
      const currentWeekId = response.data.week_id;
      
      // Check if user has paid for this week
      const paymentResponse = await axios.get(`${API}/payments/user/${currentUser.id}`);
      const payments = paymentResponse.data;
      
      const weekPayment = payments.find(p => 
        p.week_id === currentWeekId && p.payment_status === 'paid'
      );
      
      setUserPayment(weekPayment || null);
    } catch (error) {
      console.error('Error checking payment status:', error);
    }
  };

  const handlePayment = async (stakeAmount) => {
    if (!currentUser) {
      toast.error('Please log in first');
      return;
    }

    try {
      // If play for fun (0.0), just close modal
      if (stakeAmount === 0.0) {
        toast.success(t.messages.playForFunActivated);
        setShowPaymentModal(false);
        return;
      }

      // Get origin URL
      const originUrl = window.location.origin;

      // Create checkout session
      const response = await axios.post(`${API}/stripe/create-checkout`, null, {
        params: {
          user_email: currentUser.email,
          user_name: currentUser.username,
          stake_amount: stakeAmount,
          origin_url: originUrl
        }
      });

      if (response.data.status === 'already_paid') {
        toast.info(response.data.message);
        setShowPaymentModal(false);
        return;
      }

      if (response.data.play_for_fun) {
        toast.success(response.data.message);
        setShowPaymentModal(false);
        return;
      }

      // Redirect to Stripe checkout
      if (response.data.url) {
        window.location.href = response.data.url;
      }
    } catch (error) {
      console.error('Payment error:', error);
      toast.error(error.response?.data?.detail || 'Error creating payment session');
    }
  };

  const loadLeagues = async () => {
    try {
      const response = await axios.get(`${API}/leagues`);
      setLeagues(response.data);
    } catch (error) {
      console.error('Error loading leagues:', error);
    }
  };

  const loadFixtures = async () => {
    setLoading(true);
    try {
      const leagueIds = selectedLeagues.join(',');
      let url = `${API}/fixtures?league_ids=${leagueIds}`;
      
      if (selectedMatchday) {
        // If specific matchday selected, show that matchday
        url += `&matchday=${selectedMatchday}`;
      } else {
        // Default view: show current week (recent results + upcoming fixtures)
        url += `&days_ahead=${daysAhead}`;
      }
      
      const response = await axios.get(url);
      let fixturesData = response.data;
      
      // If no fixtures found and using current week view, try extended range
      if (!selectedMatchday && fixturesData.length === 0) {
        console.log('No fixtures in current range (likely international break), trying extended range...');
        const fallbackUrl = `${API}/fixtures?league_ids=${leagueIds}&days_ahead=30&upcoming_only=true`;
        const fallbackResponse = await axios.get(fallbackUrl);
        fixturesData = fallbackResponse.data;
      }
      
      setFixtures(fixturesData);
    } catch (error) {
      console.error('Error loading fixtures:', error);
      toast.error('Failed to load fixtures');
    } finally {
      setLoading(false);
    }
  };

  const loadStandings = async () => {
    setLoading(true);
    try {
      // Default to major leagues if none selected
      const leagueIds = selectedLeagues.length > 0 
        ? selectedLeagues.join(',') 
        : '39,40,140,78,135,61'; // Premier League, Championship, La Liga, Bundesliga, Serie A, Ligue 1
      const response = await axios.get(`${API}/standings?league_ids=${leagueIds}`);
      setStandings(response.data);
    } catch (error) {
      console.error('Error loading standings:', error);
      toast.error('Failed to load standings');
    } finally {
      setLoading(false);
    }
  };

  const loadUserPredictions = async () => {
    if (!currentUser) return;
    try {
      const response = await axios.get(`${API}/predictions/user/${currentUser.id}`);
      setPredictions(response.data);
    } catch (error) {
      console.error('Error loading predictions:', error);
    }
  };

  const loadLeaderboard = async () => {
    try {
      if (!selectedTeam) {
        console.log('No team selected, skipping leaderboard load');
        return;
      }
      const response = await axios.get(`${API}/teams/${selectedTeam.id}/leaderboard/by-league`);
      setLeaderboard(response.data); // Now an array of {league_name, leaderboard[]}
    } catch (error) {
      console.error('Error loading leaderboard:', error);
    }
  };

  const loadUserTeams = async () => {
    if (!currentUser) return;
    try {
      const response = await axios.get(`${API}/user/${currentUser.id}/teams`);
      if (response.data.teams && response.data.teams.length > 0) {
        setUserTeams(response.data.teams);
        // Set first team as selected by default if none selected
        if (!selectedTeam) {
          setSelectedTeam(response.data.teams[0].team);
        }
      } else {
        setUserTeams([]);
        setSelectedTeam(null);
      }
    } catch (error) {
      console.error('Error loading user teams:', error);
    }
  };

  const handleLogin = async () => {
    if (!username.trim()) {
      toast.error('Please enter a username');
      return;
    }

    try {
      // Try to get existing user
      let response;
      try {
        response = await axios.get(`${API}/users/${username}`);
        toast.success(`Welcome back, ${username}!`);
      } catch (error) {
        // User doesn't exist, create new one
        if (!email.trim()) {
          toast.error('Please enter an email for new account');
          return;
        }
        response = await axios.post(`${API}/users`, { username, email });
        toast.success(`Account created! Welcome, ${username}!`);
      }

      const user = response.data;
      setCurrentUser(user);
      localStorage.setItem('currentUser', JSON.stringify(user));
      
      // Check if profile needs to be completed
      if (!user.profile_completed) {
        setTimeout(() => {
          setShowProfileSetup(true);
          toast.info('Please complete your profile to join the community');
        }, 1000);
      }
    } catch (error) {
      toast.error('Error logging in');
      console.error(error);
    }
  };

  const handleLogout = () => {
    setCurrentUser(null);
    localStorage.removeItem('currentUser');
    setPredictions([]);
    toast.success('Logged out successfully');
  };

  const handleProfileCompleted = (updatedUser) => {
    setCurrentUser(updatedUser);
    localStorage.setItem('currentUser', JSON.stringify(updatedUser));
    // Switch to Community tab after profile completion
    setActiveTab('community');
    toast.success('Welcome to the HadFun Community! 🎉');
  };

  const handlePredict = async (fixtureId, prediction, leagueId, matchDate) => {
    if (!currentUser) {
      toast.error(t.messages.predictionError || 'Please log in to make predictions');
      return;
    }

    try {
      const response = await axios.post(`${API}/predictions`, {
        user_id: currentUser.id,
        username: currentUser.username,
        fixture_id: fixtureId,
        prediction,
        league_id: leagueId,
        match_date: matchDate,
      });

      // Check if this was an update or new prediction
      const existingPred = predictions.find(p => p.fixture_id === fixtureId);
      
      if (existingPred) {
        toast.success(`✅ Prediction updated to: ${prediction.toUpperCase()}! You can change this until Wed 23:59`);
      } else {
        toast.success(`✅ Prediction saved: ${prediction.toUpperCase()}! You can change this until Wed 23:59`);
      }
      
      loadUserPredictions();
    } catch (error) {
      if (error.response?.status === 400 && error.response?.data?.detail?.includes('locked')) {
        toast.error('🔒 ' + (error.response?.data?.detail || 'Predictions are locked'));
      } else {
        toast.error('Error: ' + (error.response?.data?.detail || error.message));
      }
      console.error(error);
    }
  };


  const handleDeletePrediction = async (predictionId) => {
    if (!currentUser) {
      toast.error('Please log in to delete predictions');
      return;
    }

    // Confirm deletion
    if (!window.confirm('Are you sure you want to delete this prediction? This action cannot be undone.')) {
      return;
    }

    try {
      await axios.delete(`${API}/predictions/${predictionId}?user_id=${currentUser.id}`);
      toast.success('✅ Prediction deleted successfully');
      loadUserPredictions(); // Reload predictions list
    } catch (error) {
      if (error.response?.status === 400) {
        toast.error('❌ ' + (error.response?.data?.detail || 'Cannot delete this prediction'));
      } else if (error.response?.status === 403) {
        toast.error('❌ You can only delete your own predictions');
      } else {
        toast.error('❌ Error deleting prediction: ' + (error.response?.data?.detail || error.message));
      }
      console.error(error);
    }
  };


  const toggleLeague = (leagueId) => {
    if (selectedLeagues.includes(leagueId)) {
      setSelectedLeagues(selectedLeagues.filter((id) => id !== leagueId));
    } else {
      setSelectedLeagues([...selectedLeagues, leagueId]);
    }
  };

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-GB', {
      weekday: 'short',
      day: 'numeric',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getUserPrediction = (fixtureId) => {
    return predictions.find((p) => p.fixture_id === fixtureId);
  };
  
  const isPredictionLocked = (matchDate) => {
    // Check if match has started or if it's past Wednesday 23:59
    const now = new Date();
    const match = new Date(matchDate);
    
    // Check if match has already started
    if (now >= match) {
      return true;
    }
    
    // Find this week's Wednesday at 23:59
    const currentDayOfWeek = now.getDay(); // 0=Sun, 1=Mon, 2=Tue, 3=Wed, 4=Thu, 5=Fri, 6=Sat
    
    // Calculate days until next Wednesday (or if today is Wed, use today)
    let daysUntilWednesday;
    if (currentDayOfWeek <= 3) {
      // Mon, Tue, Wed - use this week's Wednesday
      daysUntilWednesday = 3 - currentDayOfWeek;
    } else {
      // Thu, Fri, Sat, Sun - use next week's Wednesday
      daysUntilWednesday = (7 - currentDayOfWeek) + 3;
    }
    
    const wednesdayDeadline = new Date(now);
    wednesdayDeadline.setDate(now.getDate() + daysUntilWednesday);
    wednesdayDeadline.setHours(23, 59, 59, 999);
    
    // If we're past this week's Wednesday deadline, lock predictions for matches in the next 7 days
    if (now > wednesdayDeadline) {
      const daysUntilMatch = (match - now) / (1000 * 60 * 60 * 24);
      return daysUntilMatch < 7; // Lock if match is within next 7 days
    }
    
    return false;
  };

  // Show About page
  if (showAbout) {
    return <AboutPage onBack={() => setShowAbout(false)} />;
  }

  // Show Terms page
  if (showTerms) {
    return <TermsPage onBack={() => setShowTerms(false)} />;
  }

  // Show Rules page
  if (showRules) {
    return <RulesPage onBack={() => setShowRules(false)} />;
  }

  // Show Twitter Feed
  if (showTwitter) {
    return <TwitterFeed onBack={() => setShowTwitter(false)} />;
  }

  // Show Team Management
  if (showTeam) {
    return <TeamManagement 
      currentUser={currentUser} 
      onBack={() => {
        setShowTeam(false);
        loadUserTeams(); // Reload teams when returning from team management
      }} 
    />;
  }

  if (!currentUser) {
    return (
      <>
        <Navbar 
          onShowAbout={() => setShowAbout(true)}
          onShowTerms={() => setShowTerms(true)}
          onShowRules={() => setShowRules(true)}
          onShowTwitter={() => setShowTwitter(true)}
          currentUser={null}
        />
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
          <Toaster />
          <Card className="w-full max-w-md">
            <CardHeader className="text-center">
              <div className="flex justify-center mb-4">
                <img 
                  src="/hadfun-logo.jpg" 
                  alt="HadFun Predictor" 
                  className="w-64 h-auto object-contain"
                />
              </div>
              <CardDescription className="text-lg">Predict match results from leagues around the world</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="username">{t.login.username}</Label>
                <Input
                  id="username"
                  data-testid="username-input"
                  placeholder={t.login.placeholder}
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleLogin()}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="email">{t.login.emailForNew}</Label>
                <Input
                  id="email"
                  data-testid="email-input"
                  type="email"
                  placeholder={t.login.emailPlaceholder}
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleLogin()}
                />
              </div>
              <Button
                data-testid="login-button"
                onClick={handleLogin}
                className="w-full bg-indigo-600 hover:bg-indigo-700"
              >
                {t.login.button}
              </Button>
            </CardContent>
          </Card>
        </div>
      </>
    );
  }

  return (
    <div className="min-h-screen football-bg football-pattern">
      <Toaster />
      
      {/* Navigation Bar */}
      <Navbar 
        onShowAbout={() => setShowAbout(true)}
        onShowTerms={() => setShowTerms(true)}
        onShowRules={() => setShowRules(true)}
        onShowTwitter={() => setShowTwitter(true)}
        currentUser={currentUser}
        onLogout={handleLogout}
      />

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <div className="w-full overflow-x-auto pb-2">
            <TabsList className="inline-flex w-auto min-w-full lg:grid lg:w-full lg:max-w-6xl lg:mx-auto lg:grid-cols-6 bg-gradient-to-r from-indigo-100 to-blue-100 p-1 rounded-lg shadow-md">
              <TabsTrigger 
                value="fixtures" 
                data-testid="fixtures-tab"
                className="data-[state=active]:bg-blue-600 data-[state=active]:text-white data-[state=active]:shadow-lg transition-all duration-200 font-semibold text-xs sm:text-sm whitespace-nowrap px-3 sm:px-4"
              >
                <Calendar className="w-4 h-4 sm:mr-1" />
                <span className="hidden sm:inline">{t.tabs.fixtures}</span>
              </TabsTrigger>
              <TabsTrigger 
                value="worldcup" 
                data-testid="worldcup-tab"
                className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-yellow-500 data-[state=active]:to-yellow-600 data-[state=active]:text-white data-[state=active]:shadow-lg transition-all duration-200 font-semibold text-xs sm:text-sm whitespace-nowrap px-3 sm:px-4"
              >
                <Trophy className="w-4 h-4 sm:mr-1" />
                <span className="hidden sm:inline">World Cup</span>
              </TabsTrigger>
              <TabsTrigger 
                value="standings" 
                data-testid="standings-tab"
                className="data-[state=active]:bg-indigo-600 data-[state=active]:text-white data-[state=active]:shadow-lg transition-all duration-200 font-semibold text-xs sm:text-sm whitespace-nowrap px-3 sm:px-4"
              >
                <Trophy className="w-4 h-4 sm:mr-1" />
                <span className="hidden sm:inline">Standings</span>
              </TabsTrigger>
              <TabsTrigger 
                value="predictions" 
                data-testid="predictions-tab"
                className="data-[state=active]:bg-green-600 data-[state=active]:text-white data-[state=active]:shadow-lg transition-all duration-200 font-semibold text-xs sm:text-sm whitespace-nowrap px-3 sm:px-4"
              >
                <TrendingUp className="w-4 h-4 sm:mr-1" />
                <span className="hidden sm:inline">{t.tabs.predictions}</span>
              </TabsTrigger>
              <TabsTrigger 
                value="team" 
                data-testid="team-tab" 
                onClick={() => setShowTeam(true)}
                className="data-[state=active]:bg-purple-600 data-[state=active]:text-white data-[state=active]:shadow-lg transition-all duration-200 font-semibold text-xs sm:text-sm whitespace-nowrap px-3 sm:px-4"
              >
                <Trophy className="w-4 h-4 sm:mr-1" />
                <span className="hidden sm:inline">{t.tabs.team}</span>
              </TabsTrigger>
              <TabsTrigger 
                value="community" 
                data-testid="community-tab"
                className="data-[state=active]:bg-pink-600 data-[state=active]:text-white data-[state=active]:shadow-lg transition-all duration-200 font-semibold text-xs sm:text-sm whitespace-nowrap px-3 sm:px-4"
              >
                <Users className="w-4 h-4 sm:mr-1" />
                <span className="hidden sm:inline">{t.tabs?.community || 'Community'}</span>
              </TabsTrigger>
            </TabsList>
          </div>

          {/* Fixtures Tab */}
          <TabsContent value="fixtures" className="space-y-6">
            {/* Community Welcome Banner */}
            {showCommunityBanner && currentUser && currentUser.profile_completed && (
              <div className="relative bg-gradient-to-r from-purple-500 via-pink-500 to-blue-500 rounded-lg p-6 shadow-lg overflow-hidden">
                {/* Animated background elements */}
                <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full -mr-32 -mt-32"></div>
                <div className="absolute bottom-0 left-0 w-48 h-48 bg-white/10 rounded-full -ml-24 -mb-24"></div>
                
                <div className="relative z-10">
                  {/* Close button */}
                  <button
                    onClick={dismissCommunityBanner}
                    className="absolute top-0 right-0 text-white/80 hover:text-white text-2xl font-bold px-2"
                    aria-label="Dismiss"
                  >
                    ×
                  </button>
                  
                  <div className="max-w-4xl">
                    {/* Icon and Title */}
                    <div className="flex items-center gap-3 mb-3">
                      <div className="bg-white/20 rounded-full p-3">
                        <Users className="h-8 w-8 text-white" />
                      </div>
                      <div>
                        <h3 className="text-2xl font-bold text-white flex items-center gap-2">
                          🎉 New Community Feature!
                        </h3>
                        <p className="text-white/90 text-sm">Connect with other football fans</p>
                      </div>
                    </div>
                    
                    {/* Description */}
                    <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4 mb-4">
                      <p className="text-white text-lg mb-3">
                        Share your predictions, celebrate wins, and connect with your team!
                      </p>
                      <div className="grid md:grid-cols-3 gap-3 text-sm text-white/90">
                        <div className="flex items-start gap-2">
                          <span className="text-xl">💬</span>
                          <span>Post thoughts & reactions</span>
                        </div>
                        <div className="flex items-start gap-2">
                          <span className="text-xl">🏆</span>
                          <span>Celebrate team victories</span>
                        </div>
                        <div className="flex items-start gap-2">
                          <span className="text-xl">📸</span>
                          <span>Share photos & videos</span>
                        </div>
                      </div>
                    </div>
                    
                    {/* CTA Buttons */}
                    <div className="flex flex-wrap gap-3">
                      <Button
                        onClick={goToCommunity}
                        className="bg-white text-purple-600 hover:bg-white/90 font-bold shadow-lg"
                        size="lg"
                      >
                        Check it out! →
                      </Button>
                      <Button
                        onClick={dismissCommunityBanner}
                        variant="outline"
                        className="border-white/30 text-white hover:bg-white/10"
                      >
                        Maybe later
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            {/* League Filter */}
            <Card>
              <CardHeader>
                <CardTitle>{t.messages.selectLeagues}</CardTitle>
                <CardDescription>{t.messages.chooseLeagues}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {leagues.map((league) => (
                    <Button
                      key={league.id}
                      data-testid={`league-${league.id}`}
                      variant={selectedLeagues.includes(league.id) ? 'default' : 'outline'}
                      onClick={() => toggleLeague(league.id)}
                      className="text-sm"
                    >
                      {league.name}
                    </Button>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Filter Options */}
            <Card>
              <CardHeader>
                <CardTitle>View Options</CardTitle>
                <CardDescription>
                  By default, you see current week fixtures (recent results + upcoming matches). 
                  Use "Full Season" to view all past and future matches with scores.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Days Ahead Selector */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Time Range
                    </label>
                    <select
                      value={daysAhead}
                      onChange={(e) => {
                        setDaysAhead(parseInt(e.target.value));
                        setSelectedMatchday(null); // Clear matchday filter
                      }}
                      className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value={7}>Current Week</option>
                      <option value={14}>Next 2 Weeks</option>
                      <option value={28}>Next 4 Weeks (Default)</option>
                      <option value={60}>Next 2 Months</option>
                      <option value={90}>Next 3 Months</option>
                      <option value={365}>Full Season (All Past & Future)</option>
                    </select>
                  </div>

                  {/* Matchday Selector */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Matchday (Optional)
                    </label>
                    <div className="flex gap-2">
                      <input
                        type="number"
                        min="1"
                        max="38"
                        placeholder="e.g., 10"
                        value={selectedMatchday || ''}
                        onChange={(e) => setSelectedMatchday(e.target.value)}
                        className="flex-1 p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                      />
                      {selectedMatchday && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setSelectedMatchday(null)}
                          className="px-3"
                        >
                          Clear
                        </Button>
                      )}
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                      Enter matchday number to view specific round
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Weekly Pot Card */}
            <Card className="bg-gradient-to-br from-emerald-50 via-green-50 to-teal-50 border-2 border-emerald-300 shadow-lg">
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div>
                    <CardTitle className="text-2xl flex items-center gap-2 text-emerald-900">
                      <Trophy className="w-6 h-6 text-yellow-600" />
                      {t.pot.title}
                    </CardTitle>
                    <CardDescription className="text-emerald-700 font-medium">{t.messages.joinCompetition}</CardDescription>
                  </div>
                  {userPayment ? (
                    <Badge className="bg-green-600 text-white font-semibold">✓ Entered</Badge>
                  ) : (
                    <Badge variant="outline" className="border-emerald-600 text-emerald-700">{t.messages.notEntered}</Badge>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                {checkingPayment ? (
                  <div className="text-center py-4">
                    <p className="text-gray-600">Checking payment status...</p>
                  </div>
                ) : userPayment ? (
                  <div className="bg-white rounded-lg p-4">
                    <p className="text-green-700 font-medium mb-2">{t.messages.enteredPot}</p>
                    <p className="text-sm text-gray-600">
                      {t.messages.makePredictions}
                    </p>
                  </div>
                ) : (
                  <div className="bg-white rounded-lg p-4">
                    <p className="text-gray-700 mb-2 font-medium">
                      {t.messages.playForFunTitle}
                    </p>
                    <p className="text-sm text-gray-600 mb-3">
                      {t.messages.playForFunDesc}
                    </p>
                    <Button
                      onClick={() => setShowPaymentModal(true)}
                      className="w-full bg-green-600 hover:bg-green-700"
                    >
                      <Trophy className="w-4 h-4 mr-2" />
                      Choose How to Play
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Fixtures List - Grouped by Matchday */}
            <div className="space-y-6">
              {loading ? (
                <Card>
                  <CardContent className="py-8 text-center">
                    <p className="text-gray-600">{t.fixtures.loading}</p>
                  </CardContent>
                </Card>
              ) : fixtures.length === 0 ? (
                <Card>
                  <CardContent className="py-8 text-center">
                    <div className="space-y-4">
                      <div className="text-4xl">⚽</div>
                      {daysAhead <= 7 && !selectedMatchday ? (
                        <div>
                          <p className="text-lg font-semibold text-gray-700 mb-2">
                            No fixtures this week
                          </p>
                          <p className="text-gray-600">
                            This might be an international break. Use the filters above to view upcoming matches.
                          </p>
                        </div>
                      ) : (
                        <p className="text-gray-600">{t.fixtures.noFixtures}</p>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ) : (
                (() => {
                  // Group fixtures by league and matchday
                  const grouped = {};
                  
                  // BUGFIX: Deduplicate fixtures before grouping to prevent duplicate rendering
                  // This ensures each fixture_id is only rendered once, even if there are
                  // duplicate entries in the fixtures array (defensive programming)
                  const uniqueFixtures = [];
                  const seenIds = new Set();
                  fixtures.forEach(fixture => {
                    if (!seenIds.has(fixture.fixture_id)) {
                      seenIds.add(fixture.fixture_id);
                      uniqueFixtures.push(fixture);
                    }
                  });
                  
                  uniqueFixtures.forEach(fixture => {
                    const leagueName = fixture.league_name || 'Unknown League';
                    const matchdayRaw = fixture.matchday || 'Unknown';
                    // Extract just the number from "Regular Season - 12" format
                    const matchdayNumber = matchdayRaw.match(/\d+/) ? matchdayRaw.match(/\d+/)[0] : matchdayRaw;
                    const key = `${leagueName}|||${matchdayNumber}`;
                    
                    if (!grouped[key]) {
                      grouped[key] = {
                        leagueName,
                        matchday: matchdayNumber,
                        fixtures: []
                      };
                    }
                    grouped[key].fixtures.push(fixture);
                  });

                  // Sort groups by league and matchday number
                  // Regular leagues (Premier League, etc.) - show in ascending matchday order (21, 22, 23, 24)
                  // Tournaments (World Cup, FA Cup) - show chronologically
                  const tournamentLeagues = ['World Cup', 'FA Cup', 'UEFA Champions League', 'UEFA Europa League', 'UEFA Conference League'];
                  
                  // Helper to extract matchday number
                  const getMatchdayNum = (matchday) => {
                    if (!matchday) return 0;
                    const parts = String(matchday).split(/\s+/);
                    for (let i = parts.length - 1; i >= 0; i--) {
                      const num = parseInt(parts[i], 10);
                      if (!isNaN(num)) return num;
                    }
                    return 0;
                  };
                  
                  const sortedGroups = Object.values(grouped).sort((a, b) => {
                    if (a.leagueName !== b.leagueName) {
                      return a.leagueName.localeCompare(b.leagueName);
                    }
                    
                    // Check if this is a tournament league
                    const isTournament = tournamentLeagues.some(t => a.leagueName.includes(t));
                    
                    if (isTournament) {
                      // Tournaments: chronological order by date (earliest first)
                      const getEarliestDate = (fixtures) => {
                        const dates = fixtures.filter(f => f.utc_date).map(f => new Date(f.utc_date).getTime());
                        return dates.length > 0 ? Math.min(...dates) : Infinity;
                      };
                      return getEarliestDate(a.fixtures) - getEarliestDate(b.fixtures);
                    } else {
                      // Regular leagues: sort by matchday NUMBER ascending (21, 22, 23, 24)
                      const matchdayA = getMatchdayNum(a.matchday);
                      const matchdayB = getMatchdayNum(b.matchday);
                      return matchdayA - matchdayB; // Ascending order
                    }
                  });

                  // Sort fixtures within each group
                  sortedGroups.forEach(group => {
                    const isTournament = tournamentLeagues.some(t => group.leagueName.includes(t));
                    
                    group.fixtures.sort((a, b) => {
                      // Handle null dates - put them at the end
                      if (!a.utc_date && !b.utc_date) return 0;
                      if (!a.utc_date) return 1;
                      if (!b.utc_date) return -1;
                      
                      const dateA = new Date(a.utc_date);
                      const dateB = new Date(b.utc_date);
                      // Tournaments: earliest first, Regular leagues: earliest first within matchday
                      return dateA - dateB;
                    });
                  });

                  return sortedGroups.map((group, groupIndex) => (
                    <div key={`${group.leagueName}-${group.matchday}`} className="space-y-4">
                      {/* Matchday Header */}
                      <div className="bg-gradient-to-r from-indigo-600 to-blue-600 text-white rounded-lg p-4 shadow-lg">
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <h3 className="text-2xl font-bold">{group.leagueName}</h3>
                            <p className="text-blue-100 text-lg font-semibold mt-1">
                              {t.fixtures.matchday} {group.matchday}
                            </p>
                          </div>
                          <div className="text-right">
                            <p className="text-sm text-blue-100 mb-1">{group.fixtures.length} {t.fixtures.matches}</p>
                            <div className="bg-white/20 backdrop-blur-sm rounded px-3 py-2">
                              <p className="text-xs text-blue-100 font-medium mb-1">Matchday Period:</p>
                              <p className="text-xs text-white font-bold">
                                📅 {new Date(group.fixtures[0].utc_date).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })}
                              </p>
                              <p className="text-xs text-blue-100 my-1">to</p>
                              <p className="text-xs text-white font-bold">
                                📅 {new Date(group.fixtures[group.fixtures.length - 1].utc_date).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })}
                              </p>
                              {(() => {
                                const now = new Date();
                                const lastMatchDate = new Date(group.fixtures[group.fixtures.length - 1].utc_date);
                                const firstMatchDate = new Date(group.fixtures[0].utc_date);
                                
                                if (now < firstMatchDate) {
                                  return <p className="text-xs text-green-200 mt-2 font-semibold">⏰ Upcoming</p>;
                                } else if (now >= firstMatchDate && now <= lastMatchDate) {
                                  return <p className="text-xs text-yellow-200 mt-2 font-semibold">🟢 In Progress</p>;
                                } else {
                                  return <p className="text-xs text-gray-300 mt-2 font-semibold">✓ Finished</p>;
                                }
                              })()}
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Fixtures in this matchday */}
                      <div className="space-y-3 pl-4 border-l-4 border-indigo-300">
                        {group.fixtures.map((fixture) => {
                          const userPred = getUserPrediction(fixture.fixture_id);
                          return (
                            <Card key={fixture.fixture_id} data-testid={`fixture-${fixture.fixture_id}`} className="match-card hover:shadow-lg transition-all duration-200 border-2 border-gray-200 hover:border-blue-300">
                              <CardHeader className="bg-gradient-to-r from-blue-50 to-indigo-50 py-3">
                                <div className="flex justify-between items-start">
                                  <div>
                                    <CardDescription className="font-medium text-gray-700">{formatDate(fixture.utc_date)}</CardDescription>
                                  </div>
                                  {userPred && (
                                    <Badge variant="default" className="bg-green-600 text-white font-semibold">
                                      ✓ {userPred.prediction.toUpperCase()}
                                    </Badge>
                                  )}
                                </div>
                              </CardHeader>
                              <CardContent className="py-6">
                                <div className="grid grid-cols-3 gap-4 items-center mb-4">
                                  {/* Home Team */}
                                  <div className="text-center">
                                    <p className="font-bold text-xl text-gray-900">{fixture.home_team}</p>
                                  </div>

                                  {/* VS */}
                                  <div className="text-center">
                                    <span className="text-gray-400 font-bold text-sm">{t.fixtures.vs}</span>
                                  </div>

                                  {/* Away Team */}
                                  <div className="text-center">
                                    <p className="font-bold text-xl text-gray-900">{fixture.away_team}</p>
                                  </div>
                                </div>

                                {/* Prediction Buttons - Always show, highlight selected */}
                                {(() => {
                                  const isLocked = isPredictionLocked(fixture.utc_date);
                                  const userPrediction = userPred?.prediction;
                                  const isFinished = fixture.status === 'FINISHED' || fixture.status === 'FINISHED_AET';
                                  const isAbandoned = fixture.status === 'ABANDONED';
                                  const isPostponed = fixture.status === 'POSTPONED';
                                  const hasScore = fixture.score && fixture.score.home !== null && fixture.score.home !== undefined;
                                  const hasPenaltyWinner = fixture.penalty_winner;
                                  
                                  return (
                                    <div className="space-y-2 mt-4">
                                      {/* Match Result - Show for finished matches */}
                                      {isFinished && hasScore && (
                                        <div className="text-center p-3 bg-blue-50 rounded-lg mb-4">
                                          <p className="text-xs text-blue-600 font-semibold mb-1">⚽ FINAL SCORE</p>
                                          <p className="text-2xl font-bold text-blue-900">
                                            {fixture.score.home} - {fixture.score.away}
                                            {hasPenaltyWinner && <span className="text-sm ml-2">(Pens: {hasPenaltyWinner === 'home' ? fixture.home_team : fixture.away_team} win)</span>}
                                          </p>
                                        </div>
                                      )}
                                      
                                      {/* Abandoned Match - Show special message */}
                                      {isAbandoned && (
                                        <div className="text-center p-3 bg-orange-50 rounded-lg mb-4 border border-orange-200">
                                          <p className="text-xs text-orange-600 font-semibold mb-1">⚠️ MATCH ABANDONED</p>
                                          <p className="text-sm text-orange-700">
                                            This match was abandoned. No predictions will be scored.
                                          </p>
                                        </div>
                                      )}
                                      
                                      {/* Postponed Match - Show special message */}
                                      {isPostponed && (
                                        <div className="text-center p-3 bg-gray-100 rounded-lg mb-4 border border-gray-300">
                                          <p className="text-xs text-gray-600 font-semibold mb-1">📅 MATCH POSTPONED</p>
                                          <p className="text-sm text-gray-600">
                                            This match has been postponed. A new date will be announced.
                                          </p>
                                        </div>
                                      )}
                                      
                                      {/* Deadline info */}
                                      {!isLocked && !isFinished && !isAbandoned && !isPostponed && (
                                        <p className="text-xs text-gray-500 text-center">
                                          💡 You can change your prediction until Wed 23:59
                                        </p>
                                      )}
                                      {isLocked && !isFinished && !isAbandoned && !isPostponed && (
                                        <p className="text-xs text-red-600 text-center font-medium">
                                          🔒 Predictions locked
                                        </p>
                                      )}
                                      {isFinished && !hasScore && (
                                        <p className="text-xs text-gray-600 text-center font-medium">
                                          ✓ Match Finished
                                        </p>
                                      )}
                                      
                                      <div className="grid grid-cols-3 gap-2">
                                        <Button
                                          data-testid={`predict-home-${fixture.fixture_id}`}
                                          onClick={() =>
                                            !isLocked && !isAbandoned && !isPostponed && handlePredict(
                                              fixture.fixture_id,
                                              'home',
                                              fixture.league_id,
                                              fixture.utc_date
                                            )
                                          }
                                          disabled={isLocked || isAbandoned || isPostponed}
                                          className={`${
                                            userPrediction === 'home' 
                                              ? 'bg-green-700 ring-4 ring-green-300 font-bold' 
                                              : 'bg-green-600 hover:bg-green-700'
                                          } ${isLocked || isAbandoned || isPostponed ? 'opacity-50 cursor-not-allowed' : ''}`}
                                        >
                                          {userPrediction === 'home' ? '✓ ' : ''}{t.predict.home}
                                        </Button>
                                        <Button
                                          data-testid={`predict-away-${fixture.fixture_id}`}
                                          onClick={() =>
                                            !isLocked && !isAbandoned && !isPostponed && handlePredict(
                                              fixture.fixture_id,
                                              'away',
                                              fixture.league_id,
                                              fixture.utc_date
                                            )
                                          }
                                          disabled={isLocked || isAbandoned || isPostponed}
                                          className={`${
                                            userPrediction === 'away' 
                                              ? 'bg-red-700 ring-4 ring-red-300 font-bold' 
                                              : 'bg-red-600 hover:bg-red-700'
                                          } ${isLocked || isAbandoned || isPostponed ? 'opacity-50 cursor-not-allowed' : ''}`}
                                        >
                                          {userPrediction === 'away' ? '✓ ' : ''}{t.predict.away}
                                        </Button>
                                        <Button
                                          data-testid={`predict-draw-${fixture.fixture_id}`}
                                          onClick={() =>
                                            !isLocked && !isAbandoned && !isPostponed && handlePredict(
                                              fixture.fixture_id,
                                              'draw',
                                              fixture.league_id,
                                              fixture.utc_date
                                            )
                                          }
                                          disabled={isLocked || isAbandoned || isPostponed}
                                          className={`${
                                            userPrediction === 'draw' 
                                              ? 'bg-amber-600 ring-4 ring-amber-300 font-bold' 
                                              : 'bg-amber-500 hover:bg-amber-600'
                                          } ${isLocked || isAbandoned || isPostponed ? 'opacity-50 cursor-not-allowed' : ''} text-white`}
                                        >
                                          {userPrediction === 'draw' ? '✓ ' : ''}{t.predict.draw}
                                        </Button>
                                      </div>
                                    </div>
                                  );
                                })()}
                              </CardContent>
                            </Card>
                          );
                        })}
                      </div>
                    </div>
                  ));
                })()
              )}
            </div>
          </TabsContent>

          {/* World Cup 2026 Tab */}
          <TabsContent value="worldcup">
            <WorldCupGroups />
          </TabsContent>

          {/* My Predictions Tab */}
          <TabsContent value="predictions">
            <Card>
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div>
                    <CardTitle>{t.tabs.predictions}</CardTitle>
                    <CardDescription>{t.messages.viewAllPredictions || "View all your predictions and results"}</CardDescription>
                  </div>
                  {/* Show current team with selector if multiple teams */}
                  {userTeams.length > 0 && (
                    <div className="bg-indigo-50 px-4 py-2 rounded-lg border border-indigo-200">
                      <p className="text-xs text-gray-600 mb-2">{t.team?.teamName || "Team"}</p>
                      {userTeams.length === 1 ? (
                        <>
                          <p className="font-bold text-indigo-600">{selectedTeam?.name}</p>
                          <p className="text-xs text-gray-500">
                            {selectedTeam?.play_mode === 'pot' 
                              ? `£${selectedTeam?.stake_amount} ${t.team?.weeklyPot || 'pot'}` 
                              : t.team?.playingForFun || 'Playing for fun'}
                          </p>
                        </>
                      ) : (
                        <Select
                          value={selectedTeam?.id}
                          onValueChange={(teamId) => {
                            const team = userTeams.find(ut => ut.team.id === teamId);
                            if (team) setSelectedTeam(team.team);
                          }}
                        >
                          <SelectTrigger className="w-48 bg-white">
                            <SelectValue>
                              {selectedTeam?.name || 'Select Team'}
                            </SelectValue>
                          </SelectTrigger>
                          <SelectContent>
                            {userTeams.map((userTeam) => (
                              <SelectItem key={userTeam.team.id} value={userTeam.team.id}>
                                <div>
                                  <p className="font-medium">{userTeam.team.name}</p>
                                  <p className="text-xs text-gray-500">
                                    {userTeam.team.play_mode === 'pot' 
                                      ? `£${userTeam.team.stake_amount} pot` 
                                      : 'For fun'}
                                  </p>
                                </div>
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      )}
                    </div>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                {predictions.length === 0 ? (
                  <p className="text-center text-gray-600 py-8">{t.messages.noPredictionsYet}</p>
                ) : (
                  <div className="space-y-6">
                    {/* Group predictions by league only - NO matchday subgroups */}
                    {(() => {
                      const groupedByLeague = predictions.reduce((acc, pred) => {
                        // Check multiple possible field names for league
                        const leagueName = pred.league_name || pred.league || 'Unknown League';
                        if (!acc[leagueName]) {
                          acc[leagueName] = [];
                        }
                        acc[leagueName].push(pred);
                        return acc;
                      }, {});

                      return Object.entries(groupedByLeague)
                        .sort(([leagueA], [leagueB]) => {
                          // Sort leagues alphabetically
                          if (leagueA === 'Unknown League') return 1;
                          if (leagueB === 'Unknown League') return -1;
                          return leagueA.localeCompare(leagueB);
                        })
                        .map(([leagueName, leaguePredictions]) => {
                          // Sort all predictions in this league by date
                          leaguePredictions.sort((a, b) => {
                            const dateA = new Date(a.utc_date || a.match_date);
                            const dateB = new Date(b.utc_date || b.match_date);
                            return dateA - dateB;
                          });
                          
                          return (
                          <div key={leagueName} className="mb-6 border-2 border-indigo-200 rounded-lg overflow-hidden">
                            {/* League Header */}
                            <div className="bg-gradient-to-r from-indigo-600 to-blue-600 text-white p-4">
                              <h3 className="text-2xl font-bold flex items-center gap-2">
                                <Trophy className="w-6 h-6" />
                                {leagueName}
                              </h3>
                              <p className="text-sm text-indigo-100 mt-1">
                                {leaguePredictions.length} {leaguePredictions.length === 1 ? 'prediction' : 'predictions'}
                              </p>
                            </div>
                            
                            {/* All predictions for this league */}
                            <div className="p-4 space-y-3">
                              {leaguePredictions.map((pred) => (
                                <div
                                  key={pred.id}
                                  className="bg-gradient-to-r from-gray-50 to-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                                >
                                  {/* Match Details */}
                                  <div className="flex justify-between items-start mb-3">
                                    <div className="flex-1">
                                      <div className="flex items-center gap-2 mb-1">
                                        <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                                          {pred.league || 'League'}
                                        </span>
                                        {pred.status === 'FINISHED' && (
                                          <span className="text-xs text-green-600 bg-green-50 px-2 py-1 rounded font-medium">
                                            ✓ Finished
                                          </span>
                                        )}
                                        {pred.status === 'ABANDONED' && (
                                          <span className="text-xs text-orange-600 bg-orange-50 px-2 py-1 rounded font-medium">
                                            ⚠️ Abandoned
                                          </span>
                                        )}
                                      </div>
                                      <p className="text-lg font-bold text-gray-800">
                                        {pred.home_team || 'Home'} <span className="text-gray-400">vs</span> {pred.away_team || 'Away'}
                                      </p>
                                      <p className="text-sm text-gray-600">
                                        {(pred.utc_date || pred.match_date) ? formatDate(pred.utc_date || pred.match_date) : 'Date TBD'}
                                      </p>
                                    </div>
                                    
                                    {/* Score Display */}
                                    {pred.status === 'FINISHED' && pred.score && pred.score.home !== null && pred.score.away !== null && (
                                      <div className="bg-indigo-50 px-4 py-2 rounded-lg">
                                        <p className="text-xs text-gray-600 mb-1">Final Score</p>
                                        <p className="text-2xl font-bold text-indigo-600">
                                          {pred.score.home} - {pred.score.away}
                                        </p>
                                      </div>
                                    )}
                                    
                                    {/* Abandoned Match Display */}
                                    {pred.status === 'ABANDONED' && (
                                      <div className="bg-orange-50 px-4 py-2 rounded-lg border border-orange-200">
                                        <p className="text-xs text-orange-600 mb-1">Match Status</p>
                                        <p className="text-sm font-bold text-orange-700">
                                          ABANDONED
                                        </p>
                                        <p className="text-xs text-orange-600">No points awarded</p>
                                      </div>
                                    )}
                                  </div>

                                  {/* Prediction & Result */}
                                  <div className="flex justify-between items-center pt-3 border-t border-gray-200">
                                    <div>
                                      <p className="text-xs text-gray-600 mb-1">Your Prediction</p>
                                      <Badge variant="outline" className="text-base font-semibold px-3 py-1">
                                        {pred.prediction === 'home' ? (
                                          <span className="text-green-700">HOME: {pred.home_team || 'Home Team'}</span>
                                        ) : pred.prediction === 'away' ? (
                                          <span className="text-red-700">AWAY: {pred.away_team || 'Away Team'}</span>
                                        ) : (
                                          <span className="text-amber-700">DRAW</span>
                                        )}
                                      </Badge>
                                    </div>
                                    
                                    <div className="flex items-center gap-3">
                                      {/* Delete button - only show for pending predictions (not abandoned or finished) */}
                                      {pred.result === 'pending' && pred.status !== 'FINISHED' && pred.status !== 'ABANDONED' && (
                                        <Button
                                          variant="ghost"
                                          size="sm"
                                          onClick={() => handleDeletePrediction(pred.id)}
                                          className="text-red-600 hover:text-red-700 hover:bg-red-50"
                                          title="Delete this prediction"
                                        >
                                          🗑️ Cancel
                                        </Button>
                                      )}
                                      
                                      <div className="text-right">
                                        <p className="text-xs text-gray-600 mb-1">Result</p>
                                        {pred.result === 'correct' ? (
                                          <Badge className="bg-green-600">
                                            ✓ Correct
                                          </Badge>
                                        ) : pred.result === 'incorrect' ? (
                                          <Badge className="bg-red-600">
                                            ✗ Wrong
                                          </Badge>
                                        ) : (
                                          <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">
                                            ⏳ Pending
                                          </Badge>
                                        )}
                                      </div>
                                    </div>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        );
                      });
                    })()}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Leaderboard tab removed - now only in My Team section */}

          {/* Standings Tab */}
          <TabsContent value="standings">
            <div className="space-y-6">
              {loading ? (
                <Card>
                  <CardContent className="py-8 text-center">
                    <p className="text-gray-600">Loading standings...</p>
                  </CardContent>
                </Card>
              ) : Object.keys(standings).length === 0 ? (
                <Card>
                  <CardContent className="py-8 text-center">
                    <p className="text-gray-600">No standings available</p>
                  </CardContent>
                </Card>
              ) : (
                Object.entries(standings).map(([leagueId, leagueData]) => (
                  <Card key={leagueId}>
                    <CardHeader className="bg-gradient-to-r from-indigo-50 to-blue-50">
                      <div className="flex items-center gap-3">
                        {leagueData.logo && (
                          <img src={leagueData.logo} alt={leagueData.league_name} className="w-10 h-10" />
                        )}
                        <div>
                          <CardTitle className="text-xl">{leagueData.league_name}</CardTitle>
                          <CardDescription>{leagueData.country} - Season {leagueData.season}</CardDescription>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent className="p-0">
                      <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                          <thead className="bg-gray-100 border-b-2 border-gray-300">
                            <tr>
                              <th className="text-left p-2 font-semibold w-12">#</th>
                              <th className="text-left p-2 font-semibold">Team</th>
                              <th className="text-center p-2 font-semibold w-12">P</th>
                              <th className="text-center p-2 font-semibold w-12">W</th>
                              <th className="text-center p-2 font-semibold w-12">D</th>
                              <th className="text-center p-2 font-semibold w-12">L</th>
                              <th className="text-center p-2 font-semibold w-12">GF</th>
                              <th className="text-center p-2 font-semibold w-12">GA</th>
                              <th className="text-center p-2 font-semibold w-12">GD</th>
                              <th className="text-center p-2 font-semibold w-12">Pts</th>
                              <th className="text-center p-2 font-semibold w-20">Form</th>
                            </tr>
                          </thead>
                          <tbody>
                            {leagueData.standings.map((team, index) => (
                              <tr 
                                key={team.rank} 
                                className={`border-b hover:bg-gray-50 ${
                                  team.description?.includes('Champions League') ? 'bg-blue-50' :
                                  team.description?.includes('Europa League') ? 'bg-green-50' :
                                  team.description?.includes('Relegation') ? 'bg-red-50' : ''
                                }`}
                              >
                                <td className="p-2 font-semibold text-gray-700">{team.rank}</td>
                                <td className="p-2">
                                  <div className="flex items-center gap-2">
                                    {team.team_logo && (
                                      <img src={team.team_logo} alt={team.team_name} className="w-6 h-6" />
                                    )}
                                    <span className="font-medium">{team.team_name}</span>
                                  </div>
                                </td>
                                <td className="p-2 text-center text-gray-600">{team.played}</td>
                                <td className="p-2 text-center text-green-600 font-semibold">{team.won}</td>
                                <td className="p-2 text-center text-gray-600">{team.drawn}</td>
                                <td className="p-2 text-center text-red-600">{team.lost}</td>
                                <td className="p-2 text-center text-gray-600">{team.goals_for}</td>
                                <td className="p-2 text-center text-gray-600">{team.goals_against}</td>
                                <td className={`p-2 text-center font-semibold ${team.goal_difference > 0 ? 'text-green-600' : team.goal_difference < 0 ? 'text-red-600' : 'text-gray-600'}`}>
                                  {team.goal_difference > 0 ? '+' : ''}{team.goal_difference}
                                </td>
                                <td className="p-2 text-center font-bold text-indigo-600">{team.points}</td>
                                <td className="p-2 text-center text-xs">
                                  <div className="flex gap-0.5 justify-center">
                                    {team.form?.split('').slice(-5).map((result, i) => (
                                      <span 
                                        key={i}
                                        className={`w-5 h-5 flex items-center justify-center rounded ${
                                          result === 'W' ? 'bg-green-500 text-white' :
                                          result === 'D' ? 'bg-gray-400 text-white' :
                                          result === 'L' ? 'bg-red-500 text-white' : 'bg-gray-200'
                                        }`}
                                      >
                                        {result}
                                      </span>
                                    ))}
                                  </div>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          </TabsContent>

          {/* Community Tab */}
          <TabsContent value="community">
            <SocialFeed currentUser={currentUser} onTabChange={setActiveTab} />
          </TabsContent>
        </Tabs>
      </div>

      {/* Footer */}
      <div className="container mx-auto px-4 py-6 mt-8 border-t border-gray-200">
        <div className="text-center text-sm text-gray-600">
          <p>Contact us: <a href="mailto:info@hadfun.co.uk" className="text-indigo-600 hover:underline">info@hadfun.co.uk</a></p>
          <p className="mt-2 text-xs text-gray-500">© 2025 HadFun. All rights reserved.</p>
          <p className="mt-1 text-xs text-gray-400">
            "HadFun", "Football With Purpose", and "Charity Begins at Home" are trademarks of HadFun.
          </p>
          <p className="mt-1 text-xs text-gray-400">
            Governed by the laws of England and Wales.
          </p>
        </div>
      </div>

      {/* Payment Modal */}
      <PaymentModal
        isOpen={showPaymentModal}
        onClose={() => setShowPaymentModal(false)}
        onPayment={handlePayment}
        userEmail={currentUser?.email}
        userName={currentUser?.username}
      />

      {/* Profile Setup Modal */}
      {currentUser && !currentUser.profile_completed && (
        <ProfileSetup
          open={showProfileSetup}
          onClose={() => setShowProfileSetup(false)}
          user={currentUser}
          onProfileCompleted={handleProfileCompleted}
        />
      )}

      {/* Admin Dashboard Modal */}
      {showAdminDashboard && (
        <AdminDashboard onClose={() => setShowAdminDashboard(false)} />
      )}

      {/* Admin Button - Only visible to admin users */}
      {currentUser && ADMIN_USERS.includes(currentUser.username?.toLowerCase()) && (
        <button
          onClick={() => setShowAdminDashboard(true)}
          className="fixed bottom-4 right-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white p-3 rounded-full shadow-lg hover:shadow-xl transition-all z-40"
          title="Admin Dashboard"
        >
          <BarChart3 className="h-6 w-6" />
        </button>
      )}
    </div>
  );
}

export default App;
