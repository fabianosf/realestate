function formatMoney(cents, currency) {
  if (cents == null) return '—';
  return new Intl.NumberFormat(currency === 'BRL' ? 'pt-BR' : 'en-US', {
    style: 'currency', currency,
  }).format(cents / 100);
}

function roiColor(roi) {
  if (roi >= 100) return 'text-emerald-600 bg-emerald-50';
  if (roi >= 50)  return 'text-green-600 bg-green-50';
  if (roi >= 20)  return 'text-yellow-600 bg-yellow-50';
  return 'text-red-600 bg-red-50';
}

const FLAG = { BR: '🇧🇷', US: '🇺🇸' };
const AUCTION_LABEL = {
  judicial: 'Judicial', extrajudicial: 'Extrajud.',
  foreclosure: 'Foreclosure', tax_lien: 'Tax Lien', tax_deed: 'Tax Deed',
};
const DEBT_SHORT = {
  iptu: 'IPTU', condominium: 'Cond.', mortgage: 'Hipot.',
  property_tax: 'Prop.Tax', hoa: 'HOA', other: 'Outro',
};

export function PropertyCard({ property: p, onStatusChange, onDetailOpen }) {
  const roi = p.estimated_profit_pct;

  return (
    <div
      className="bg-white rounded-xl border border-gray-100 shadow-sm hover:shadow-md
                 transition-shadow overflow-hidden flex flex-col cursor-pointer"
      onClick={() => onDetailOpen(p.id)}
    >
      <div className="p-3 sm:p-4 flex-1">
        {/* Badges + ROI */}
        <div className="flex items-start justify-between gap-1.5 mb-2">
          <div className="flex-1 min-w-0">
            <div className="flex flex-wrap items-center gap-1 mb-1">
              <span className="text-sm">{FLAG[p.country]}</span>
              <span className="text-[10px] sm:text-xs font-medium bg-indigo-50 text-indigo-700 px-1.5 py-0.5 rounded-full whitespace-nowrap">
                {AUCTION_LABEL[p.auction_type] || p.auction_type}
              </span>
              {p.debt_type && (
                <span className="text-[10px] sm:text-xs font-medium bg-orange-50 text-orange-700 px-1.5 py-0.5 rounded-full whitespace-nowrap">
                  {DEBT_SHORT[p.debt_type] || p.debt_type.toUpperCase()}
                </span>
              )}
            </div>
            <p className="text-xs sm:text-sm font-semibold text-gray-900 truncate leading-tight">
              {p.address || p.external_id}
            </p>
            <p className="text-[10px] sm:text-xs text-gray-400 truncate">
              {p.city}{p.state_province ? `, ${p.state_province}` : ''}
            </p>
          </div>

          {roi != null && (
            <div className={`shrink-0 px-1.5 sm:px-2.5 py-1 sm:py-1.5 rounded-lg text-center font-bold ${roiColor(Number(roi))}`}>
              <div className="text-[9px] sm:text-xs font-normal opacity-60">ROI</div>
              <div className="text-xs sm:text-sm leading-tight">{Number(roi).toFixed(0)}%</div>
            </div>
          )}
        </div>

        {/* Financeiro */}
        <div className="grid grid-cols-3 gap-1 sm:gap-2 mt-1 sm:mt-2">
          {[
            { label: 'Lance',     val: formatMoney(p.minimum_bid_cents, p.currency),    cls: 'text-gray-900 font-semibold' },
            { label: 'Avaliação', val: formatMoney(p.appraised_value_cents, p.currency), cls: 'text-gray-700' },
            { label: 'Dívida',    val: formatMoney(p.total_debt_cents, p.currency),      cls: 'text-red-600' },
          ].map(item => (
            <div key={item.label}>
              <p className="text-[9px] sm:text-xs text-gray-400 leading-tight">{item.label}</p>
              <p className={`text-[10px] sm:text-xs ${item.cls} leading-tight`}>{item.val}</p>
            </div>
          ))}
        </div>

        {p.auction_date && (
          <p className="text-[10px] sm:text-xs text-gray-400 mt-2">
            📅 {new Date(p.auction_date).toLocaleDateString('pt-BR')}
          </p>
        )}
      </div>

      {/* Footer */}
      <div
        className="border-t border-gray-50 px-2 sm:px-3 py-1.5 sm:py-2 bg-gray-50
                   flex items-center justify-between gap-1"
        onClick={e => e.stopPropagation()}
      >
        <div className="flex gap-1">
          {[
            { v: 'opportunity', l: '⭐', title: 'Oportunidade', c: 'bg-green-100 text-green-700 hover:bg-green-200' },
            { v: 'analyzing',   l: '🔍', title: 'Analisar',     c: 'bg-yellow-100 text-yellow-700 hover:bg-yellow-200' },
            { v: 'discarded',   l: '✕',  title: 'Descartar',    c: 'bg-red-100 text-red-500 hover:bg-red-200' },
          ].map(btn => (
            <button key={btn.v} title={btn.title}
              onClick={() => onStatusChange(p.id, btn.v)}
              className={`w-6 h-6 sm:w-7 sm:h-7 rounded-lg text-xs sm:text-sm font-medium transition-colors touch-manipulation ${btn.c}`}>
              {btn.l}
            </button>
          ))}
        </div>
        <div className="flex gap-1.5 sm:gap-2 text-xs">
          {p.source_url && (
            <a href={p.source_url} target="_blank" rel="noopener noreferrer"
              className="text-indigo-500 hover:underline text-[10px] sm:text-xs whitespace-nowrap">
              Fonte ↗
            </a>
          )}
          {p.pdf_file_url && (
            <a href={p.pdf_file_url} target="_blank" rel="noopener noreferrer"
              className="text-gray-400 hover:text-gray-600 text-[10px] sm:text-xs">PDF ↗</a>
          )}
        </div>
      </div>
    </div>
  );
}
