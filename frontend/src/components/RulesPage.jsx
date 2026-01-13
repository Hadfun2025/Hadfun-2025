import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Trophy, Users, Calendar, Heart } from 'lucide-react';
import { useLanguage } from '../LanguageContext';

export function RulesPage({ onBack }) {
  const { t } = useLanguage();

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      {/* Header with Back Button */}
      <Button onClick={onBack} variant="outline" className="mb-4">
        <ArrowLeft className="w-4 h-4 mr-2" />
        {t.rules?.backButton || "Back to App"}
      </Button>

      <Card className="shadow-lg">
        <CardHeader className="bg-gradient-to-r from-green-600 to-emerald-600 text-white">
          <CardTitle className="text-3xl flex items-center gap-3">
            <Trophy className="w-8 h-8" />
            {t.rules?.title || "How to Play HadFun"}
          </CardTitle>
          <p className="text-green-100 text-lg mt-2">{t.rules?.subtitle || "Your guide to football predictions"}</p>
        </CardHeader>
        
        <CardContent className="space-y-6 pt-6">
          
          {/* Free to Play Banner */}
          <div className="bg-green-50 border-2 border-green-500 rounded-lg p-6">
            <h2 className="text-2xl font-bold text-green-700 mb-3 flex items-center gap-2">
              <span>✅</span> {t.rules?.freeToPlayTitle || "100% Free to Play"}
            </h2>
            <p className="text-gray-700 mb-4">
              {t.rules?.freeToPlayDesc || "HadFun is completely free to play. No payment is ever required to make predictions, compete with friends, or appear on leaderboards."}
            </p>
            <ul className="space-y-2 text-gray-700">
              <li>• {t.rules?.freePoint1 || "No subscription fees"}</li>
              <li>• {t.rules?.freePoint2 || "No entry fees for competitions"}</li>
              <li>• {t.rules?.freePoint3 || "No hidden costs"}</li>
              <li>• {t.rules?.freePoint4 || "Play as often as you like"}</li>
            </ul>
          </div>

          {/* Not Gambling Statement */}
          <div className="bg-red-50 border-2 border-red-400 rounded-lg p-4">
            <h3 className="text-lg font-bold text-red-700 mb-2 flex items-center gap-2">
              <span>🚫</span> {t.rules?.notGamblingTitle || "Not Gambling"}
            </h3>
            <p className="text-gray-700">
              {t.rules?.notGamblingText || "HadFun is a free-to-play prediction game. No purchase is required. We do not offer betting, wagering, or prize-based gambling."}
            </p>
          </div>

          {/* How It Works */}
          <div>
            <h2 className="text-2xl font-bold text-emerald-600 mb-3 flex items-center gap-2">
              <Calendar className="w-6 h-6" />
              {t.rules?.howItWorks || "How It Works"}
            </h2>
            <div className="space-y-3 text-gray-700">
              <p className="leading-relaxed">
                <strong>{t.rules?.theObject || "The Object:"}</strong> {t.rules?.objectDesc || "Predict match outcomes (Home Win, Away Win, or Draw) and earn points for correct predictions."}
              </p>
              <p className="leading-relaxed">
                <strong>{t.rules?.predictions || "Predictions:"}</strong> {t.rules?.predictionsDesc || "Submit your predictions before match kick-off. You can change predictions until the deadline (Wednesday 11:59 PM for weekend matches)."}
              </p>
              <p className="leading-relaxed">
                <strong>{t.rules?.scoring || "Scoring:"}</strong> {t.rules?.scoringDesc || "Earn 1 point for each correct prediction. Track your score on the leaderboard."}
              </p>
            </div>
          </div>

          {/* Teams & Private Forum */}
          <div>
            <h2 className="text-2xl font-bold text-emerald-600 mb-3 flex items-center gap-2">
              <Users className="w-6 h-6" />
              {t.rules?.teamsPrivateForum || "Teams & Private Forum"}
            </h2>
            <div className="space-y-3 text-gray-700">
              <p className="leading-relaxed">
                {t.rules?.forumDesc || "Create or join a private team to compete with friends, family, or colleagues. Each team has its own private leaderboard and chat forum."}
              </p>
              <p className="leading-relaxed">
                <strong>{t.rules?.creatingTeam || "Creating a Team:"}</strong> {t.rules?.creatingDesc || "You become the admin and receive a unique join code to share with friends."}
              </p>
              <p className="leading-relaxed">
                <strong>{t.rules?.joiningTeam || "Joining a Team:"}</strong> {t.rules?.joiningDesc || "Enter the join code shared by your friend to join their team."}
              </p>
              <p className="leading-relaxed">
                <strong>{t.rules?.teamSize || "Team Size:"}</strong> {t.rules?.teamSizeDesc || "Teams are limited to a maximum of 30 members."}
              </p>
            </div>
          </div>

          {/* Weekly Challenge */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h2 className="text-xl font-bold text-blue-900 mb-3 flex items-center gap-2">
              <Trophy className="w-5 h-5" />
              {t.rules?.weeklyChallengeTitle || "Weekly Challenge"}
            </h2>
            <p className="text-gray-700 mb-3">
              {t.rules?.weeklyChallengeDesc || "Each week, compete to be the top predictor in your team. The player with the most correct predictions earns bragging rights!"}
            </p>
            <ul className="list-disc list-inside space-y-1 text-gray-700">
              <li>{t.rules?.challengePoint1 || "Compete for fun with friends"}</li>
              <li>{t.rules?.challengePoint2 || "Track weekly and all-time scores"}</li>
              <li>{t.rules?.challengePoint3 || "See who's the best predictor"}</li>
              <li>{t.rules?.challengePoint4 || "No entry fee required"}</li>
            </ul>
          </div>

          {/* Optional Charity Donations */}
          <div className="bg-gradient-to-r from-pink-50 to-purple-50 border-2 border-pink-400 rounded-lg p-6">
            <h2 className="text-2xl font-bold text-pink-700 mb-3 flex items-center gap-2">
              <Heart className="w-6 h-6" />
              {t.rules?.charityTitle || "Optional Charity Donations"}
            </h2>
            <p className="text-gray-700 mb-4">
              {t.rules?.charityIntro || "HadFun allows you to optionally support charities you care about. Donations are completely separate from gameplay."}
            </p>
            
            <div className="bg-white/70 rounded-lg p-4 mb-4">
              <h3 className="font-bold text-pink-800 mb-2">{t.rules?.charityHowTitle || "How Charity Donations Work:"}</h3>
              <ul className="space-y-2 text-gray-700">
                <li>✅ {t.rules?.charityHow1 || "Donations are 100% voluntary"}</li>
                <li>✅ {t.rules?.charityHow2 || "Choose from verified charities"}</li>
                <li>✅ {t.rules?.charityHow3 || "100% of your donation goes to charity"}</li>
                <li>✅ {t.rules?.charityHow4 || "Donate any amount you choose"}</li>
              </ul>
            </div>

            <div className="bg-amber-100 rounded-lg p-4">
              <h3 className="font-bold text-amber-800 mb-2">{t.rules?.importantTitle || "Important:"}</h3>
              <ul className="space-y-1 text-gray-700 text-sm">
                <li>❌ {t.rules?.donationRule1 || "Donations do NOT affect your score"}</li>
                <li>❌ {t.rules?.donationRule2 || "Donations do NOT affect rankings"}</li>
                <li>❌ {t.rules?.donationRule3 || "Donations do NOT give any gameplay advantage"}</li>
                <li>❌ {t.rules?.donationRule4 || "Donations are NOT required to play"}</li>
              </ul>
            </div>
          </div>

          {/* Fair Play */}
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <h2 className="text-xl font-bold text-gray-800 mb-2">{t.rules?.fairPlayTitle || "Fair Play"}</h2>
            <p className="text-gray-700">
              {t.rules?.fairPlayDesc || "HadFun is a friendly community. Treat all users with respect. Abuse, harassment, or inappropriate behaviour may result in removal from the platform."}
            </p>
          </div>

          {/* Entertainment Disclaimer */}
          <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded">
            <p className="text-blue-800 font-medium">
              {t.rules?.entertainmentDisclaimer || "HadFun is intended for entertainment purposes only. Please play responsibly. If you choose to donate, please only donate what you can afford."}
            </p>
          </div>

          {/* Back Button */}
          <div className="flex justify-center pt-4">
            <Button onClick={onBack} className="bg-emerald-600 hover:bg-emerald-700">
              <ArrowLeft className="w-4 h-4 mr-2" />
              {t.rules?.backButton || "Back to App"}
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
