import { useLanguage } from '../LanguageContext';

export function LegalFooter() {
  const { t } = useLanguage();
  
  return (
    <div className="w-full bg-gray-100 border-t border-gray-200 py-3 px-4 mt-auto">
      <p className="text-center text-xs text-gray-500">
        {t.footer?.legalText || "HadFun is free-to-play. No purchase is required to play. Optional charity donations are separate from gameplay and do not affect results."}
      </p>
    </div>
  );
}

export function InfoBadge({ className = "" }) {
  const { t } = useLanguage();
  
  return (
    <div className={`inline-flex items-center gap-1 px-2 py-1 bg-blue-50 border border-blue-200 rounded-full text-xs text-blue-700 ${className}`}>
      <span className="font-bold">ℹ️</span>
      <span>{t.footer?.shortInfo || "Free-to-play. Donations are optional and don't affect results."}</span>
    </div>
  );
}
