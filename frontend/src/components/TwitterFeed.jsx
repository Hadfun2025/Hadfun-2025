import { useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ArrowLeft, ExternalLink, Tv, Newspaper, Video, Radio } from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useLanguage } from '../LanguageContext';

export function TwitterFeed({ onBack }) {
  const { t } = useLanguage();
  useEffect(() => {
    // Load Twitter widget script
    const script = document.createElement('script');
    script.src = 'https://platform.twitter.com/widgets.js';
    script.async = true;
    document.body.appendChild(script);

    return () => {
      // Cleanup
      if (document.body.contains(script)) {
        document.body.removeChild(script);
      }
    };
  }, []);

  const footballSites = [
    {
      name: 'BBC Sport Football',
      url: 'https://www.bbc.co.uk/sport/football',
      description: 'FREE highlights, live scores, Match of the Day',
      icon: Tv,
      category: 'news'
    },
    {
      name: 'Sky Sports Football',
      url: 'https://www.skysports.com/football',
      description: 'Live updates, extended highlights, analysis',
      icon: Tv,
      category: 'news'
    },
    {
      name: 'ESPN FC',
      url: 'https://www.espn.com/soccer/',
      description: 'International coverage, highlights, analysis',
      icon: Newspaper,
      category: 'news'
    },
    {
      name: 'Goal.com',
      url: 'https://www.goal.com',
      description: 'Global football news, transfer rumors',
      icon: Newspaper,
      category: 'news'
    },
    {
      name: 'The Guardian Football',
      url: 'https://www.theguardian.com/football',
      description: 'Quality journalism, match reports, analysis',
      icon: Newspaper,
      category: 'news'
    },
    {
      name: 'Football.London',
      url: 'https://www.football.london',
      description: 'Premier League news & updates',
      icon: Newspaper,
      category: 'news'
    },
    {
      name: 'talkSPORT',
      url: 'https://talksport.com/football/',
      description: 'Live radio, podcasts, breaking news',
      icon: Radio,
      category: 'news'
    },
    {
      name: 'FourFourTwo',
      url: 'https://www.fourfourtwo.com',
      description: 'Tactical analysis, features, interviews',
      icon: Newspaper,
      category: 'news'
    },
  ];

  const videoSites = [
    {
      name: 'BBC Sport Highlights',
      url: 'https://www.bbc.co.uk/sport/football/video',
      description: 'FREE Match of the Day highlights on BBC website',
      icon: Video,
      type: 'direct'
    },
    {
      name: 'Sky Sports Videos',
      url: 'https://www.skysports.com/watch/video/sports/football',
      description: 'FREE highlights on Sky Sports website',
      icon: Video,
      type: 'direct'
    },
    {
      name: 'ITV Sport Football',
      url: 'https://www.itv.com/sport/football',
      description: 'FREE highlights & match coverage',
      icon: Video,
      type: 'direct'
    },
    {
      name: 'BT Sport Videos',
      url: 'https://www.bt.com/sport/football',
      description: 'Selected FREE highlights & clips',
      icon: Video,
      type: 'direct'
    },
    {
      name: 'Dailymotion Football',
      url: 'https://www.dailymotion.com/search/football%20highlights/videos',
      description: 'Match highlights (YouTube alternative)',
      icon: Video,
      type: 'alternative'
    },
    {
      name: 'ScoreBat Highlights',
      url: 'https://www.scorebat.com/live-football-highlights/',
      description: 'FREE match highlights from all leagues',
      icon: Video,
      type: 'direct'
    },
  ];

  const liveScoreSites = [
    {
      name: 'LiveScore',
      url: 'https://www.livescore.com',
      description: 'Real-time scores, ALL leagues',
      icon: Tv,
    },
    {
      name: 'FlashScore',
      url: 'https://www.flashscore.com',
      description: 'Live scores, stats, head-to-head',
      icon: Tv,
    },
    {
      name: 'SofaScore',
      url: 'https://www.sofascore.com',
      description: 'Detailed stats, live commentary',
      icon: Tv,
    },
    {
      name: 'OneFootball',
      url: 'https://onefootball.com',
      description: 'Personalized news & scores',
      icon: Tv,
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8">
      <div className="container mx-auto px-4 max-w-7xl">
        <Button onClick={onBack} variant="outline" className="mb-6">
          <ArrowLeft className="w-4 h-4 mr-2" />
          {t.news.backToApp}
        </Button>

        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="text-3xl">{t.news.title}</CardTitle>
            <CardDescription>{t.news.subtitle}</CardDescription>
          </CardHeader>
        </Card>

        <Tabs defaultValue="news" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="news">{t.news.newsSites}</TabsTrigger>
            <TabsTrigger value="videos">{t.news.videos}</TabsTrigger>
            <TabsTrigger value="scores">{t.news.liveScores}</TabsTrigger>
            <TabsTrigger value="social">{t.news.social}</TabsTrigger>
          </TabsList>

          {/* News Sites Tab */}
          <TabsContent value="news">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {footballSites.map((site) => {
                const Icon = site.icon;
                return (
                  <Card key={site.name} className="hover:shadow-lg transition-shadow">
                    <CardHeader>
                      <div className="flex items-start justify-between">
                        <div className="flex items-center gap-2">
                          <Icon className="w-5 h-5 text-indigo-600" />
                          <CardTitle className="text-lg">{site.name}</CardTitle>
                        </div>
                        <a
                          href={site.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-indigo-600 hover:text-indigo-700"
                        >
                          <ExternalLink className="w-5 h-5" />
                        </a>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-gray-600">{site.description}</p>
                      <a
                        href={site.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-block mt-3 text-sm text-indigo-600 hover:underline font-medium"
                      >
                        {t.news.visitSite}
                      </a>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </TabsContent>

          {/* Videos Tab */}
          <TabsContent value="videos">
            <Card className="mb-6 bg-blue-50 border-blue-200">
              <CardContent className="pt-6">
                <p className="text-sm text-blue-900">
                  {t.news.noYouTube}
                </p>
              </CardContent>
            </Card>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {videoSites.map((site) => {
                const Icon = site.icon;
                const cardColor = site.type === 'direct' ? 'bg-green-50' : 'bg-orange-50';
                const textColor = site.type === 'direct' ? 'text-green-600' : 'text-orange-600';
                const badgeText = site.type === 'direct' ? t.news.directAccess : t.news.alternative;
                
                return (
                  <Card key={site.name} className={`hover:shadow-lg transition-shadow ${cardColor}`}>
                    <CardHeader>
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <Icon className={`w-5 h-5 ${textColor}`} />
                          <CardTitle className="text-lg">{site.name}</CardTitle>
                        </div>
                        <a
                          href={site.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className={`${textColor} hover:opacity-80`}
                        >
                          <ExternalLink className="w-5 h-5" />
                        </a>
                      </div>
                      <span className={`text-xs px-2 py-1 rounded ${site.type === 'direct' ? 'bg-green-200 text-green-800' : 'bg-orange-200 text-orange-800'}`}>
                        {badgeText}
                      </span>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-gray-700">{site.description}</p>
                      <a
                        href={site.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className={`inline-block mt-3 text-sm ${textColor} hover:underline font-medium`}
                      >
                        {t.news.watchHighlights}
                      </a>
                    </CardContent>
                  </Card>
                );
              })}
            </div>

            {/* Additional info */}
            <Card className="mt-6 bg-gradient-to-r from-orange-50 to-red-50 border-orange-200">
              <CardHeader>
                <CardTitle className="text-orange-900">📺 {t.news?.moreHighlights || "More FREE Highlight Sources"}</CardTitle>
                <CardDescription>Click to access highlights</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                  <a
                    href="https://www.premierleague.com/"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="border-2 border-green-200 hover:border-green-400 rounded-lg p-3 hover:bg-green-50 transition-all block"
                  >
                    <p className="font-bold text-green-900">{t.news?.premierLeagueApp || "Premier League App"}</p>
                    <p className="text-gray-600 mt-1">{t.news?.premierLeagueDesc || "Official app with FREE highlights (iOS/Android)"}</p>
                  </a>
                  <a
                    href="https://www.facebook.com/watch/search/?q=football%20highlights"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="border-2 border-blue-200 hover:border-blue-400 rounded-lg p-3 hover:bg-blue-50 transition-all block"
                  >
                    <p className="font-bold text-blue-900">{t.news?.facebookWatch || "Facebook Watch"}</p>
                    <p className="text-gray-600 mt-1">{t.news?.facebookDesc || "Many leagues post highlights on Facebook"}</p>
                  </a>
                  <a
                    href="https://twitter.com/search?q=football%20goals&f=video"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="border-2 border-sky-200 hover:border-sky-400 rounded-lg p-3 hover:bg-sky-50 transition-all block"
                  >
                    <p className="font-bold text-sky-900">{t.news?.twitterVideos || "Twitter/X Videos"}</p>
                    <p className="text-gray-600 mt-1">{t.news?.twitterDesc || "Goal clips posted by official accounts"}</p>
                  </a>
                  <a
                    href="https://www.reddit.com/r/soccer/"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="border-2 border-orange-200 hover:border-orange-400 rounded-lg p-3 hover:bg-orange-50 transition-all block"
                  >
                    <p className="font-bold text-orange-900">{t.news?.reddit || "Reddit r/soccer"}</p>
                    <p className="text-gray-600 mt-1">{t.news?.redditDesc || "Community posts goals & highlights"}</p>
                  </a>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Live Scores Tab */}
          <TabsContent value="scores">
            <div className="space-y-6">
              {/* Info Banner */}
              <Card className="bg-green-50 border-green-200">
                <CardContent className="pt-6">
                  <p className="text-sm text-green-900">
                    ✅ <strong>No restrictions!</strong> All sites below show EVERY match from ALL leagues - 100% coverage, no limitations!
                  </p>
                </CardContent>
              </Card>

              {/* Live Score Sites Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {liveScoreSites.map((site) => {
                  const Icon = site.icon;
                  return (
                    <Card key={site.name} className="hover:shadow-lg transition-shadow bg-white border-2 border-green-200 hover:border-green-400">
                      <CardHeader>
                        <div className="flex items-start justify-between">
                          <div className="flex items-center gap-2">
                            <Icon className="w-6 h-6 text-green-600" />
                            <CardTitle className="text-lg">{site.name}</CardTitle>
                          </div>
                          <a
                            href={site.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-green-600 hover:text-green-700"
                          >
                            <ExternalLink className="w-5 h-5" />
                          </a>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <p className="text-sm text-gray-700 mb-3">{site.description}</p>
                        <a
                          href={site.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium text-sm"
                        >
                          View All Live Scores
                          <ExternalLink className="w-4 h-4" />
                        </a>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>

              {/* Additional Features */}
              <Card>
                <CardHeader>
                  <CardTitle>⚡ What These Sites Show</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                      <span className="text-2xl">✅</span>
                      <div>
                        <p className="font-bold text-gray-900">Every Premier League Match</p>
                        <p className="text-sm text-gray-600">All 10 matches per matchweek</p>
                      </div>
                    </div>
                    <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                      <span className="text-2xl">⚽</span>
                      <div>
                        <p className="font-bold text-gray-900">All Championships</p>
                        <p className="text-sm text-gray-600">Every match from EFL Championship</p>
                      </div>
                    </div>
                    <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                      <span className="text-2xl">🌍</span>
                      <div>
                        <p className="font-bold text-gray-900">International Leagues</p>
                        <p className="text-sm text-gray-600">La Liga, Bundesliga, Serie A, Ligue 1</p>
                      </div>
                    </div>
                    <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                      <span className="text-2xl">🔴</span>
                      <div>
                        <p className="font-bold text-gray-900">Live Updates</p>
                        <p className="text-sm text-gray-600">Real-time goals, cards, subs</p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Pro Tip */}
              <Card className="bg-blue-50 border-blue-200">
                <CardContent className="pt-6">
                  <p className="text-sm text-blue-900">
                    💡 <strong>Pro Tip:</strong> Bookmark these sites on your phone for instant access to scores during matchday!
                  </p>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Social/Twitter Tab */}
          <TabsContent value="social">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Left Column - Twitter Accounts */}
              <div className="space-y-6">
            <Card className="bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <img 
                    src="https://abs.twimg.com/icons/apple-touch-icon-192x192.png" 
                    alt="Twitter" 
                    className="w-6 h-6"
                  />
                  {t.news?.footballTwitter || "Football Twitter Feeds"}
                </CardTitle>
                <CardDescription>Click to follow top football accounts</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {/* BBC Sport */}
                <a
                  href="https://twitter.com/BBCSport"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block border-2 border-red-200 hover:border-red-400 rounded-lg p-4 hover:bg-red-50 transition-all"
                >
                  <div className="flex items-center gap-3 mb-2">
                    <img 
                      src="https://abs.twimg.com/icons/apple-touch-icon-192x192.png" 
                      alt="Twitter" 
                      className="w-8 h-8"
                    />
                    <div>
                      <p className="font-bold text-red-900 text-lg">BBC Sport</p>
                      <p className="text-xs text-gray-600">@BBCSport</p>
                    </div>
                  </div>
                  <p className="text-sm text-gray-700">Breaking sports news, live scores, and match updates from BBC</p>
                  <p className="text-xs text-red-600 mt-2">Click to view on Twitter/X →</p>
                </a>

                {/* Sky Sports News */}
                <a
                  href="https://twitter.com/SkySportsNews"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block border-2 border-sky-200 hover:border-sky-400 rounded-lg p-4 hover:bg-sky-50 transition-all"
                >
                  <div className="flex items-center gap-3 mb-2">
                    <img 
                      src="https://abs.twimg.com/icons/apple-touch-icon-192x192.png" 
                      alt="Twitter" 
                      className="w-8 h-8"
                    />
                    <div>
                      <p className="font-bold text-sky-900 text-lg">Sky Sports News</p>
                      <p className="text-xs text-gray-600">@SkySportsNews</p>
                    </div>
                  </div>
                  <p className="text-sm text-gray-700">24/7 sports news, transfers, and breaking football stories</p>
                  <p className="text-xs text-sky-600 mt-2">Click to view on Twitter/X →</p>
                </a>

                {/* ESPN FC */}
                <a
                  href="https://twitter.com/ESPNFC"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block border-2 border-rose-200 hover:border-rose-400 rounded-lg p-4 hover:bg-rose-50 transition-all"
                >
                  <div className="flex items-center gap-3 mb-2">
                    <img 
                      src="https://abs.twimg.com/icons/apple-touch-icon-192x192.png" 
                      alt="Twitter" 
                      className="w-8 h-8"
                    />
                    <div>
                      <p className="font-bold text-rose-900 text-lg">ESPN FC</p>
                      <p className="text-xs text-gray-600">@ESPNFC</p>
                    </div>
                  </div>
                  <p className="text-sm text-gray-700">Global football coverage, analysis, and live match updates</p>
                  <p className="text-xs text-rose-600 mt-2">Click to view on Twitter/X →</p>
                </a>
              </CardContent>
            </Card>
          </div>

              {/* Right Column - More Twitter & Info */}
              <div className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle>🔥 Trending Football Accounts</CardTitle>
                    <CardDescription>Click to follow on Twitter/X</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <a
                      href="https://twitter.com/FabrizioRomano"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="block border-2 border-blue-200 hover:border-blue-400 rounded-lg p-3 hover:bg-blue-50 transition-all"
                    >
                      <p className="font-bold text-blue-600">@FabrizioRomano</p>
                      <p className="text-sm text-gray-600">{t.news?.transferExpert || "Transfer news expert"}</p>
                    </a>
                    <a
                      href="https://twitter.com/OptaJoe"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="block border-2 border-green-200 hover:border-green-400 rounded-lg p-3 hover:bg-green-50 transition-all"
                    >
                      <p className="font-bold text-green-600">@OptaJoe</p>
                      <p className="text-sm text-gray-600">{t.news?.footballStats || "Football statistics"}</p>
                    </a>
                    <a
                      href="https://twitter.com/GaryLineker"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="block border-2 border-purple-200 hover:border-purple-400 rounded-lg p-3 hover:bg-purple-50 transition-all"
                    >
                      <p className="font-bold text-purple-600">@GaryLineker</p>
                      <p className="text-sm text-gray-600">{t.news?.matchOfDay || "Match of the Day host"}</p>
                    </a>
                    <a
                      href="https://twitter.com/ChampionsLeague"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="block border-2 border-indigo-200 hover:border-indigo-400 rounded-lg p-3 hover:bg-indigo-50 transition-all"
                    >
                      <p className="font-bold text-indigo-600">@ChampionsLeague</p>
                      <p className="text-sm text-gray-600">{t.news?.uclOfficial || "UCL official"}</p>
                    </a>
                  </CardContent>
                </Card>

            {/* More Twitter Feeds */}
            <Card className="bg-gradient-to-r from-cyan-50 to-blue-50 border-cyan-200">
              <CardHeader>
                <CardTitle className="text-cyan-900">{t.news?.moreTwitter || "More Football Twitter"}</CardTitle>
                <CardDescription>Follow for daily football content</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <a
                  href="https://twitter.com/433"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block border-2 border-cyan-200 hover:border-cyan-400 rounded-lg p-4 hover:bg-cyan-50 transition-all"
                >
                  <div className="flex items-center gap-3 mb-2">
                    <img 
                      src="https://abs.twimg.com/icons/apple-touch-icon-192x192.png" 
                      alt="Twitter" 
                      className="w-8 h-8"
                    />
                    <div>
                      <p className="font-bold text-cyan-900 text-lg">433</p>
                      <p className="text-xs text-gray-600">@433</p>
                    </div>
                  </div>
                  <p className="text-sm text-gray-700">{t.news?.footballContent || "Football Content"} - Daily videos, goals, skills, and football culture</p>
                  <p className="text-xs text-cyan-600 mt-2">Click to view on Twitter/X →</p>
                </a>
                
                {/* Additional accounts */}
                <a
                  href="https://twitter.com/goal"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block border-2 border-emerald-200 hover:border-emerald-400 rounded-lg p-4 hover:bg-emerald-50 transition-all"
                >
                  <div className="flex items-center gap-3 mb-2">
                    <img 
                      src="https://abs.twimg.com/icons/apple-touch-icon-192x192.png" 
                      alt="Twitter" 
                      className="w-8 h-8"
                    />
                    <div>
                      <p className="font-bold text-emerald-900 text-lg">GOAL</p>
                      <p className="text-xs text-gray-600">@goal</p>
                    </div>
                  </div>
                  <p className="text-sm text-gray-700">Latest football news, transfers, scores and highlights</p>
                  <p className="text-xs text-emerald-600 mt-2">Click to view on Twitter/X →</p>
                </a>

                <a
                  href="https://twitter.com/brfootball"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block border-2 border-amber-200 hover:border-amber-400 rounded-lg p-4 hover:bg-amber-50 transition-all"
                >
                  <div className="flex items-center gap-3 mb-2">
                    <img 
                      src="https://abs.twimg.com/icons/apple-touch-icon-192x192.png" 
                      alt="Twitter" 
                      className="w-8 h-8"
                    />
                    <div>
                      <p className="font-bold text-amber-900 text-lg">B/R Football</p>
                      <p className="text-xs text-gray-600">@brfootball</p>
                    </div>
                  </div>
                  <p className="text-sm text-gray-700">Bleacher Report Football - News, memes, and match updates</p>
                  <p className="text-xs text-amber-600 mt-2">Click to view on Twitter/X →</p>
                </a>
              </CardContent>
            </Card>

                {/* Podcasts */}
                <Card className="bg-gradient-to-r from-purple-50 to-pink-50 border-purple-200">
                  <CardHeader>
                    <CardTitle className="text-purple-900">{t.news?.footballPodcasts || "🎙️ Football Podcasts"}</CardTitle>
                    <CardDescription>Click to listen</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-3 text-sm">
                      <li>
                        <a
                          href="https://podcasts.apple.com/us/podcast/the-totally-football-show-with-james-richardson/id1267958765"
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-start gap-2 p-2 hover:bg-purple-100 rounded-lg transition-all"
                        >
                          <span className="text-purple-600 font-bold">•</span>
                          <div>
                            <strong className="text-purple-800">The Totally Football Show</strong>
                            <span className="text-gray-600"> - {t.news?.dailyAnalysis || "Daily analysis"}</span>
                          </div>
                        </a>
                      </li>
                      <li>
                        <a
                          href="https://shows.acast.com/footballramble"
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-start gap-2 p-2 hover:bg-purple-100 rounded-lg transition-all"
                        >
                          <span className="text-purple-600 font-bold">•</span>
                          <div>
                            <strong className="text-purple-800">Football Ramble</strong>
                            <span className="text-gray-600"> - {t.news?.comedyFootball || "Comedy & football"}</span>
                          </div>
                        </a>
                      </li>
                      <li>
                        <a
                          href="https://theathletic.com/podcast/the-athletic-football-podcast/"
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-start gap-2 p-2 hover:bg-purple-100 rounded-lg transition-all"
                        >
                          <span className="text-purple-600 font-bold">•</span>
                          <div>
                            <strong className="text-purple-800">The Athletic Football Podcast</strong>
                            <span className="text-gray-600"> - {t.news?.inDepth || "In-depth"}</span>
                          </div>
                        </a>
                      </li>
                      <li>
                        <a
                          href="https://www.bbc.co.uk/programmes/p02nrss1/episodes/downloads"
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-start gap-2 p-2 hover:bg-purple-100 rounded-lg transition-all"
                        >
                          <span className="text-purple-600 font-bold">•</span>
                          <div>
                            <strong className="text-purple-800">BBC 5 Live Football Daily</strong>
                            <span className="text-gray-600"> - {t.news?.newsInterviews || "News & interviews"}</span>
                          </div>
                        </a>
                      </li>
                    </ul>
                  </CardContent>
                </Card>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
