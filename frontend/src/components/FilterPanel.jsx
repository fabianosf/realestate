const AUCTION_TYPES = [
  { value: '', label: 'Todos' },
  { value: 'judicial', label: 'Judicial (BR)' },
  { value: 'extrajudicial', label: 'Extrajudicial (BR)' },
  { value: 'foreclosure', label: 'Foreclosure (US)' },
  { value: 'tax_lien', label: 'Tax Lien (US)' },
  { value: 'tax_deed', label: 'Tax Deed (US)' },
];

const DEBT_TYPES = [
  { value: '', label: 'Todos' },
  { value: 'iptu', label: 'IPTU' },
  { value: 'condominium', label: 'Condomínio' },
  { value: 'mortgage', label: 'Hipoteca' },
  { value: 'property_tax', label: 'Property Tax' },
  { value: 'hoa', label: 'HOA' },
];

export function FilterPanel({ filters, onChange }) {
  const set = (key, val) => onChange({ ...filters, [key]: val });

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5 space-y-5">
      <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Filtros</h2>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1.5">País</label>
        <div className="flex gap-2">
          {[['', 'Todos'], ['BR', '🇧🇷 BR'], ['US', '🇺🇸 US']].map(([v, l]) => (
            <button key={v} onClick={() => set('country', v)}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                filters.country === v
                  ? 'bg-indigo-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}>{l}</button>
          ))}
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Tipo de Leilão</label>
        <select value={filters.auction_type} onChange={e => set('auction_type', e.target.value)}
          className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent">
          {AUCTION_TYPES.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Tipo de Dívida</label>
        <select value={filters.debt_type} onChange={e => set('debt_type', e.target.value)}
          className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent">
          {DEBT_TYPES.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          ROI Mínimo: <span className="text-indigo-600 font-semibold">{filters.min_roi}%</span>
        </label>
        <input type="range" min="0" max="300" step="5" value={filters.min_roi}
          onChange={e => set('min_roi', Number(e.target.value))}
          className="w-full accent-indigo-600" />
        <div className="flex justify-between text-xs text-gray-400 mt-0.5">
          <span>0%</span><span>150%</span><span>300%</span>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Lance Máximo</label>
        <input type="number" placeholder="Ex: 500000" value={filters.max_bid}
          onChange={e => set('max_bid', e.target.value)}
          className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500" />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1.5">Status</label>
        <div className="flex flex-wrap gap-1.5">
          {[
            { v: '', l: 'Todos', c: 'bg-gray-100 text-gray-600' },
            { v: 'discovered', l: 'Novo', c: 'bg-blue-100 text-blue-700' },
            { v: 'opportunity', l: 'Oportunidade', c: 'bg-green-100 text-green-700' },
            { v: 'analyzing', l: 'Análise', c: 'bg-yellow-100 text-yellow-700' },
          ].map(s => (
            <button key={s.v} onClick={() => set('status', s.v)}
              className={`px-2.5 py-1 rounded-full text-xs font-medium transition-all ${s.c} ${
                filters.status === s.v ? 'ring-2 ring-offset-1 ring-current' : ''
              }`}>{s.l}</button>
          ))}
        </div>
      </div>

      <button
        onClick={() => onChange({ country: '', auction_type: '', debt_type: '', status: '', min_roi: 0, max_bid: '', ordering: '-roi_score' })}
        className="w-full text-xs text-gray-400 hover:text-gray-600 py-1 transition-colors">
        Limpar filtros
      </button>
    </div>
  );
}
