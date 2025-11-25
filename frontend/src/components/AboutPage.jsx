import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Globe } from 'lucide-react';
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
          {t.about.backButton}
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
          <CardTitle className="text-3xl">{t.about.title}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6 pt-6">
          {/* Origin Story */}
          <div>
            <h2 className="text-2xl font-bold text-indigo-600 mb-3">{t.about.origin}</h2>
            <p className="text-gray-700 leading-relaxed">{t.about.originText}</p>
          </div>

          {/* How to Play */}
          <div>
            <h2 className="text-2xl font-bold text-indigo-600 mb-3">{t.about.howToPlay}</h2>
            <ol className="list-decimal list-inside space-y-2 text-gray-700">
              {t.about.howToPlaySteps.map((step, index) => (
                <li key={index} className="leading-relaxed">{step}</li>
              ))}
            </ol>
          </div>

          {/* Purpose */}
          <div>
            <h2 className="text-2xl font-bold text-indigo-600 mb-3">{t.about.purpose}</h2>
            <p className="text-gray-700 leading-relaxed">{t.about.purposeText}</p>
          </div>

          {/* Football With Purpose */}
          <div className="border-t-2 border-indigo-200 pt-6">
            <h2 className="text-2xl font-bold text-indigo-600 mb-4">{t.about.footballWithPurpose}</h2>
            <div className="space-y-4">
              {t.about.footballWithPurposeText.slice(0, 4).map((paragraph, index) => (
                <p key={index} className="text-gray-700 leading-relaxed">{paragraph}</p>
              ))}
              
              {/* Charity List */}
              <ul className="list-disc list-inside space-y-2 ml-4 text-gray-700">
                {t.about.charityList.map((item, index) => (
                  <li key={index} className="leading-relaxed">{item}</li>
                ))}
              </ul>

              {t.about.footballWithPurposeText.slice(5).map((paragraph, index) => (
                <p key={index + 5} className="text-gray-700 leading-relaxed">{paragraph}</p>
              ))}

              {/* Closing message with emphasis */}
              <p className="text-lg font-semibold text-indigo-700 mt-6 text-center italic">
                "Lets HadFun — Where every goal helps change the world."
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
