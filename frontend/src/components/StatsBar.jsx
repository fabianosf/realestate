export function StatsBar({ stats }) {
  const items = [
    { label: 'Total',        value: stats.total_properties?.toLocaleString('pt-BR'), color: 'text-indigo-600' },
    { label: 'Oportunidades',value: stats.opportunities,                              color: 'text-green-600' },
    { label: 'ROI Médio',    value: stats.avg_roi != null ? `${Number(stats.avg_roi).toFixed(1)}%` : '—', color: 'text-emerald-600' },
    { label: 'Em Análise',   value: stats.analyzing,                                  color: 'text-yellow-600' },
    { label: 'Brasil 🇧🇷',  value: stats.by_country?.BR ?? '—',                      color: 'text-blue-600' },
    { label: 'EUA 🇺🇸',     value: stats.by_country?.US ?? '—',                      color: 'text-purple-600' },
  ];

  return (
    <div className="bg-white border-b border-gray-200">
      <div className="max-w-screen-2xl mx-auto px-4 sm:px-6 py-2 sm:py-3
                      grid grid-cols-3 sm:grid-cols-6 gap-y-2 gap-x-2 sm:gap-8">
        {items.map(item => (
          <div key={item.label} className="text-center">
            <p className={`text-base sm:text-lg font-bold ${item.color}`}>{item.value ?? '—'}</p>
            <p className="text-[10px] sm:text-xs text-gray-400 whitespace-nowrap">{item.label}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
