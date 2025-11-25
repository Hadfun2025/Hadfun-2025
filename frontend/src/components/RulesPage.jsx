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
        {t.rules.backButton}
      </Button>

      <Card className="shadow-lg">
        <CardHeader className="bg-gradient-to-r from-green-600 to-emerald-600 text-white">
          <CardTitle className="text-3xl flex items-center gap-3">
            <Trophy className="w-8 h-8" />
            {t.rules.title}
          </CardTitle>
          <p className="text-green-100 text-lg mt-2">{t.rules.subtitle}</p>
        </CardHeader>
        
        <CardContent className="space-y-6 pt-6">
          {/* Free to Play */}
          <div className="bg-blue-50 border-l-4 border-blue-600 p-4 rounded">
            <h2 className="text-2xl font-bold text-blue-900 mb-2 flex items-center gap-2">
              <Trophy className="w-6 h-6" />
              {t.rules.freeToPlay}
            </h2>
            <p className="text-blue-800 font-semibold">{t.rules.noSubscriptions}</p>
            <p className="text-gray-700 mt-2">
              {t.rules.freePlayDesc}
            </p>
          </div>

          {/* How It Works */}
          <div>
            <h2 className="text-2xl font-bold text-emerald-600 mb-3 flex items-center gap-2">
              <Calendar className="w-6 h-6" />
              {t.rules.howItWorks}
            </h2>
            <div className="space-y-3 text-gray-700">
              <p className="leading-relaxed">
                <strong>{t.rules.theObject}</strong> {t.rules.objectDesc}
              </p>
              <p className="leading-relaxed">
                <strong>{t.rules.predictions}</strong> {t.rules.predictionsDesc}
              </p>
              <p className="leading-relaxed">
                <strong>{t.rules.scoring}</strong> {t.rules.scoringDesc}
              </p>
            </div>
          </div>

          {/* Teams & Private Forum */}
          <div>
            <h2 className="text-2xl font-bold text-emerald-600 mb-3 flex items-center gap-2">
              <Users className="w-6 h-6" />
              {t.rules.teamsPrivateForum}
            </h2>
            <div className="space-y-3 text-gray-700">
              <p className="leading-relaxed">
                {t.rules.forumDesc}
              </p>
              <p className="leading-relaxed">
                <strong>{t.rules.creatingTeam}</strong> {t.rules.creatingDesc}
              </p>
              <p className="leading-relaxed">
                <strong>{t.rules.joiningTeam}</strong> {t.rules.joiningDesc}
              </p>
            </div>
          </div>

          {/* Play Modes */}
          <div>
            <h2 className="text-2xl font-bold text-emerald-600 mb-3 flex items-center gap-2">
              <Coins className="w-6 h-6" />
              {t.rules.twoWaysToPlay}
            </h2>
            
            {/* Free Mode */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
              <h3 className="text-xl font-bold text-blue-900 mb-2">{t.rules.playForFreeTitle}</h3>
              <ul className="list-disc list-inside space-y-2 text-gray-700">
                {t.rules.playForFreeList.map((item, index) => (
                  <li key={index}>{item}</li>
                ))}
              </ul>
            </div>

            {/* Paid Mode */}
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <h3 className="text-xl font-bold text-green-900 mb-2">{t.rules.weeklyPotTitle}</h3>
              <ul className="list-disc list-inside space-y-2 text-gray-700 mb-3">
                {t.rules.weeklyPotList.map((item, index) => (
                  <li key={index}>{item}</li>
                ))}
              </ul>
              <p className="text-sm text-gray-600 italic">
                <strong>Note:</strong> {t.rules.weeklyPotNote}
              </p>
            </div>
          </div>

          {/* Payment Details */}
          <div className="bg-amber-50 border-l-4 border-amber-600 p-4 rounded">
            <h3 className="text-xl font-bold text-amber-900 mb-2">{t.rules.paymentInfo}</h3>
            <ul className="list-disc list-inside space-y-2 text-gray-700">
              {t.rules.paymentList.map((item, index) => (
                <li key={index}>{item}</li>
              ))}
            </ul>
          </div>

          {/* Charity & Social Impact */}
          <div className="bg-gradient-to-r from-pink-50 to-purple-50 border-l-4 border-pink-500 p-4 rounded">
            <h3 className="text-xl font-bold text-pink-900 mb-3 flex items-center gap-2">
              ❤️ {t.rules?.charityTitle || 'Football With Purpose: Supporting Each Other & Charities'}
            </h3>
            <div className="space-y-4 text-gray-700">
              <p className="leading-relaxed font-medium text-pink-900">
                {t.rules?.charityIntro || "At HadFun, we believe in playing with purpose - whether that's supporting charities or supporting each other. After all, charity begins at home!"}
              </p>
              
              {/* Community Support Feature */}
              <div className="bg-white/70 rounded-lg p-4 border-2 border-pink-300">
                <h4 className="font-bold text-pink-900 mb-2 flex items-center gap-2">
                  🤝 {t.community?.communityCareBanner || 'Charity Begins at Home - Community Care'}
                </h4>
                <p className="leading-relaxed mb-3">
                  {t.community?.communityCareDesc || 'HadFun isn\'t just about predictions - it\'s about building a caring community. Through our Community Care feature, team members can nominate teammates facing hardship. When someone wins, they can choose to share their winnings with those who need support.'}
                </p>
                <ul className="list-disc list-inside space-y-1 ml-4 text-sm">
                  <li>{t.rules?.charityPoint1 || 'Nominate teammates respectfully and compassionately'}</li>
                  <li>{t.rules?.charityPoint2 || 'Winners see nominations when they win'}</li>
                  <li>{t.rules?.charityPoint3 || 'Completely optional - no pressure on anyone'}</li>
                  <li>{t.rules?.charityPoint4 || 'All acts of kindness are celebrated in your team'}</li>
                </ul>
              </div>
              
              {/* External Charities */}
              <div>
                <h4 className="font-bold text-pink-900 mb-2">{t.rules?.externalCharityTitle || '🌍 Support External Charities'}</h4>
                <p className="leading-relaxed mb-2">
                  {t.rules?.externalCharityDesc || "Teams can also choose to donate winnings to external charities they're passionate about!"}
                </p>
                <ul className="list-disc list-inside space-y-1 ml-4 text-sm">
                  <li>{t.rules?.externalCharityPoint1 || 'Teams decide together which charity to support'}</li>
                  <li>{t.rules?.externalCharityPoint2 || 'Switch charities weekly or stay committed to one cause'}</li>
                  <li>{t.rules?.externalCharityPoint3 || 'Split winnings between team members and charity'}</li>
                  <li>{t.rules?.externalCharityPoint4 || 'Or keep the pot within the team - your choice!'}</li>
                </ul>
              </div>
              
              <p className="text-sm text-pink-800 italic mt-3 bg-white/50 p-3 rounded">
                {t.rules?.charityClosing || 'Your Team, Your Choice: Whether you support teammates, donate to charities, or keep winnings amongst yourselves - it\'s entirely up to your team. HadFun provides the platform and community features; you decide how to use them with purpose!'}
              </p>
            </div>
          </div>

          {/* Flexibility */}
          <div>
            <h2 className="text-2xl font-bold text-emerald-600 mb-3">{t.rules.flexibility}</h2>
            <div className="space-y-3 text-gray-700">
              <p className="leading-relaxed">
                <strong>{t.rules.noSubscriptionsDesc}</strong>
              </p>
              <p className="leading-relaxed">
                <strong>{t.rules.multipleLeagues}</strong> {t.rules.multipleLeaguesDesc}
              </p>
              <p className="leading-relaxed">
                <strong>{t.rules.multiLanguage}</strong> {t.rules.multiLanguageDesc}
              </p>
            </div>
          </div>

          {/* Available Leagues */}
          <div className="bg-gradient-to-r from-indigo-50 to-blue-50 rounded-lg p-4">
            <h3 className="text-xl font-bold text-indigo-900 mb-3">{t.rules.availableLeagues}</h3>
            <div className="grid grid-cols-2 gap-3 text-gray-700">
              {t.rules.leagues.map((league, index) => (
                <div key={index}>• {league}</div>
              ))}
            </div>
          </div>

          {/* Call to Action */}
          <div className="bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-lg p-6 text-center">
            <h2 className="text-3xl font-bold mb-2">{t.rules.callToAction}</h2>
            <p className="text-green-100 text-lg">
              {t.rules.callToActionDesc}
            </p>
          </div>

          {/* Contact */}
          <div className="border-t pt-4 text-center">
            <p className="text-gray-600 text-sm">
              {t.rules.questions}{' '}
              <a href={`mailto:${t.rules.emailContact}`} className="text-emerald-600 hover:underline font-semibold">
                {t.rules.emailContact}
              </a>
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
