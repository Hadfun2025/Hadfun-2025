import { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { 
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  AreaChart, Area
} from 'recharts';
import { 
  Users, TrendingUp, Trophy, Activity, Clock, Target,
  RefreshCw, BarChart3, PieChart as PieChartIcon
} from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

const COLORS = ['#6366f1', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#ec4899', '#14b8a6'];

export function AdminDashboard({ onClose }) {
  const [overview, setOverview] = useState(null);
  const [userActivity, setUserActivity] = useState(null);
  const [leaguePopularity, setLeaguePopularity] = useState(null);
  const [retention, setRetention] = useState(null);
  const [topUsers, setTopUsers] = useState(null);
  const [featureUsage, setFeatureUsage] = useState(null);
  const [peakTimes, setPeakTimes] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  const fetchAllData = async () => {
    setLoading(true);
    try {
      const [overviewRes, activityRes, leagueRes, retentionRes, topUsersRes, featureRes, peakRes] = await Promise.all([
        axios.get(`${API}/admin/analytics/overview`),
        axios.get(`${API}/admin/analytics/user-activity`),
        axios.get(`${API}/admin/analytics/league-popularity`),
        axios.get(`${API}/admin/analytics/user-retention`),
        axios.get(`${API}/admin/analytics/top-users`),
        axios.get(`${API}/admin/analytics/feature-usage`),
        axios.get(`${API}/admin/analytics/peak-times`)
      ]);

      setOverview(overviewRes.data);
      setUserActivity(activityRes.data);
      setLeaguePopularity(leagueRes.data);
      setRetention(retentionRes.data);
      setTopUsers(topUsersRes.data);
      setFeatureUsage(featureRes.data);
      setPeakTimes(peakRes.data);
    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAllData();
  }, []);

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <Card className="w-96">
          <CardContent className="p-8 text-center">
            <RefreshCw className="h-12 w-12 animate-spin mx-auto text-indigo-600 mb-4" />
            <p className="text-lg font-medium">Loading Analytics...</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black/50 overflow-y-auto z-50">
      <div className="min-h-screen p-4 md:p-8">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-t-xl p-6 text-white">
            <div className="flex justify-between items-center">
              <div>
                <h1 className="text-2xl font-bold flex items-center gap-2">
                  <BarChart3 className="h-8 w-8" />
                  Admin Analytics Dashboard
                </h1>
                <p className="text-indigo-200 mt-1">Key performance metrics and insights</p>
              </div>
              <div className="flex gap-2">
                <Button 
                  variant="secondary" 
                  size="sm" 
                  onClick={fetchAllData}
                  className="bg-white/20 hover:bg-white/30 text-white"
                >
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Refresh
                </Button>
                <Button 
                  variant="secondary" 
                  size="sm" 
                  onClick={onClose}
                  className="bg-white/20 hover:bg-white/30 text-white"
                >
                  Close
                </Button>
              </div>
            </div>

            {/* Tab Navigation */}
            <div className="flex gap-2 mt-6 flex-wrap">
              {['overview', 'activity', 'users', 'engagement'].map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`px-4 py-2 rounded-lg font-medium transition-all ${
                    activeTab === tab 
                      ? 'bg-white text-indigo-600' 
                      : 'bg-white/20 text-white hover:bg-white/30'
                  }`}
                >
                  {tab.charAt(0).toUpperCase() + tab.slice(1)}
                </button>
              ))}
            </div>
          </div>

          {/* Main Content */}
          <div className="bg-gray-50 rounded-b-xl p-6">
            {activeTab === 'overview' && overview && (
              <div className="space-y-6">
                {/* Key Metrics Cards */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white">
                    <CardContent className="p-4">
                      <div className="flex items-center gap-3">
                        <Users className="h-10 w-10 opacity-80" />
                        <div>
                          <p className="text-blue-100 text-sm">Total Users</p>
                          <p className="text-3xl font-bold">{overview.users.total}</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="bg-gradient-to-br from-green-500 to-green-600 text-white">
                    <CardContent className="p-4">
                      <div className="flex items-center gap-3">
                        <Activity className="h-10 w-10 opacity-80" />
                        <div>
                          <p className="text-green-100 text-sm">DAU / WAU / MAU</p>
                          <p className="text-2xl font-bold">
                            {overview.users.dau} / {overview.users.wau} / {overview.users.mau}
                          </p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="bg-gradient-to-br from-purple-500 to-purple-600 text-white">
                    <CardContent className="p-4">
                      <div className="flex items-center gap-3">
                        <Target className="h-10 w-10 opacity-80" />
                        <div>
                          <p className="text-purple-100 text-sm">Total Predictions</p>
                          <p className="text-3xl font-bold">{overview.predictions.total}</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="bg-gradient-to-br from-amber-500 to-amber-600 text-white">
                    <CardContent className="p-4">
                      <div className="flex items-center gap-3">
                        <Trophy className="h-10 w-10 opacity-80" />
                        <div>
                          <p className="text-amber-100 text-sm">Accuracy Rate</p>
                          <p className="text-3xl font-bold">{overview.predictions.accuracy_rate}%</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>

                {/* Secondary Metrics */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <Card>
                    <CardContent className="p-4 text-center">
                      <p className="text-gray-500 text-sm">Predictions Today</p>
                      <p className="text-2xl font-bold text-indigo-600">{overview.predictions.today}</p>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardContent className="p-4 text-center">
                      <p className="text-gray-500 text-sm">Predictions This Week</p>
                      <p className="text-2xl font-bold text-indigo-600">{overview.predictions.this_week}</p>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardContent className="p-4 text-center">
                      <p className="text-gray-500 text-sm">Total Teams</p>
                      <p className="text-2xl font-bold text-indigo-600">{overview.teams.total}</p>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardContent className="p-4 text-center">
                      <p className="text-gray-500 text-sm">Preds per User</p>
                      <p className="text-2xl font-bold text-indigo-600">{overview.engagement.predictions_per_user}</p>
                    </CardContent>
                  </Card>
                </div>

                {/* Charts Row */}
                <div className="grid md:grid-cols-2 gap-6">
                  {/* League Popularity Pie Chart */}
                  {leaguePopularity && (
                    <Card>
                      <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                          <PieChartIcon className="h-5 w-5" />
                          League Popularity
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <ResponsiveContainer width="100%" height={300}>
                          <PieChart>
                            <Pie
                              data={leaguePopularity.league_popularity.slice(0, 6)}
                              dataKey="predictions"
                              nameKey="league"
                              cx="50%"
                              cy="50%"
                              outerRadius={100}
                              label={({name, percent}) => `${name.split(' ')[0]} ${(percent * 100).toFixed(0)}%`}
                            >
                              {leaguePopularity.league_popularity.slice(0, 6).map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                              ))}
                            </Pie>
                            <Tooltip />
                          </PieChart>
                        </ResponsiveContainer>
                      </CardContent>
                    </Card>
                  )}

                  {/* Peak Usage Times */}
                  {peakTimes && (
                    <Card>
                      <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                          <Clock className="h-5 w-5" />
                          Peak Usage Times
                        </CardTitle>
                        <CardDescription>
                          Predictions by hour of day
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <ResponsiveContainer width="100%" height={300}>
                          <BarChart data={peakTimes.hourly_distribution}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="label" tick={{fontSize: 10}} />
                            <YAxis />
                            <Tooltip />
                            <Bar dataKey="predictions" fill="#6366f1" radius={[4, 4, 0, 0]} />
                          </BarChart>
                        </ResponsiveContainer>
                      </CardContent>
                    </Card>
                  )}
                </div>
              </div>
            )}

            {activeTab === 'activity' && userActivity && (
              <div className="space-y-6">
                {/* Activity Chart */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <TrendingUp className="h-5 w-5" />
                      User Activity (Last 30 Days)
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={400}>
                      <AreaChart data={userActivity.daily_activity}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="day_name" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Area 
                          type="monotone" 
                          dataKey="active_users" 
                          stackId="1"
                          stroke="#6366f1" 
                          fill="#6366f1" 
                          fillOpacity={0.6}
                          name="Active Users"
                        />
                        <Area 
                          type="monotone" 
                          dataKey="predictions" 
                          stackId="2"
                          stroke="#22c55e" 
                          fill="#22c55e" 
                          fillOpacity={0.6}
                          name="Predictions"
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>

                {/* New Signups Chart */}
                <Card>
                  <CardHeader>
                    <CardTitle>New User Signups</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={250}>
                      <LineChart data={userActivity.daily_activity}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" tick={{fontSize: 10}} />
                        <YAxis />
                        <Tooltip />
                        <Line 
                          type="monotone" 
                          dataKey="new_signups" 
                          stroke="#f59e0b" 
                          strokeWidth={2}
                          dot={{fill: '#f59e0b'}}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </div>
            )}

            {activeTab === 'users' && topUsers && (
              <div className="space-y-6">
                <div className="grid md:grid-cols-2 gap-6">
                  {/* Top Predictors */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Trophy className="h-5 w-5 text-amber-500" />
                        Top Predictors (by Volume)
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        {topUsers.top_predictors.map((user, index) => (
                          <div key={user.user_id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                            <div className="flex items-center gap-3">
                              <span className={`w-8 h-8 rounded-full flex items-center justify-center font-bold ${
                                index === 0 ? 'bg-amber-400 text-white' :
                                index === 1 ? 'bg-gray-300 text-gray-700' :
                                index === 2 ? 'bg-amber-600 text-white' :
                                'bg-gray-200 text-gray-600'
                              }`}>
                                {index + 1}
                              </span>
                              <span className="font-medium">{user.username}</span>
                            </div>
                            <div className="text-right">
                              <p className="font-bold text-indigo-600">{user.total_predictions}</p>
                              <p className="text-xs text-gray-500">{user.accuracy}% accuracy</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>

                  {/* Top Accuracy */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Target className="h-5 w-5 text-green-500" />
                        Top Accuracy (min 10 predictions)
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        {topUsers.top_accuracy.map((user, index) => (
                          <div key={user.user_id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                            <div className="flex items-center gap-3">
                              <span className={`w-8 h-8 rounded-full flex items-center justify-center font-bold ${
                                index === 0 ? 'bg-green-500 text-white' :
                                index === 1 ? 'bg-green-400 text-white' :
                                index === 2 ? 'bg-green-300 text-gray-700' :
                                'bg-gray-200 text-gray-600'
                              }`}>
                                {index + 1}
                              </span>
                              <span className="font-medium">{user.username}</span>
                            </div>
                            <div className="text-right">
                              <p className="font-bold text-green-600">{user.accuracy}%</p>
                              <p className="text-xs text-gray-500">{user.correct_predictions}/{user.total_predictions}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </div>
            )}

            {activeTab === 'engagement' && retention && featureUsage && (
              <div className="space-y-6">
                {/* Retention Metrics */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <Card className="border-2 border-green-200">
                    <CardContent className="p-4 text-center">
                      <p className="text-gray-500 text-sm">7-Day Retention</p>
                      <p className="text-3xl font-bold text-green-600">{retention.retention_7_day}%</p>
                      <p className="text-xs text-gray-400">{retention.active_last_7_days} users</p>
                    </CardContent>
                  </Card>
                  <Card className="border-2 border-blue-200">
                    <CardContent className="p-4 text-center">
                      <p className="text-gray-500 text-sm">30-Day Retention</p>
                      <p className="text-3xl font-bold text-blue-600">{retention.retention_30_day}%</p>
                      <p className="text-xs text-gray-400">{retention.active_last_30_days} users</p>
                    </CardContent>
                  </Card>
                  <Card className="border-2 border-red-200">
                    <CardContent className="p-4 text-center">
                      <p className="text-gray-500 text-sm">Churn Rate</p>
                      <p className="text-3xl font-bold text-red-600">{retention.churn_rate}%</p>
                      <p className="text-xs text-gray-400">{retention.inactive_users} inactive</p>
                    </CardContent>
                  </Card>
                  <Card className="border-2 border-purple-200">
                    <CardContent className="p-4 text-center">
                      <p className="text-gray-500 text-sm">Total Users</p>
                      <p className="text-3xl font-bold text-purple-600">{retention.total_users}</p>
                    </CardContent>
                  </Card>
                </div>

                {/* Feature Usage */}
                <Card>
                  <CardHeader>
                    <CardTitle>Feature Usage</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid md:grid-cols-2 gap-6">
                      <div>
                        <h4 className="font-medium mb-3">Community Features</h4>
                        <div className="space-y-2">
                          <div className="flex justify-between items-center p-2 bg-gray-50 rounded">
                            <span>Posts</span>
                            <Badge>{featureUsage.community.posts}</Badge>
                          </div>
                          <div className="flex justify-between items-center p-2 bg-gray-50 rounded">
                            <span>Comments</span>
                            <Badge>{featureUsage.community.comments}</Badge>
                          </div>
                          <div className="flex justify-between items-center p-2 bg-gray-50 rounded">
                            <span>Team Messages</span>
                            <Badge>{featureUsage.community.team_messages}</Badge>
                          </div>
                        </div>
                      </div>
                      <div>
                        <h4 className="font-medium mb-3">Predictions by Competition</h4>
                        <div className="space-y-2">
                          <div className="flex justify-between items-center p-2 bg-gray-50 rounded">
                            <span>Premier League</span>
                            <Badge variant="secondary">{featureUsage.predictions_by_competition.premier_league}</Badge>
                          </div>
                          <div className="flex justify-between items-center p-2 bg-gray-50 rounded">
                            <span>FA Cup</span>
                            <Badge variant="secondary">{featureUsage.predictions_by_competition.fa_cup}</Badge>
                          </div>
                          <div className="flex justify-between items-center p-2 bg-gray-50 rounded">
                            <span>World Cup</span>
                            <Badge variant="secondary">{featureUsage.predictions_by_competition.world_cup}</Badge>
                          </div>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default AdminDashboard;
