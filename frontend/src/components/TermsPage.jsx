import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Globe } from 'lucide-react';
import { useLanguage } from '../LanguageContext';

export function TermsPage({ onBack }) {
  const { language, setLanguage, t } = useLanguage();
  
  const languages = [
    { code: 'en', name: 'English', flag: '🇬🇧' },
    { code: 'es', name: 'Español', flag: '🇪🇸' },
    { code: 'de', name: 'Deutsch', flag: '🇩🇪' },
    { code: 'fr', name: 'Français', flag: '🇫🇷' },
    { code: 'it', name: 'Italiano', flag: '🇮🇹' },
    { code: 'nl', name: 'Nederlands', flag: '🇳🇱' },
    { code: 'pt', name: 'Português', flag: '🇵🇹' },
    { code: 'tr', name: 'Türkçe', flag: '🇹🇷' }
  ];

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      {/* Header with Back Button and Language Selector */}
      <div className="flex justify-between items-center mb-6">
        <Button onClick={onBack} variant="outline" className="mb-4">
          <ArrowLeft className="w-4 h-4 mr-2" />
          {t.terms.backButton}
        </Button>
        
        {/* Language Selector */}
        <div className="flex items-center gap-2">
          <Globe className="w-5 h-5 text-gray-600" />
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="px-4 py-2 border-2 border-gray-300 rounded-lg font-semibold text-gray-700 bg-white hover:border-purple-500 focus:border-purple-500 focus:outline-none cursor-pointer"
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
        <CardHeader className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white">
          <CardTitle className="text-3xl">{t.terms.title}</CardTitle>
          <p className="text-purple-100 text-sm mt-2">{t.terms.lastUpdated}: November 16, 2025</p>
        </CardHeader>
        <CardContent className="space-y-8 pt-6">
          {/* Important Notice */}
          <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded">
            <p className="text-sm text-blue-900">
              <strong>Important:</strong> By using HadFun, you agree to these Terms of Service and Privacy Policy. 
              Please read them carefully. If you don't agree, please don't use the platform.
            </p>
          </div>

          {/* App Disclaimer */}
          <div className="bg-amber-50 border-2 border-amber-400 rounded-lg p-6">
            <h2 className="text-2xl font-bold text-amber-700 mb-4 flex items-center gap-2">
              <span>✅</span> {t.terms.disclaimer?.title || "HadFun – App Disclaimer"}
            </h2>
            
            <p className="text-gray-800 font-medium mb-4">
              {t.terms.disclaimer?.intro || "HadFun is a social football prediction game for entertainment only."}
            </p>
            
            <ul className="space-y-2 text-gray-700 mb-6">
              {(t.terms.disclaimer?.points || [
                "Players compete by comparing prediction scores within their own team.",
                "HadFun is not a betting company, casino, or \"house\".",
                "HadFun does not set odds, and users are not playing against the app.",
                "Teams can play for free."
              ]).map((point, index) => (
                <li key={index}>• {point}</li>
              ))}
            </ul>

            <h3 className="font-bold text-amber-700 mb-2">{t.terms.disclaimer?.optionalStakesTitle || "Optional Stakes (If Your Team Chooses)"}</h3>
            <ul className="space-y-2 text-gray-700 mb-6">
              {(t.terms.disclaimer?.optionalStakesPoints || [
                "Some teams may choose to play with an optional stake of up to £5 per player.",
                "Any stake is a private agreement between team members.",
                "HadFun does not charge commission, fees, or take any cut."
              ]).map((point, index) => (
                <li key={index}>• {point}</li>
              ))}
            </ul>

            <h3 className="font-bold text-amber-700 mb-2">{t.terms.disclaimer?.noMoneyTitle || "No Money Handling"}</h3>
            <p className="text-gray-700 mb-6">
              {t.terms.disclaimer?.noMoneyText || "HadFun does not hold, collect, process, or distribute money. Any payments, prizes, or charity donations are handled directly by users."}
            </p>

            <h3 className="font-bold text-amber-700 mb-2">{t.terms.disclaimer?.teamSizeTitle || "Team Size"}</h3>
            <p className="text-gray-700 mb-6">
              {t.terms.disclaimer?.teamSizeText || "Teams are limited to a maximum of 30 members."}
            </p>

            <h3 className="font-bold text-amber-700 mb-2">{t.terms.disclaimer?.fairPlayTitle || "Fair Play"}</h3>
            <p className="text-gray-700 mb-6">
              {t.terms.disclaimer?.fairPlayText || "HadFun is a friendly community app. Abuse or inappropriate behaviour may lead to removal from the platform."}
            </p>

            <div className="bg-amber-100 rounded p-4 mt-4">
              <p className="text-amber-900 font-semibold text-center">
                {t.terms.disclaimer?.agreement || "By using HadFun you agree to play responsibly and accept this disclaimer."}
              </p>
            </div>
          </div>

          {/* Terms and Conditions */}
          <div>
            <h2 className="text-2xl font-bold text-purple-600 mb-4 flex items-center gap-2">
              <span>📜</span> {t.terms.terms}
            </h2>
            <p className="text-gray-700 mb-4 leading-relaxed">{t.terms.termsIntro}</p>
            <div className="space-y-3">
              {t.terms.termsPoints.map((point, index) => (
                <div key={index} className="flex gap-3">
                  <span className="text-purple-500 font-bold text-lg mt-0.5">{index + 1}.</span>
                  <p className="text-gray-700 leading-relaxed flex-1">{point}</p>
                </div>
              ))}
            </div>
          </div>

          <hr className="border-gray-300" />

          {/* Privacy Policy */}
          <div>
            <h2 className="text-2xl font-bold text-purple-600 mb-4 flex items-center gap-2">
              <span>🔒</span> {t.terms.privacy}
            </h2>
            <p className="text-gray-700 mb-4 leading-relaxed">{t.terms.privacyIntro}</p>
            <div className="space-y-3">
              {t.terms.privacyPoints.map((point, index) => (
                <div key={index} className="flex gap-3">
                  <span className="text-purple-500 font-bold text-lg mt-0.5">{index + 1}.</span>
                  <p className="text-gray-700 leading-relaxed flex-1">{point}</p>
                </div>
              ))}
            </div>
          </div>

          <hr className="border-gray-300" />

          {/* Key Highlights */}
          <div className="bg-green-50 border-l-4 border-green-500 p-5 rounded">
            <h3 className="font-bold text-green-900 mb-3 text-lg">✅ Key Highlights</h3>
            <ul className="space-y-2 text-green-900 text-sm">
              <li>• <strong>Your Data:</strong> We never sell your personal information</li>
              <li>• <strong>Charity:</strong> 100% of donations go to charities (we take no cut)</li>
              <li>• <strong>Your Rights:</strong> Request data export or deletion anytime</li>
              <li>• <strong>UK GDPR:</strong> Full compliance with UK data protection laws</li>
              <li>• <strong>Security:</strong> Bank-level encryption and PCI DSS compliance</li>
            </ul>
          </div>

          {/* Contact */}
          <div className="bg-gradient-to-r from-gray-50 to-gray-100 rounded-lg p-5 border border-gray-200">
            <h3 className="font-bold text-gray-900 mb-3 text-lg flex items-center gap-2">
              <span>📧</span> {t.terms.contact}
            </h3>
            <p className="text-gray-700 mb-3">{t.terms.contactText}</p>
            <div className="space-y-2">
              <a 
                href="mailto:info@hadfun.co.uk" 
                className="block font-semibold text-purple-600 hover:underline"
              >
                📮 General Inquiries: info@hadfun.co.uk
              </a>
              <a 
                href="mailto:privacy@hadfun.co.uk" 
                className="block font-semibold text-purple-600 hover:underline"
              >
                🔒 Privacy & Data Rights: privacy@hadfun.co.uk
              </a>
              <p className="text-sm text-gray-600 mt-3">
                💡 <strong>Tip:</strong> For data access/deletion requests, email privacy@hadfun.co.uk. 
                We respond within 30 days as required by UK GDPR.
              </p>
            </div>
          </div>

          {/* Legal Note */}
          <div className="text-xs text-gray-500 text-center pt-4 border-t border-gray-200">
            <p>HadFun is governed by the laws of England and Wales.</p>
            <p className="mt-1">Complaints about data handling can be made to the UK Information Commissioner's Office (ICO).</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
