import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from '@/components/ui/sheet';
import { Menu, Info, FileText, Twitter, Trophy } from 'lucide-react';
import { useLanguage } from '@/LanguageContext';

export function Navbar({ onShowAbout, onShowTerms, onShowRules, onShowTwitter, currentUser, onLogout }) {
  const [open, setOpen] = useState(false);
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

  const handleNavClick = (action) => {
    setOpen(false);
    action();
  };

  return (
    <div className="bg-gradient-to-r from-indigo-600 via-blue-600 to-indigo-700 shadow-lg border-b-4 border-indigo-800 sticky top-0 z-50">
      <div className="container mx-auto px-4 py-3">
        <div className="flex justify-between items-center">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <img 
              src="/hadfun-logo.jpg" 
              alt="HadFun Predictor" 
              className="h-12 w-auto object-contain cursor-pointer"
              onClick={() => window.location.reload()}
            />
          </div>

          {/* Desktop Menu */}
          <div className="hidden md:flex items-center gap-4">
            {/* Language Selector */}
            <div className="relative">
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="bg-white/10 text-white border border-white/20 rounded-md px-3 py-1 text-sm font-medium hover:bg-white/20 transition-colors cursor-pointer"
              >
                {languages.map((lang) => (
                  <option key={lang.code} value={lang.code} className="bg-indigo-600 text-white">
                    {lang.flag} {lang.name}
                  </option>
                ))}
              </select>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={onShowAbout}
              className="text-white bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 shadow-md font-semibold"
            >
              <Info className="w-4 h-4 mr-2" />
              {t.nav.about}
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={onShowRules}
              className="text-white bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 shadow-md font-semibold"
            >
              <Trophy className="w-4 h-4 mr-2" />
              Rules
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={onShowTerms}
              className="text-white bg-gradient-to-r from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700 shadow-md font-semibold"
            >
              <FileText className="w-4 h-4 mr-2" />
              {t.nav.termsPrivacy}
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={onShowTwitter}
              className="text-white bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 shadow-md font-semibold"
            >
              <Twitter className="w-4 h-4 mr-2" />
              {t.nav.footballNews}
            </Button>
            {currentUser && (
              <>
                <div className="text-right border-l pl-4 border-white/30 bg-white/10 rounded-lg px-3 py-1">
                  <p className="text-xs text-white font-medium">{t.nav.welcome}, {currentUser.username}</p>
                  <p className="text-sm font-bold text-yellow-300">⚽ {currentUser.total_points} {t.nav.pts}</p>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={onLogout}
                  className="bg-red-500 text-white border-2 border-red-600 hover:bg-red-600 hover:border-red-700 font-semibold shadow-lg transition-all duration-200"
                >
                  🚪 {t.nav.logout}
                </Button>
              </>
            )}
          </div>

          {/* Mobile Hamburger Menu */}
          <div className="md:hidden flex items-center gap-3">
            {currentUser && (
              <div className="text-right">
                <p className="text-xs text-white font-medium">{currentUser.username}</p>
                <p className="text-sm font-bold text-yellow-300">{currentUser.total_points} pts</p>
              </div>
            )}
            <Sheet open={open} onOpenChange={setOpen}>
              <SheetTrigger asChild>
                <Button variant="ghost" size="sm" data-testid="hamburger-menu">
                  <Menu className="w-6 h-6 text-white" />
                </Button>
              </SheetTrigger>
              <SheetContent>
                <SheetHeader>
                  <SheetTitle className="flex items-center gap-2">
                    <img 
                      src="/hadfun-logo.jpg" 
                      alt="HadFun" 
                      className="h-10 w-auto object-contain"
                    />
                  </SheetTitle>
                </SheetHeader>
                <div className="flex flex-col gap-4 mt-6">
                  {/* Language Selector for Mobile */}
                  <div className="border-b pb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">{t.nav.language}</label>
                    <select
                      value={language}
                      onChange={(e) => setLanguage(e.target.value)}
                      className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm bg-white"
                    >
                      {languages.map((lang) => (
                        <option key={lang.code} value={lang.code}>
                          {lang.flag} {lang.name}
                        </option>
                      ))}
                    </select>
                  </div>
                  <Button
                    variant="ghost"
                    className="justify-start text-left"
                    onClick={() => handleNavClick(onShowAbout)}
                  >
                    <Info className="w-5 h-5 mr-3" />
                    {t.nav.about}
                  </Button>
                  <Button
                    variant="ghost"
                    className="justify-start text-left"
                    onClick={() => handleNavClick(onShowRules)}
                  >
                    <Trophy className="w-5 h-5 mr-3" />
                    Rules
                  </Button>
                  <Button
                    variant="ghost"
                    className="justify-start text-left"
                    onClick={() => handleNavClick(onShowTerms)}
                  >
                    <FileText className="w-5 h-5 mr-3" />
                    {t.nav.termsPrivacy}
                  </Button>
                  <Button
                    variant="ghost"
                    className="justify-start text-left"
                    onClick={() => handleNavClick(onShowTwitter)}
                  >
                    <Twitter className="w-5 h-5 mr-3" />
                    {t.nav.footballNews}
                  </Button>
                  {currentUser && (
                    <>
                      <div className="border-t pt-4">
                        <p className="text-sm text-gray-600 mb-1">{t.nav.loggedInAs}:</p>
                        <p className="font-bold text-gray-900">{currentUser.username}</p>
                        <p className="text-sm text-indigo-600 mt-1">
                          {currentUser.total_points} {t.nav.points}
                        </p>
                      </div>
                      <Button
                        variant="destructive"
                        className="w-full mt-2 font-semibold"
                        onClick={() => handleNavClick(onLogout)}
                      >
                        🚪 {t.nav.logout}
                      </Button>
                    </>
                  )}
                </div>
              </SheetContent>
            </Sheet>
          </div>
        </div>
      </div>
    </div>
  );
}
// VERSION CHECK: ALL_6_LANGUAGES_134517
