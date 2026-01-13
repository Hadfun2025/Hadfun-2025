import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useLanguage } from '../LanguageContext';

export function OnboardingModal({ onAccept }) {
  const { t } = useLanguage();
  const [show, setShow] = useState(false);

  useEffect(() => {
    // Check if user has already accepted the onboarding
    const hasAccepted = localStorage.getItem('hadfun_onboarding_accepted');
    if (!hasAccepted) {
      setShow(true);
    }
  }, []);

  const handleAccept = () => {
    localStorage.setItem('hadfun_onboarding_accepted', 'true');
    setShow(false);
    if (onAccept) onAccept();
  };

  if (!show) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="max-w-md w-full bg-white shadow-2xl animate-in fade-in zoom-in duration-300">
        <CardHeader className="bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-t-lg">
          <CardTitle className="text-2xl flex items-center gap-2">
            <span>🎉</span> {t.onboarding?.title || "Welcome to HadFun"}
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-6 space-y-4">
          <p className="text-gray-700">
            {t.onboarding?.intro || "HadFun is free-to-play. You can make predictions, compete with friends and chat in leagues — just for fun."}
          </p>
          
          <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded">
            <p className="text-sm text-blue-800">
              {t.onboarding?.charityInfo || "You can also support charity with optional donations, but donating is not required and does not affect scores, rankings, or results."}
            </p>
          </div>

          <div className="bg-gray-50 p-3 rounded text-sm text-gray-600">
            <p className="font-semibold mb-1">{t.onboarding?.keyPoints || "Key Points:"}</p>
            <ul className="space-y-1">
              <li>✅ {t.onboarding?.point1 || "100% free to play"}</li>
              <li>✅ {t.onboarding?.point2 || "No payment required"}</li>
              <li>✅ {t.onboarding?.point3 || "Donations are optional & separate from gameplay"}</li>
              <li>✅ {t.onboarding?.point4 || "For entertainment only"}</li>
            </ul>
          </div>

          <Button 
            onClick={handleAccept}
            className="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-3"
            data-testid="onboarding-accept-btn"
          >
            ✅ {t.onboarding?.acceptButton || "I understand – Let's play"}
          </Button>
          
          <p className="text-xs text-center text-gray-400">
            {t.onboarding?.termsNote || "By continuing, you agree to our Terms of Service and Privacy Policy."}
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
