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
          {t.terms?.backButton || "Back to App"}
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
          <CardTitle className="text-3xl">{t.terms?.title || "Terms of Service & Privacy Policy"}</CardTitle>
          <p className="text-purple-100 text-sm mt-2">{t.terms?.lastUpdated || "Last Updated"}: January 13, 2026</p>
        </CardHeader>
        <CardContent className="space-y-8 pt-6">
          
          {/* MAIN DISCLAIMER - Free to Play & Charity */}
          <div className="bg-green-50 border-2 border-green-500 rounded-lg p-6">
            <h2 className="text-2xl font-bold text-green-700 mb-4 flex items-center gap-2">
              <span>✅</span> {t.terms?.freePlayDisclaimer?.title || "HadFun – Free-to-Play & Charity Donations"}
            </h2>
            
            <p className="text-gray-800 font-medium mb-4">
              {t.terms?.freePlayDisclaimer?.intro || "HadFun is a free-to-play football prediction game created purely for fun and social interaction."}
            </p>
            
            <ul className="space-y-2 text-gray-700 mb-6">
              <li>• {t.terms?.freePlayDisclaimer?.point1 || "No payment is required to play HadFun."}</li>
              <li>• {t.terms?.freePlayDisclaimer?.point2 || "HadFun does not operate as a lottery or a betting service."}</li>
              <li>• {t.terms?.freePlayDisclaimer?.point3 || "HadFun does not offer cash prizes based on match outcomes or predictions."}</li>
            </ul>

            <h3 className="font-bold text-green-700 mb-2">{t.terms?.freePlayDisclaimer?.charityTitle || "Charity Support"}</h3>
            <p className="text-gray-700 mb-2">
              {t.terms?.freePlayDisclaimer?.charityIntro || "HadFun allows users to optionally donate to selected charities."}
            </p>
            <ul className="space-y-1 text-gray-700 mb-6">
              <li>• {t.terms?.freePlayDisclaimer?.charityPoint1 || "Donations are voluntary"}</li>
              <li>• {t.terms?.freePlayDisclaimer?.charityPoint2 || "Donations are separate from gameplay"}</li>
              <li>• {t.terms?.freePlayDisclaimer?.charityPoint3 || "Donating does not affect scores, rankings, results, or chances of winning"}</li>
            </ul>

            <div className="bg-green-100 rounded p-4 mt-4">
              <h4 className="font-bold text-green-800 mb-2">{t.terms?.freePlayDisclaimer?.importantTitle || "Important Notice"}</h4>
              <p className="text-green-900">
                {t.terms?.freePlayDisclaimer?.importantText || "HadFun is intended as entertainment only. Please play responsibly. If you choose to donate, please donate only what you can afford."}
              </p>
            </div>
          </div>

          {/* NOT GAMBLING Statement */}
          <div className="bg-red-50 border-2 border-red-400 rounded-lg p-6">
            <h2 className="text-xl font-bold text-red-700 mb-3 flex items-center gap-2">
              <span>🚫</span> {t.terms?.notGambling?.title || "Not Gambling / Not Betting"}
            </h2>
            <p className="text-gray-700">
              {t.terms?.notGambling?.text || "HadFun is a free-to-play prediction game. No purchase is required. We do not offer betting, wagering, or prize-based gambling."}
            </p>
          </div>

          {/* Terms of Service */}
          <div>
            <h2 className="text-2xl font-bold text-gray-800 mb-4 border-b-2 border-purple-500 pb-2">
              {t.terms?.terms || "Terms of Service"}
            </h2>
            <p className="text-gray-700 mb-4">
              {t.terms?.termsIntro || "By accessing or using HadFun, you agree to be bound by these Terms of Service. HadFun is a free-to-play football prediction game for entertainment and social interaction."}
            </p>
            <ul className="space-y-3 text-gray-700">
              {(t.terms?.termsPoints || [
                "Eligibility: You must be 13+ to use the platform. Parental consent required for users aged 13-17.",
                "Account Security: You are responsible for maintaining the confidentiality of your credentials. One account per person.",
                "User Content: You retain ownership of content you post (predictions, posts, photos). By posting, you grant HadFun a license to display your content.",
                "Prohibited Content: No illegal, harmful, threatening, abusive, harassing, defamatory, vulgar, obscene, or hateful content.",
                "Community Standards: Treat all users with respect. No harassment or bullying. Keep content relevant to football and community.",
                "Free to Play: HadFun is completely free to play. No payment is required to make predictions or compete.",
                "Charity Donations: Optional donations to verified charities. 100% of donations go to charities. Donations do not affect gameplay.",
                "Termination: You can delete your account at any time. We may suspend accounts for violations or illegal activity.",
                "Disclaimers: Service provided 'as is' without warranties. This is not financial or gambling advice.",
                "Governing Law: These Terms are governed by the laws of England and Wales."
              ]).map((point, index) => (
                <li key={index} className="flex items-start">
                  <span className="text-purple-600 font-bold mr-2">•</span>
                  <span>{point}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Privacy Policy */}
          <div>
            <h2 className="text-2xl font-bold text-gray-800 mb-4 border-b-2 border-purple-500 pb-2">
              {t.terms?.privacy || "Privacy Policy"}
            </h2>
            <p className="text-gray-700 mb-4">
              {t.terms?.privacyIntro || "HadFun respects your privacy. This policy explains how we collect, use, and protect your information. We comply with UK GDPR."}
            </p>
            <ul className="space-y-3 text-gray-700">
              {(t.terms?.privacyPoints || [
                "Information Collected: Account info (username, email), user content (predictions, posts), usage data (IP, browser, device).",
                "How We Use It: To provide the service, manage accounts, enable social features, detect fraud, improve the platform.",
                "How We Share: With service providers (database, hosting), with other users (public posts, leaderboards). We NEVER sell your data.",
                "Data Retention: Active accounts retained indefinitely. Deleted accounts purged within 30 days.",
                "Your Rights (UK GDPR): Access your data, export predictions, correct inaccurate data, request deletion, object to marketing.",
                "Security: SSL/TLS encryption in transit. Role-based access control. Regular encrypted backups.",
                "Children: Users under 13 are not permitted. Ages 13-17 require parental consent.",
                "Cookies: Essential (login, security), Analytics (anonymized), Preferences (language, settings). No advertising cookies.",
                "Updates: We may update this policy periodically. Continued use means acceptance."
              ]).map((point, index) => (
                <li key={index} className="flex items-start">
                  <span className="text-purple-600 font-bold mr-2">•</span>
                  <span>{point}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Contact */}
          <div className="bg-gray-100 rounded-lg p-4">
            <p className="text-gray-700">
              <strong>{t.terms?.contact || "Contact"}:</strong> privacy@hadfun.co.uk
            </p>
          </div>

          {/* Back Button */}
          <div className="flex justify-center pt-4">
            <Button onClick={onBack} className="bg-purple-600 hover:bg-purple-700">
              <ArrowLeft className="w-4 h-4 mr-2" />
              {t.terms?.backButton || "Back to App"}
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
