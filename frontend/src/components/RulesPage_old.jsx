import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Trophy, Users, Calendar, Coins } from 'lucide-react';
import { useLanguage } from '../LanguageContext';

export function RulesPage({ onBack }) {
  const { t } = useLanguage();

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      {/* Header with Back Button */}
      <Button onClick={onBack} variant="outline" className="mb-4">
        <ArrowLeft className="w-4 h-4 mr-2" />
        Back to App
      </Button>

      <Card className="shadow-lg">
        <CardHeader className="bg-gradient-to-r from-green-600 to-emerald-600 text-white">
          <CardTitle className="text-3xl flex items-center gap-3">
            <Trophy className="w-8 h-8" />
            Rules of the Game
          </CardTitle>
          <p className="text-green-100 text-lg mt-2">How to Play HadFun Predictor</p>
        </CardHeader>
        
        <CardContent className="space-y-6 pt-6">
          {/* Free to Play */}
          <div className="bg-blue-50 border-l-4 border-blue-600 p-4 rounded">
            <h2 className="text-2xl font-bold text-blue-900 mb-2 flex items-center gap-2">
              <Trophy className="w-6 h-6" />
              IT'S FREE TO PLAY
            </h2>
            <p className="text-blue-800 font-semibold">NO SUBSCRIPTIONS REQUIRED</p>
            <p className="text-gray-700 mt-2">
              You can start playing straight away! Join an existing team like "Cheshunt Crew" or create your own team with friends.
            </p>
          </div>

          {/* How It Works */}
          <div>
            <h2 className="text-2xl font-bold text-emerald-600 mb-3 flex items-center gap-2">
              <Calendar className="w-6 h-6" />
              How It Works
            </h2>
            <div className="space-y-3 text-gray-700">
              <p className="leading-relaxed">
                <strong>The Object:</strong> Choose from multiple leagues (Premier League, La Liga, Bundesliga, Serie A, Ligue 1, Eredivisie, Primeira Liga, Championship) and predict the outcomes of the week's fixtures - home win, away win, or draw.
              </p>
              <p className="leading-relaxed">
                <strong>Predictions:</strong> Make your predictions before <span className="font-bold text-red-600">Wednesday 11:59 PM</span> each week. After the deadline, predictions are locked for that matchday.
              </p>
              <p className="leading-relaxed">
                <strong>Scoring:</strong> Earn points for correct predictions. Your name appears on your team's leaderboard, showing your position based on weekly points throughout the season.
              </p>
            </div>
          </div>

          {/* Teams & Private Forum */}
          <div>
            <h2 className="text-2xl font-bold text-emerald-600 mb-3 flex items-center gap-2">
              <Users className="w-6 h-6" />
              Teams & Private Forum
            </h2>
            <div className="space-y-3 text-gray-700">
              <p className="leading-relaxed">
                Each team/syndicate has its own <strong>private forum</strong> where participants can chat with each other - like a WhatsApp group chat but built into the app!
              </p>
              <p className="leading-relaxed">
                <strong>Creating a Team:</strong> Name your team (e.g., "Cheshunt Crew"), invite friends via email or join code, and start predicting together.
              </p>
              <p className="leading-relaxed">
                <strong>Joining a Team:</strong> Use a join code or email invitation from a team admin to join existing teams.
              </p>
            </div>
          </div>

          {/* Play Modes */}
          <div>
            <h2 className="text-2xl font-bold text-emerald-600 mb-3 flex items-center gap-2">
              <Coins className="w-6 h-6" />
              Two Ways to Play
            </h2>
            
            {/* Free Mode */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
              <h3 className="text-xl font-bold text-blue-900 mb-2">🎮 Play for Free (All Ages Welcome)</h3>
              <ul className="list-disc list-inside space-y-2 text-gray-700">
                <li>No payment required - completely free!</li>
                <li>Make predictions and earn points</li>
                <li>Compete on the leaderboard</li>
                <li>Access team forum and chat</li>
                <li>Perfect for families, friends, and casual players</li>
              </ul>
            </div>

            {/* Paid Mode */}
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <h3 className="text-xl font-bold text-green-900 mb-2">💰 Weekly Pot (18+ Only)</h3>
              <ul className="list-disc list-inside space-y-2 text-gray-700 mb-3">
                <li>Optional stakes: £2.13, £3.15, or £5.18 per week</li>
                <li>Prices include payment processing fees (shared 50/50)</li>
                <li>Payments processed securely via <strong>Stripe</strong></li>
                <li>Winner each week takes 90% of the pot</li>
                <li>10% goes to admin costs</li>
                <li>If multiple winners tie, pot rolls over to next week</li>
                <li>Someone in your syndicate always wins!</li>
              </ul>
              <p className="text-sm text-gray-600 italic">
                <strong>Note:</strong> Paid participation is completely optional. You can switch between free and paid modes anytime.
              </p>
            </div>
          </div>

          {/* Payment Details */}
          <div className="bg-amber-50 border-l-4 border-amber-600 p-4 rounded">
            <h3 className="text-xl font-bold text-amber-900 mb-2">Payment Information</h3>
            <ul className="list-disc list-inside space-y-2 text-gray-700">
              <li>All payments handled by <strong>Stripe</strong> (secure payment processor)</li>
              <li>Weekly pot contributions only - no subscriptions</li>
              <li>You choose when to participate - no obligation to play every week</li>
              <li>Prize fund depends on number of paid participants that week</li>
              <li>Winners paid directly by team admin via bank transfer</li>
            </ul>
          </div>

          {/* Flexibility */}
          <div>
            <h2 className="text-2xl font-bold text-emerald-600 mb-3">Flexible Participation</h2>
            <div className="space-y-3 text-gray-700">
              <p className="leading-relaxed">
                <strong>No subscriptions.</strong> Players can participate week-to-week as they choose. Play every week or drop in occasionally - it's entirely up to you!
              </p>
              <p className="leading-relaxed">
                <strong>Multiple leagues.</strong> Your team can predict fixtures from any combination of 8+ European leagues, making it exciting for fans across the continent.
              </p>
              <p className="leading-relaxed">
                <strong>Multi-language support.</strong> The app is available in English, Spanish, German, French, Italian, and Dutch - perfect for international teams!
              </p>
            </div>
          </div>

          {/* Available Leagues */}
          <div className="bg-gradient-to-r from-indigo-50 to-blue-50 rounded-lg p-4">
            <h3 className="text-xl font-bold text-indigo-900 mb-3">Available Leagues</h3>
            <div className="grid grid-cols-2 gap-3 text-gray-700">
              <div>• Premier League (England)</div>
              <div>• La Liga (Spain)</div>
              <div>• Bundesliga (Germany)</div>
              <div>• Serie A (Italy)</div>
              <div>• Ligue 1 (France)</div>
              <div>• Eredivisie (Holland)</div>
              <div>• Primeira Liga (Portugal)</div>
              <div>• Championship (England)</div>
            </div>
          </div>

          {/* Call to Action */}
          <div className="bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-lg p-6 text-center">
            <h2 className="text-3xl font-bold mb-2">So, Let's HADFUN! ⚽</h2>
            <p className="text-green-100 text-lg">
              Create your team, invite your friends, and start predicting!
            </p>
          </div>

          {/* Contact */}
          <div className="border-t pt-4 text-center">
            <p className="text-gray-600 text-sm">
              Questions? Contact us at{' '}
              <a href="mailto:info@hadfun.co.uk" className="text-emerald-600 hover:underline font-semibold">
                info@hadfun.co.uk
              </a>
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
