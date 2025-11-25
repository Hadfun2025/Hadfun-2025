import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { DollarSign, TrendingUp, Trophy, Users } from 'lucide-react';
import { useLanguage } from '../LanguageContext';

export function WeeklyPotCard({ potData, onPayment, currentUser, userPayment }) {
  const { t } = useLanguage();
  const formatCurrency = (amount) => `£${amount.toFixed(2)}`;

  return (
    <Card className="bg-gradient-to-br from-indigo-50 to-purple-50 border-2 border-indigo-200">
      <CardHeader>
        <div className="flex justify-between items-start">
          <div>
            <CardTitle className="text-2xl flex items-center gap-2">
              <Trophy className="w-6 h-6 text-yellow-600" />
              {t.weeklyPotCard.title}
            </CardTitle>
            <CardDescription>{t.weeklyPotCard.week} {potData.week_id}</CardDescription>
          </div>
          <Badge variant="default" className="bg-green-600">
            {potData.status}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Pot Amount */}
        <div className="bg-white rounded-lg p-4 shadow-sm">
          <div className="flex justify-between items-center">
            <div>
              <p className="text-sm text-gray-600">{t.weeklyPotCard.totalPot}</p>
              <p className="text-3xl font-bold text-indigo-600">
                {formatCurrency(potData.distributable_pot)}
              </p>
            </div>
            <DollarSign className="w-12 h-12 text-indigo-200" />
          </div>
          
          {potData.rollover_amount > 0 && (
            <div className="mt-2 text-sm text-orange-600 font-medium">
              + {formatCurrency(potData.rollover_amount)} {t.weeklyPotCard.rollover}
            </div>
          )}
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-white rounded-lg p-3 shadow-sm">
            <div className="flex items-center gap-2 text-gray-600 text-sm mb-1">
              <Users className="w-4 h-4" />
              <span>{t.weeklyPotCard.participants}</span>
            </div>
            <p className="text-2xl font-bold">{potData.participants}</p>
          </div>

          <div className="bg-white rounded-lg p-3 shadow-sm">
            <div className="flex items-center gap-2 text-gray-600 text-sm mb-1">
              <TrendingUp className="w-4 h-4" />
              <span>{t.weeklyPotCard.entryFee}</span>
            </div>
            <p className="text-2xl font-bold">{formatCurrency(potData.stake_amount)}</p>
          </div>
        </div>

        {/* Payment Status */}
        <div className="bg-white rounded-lg p-4 shadow-sm">
          {userPayment ? (
            <div className="text-center">
              <Badge variant="default" className="bg-green-600 mb-2">
                {t.weeklyPotCard.paidThisWeek}
              </Badge>
              <p className="text-sm text-gray-600">
                {t.weeklyPotCard.entered}
              </p>
            </div>
          ) : (
            <div>
              <p className="text-sm text-gray-700 mb-3">
                {formatCurrency(potData.stake_amount)} {t.weeklyPotCard.payToEnter}
              </p>
              <Button
                data-testid="pay-now-button"
                onClick={onPayment}
                className="w-full bg-green-600 hover:bg-green-700"
              >
                {t.weeklyPotCard.payNow}
              </Button>
            </div>
          )}
        </div>

        {/* Cutoff Info */}
        <div className="text-center text-sm text-gray-600">
          <p>{t.weeklyPotCard.cutoff} {new Date(potData.cutoff_date).toLocaleDateString('en-GB', {
            weekday: 'long',
            day: 'numeric',
            month: 'short',
            hour: '2-digit',
            minute: '2-digit'
          })}</p>
        </div>

        {potData.charity_mode && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-sm text-blue-800">
            {t.weeklyPotCard.charityMode} {potData.charity_name || 'chosen charity'}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export function WeeklyResultsTable({ results }) {
  const { t } = useLanguage();
  const formatCurrency = (amount) => `£${amount.toFixed(2)}`;

  if (!results || results.length === 0) {
    return (
      <Card>
        <CardContent className="py-8 text-center text-gray-600">
          {t.weeklyPotCard.noResults}
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t.weeklyPotCard.pastResults}</CardTitle>
        <CardDescription>{t.weeklyPotCard.recentWinners}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {results.map((result) => (
            <div
              key={result.week_id}
              className="bg-gray-50 rounded-lg p-4 border border-gray-200"
            >
              <div className="flex justify-between items-start mb-2">
                <div>
                  <p className="font-bold text-lg">{t.weeklyPotCard.week} {result.week_id}</p>
                  <p className="text-sm text-gray-600">
                    {new Date(result.week_start).toLocaleDateString('en-GB')} - {new Date(result.week_end).toLocaleDateString('en-GB')}
                  </p>
                </div>
                <Badge variant={result.is_tie ? 'secondary' : 'default'} className={result.is_tie ? '' : 'bg-green-600'}>
                  {result.is_tie ? t.weeklyPotCard.tie : t.weeklyPotCard.winner}
                </Badge>
              </div>

              {result.is_tie ? (
                <div>
                  <p className="text-sm font-medium text-orange-600 mb-1">
                    {t.weeklyPotCard.tiedPlayers} {result.tied_users.join(', ')}
                  </p>
                  <p className="text-sm text-gray-600">
                    {t.weeklyPotCard.potRolled} {formatCurrency(result.distributable_pot)} {t.weeklyPotCard.rolledOver}
                  </p>
                </div>
              ) : (
                <div>
                  <p className="text-lg font-bold text-indigo-600">
                    🏆 {result.winner_username}
                  </p>
                  <div className="flex justify-between items-center mt-2">
                    <span className="text-sm text-gray-600">{t.weeklyPotCard.prize}</span>
                    <span className="text-lg font-bold text-green-600">
                      {formatCurrency(result.distributable_pot)}
                    </span>
                  </div>
                  <div className="flex justify-between items-center text-xs text-gray-500 mt-1">
                    <span>{t.weeklyPotCard.adminFee}</span>
                    <span>{formatCurrency(result.admin_fee)}</span>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
