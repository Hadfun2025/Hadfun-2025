import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';
import { Users, Trophy, MessageCircle, Shield, Copy, UserPlus, Heart, X } from 'lucide-react';
import axios from 'axios';
import { useLanguage } from '../LanguageContext';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export function TeamManagement({ currentUser, onBack }) {
  const { t } = useLanguage();
  const [userTeam, setUserTeam] = useState(null);
  const [teamMembers, setTeamMembers] = useState([]);
  const [teamLeaderboard, setTeamLeaderboard] = useState([]);
  const [teamMessages, setTeamMessages] = useState([]);
  const [availableLeagues, setAvailableLeagues] = useState([]);
  const [selectedLeague, setSelectedLeague] = useState('');
  const [leagueLeaderboards, setLeagueLeaderboards] = useState({}); // Map: league name -> leaderboard data
  const [loading, setLoading] = useState(true);
  
  // Create team form
  const [teamName, setTeamName] = useState('');
  const [stakeAmount, setStakeAmount] = useState(5);
  const [playMode, setPlayMode] = useState('fun');
  
  // Join team form
  const [joinCode, setJoinCode] = useState('');
  
  // Message form
  const [newMessage, setNewMessage] = useState('');
  
  // Email invitation form
  const [inviteEmail, setInviteEmail] = useState('');
  const [sendingInvite, setSendingInvite] = useState(false);
  
  // Community Support
  const [nominations, setNominations] = useState([]);
  const [donations, setDonations] = useState([]);
  const [showNominateForm, setShowNominateForm] = useState(false);
  const [nomineeUserId, setNomineeUserId] = useState('');
  const [nominationReason, setNominationReason] = useState('');
  const [isAnonymous, setIsAnonymous] = useState(false);
  
  // User Search & Invitations
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [searching, setSearching] = useState(false);
  const [pendingInvitations, setPendingInvitations] = useState([]);
  const [emailInviteSent, setEmailInviteSent] = useState(false);
  const [lastInvitedUser, setLastInvitedUser] = useState('');

  const loadPendingInvitations = async () => {
    try {
      const response = await axios.get(`${API}/users/${currentUser.id}/invitations`);
      setPendingInvitations(response.data);
    } catch (error) {
      console.error('Error loading invitations:', error);
    }
  };

  useEffect(() => {
    loadUserTeam();
  }, [currentUser]);

  useEffect(() => {
    if (userTeam) {
      loadTeamData();
    }
  }, [userTeam]);

  useEffect(() => {
    if (!userTeam) {
      loadPendingInvitations();
    }
  }, [currentUser]);

  useEffect(() => {
    if (selectedLeague && selectedLeague !== 'overall' && userTeam) {
      loadLeagueLeaderboard(selectedLeague);
    }
  }, [selectedLeague, userTeam]);

  const loadUserTeam = async () => {
    try {
      const response = await axios.get(`${API}/user/${currentUser.id}/team`);
      if (response.data.team) {
        setUserTeam(response.data.team);
      }
    } catch (error) {
      console.error('Error loading team:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadTeamData = async () => {
    if (!userTeam) return;
    
    try {
      // Load members
      const membersRes = await axios.get(`${API}/teams/${userTeam.id}/members`);
      setTeamMembers(membersRes.data);
      
      // Load leaderboard
      const leaderboardRes = await axios.get(`${API}/teams/${userTeam.id}/leaderboard`);
      setTeamLeaderboard(leaderboardRes.data);
      
      // Load available leagues
      const leaguesRes = await axios.get(`${API}/teams/${userTeam.id}/leaderboard/by-league`);
      const leagues = leaguesRes.data.map(item => item.league_name);
      setAvailableLeagues(leagues);
      
      // Set default selected league to the first one
      if (leagues.length > 0 && !selectedLeague) {
        setSelectedLeague(leagues[0]);
      }
      
      // Preload all league leaderboards
      const leaderboardsMap = {};
      leaguesRes.data.forEach(item => {
        leaderboardsMap[item.league_name] = item.leaderboard;
      });
      console.log('League leaderboards loaded:', leaderboardsMap);
      setLeagueLeaderboards(leaderboardsMap);
      
      // Load messages
      const messagesRes = await axios.get(`${API}/teams/${userTeam.id}/messages`);
      setTeamMessages(messagesRes.data);
      
      // Load community support
      loadCommunitySupport();
    } catch (error) {
      console.error('Error loading team data:', error);
    }
  };

  const loadLeagueLeaderboard = async (league) => {
    if (!userTeam || !league) return;
    
    try {
      const response = await axios.get(`${API}/teams/${userTeam.id}/leaderboard/by-league`, {
        params: { league }
      });
      // Store this league's data in the map
      setLeagueLeaderboards(prev => ({
        ...prev,
        [league]: response.data
      }));
    } catch (error) {
      console.error('Error loading league leaderboard:', error);
      setLeagueLeaderboards(prev => ({
        ...prev,
        [league]: []
      }));
    }
  };

  const handleCreateTeam = async () => {
    if (!teamName.trim()) {
      toast.error('Please enter a team name');
      return;
    }

    try {
      const response = await axios.post(`${API}/teams`, {
        name: teamName,
        admin_user_id: currentUser.id,
        admin_username: currentUser.username,
        stake_amount: stakeAmount,
        play_mode: playMode,
        is_private: true
      });

      toast.success(`Team "${teamName}" created!`);
      setUserTeam(response.data);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Error creating team');
    }
  };

  const handleJoinTeam = async () => {
    if (!joinCode.trim()) {
      toast.error('Please enter a join code');
      return;
    }

    try {
      const response = await axios.post(`${API}/teams/join`, {
        user_id: currentUser.id,
        username: currentUser.username,
        join_code: joinCode.toUpperCase()
      });

      toast.success(response.data.message);
      setUserTeam(response.data.team);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Error joining team');
    }
  };

  const handleSendMessage = async () => {
    if (!newMessage.trim()) return;

    try {
      await axios.post(`${API}/teams/${userTeam.id}/messages`, {
        team_id: userTeam.id,
        user_id: currentUser.id,
        username: currentUser.username,
        message: newMessage
      });

      setNewMessage('');
      loadTeamData();
      toast.success('Message posted!');
    } catch (error) {
      toast.error('Error posting message');
    }
  };

  const copyJoinCode = () => {
    navigator.clipboard.writeText(userTeam.join_code);
    toast.success('Join code copied to clipboard!');
  };

  const handleSendInvite = async () => {
    if (!inviteEmail.trim()) {
      toast.error('Please enter an email address');
      return;
    }

    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(inviteEmail)) {
      toast.error('Please enter a valid email address');
      return;
    }

    setSendingInvite(true);
    try {
      await axios.post(`${API}/teams/${userTeam.id}/invite`, null, {
        params: {
          recipient_email: inviteEmail,
          inviter_name: currentUser.username
        }
      });

      toast.success(`Invitation sent to ${inviteEmail}!`);
      setEmailInviteSent(true);
      setInviteEmail('');
      // Auto-hide the message after 5 seconds
      setTimeout(() => setEmailInviteSent(false), 5000);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Error sending invitation');
      setEmailInviteSent(false);
    } finally {
      setSendingInvite(false);
    }
  };

  const loadCommunitySupport = async () => {
    if (!userTeam) return;
    
    try {
      const [nomsRes, donsRes] = await Promise.all([
        axios.get(`${API}/teams/${userTeam.id}/nominations?status=active`),
        axios.get(`${API}/teams/${userTeam.id}/donations`)
      ]);
      
      setNominations(nomsRes.data);
      setDonations(donsRes.data);
    } catch (error) {
      console.error('Error loading community support:', error);
    }
  };

  const handleCreateNomination = async () => {
    if (!nomineeUserId || !nominationReason.trim()) {
      toast.error('Please select a member and provide a reason');
      return;
    }

    try {
      const nominee = teamMembers.find(m => m.user_id === nomineeUserId);
      
      await axios.post(`${API}/teams/${userTeam.id}/nominations`, {
        team_id: userTeam.id,
        nominee_user_id: nomineeUserId,
        nominee_username: nominee.username,
        nominated_by_user_id: currentUser.id,
        nominated_by_username: currentUser.username,
        reason: nominationReason,
        is_anonymous: isAnonymous
      });

      toast.success('Nomination created with compassion ❤️');
      setShowNominateForm(false);
      setNomineeUserId('');
      setNominationReason('');
      setIsAnonymous(false);
      loadCommunitySupport();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Error creating nomination');
    }
  };

  const handleCancelNomination = async (nominationId) => {
    try {
      await axios.post(`${API}/teams/${userTeam.id}/nominations/${nominationId}/cancel`, {}, {
        params: { user_id: currentUser.id }
      });
      
      toast.success('Nomination cancelled');
      loadCommunitySupport();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Error cancelling nomination');
    }
  };


  const handleSearchUsers = async () => {
    if (searchQuery.length < 2) {
      toast.error('Please enter at least 2 characters');
      return;
    }

    setSearching(true);
    try {
      const response = await axios.get(`${API}/users/search`, {
        params: { q: searchQuery }
      });
      setSearchResults(response.data);
    } catch (error) {
      toast.error('Error searching users');
      console.error(error);
    } finally {
      setSearching(false);
    }
  };

  const handleInviteUser = async (invitedUserId, invitedUsername) => {
    try {
      await axios.post(`${API}/teams/${userTeam.id}/invite-user`, null, {
        params: {
          inviter_user_id: currentUser.id,
          invited_user_id: invitedUserId
        }
      });
      
      toast.success(`✅ Invitation sent to ${invitedUsername}!`);
      setLastInvitedUser(invitedUsername);
      // Remove user from search results after successful invite
      setSearchResults(searchResults.filter(u => u.id !== invitedUserId));
      // Auto-hide the message after 5 seconds
      setTimeout(() => setLastInvitedUser(''), 5000);
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Error sending invitation';
      
      // Show specific messages for different error types
      if (errorMsg.includes('already has a pending invitation')) {
        toast.info(`${invitedUsername} already has a pending invitation from your team`);
        // Remove from search results since they're already invited
        setSearchResults(searchResults.filter(u => u.id !== invitedUserId));
      } else if (errorMsg.includes('already a team member')) {
        toast.info(`${invitedUsername} is already a member of your team`);
        setSearchResults(searchResults.filter(u => u.id !== invitedUserId));
      } else {
        toast.error(errorMsg);
      }
    }
  };

  const handleAcceptInvitation = async (invitationId, teamName) => {
    try {
      await axios.post(`${API}/teams/invitations/${invitationId}/accept`, null, {
        params: { user_id: currentUser.id }
      });
      
      toast.success(`Joined ${teamName}!`);
      loadUserTeam();
      loadPendingInvitations();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Error accepting invitation');
    }
  };

  const handleDeclineInvitation = async (invitationId) => {
    try {
      await axios.post(`${API}/teams/invitations/${invitationId}/decline`, null, {
        params: { user_id: currentUser.id }
      });
      
      toast.success('Invitation declined');
      loadPendingInvitations();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Error declining invitation');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <p className="text-gray-600">{t.team.loading}</p>
      </div>
    );
  }

  // No team yet - show create/join options
  if (!userTeam) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8">
        <div className="container mx-auto px-4 max-w-4xl">
          {/* Back Button */}
          <Button onClick={onBack} variant="outline" className="mb-4">
            ← {t.team.backToPredictions}
          </Button>

          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="text-3xl flex items-center gap-2">
                <Users className="w-8 h-8 text-indigo-600" />
                {t.team.joinOrCreate}
              </CardTitle>
              <CardDescription>
                {t.team.teamsPrivate}
              </CardDescription>
            </CardHeader>
          </Card>

          <Tabs defaultValue="create" className="space-y-6">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="create">{t.team.createTeam}</TabsTrigger>
              <TabsTrigger value="join">{t.team.joinTeam}</TabsTrigger>
            </TabsList>

            {/* Create Team */}
            <TabsContent value="create">
              <Card>
                <CardHeader>
                  <CardTitle>{t.team.createYourTeam}</CardTitle>
                  <CardDescription>
                    {t.team.youllBeAdmin}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label>{t.team.teamName}</Label>
                    <Input
                      placeholder={t.team.teamNamePlaceholder}
                      value={teamName}
                      onChange={(e) => setTeamName(e.target.value)}
                    />
                  </div>

                  <div>
                    <Label>{t.team.playMode}</Label>
                    <div className="flex gap-4 mt-2">
                      <Button
                        variant={playMode === 'fun' ? 'default' : 'outline'}
                        onClick={() => setPlayMode('fun')}
                      >
                        {t.team.playForFun}
                      </Button>
                      <Button
                        variant={playMode === 'pot' ? 'default' : 'outline'}
                        onClick={() => setPlayMode('pot')}
                      >
                        {t.team.weeklyPot}
                      </Button>
                    </div>
                  </div>

                  {playMode === 'pot' && (
                    <div>
                      <Label>{t.team.weeklyStake}</Label>
                      <div className="flex gap-2 mt-2">
                        {[2, 3, 5].map((amount) => (
                          <Button
                            key={amount}
                            variant={stakeAmount === amount ? 'default' : 'outline'}
                            onClick={() => setStakeAmount(amount)}
                          >
                            £{amount}
                          </Button>
                        ))}
                      </div>
                    </div>
                  )}

                  <Button
                    onClick={handleCreateTeam}
                    className="w-full bg-indigo-600 hover:bg-indigo-700"
                  >
                    {t.team.createTeam}
                  </Button>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Join Team */}
            <TabsContent value="join">
              <Card>
                <CardHeader>
                  <CardTitle>{t.team.joinExisting}</CardTitle>
                  <CardDescription>
                    {t.team.enterJoinCode}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label>{t.team.joinCode}</Label>
                    <Input
                      placeholder={t.team.joinCodePlaceholder}
                      value={joinCode}
                      onChange={(e) => setJoinCode(e.target.value.toUpperCase())}
                      maxLength={8}
                    />
                  </div>

                  <Button
                    onClick={handleJoinTeam}
                    className="w-full bg-green-600 hover:bg-green-700"
                  >
                    <UserPlus className="w-4 h-4 mr-2" />
                    {t.team.joinTeam}
                  </Button>
                </CardContent>
              </Card>
            </TabsContent>

          </Tabs>

          {/* Pending Invitations */}
          {pendingInvitations.length > 0 && (
            <Card className="mt-6 border-2 border-green-300 bg-green-50">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <UserPlus className="w-6 h-6 text-green-600" />
                  Team Invitations ({pendingInvitations.length})
                </CardTitle>
                <CardDescription>
                  You've been invited to join teams!
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {pendingInvitations.map((invitation) => (
                  <div key={invitation.id} className="bg-white rounded-lg p-4 border border-green-200">
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <p className="font-bold text-lg text-gray-900">{invitation.team_name}</p>
                        <p className="text-sm text-gray-600">
                          Invited by <span className="font-semibold">{invitation.inviter_username}</span>
                        </p>
                        <p className="text-xs text-gray-500 mt-1">
                          {new Date(invitation.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        onClick={() => handleAcceptInvitation(invitation.id, invitation.team_name)}
                        className="bg-green-600 hover:bg-green-700"
                        size="sm"
                      >
                        Accept
                      </Button>
                      <Button
                        onClick={() => handleDeclineInvitation(invitation.id)}
                        variant="outline"
                        size="sm"
                      >
                        Decline
                      </Button>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}

        </div>
      </div>
    );
  }

  // Has team - show team interface
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8">
      <div className="container mx-auto px-4 max-w-6xl">
        {/* Back Button */}
        <Button onClick={onBack} variant="outline" className="mb-4">
          ← {t.team.backToPredictions}
        </Button>

        {/* Team Header */}
        <Card className="mb-6">
          <CardHeader>
            <div className="flex justify-between items-start">
              <div>
                <CardTitle className="text-3xl flex items-center gap-2">
                  <Shield className="w-8 h-8 text-indigo-600" />
                  {userTeam.name}
                </CardTitle>
                <CardDescription className="mt-2">
                  {teamMembers.length} {t.team.members} • {userTeam.play_mode === 'pot' ? `£${userTeam.stake_amount} ${t.team.weeklyPot.toLowerCase()}` : t.team.playingForFun}
                </CardDescription>
              </div>
              <div className="text-right">
                <Label className="text-xs text-gray-600">{t.team.joinCode}</Label>
                <div className="flex items-center gap-2 mt-1">
                  <Badge className="text-lg px-3 py-1 bg-indigo-600">{userTeam.join_code}</Badge>
                  <Button size="sm" variant="outline" onClick={copyJoinCode}>
                    <Copy className="w-4 h-4" />
                  </Button>
                </div>
                <p className="text-xs text-gray-500 mt-1">{t.team.shareCode}</p>
              </div>
            </div>
          </CardHeader>
        </Card>

        {/* Team Content Tabs */}
        <Tabs defaultValue="forum" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="forum">
              <MessageCircle className="w-4 h-4 mr-2" />
              {t.team.teamForum}
            </TabsTrigger>
            <TabsTrigger value="leaderboard">
              <Trophy className="w-4 h-4 mr-2" />
              {t.tabs.leaderboard}
            </TabsTrigger>
            <TabsTrigger value="members">
              <Users className="w-4 h-4 mr-2" />
              {t.team.teamMembers}
            </TabsTrigger>
            <TabsTrigger value="support">
              <Heart className="w-4 h-4 mr-2" />
              {t.communityCare?.title?.split(' - ')[0] || 'Community Care'}
            </TabsTrigger>
          </TabsList>

          {/* Team Forum */}
          <TabsContent value="forum">
            <Card>
              <CardHeader>
                <CardTitle>{t.team.teamChat}</CardTitle>
                <CardDescription>
                  {t.team.talkStrategy}
                </CardDescription>
              </CardHeader>
              <CardContent>
                {/* Messages */}
                <div className="space-y-3 mb-4 max-h-96 overflow-y-auto">
                  {teamMessages.length === 0 ? (
                    <p className="text-center text-gray-500 py-8">
                      {t.team.noMessages}
                    </p>
                  ) : (
                    teamMessages.map((msg) => (
                      <div
                        key={msg.id}
                        className={`p-3 rounded-lg ${
                          msg.user_id === currentUser.id ? 'bg-indigo-50 ml-8' : 'bg-gray-50 mr-8'
                        }`}
                      >
                        <div className="flex justify-between items-start mb-1">
                          <span className="font-bold text-sm">{msg.username}</span>
                          <span className="text-xs text-gray-500">
                            {new Date(msg.created_at).toLocaleString('en-GB', {
                              day: 'numeric',
                              month: 'short',
                              hour: '2-digit',
                              minute: '2-digit'
                            })}
                          </span>
                        </div>
                        <p className="text-gray-700">{msg.message}</p>
                      </div>
                    ))
                  )}
                </div>

                {/* New Message */}
                <div className="flex gap-2">
                  <Input
                    placeholder={t.team.typeMessage}
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                  />
                  <Button onClick={handleSendMessage}>
                    {t.team.send}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Team Leaderboard */}
          <TabsContent value="leaderboard">
            <Card>
              <CardHeader>
                <CardTitle>{t.team.teamLeaderboard}</CardTitle>
                <CardDescription>{t.team.privateToTeam}</CardDescription>
              </CardHeader>
              <CardContent>
                {/* League Filter Tabs */}
                <Tabs value={selectedLeague} onValueChange={setSelectedLeague} className="w-full">
                  <TabsList className="grid w-full mb-4" style={{ gridTemplateColumns: `repeat(${availableLeagues.length}, minmax(0, 1fr))` }}>
                    {availableLeagues.map(league => (
                      <TabsTrigger key={league} value={league} className="text-xs sm:text-sm">
                        {league}
                      </TabsTrigger>
                    ))}
                  </TabsList>

                  {/* League-Specific Leaderboards */}
                  {availableLeagues.map(league => {
                    const leagueData = leagueLeaderboards[league] || [];
                    console.log(`Rendering ${league} leaderboard:`, leagueData);
                    return (
                      <TabsContent key={league} value={league}>
                        {leagueData.length === 0 ? (
                          <p className="text-center text-gray-500 py-8">
                            Loading {league} leaderboard...
                          </p>
                        ) : (
                          <div className="overflow-x-auto">
                            <table className="w-full border-collapse">
                              <thead>
                                <tr className="bg-indigo-600 text-white border-b-2 border-indigo-700">
                                  <th className="text-left p-3 font-semibold w-16">#</th>
                                  <th className="text-left p-3 font-semibold">Player</th>
                                  <th className="text-center p-3 font-semibold w-24">Wins</th>
                                  <th className="text-center p-3 font-semibold w-20">Correct</th>
                                  <th className="text-center p-3 font-semibold w-20">Total</th>
                                  <th className="text-center p-3 font-semibold w-24">PTS</th>
                                </tr>
                              </thead>
                              <tbody>
                                {leagueData.map((entry) => (
                                  <tr
                                    key={entry.username}
                                    className={`border-b border-gray-200 hover:bg-gray-50 ${
                                      entry.username === currentUser.username ? 'bg-indigo-50 font-semibold' : ''
                                    }`}
                                  >
                                    <td className="p-3 text-gray-600">
                                      {entry.rank === 1 ? '🥇' : entry.rank === 2 ? '🥈' : entry.rank === 3 ? '🥉' : entry.rank}
                                    </td>
                                    <td className="p-3 font-medium text-gray-900">
                                      {entry.username}
                                      {entry.username === currentUser.username && (
                                        <span className="ml-2 text-xs bg-indigo-500 text-white px-2 py-0.5 rounded">You</span>
                                      )}
                                    </td>
                                    <td className="p-3 text-center text-gray-700">{entry.matchday_wins || 0}</td>
                                    <td className="p-3 text-center text-gray-700">{entry.correct_predictions}</td>
                                    <td className="p-3 text-center text-gray-700">{entry.total_predictions}</td>
                                    <td className="p-3 text-center font-bold text-indigo-600 text-lg">{entry.total_points || 0}</td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        )}
                      </TabsContent>
                    );
                  })}
                </Tabs>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Duplicate Members tab removed - using the one below with translations */}

          {/* Team Members */}
          <TabsContent value="members">
            <Card>
              <CardHeader>
                <CardTitle>{t.team.teamMembers}</CardTitle>
                <CardDescription>
                  {t.team.allMembersCanPredict}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Email Invitation */}
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h3 className="font-bold text-blue-900 mb-3 flex items-center gap-2">
                    <UserPlus className="w-5 h-5" />
                    {t.team.inviteViaEmail}
                  </h3>
                  <div className="flex gap-2 mb-2">
                    <Input
                      type="email"
                      placeholder={t.team.emailPlaceholder}
                      value={inviteEmail}
                      onChange={(e) => setInviteEmail(e.target.value)}
                    />
                    <Button
                      onClick={handleSendInvite}
                      disabled={sendingInvite}
                      className="bg-indigo-600 hover:bg-indigo-700"
                    >
                      {sendingInvite ? t.team.sending : t.team.sendInvite}
                    </Button>
                  </div>
                  <p className="text-sm text-gray-600">
                    {t.team.emailInviteNote}
                  </p>
                  
                  {/* Success Message */}
                  {emailInviteSent && (
                    <div className="mt-3 bg-green-50 border-l-4 border-green-500 p-3 rounded animate-pulse">
                      <p className="text-green-800 font-semibold flex items-center gap-2">
                        ✅ Message Sent! 
                        <span className="text-sm font-normal">They'll receive an email invitation to join your team.</span>
                      </p>
                    </div>
                  )}
                </div>


                {/* User Search & Invite */}
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <h3 className="font-bold text-green-900 mb-3 flex items-center gap-2">
                    <Users className="w-5 h-5" />
                    Search & Invite Users
                  </h3>
                  <div className="flex gap-2 mb-3">
                    <Input
                      placeholder="Search by username..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && handleSearchUsers()}
                    />
                    <Button
                      onClick={handleSearchUsers}
                      disabled={searching || searchQuery.length < 2}
                      className="bg-green-600 hover:bg-green-700"
                    >
                      {searching ? 'Searching...' : 'Search'}
                    </Button>
                  </div>
                  <p className="text-sm text-gray-600 mb-3">
                    Search for users by username and send them a team invitation
                  </p>
                  
                  {/* Search Results */}
                  {searchResults.length > 0 && (
                    <div className="space-y-2 mt-3">
                      <p className="text-sm font-semibold text-gray-700">Search Results:</p>
                      {searchResults.map((user) => (
                        <div key={user.id} className="flex justify-between items-center bg-white p-3 rounded border border-green-100">
                          <span className="font-medium text-gray-900">{user.username}</span>
                          <Button
                            size="sm"
                            onClick={() => handleInviteUser(user.id, user.username)}
                            className="bg-green-600 hover:bg-green-700"
                          >
                            <UserPlus className="w-4 h-4 mr-1" />
                            Invite
                          </Button>
                        </div>
                      ))}
                    </div>
                  )}
                  
                  {searchResults.length === 0 && searchQuery && !searching && (
                    <p className="text-sm text-gray-500 text-center py-2">
                      No users found matching "{searchQuery}"
                    </p>
                  )}
                  
                  {/* Success Message */}
                  {lastInvitedUser && (
                    <div className="mt-3 bg-green-50 border-l-4 border-green-500 p-3 rounded animate-pulse">
                      <p className="text-green-800 font-semibold flex items-center gap-2">
                        ✅ Invitation Sent to {lastInvitedUser}! 
                        <span className="text-sm font-normal">They'll see your team invitation when they log in.</span>
                      </p>
                    </div>
                  )}
                </div>


                {/* Current Members List */}
                <div>
                  <h3 className="font-bold mb-3">{t.team.currentMembers}</h3>
                  {teamMembers.length === 0 ? (
                    <p className="text-center text-gray-500 py-4">
                      {t.team.noMembersYet}
                    </p>
                  ) : (
                    <div className="space-y-2">
                      {teamMembers.map((member) => (
                        <div
                          key={member.user_id}
                          className={`flex justify-between items-center p-3 rounded-lg ${
                            member.user_id === currentUser.id ? 'bg-indigo-50 border-2 border-indigo-200' : 'bg-gray-50'
                          }`}
                        >
                          <div>
                            <p className="font-bold">{member.username}</p>
                            <p className="text-xs text-gray-500">
                              {t.team.joined} {new Date(member.joined_at).toLocaleDateString()}
                            </p>
                          </div>
                          {member.user_id === userTeam.admin_user_id && (
                            <Badge variant="secondary">
                              <Shield className="w-3 h-3 mr-1" />
                              {t.team.admin}
                            </Badge>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>


          {/* Community Support Tab */}
          <TabsContent value="support">
            <Card className="border-2 border-pink-200">
              <CardHeader className="bg-gradient-to-r from-pink-50 to-purple-50">
                <CardTitle className="flex items-center gap-2 text-2xl">
                  <Heart className="w-7 h-7 text-pink-600" />
                  {t.communityCare?.title || 'Community Care - Charity Begins at Home'}
                </CardTitle>
                <CardDescription className="text-base">
                  {t.communityCare?.subtitle || 'Supporting teammates through hardship. When someone wins, they can choose to share their winnings with a teammate in need. No pressure - entirely their choice.'}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6 mt-4">
                
                {/* Nominate Button */}
                {!showNominateForm && (
                  <Button 
                    onClick={() => setShowNominateForm(true)}
                    className="bg-pink-600 hover:bg-pink-700"
                  >
                    <Heart className="w-4 h-4 mr-2" />
                    {t.communityCare?.nominateButton || 'Nominate a Teammate for Support'}
                  </Button>
                )}
                
                {/* Nomination Form */}
                {showNominateForm && (
                  <Card className="border-2 border-pink-300">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Heart className="w-5 h-5 text-pink-600" />
                        {t.communityCare?.nominateTitle || 'Nominate Someone'}
                      </CardTitle>
                      <CardDescription>
                        {t.communityCare?.nominateDesc || 'Know a teammate facing hardship? Nominate them respectfully and with compassion.'}
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div>
                        <Label>{t.communityCare?.selectMember || 'Select Team Member'}</Label>
                        <select
                          value={nomineeUserId}
                          onChange={(e) => setNomineeUserId(e.target.value)}
                          className="w-full p-2 border rounded-md"
                        >
                          <option value="">{t.communityCare?.chooseMember || 'Choose a teammate...'}</option>
                          {teamMembers
                            .filter(m => m.user_id !== currentUser.id)
                            .map(member => (
                              <option key={member.user_id} value={member.user_id}>
                                {member.username}
                              </option>
                            ))}
                        </select>
                      </div>
                      
                      <div>
                        <Label>{t.communityCare?.reason || 'Reason (Brief & Respectful)'}</Label>
                        <textarea
                          value={nominationReason}
                          onChange={(e) => setNominationReason(e.target.value)}
                          placeholder={t.communityCare?.reasonPlaceholder || 'e.g., Facing medical costs, lost job recently, family emergency...'}
                          className="w-full p-2 border rounded-md h-24"
                          maxLength={200}
                        />
                        <p className="text-xs text-gray-500 mt-1">
                          {nominationReason.length}/200 {t.communityCare?.reasonChars || 'characters'}
                        </p>
                      </div>
                      
                      <div className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          id="anonymous"
                          checked={isAnonymous}
                          onChange={(e) => setIsAnonymous(e.target.checked)}
                          className="w-4 h-4"
                        />
                        <Label htmlFor="anonymous" className="text-sm">
                          {t.communityCare?.keepAnonymous || 'Keep my name anonymous'}
                        </Label>
                      </div>
                      
                      <div className="flex gap-2">
                        <Button 
                          onClick={handleCreateNomination}
                          className="bg-pink-600 hover:bg-pink-700"
                        >
                          {t.communityCare?.submitNomination || 'Submit Nomination'}
                        </Button>
                        <Button 
                          onClick={() => {
                            setShowNominateForm(false);
                            setNomineeUserId('');
                            setNominationReason('');
                            setIsAnonymous(false);
                          }}
                          variant="outline"
                        >
                          {t.communityCare?.cancel || 'Cancel'}
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                )}
                
                {/* Active Nominations */}
                <div>
                  <h3 className="font-bold text-lg mb-3 flex items-center gap-2">
                    <Heart className="w-5 h-5 text-pink-600" />
                    {t.communityCare?.currentNominations || 'Current Nominations'} ({nominations.length})
                  </h3>
                  
                  {nominations.length === 0 ? (
                    <Card className="bg-gray-50">
                      <CardContent className="py-8 text-center text-gray-500">
                        <Heart className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                        <p>{t.communityCare?.noNominationsYet || 'No active nominations yet.'}</p>
                        <p className="text-sm mt-1">{t.communityCare?.beFirstNominate || 'Be the first to nominate someone who needs support.'}</p>
                      </CardContent>
                    </Card>
                  ) : (
                    <div className="space-y-3">
                      {nominations.map(nom => (
                        <Card key={nom.id} className="border-l-4 border-l-pink-400">
                          <CardContent className="pt-4">
                            <div className="flex justify-between items-start">
                              <div className="flex-1">
                                <p className="font-bold text-lg flex items-center gap-2">
                                  🤝 {nom.nominee_username}
                                </p>
                                <p className="text-gray-700 mt-2 leading-relaxed">
                                  {nom.reason}
                                </p>
                                <p className="text-xs text-gray-500 mt-3">
                                  {t.communityCare?.nominatedBy || 'Nominated by'} {nom.is_anonymous ? (t.communityCare?.anonymous || 'Anonymous') : nom.nominated_by_username} • {new Date(nom.created_at).toLocaleDateString()}
                                </p>
                              </div>
                              
                              {(nom.nominated_by_user_id === currentUser.id || userTeam.admin_user_id === currentUser.id) && (
                                <Button
                                  size="sm"
                                  variant="ghost"
                                  onClick={() => handleCancelNomination(nom.id)}
                                  className="text-gray-400 hover:text-red-600"
                                >
                                  <X className="w-4 h-4" />
                                </Button>
                              )}
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  )}
                </div>
                
                {/* Donation History */}
                <div>
                  <h3 className="font-bold text-lg mb-3 flex items-center gap-2">
                    <Trophy className="w-5 h-5 text-yellow-600" />
                    {t.communityCare?.actsOfKindness || 'Acts of Kindness'} ({donations.length})
                  </h3>
                  
                  {donations.length === 0 ? (
                    <Card className="bg-gray-50">
                      <CardContent className="py-6 text-center text-gray-500">
                        <p className="text-sm">{t.communityCare?.noDonationsYet || 'No donations yet. When a winner shares their winnings, it will appear here.'}</p>
                      </CardContent>
                    </Card>
                  ) : (
                    <div className="space-y-2">
                      {donations.map(don => (
                        <div 
                          key={don.id}
                          className="flex items-center gap-3 p-3 bg-gradient-to-r from-pink-50 to-purple-50 rounded-lg border border-pink-200"
                        >
                          <Heart className="w-5 h-5 text-pink-600 flex-shrink-0" />
                          <div className="flex-1">
                            <p className="text-sm">
                              <span className="font-bold">{don.winner_username}</span> {t.communityCare?.donated || 'donated'}{' '}
                              <span className="font-bold text-pink-600">£{don.amount}</span> {t.communityCare?.to || 'to'}{' '}
                              <span className="font-bold">{don.recipient_username}</span>
                            </p>
                            {don.message && (
                              <p className="text-xs text-gray-600 mt-1 italic">"{don.message}"</p>
                            )}
                            <p className="text-xs text-gray-500 mt-1">
                              {new Date(don.created_at).toLocaleDateString()}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
                
                {/* Info Box */}
                <Card className="bg-blue-50 border-blue-200">
                  <CardContent className="pt-4">
                    <h4 className="font-bold text-blue-900 mb-2">{t.communityCare?.howItWorksTitle || 'How It Works'}</h4>
                    <ul className="text-sm text-blue-800 space-y-1">
                      <li>• {t.communityCare?.howItWorksPoint1 || 'Any member can nominate a teammate facing hardship'}</li>
                      <li>• {t.communityCare?.howItWorksPoint2 || 'Winners see nominations when they win the weekly pot'}</li>
                      <li>• {t.communityCare?.howItWorksPoint3 || 'Winners can choose to donate any amount (no pressure!)'}</li>
                      <li>• {t.communityCare?.howItWorksPoint4 || 'All donations are recorded to celebrate community spirit'}</li>
                    </ul>
                  </CardContent>
                </Card>
                
              </CardContent>
            </Card>
          </TabsContent>

        </Tabs>
      </div>
    </div>
  );
}
