import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Globe, Heart, Trophy, Users } from 'lucide-react';
import { useLanguage } from '../LanguageContext';

export function AboutPage({ onBack }) {
  const { language, setLanguage, t } = useLanguage();
  
  const languages = [
    { code: 'en', name: 'English', flag: '🇬🇧' },
    { code: 'es', name: 'Español', flag: '🇪🇸' },
    { code: 'de', name: 'Deutsch', flag: '🇩🇪' },
    { code: 'fr', name: 'Français', flag: '🇫🇷' },
    { code: 'it', name: 'Italiano', flag: '🇮🇹' },
    { code: 'nl', name: 'Nederlands', flag: '🇳🇱' },
    { code: 'tr', name: 'Türkçe', flag: '🇹🇷' },
    { code: 'pt', name: 'Português', flag: '🇧🇷' }
  ];

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      {/* Header with Back Button and Language Selector */}
      <div className="flex justify-between items-center mb-6">
        <Button onClick={onBack} variant="outline" className="mb-4">
          <ArrowLeft className="w-4 h-4 mr-2" />
          {t.about?.backButton || "Back to App"}
        </Button>
        
        {/* Language Selector */}
        <div className="flex items-center gap-2">
          <Globe className="w-5 h-5 text-gray-600" />
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="px-4 py-2 border-2 border-gray-300 rounded-lg font-semibold text-gray-700 bg-white hover:border-blue-500 focus:border-blue-500 focus:outline-none cursor-pointer"
          >
            {languages.map(lang => (
              <option key={lang.code} value={lang.code}>
                {lang.flag} {lang.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      <Card className="shadow-lg">
        <CardHeader className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white">
          <CardTitle className="text-3xl">{t.about?.title || "About HadFun Predictor"}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6 pt-6">
          
          {/* Free to Play Banner */}
          <div className="bg-green-50 border-2 border-green-500 rounded-lg p-6">
            <h2 className="text-2xl font-bold text-green-700 mb-3 flex items-center gap-2">
              <span>✅</span> Free-to-Play Football Predictions
            </h2>
            <p className="text-gray-700 mb-3">
              HadFun is a <strong>100% free-to-play</strong> football prediction game. No payment is ever required to play.
            </p>
            <ul className="space-y-1 text-gray-700">
              <li>• No subscription fees</li>
              <li>• No entry fees</li>
              <li>• No hidden costs</li>
              <li>• Just pure football fun!</li>
            </ul>
          </div>

          {/* Origin Story */}
          <div>
            <h2 className="text-2xl font-bold text-indigo-600 mb-3">{t.about?.origin || "Our Origin Story"}</h2>
            <p className="text-gray-700 leading-relaxed">{t.about?.originText || "HadFun Predictor was born from a simple idea: making football predictions with friends should be fun and social. Whether you're playing for bragging rights or supporting charity, HadFun brings people together through the beautiful game."}</p>
          </div>

          {/* How to Play */}
          <div>
            <h2 className="text-2xl font-bold text-indigo-600 mb-3 flex items-center gap-2">
              <Trophy className="w-6 h-6" />
              {t.about?.howToPlay || "How to Play (Free!)"}
            </h2>
            <ol className="list-decimal list-inside space-y-2 text-gray-700">
              {(t.about?.howToPlaySteps || [
                "Sign up and join or create a team",
                "Select your leagues to follow",
                "Make your predictions before Wednesday 11:59 PM",
                "Track your performance on the leaderboard",
                "Compete for bragging rights with friends!",
                "Optionally support charity with donations"
              ]).map((step, index) => (
                <li key={index} className="leading-relaxed">{step}</li>
              ))}
            </ol>
          </div>

          {/* Purpose */}
          <div>
            <h2 className="text-2xl font-bold text-indigo-600 mb-3">{t.about?.purpose || "Our Purpose"}</h2>
            <p className="text-gray-700 leading-relaxed">{t.about?.purposeText || "To create a friendly, engaging platform where football fans can test their prediction skills, compete with friends and family, and enjoy the excitement of the beautiful game together."}</p>
          </div>

          {/* Teams */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h2 className="text-xl font-bold text-blue-900 mb-3 flex items-center gap-2">
              <Users className="w-5 h-5" />
              Create or Join a Team
            </h2>
            <ul className="list-disc list-inside space-y-2 text-gray-700">
              <li>Create your own team and invite friends</li>
              <li>Private leaderboards for your team only</li>
              <li>Team chat and forum</li>
              <li>Compete within your circle</li>
              <li>Teams are limited to 30 members</li>
            </ul>
          </div>

          {/* Football With Purpose */}
          <div className="border-t-2 border-indigo-200 pt-6">
            <h2 className="text-2xl font-bold text-indigo-600 mb-4">{t.about?.footballWithPurpose || "HadFun — Football With Purpose"}</h2>
            <div className="space-y-4">
              {(t.about?.footballWithPurposeText || [
                "Football has always been more than a game — it's a universal language that unites people across borders, cultures, and generations.",
                "Even during the First World War, on Christmas Day 1914, English and German soldiers famously laid down their weapons and came together in no man's land to play football. For that brief, extraordinary moment, enemies became teammates. Humanity triumphed over conflict — proving that the power of sport can transcend even the darkest times.",
                "That story has always inspired me. It's a reminder that football isn't just about competition — it's about connection, compassion, and community.",
                "HadFun was born from that belief: that the beautiful game can do more than entertain — it can make a difference."
              ]).slice(0, 4).map((paragraph, index) => (
                <p key={index} className="text-gray-700 leading-relaxed">{paragraph}</p>
              ))}
            </div>
          </div>

          {/* Charity Support */}
          <div className="bg-gradient-to-r from-pink-50 to-purple-50 border-2 border-pink-400 rounded-lg p-6">
            <h2 className="text-2xl font-bold text-pink-700 mb-3 flex items-center gap-2">
              <Heart className="w-6 h-6" />
              Optional Charity Support
            </h2>
            <p className="text-gray-700 mb-4">
              HadFun allows users to optionally support charities they care about. Donations are completely voluntary and separate from gameplay.
            </p>
            <ul className="space-y-2 text-gray-700 mb-4">
              <li>✅ Choose from verified charities</li>
              <li>✅ 100% of donations go to charity</li>
              <li>✅ Donations are completely optional</li>
              <li>✅ Donating does NOT affect scores or rankings</li>
            </ul>
            <div className="bg-white/70 rounded p-3">
              <p className="text-sm text-pink-800 italic">
                HadFun is 100% free-to-play. Charity donations are completely optional and do not affect gameplay in any way.
              </p>
            </div>
          </div>

          {/* Available Leagues */}
          <div>
            <h2 className="text-2xl font-bold text-indigo-600 mb-3">{t.about?.availableLeagues || "Available Leagues"}</h2>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-2 text-gray-700">
              {(t.about?.leagues || [
                "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League",
                "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Championship",
                "🏴󠁧󠁢󠁳󠁣󠁴󠁿 Scottish Premiership",
                "🇪🇸 La Liga",
                "🇩🇪 Bundesliga",
                "🇮🇹 Serie A",
                "🇫🇷 Ligue 1",
                "🇵🇹 Primeira Liga",
                "🇳🇱 Eredivisie",
                "🇹🇷 Süper Lig",
                "🇺🇸 MLS",
                "🇧🇷 Brasileirão"
              ]).map((league, index) => (
                <span key={index} className="text-sm">{league}</span>
              ))}
            </div>
          </div>

          {/* Call to Action */}
          <div className="text-center bg-indigo-50 rounded-lg p-6">
            <h2 className="text-2xl font-bold text-indigo-700 mb-2">{t.about?.callToAction || "So, Let's HADFUN! ⚽"}</h2>
            <p className="text-gray-700">{t.about?.callToActionDesc || "Create your team, invite your friends, and start predicting!"}</p>
          </div>

          {/* Contact */}
          <div className="text-center text-gray-600">
            <p>{t.about?.questions || "Questions? Contact us at"} <a href="mailto:info@hadfun.co.uk" className="text-indigo-600 hover:underline">{t.about?.emailContact || "info@hadfun.co.uk"}</a></p>
          </div>

          {/* Back Button */}
          <div className="flex justify-center pt-4">
            <Button onClick={onBack} className="bg-indigo-600 hover:bg-indigo-700">
              <ArrowLeft className="w-4 h-4 mr-2" />
              {t.about?.backButton || "Back to App"}
            </Button>
          </div>
        </CardContent>
      </Card>
      
      {/* Legal Footer */}
      <div className="mt-6 text-center text-sm text-gray-500 border-t pt-4">
        <p>{t.footer?.legalText || "HadFun is free-to-play. No purchase is required to play. Optional charity donations are separate from gameplay and do not affect results."}</p>
      </div>
    </div>
  );
}
