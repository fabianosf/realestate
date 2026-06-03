import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';

function fmt(cents, currency = 'BRL') {
  if (cents == null) return '—';
  return new Intl.NumberFormat(currency === 'BRL' ? 'pt-BR' : 'en-US', {
    style: 'currency', currency,
  }).format(cents / 100);
}

const STATUS_OPTIONS = [
  { v: 'discovered',  l: 'Descoberto',   c: 'bg-blue-100 text-blue-700' },
  { v: 'analyzing',   l: 'Em Análise',   c: 'bg-yellow-100 text-yellow-700' },
  { v: 'opportunity', l: 'Oportunidade', c: 'bg-green-100 text-green-700' },
  { v: 'discarded',   l: 'Descartado',   c: 'bg-red-100 text-red-500' },
  { v: 'acquired',    l: 'Adquirido',    c: 'bg-purple-100 text-purple-700' },
];

export function PropertyDetail({ propertyId, onClose, onUpdate }) {
  const { authFetch, API } = useAuth();
  const [detail, setDetail]           = useState(null);
  const [loading, setLoading]         = useState(true);
  const [saving, setSaving]           = useState(false);
  const [marketValue, setMarketValue] = useState('');
  const [notes, setNotes]             = useState('');
  const [selStatus, setSelStatus]     = useState('');

  useEffect(() => {
    setLoading(true);
    authFetch(`${API}/properties/${propertyId}/`)
      .then(r => r.json())
      .then(data => {
        setDetail(data);
        setMarketValue(data.market_value_cents ? (data.market_value_cents / 100).toFixed(2) : '');
        setNotes(data.notes || '');
        setSelStatus(data.status);
      })
      .finally(() => setLoading(false));
  }, [propertyId]);

  const handleSave = async () => {
    setSaving(true);
    try {
      await authFetch(`${API}/properties/${propertyId}/`, {
        method: 'PATCH',
        body: JSON.stringify({
          status: selStatus,
          notes,
          market_value_cents: marketValue ? Math.round(Number(marketValue) * 100) : null,
        }),
      });
      onUpdate?.();
      onClose();
    } finally {
      setSaving(false);
    }
  };

  const pdfUrl      = detail?.pdf_file_url || detail?.pdf_url || null;
  const keyValues   = detail?.extra_data?.pdf_extraction?.key_values || {};
  const debtMentions = detail?.extra_data?.pdf_extraction?.debt_mentions_count;

  return (
    /* Overlay */
    <div className="fixed inset-0 z-50 flex" onClick={onClose}>
      {/* Backdrop — oculto em mobile (drawer cobre tela toda) */}
      <div className="hidden sm:block flex-1 bg-black/30" />

      {/* Drawer — tela cheia no mobile, largura parcial no desktop */}
      <div
        className="
          w-full
          sm:w-[420px]
          md:w-[480px]
          lg:w-[560px]
          xl:w-[620px]
          bg-white shadow-2xl flex flex-col overflow-hidden
          max-h-screen
        "
        onClick={e => e.stopPropagation()}
      >
        {/* Header */}
        <div className="px-4 sm:px-6 py-3 sm:py-4 border-b border-gray-100 flex items-center justify-between shrink-0">
          <h2 className="font-bold text-gray-900 text-sm sm:text-base truncate pr-2">
            {loading ? 'Carregando...' : (detail?.address || detail?.external_id || 'Imóvel')}
          </h2>
          <button
            onClick={onClose}
            className="shrink-0 w-8 h-8 flex items-center justify-center rounded-lg text-gray-400 hover:text-gray-700 hover:bg-gray-100 text-xl leading-none transition-colors">
            ×
          </button>
        </div>

        {loading ? (
          <div className="flex-1 flex items-center justify-center">
            <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : detail ? (
          <div className="flex-1 overflow-y-auto divide-y divide-gray-50 overscroll-contain">

            {/* Localização */}
            <section className="px-4 sm:px-6 py-4">
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Localização</p>
              <p className="text-sm font-medium text-gray-800 break-words">{detail.address || '—'}</p>
              <p className="text-sm text-gray-500 break-words">
                {detail.city}{detail.state_province ? `, ${detail.state_province}` : ''}
                {detail.zip_code ? ` · ${detail.zip_code}` : ''}
                {detail.county ? ` · ${detail.county}` : ''}
              </p>
            </section>

            {/* Financeiro */}
            <section className="px-4 sm:px-6 py-4">
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Financeiro</p>
              <div className="grid grid-cols-2 gap-2 sm:gap-3 mb-3">
                <div className="bg-gray-50 rounded-xl p-2.5 sm:p-3">
                  <p className="text-xs text-gray-400 mb-0.5">Lance Mínimo</p>
                  <p className="font-bold text-gray-900 text-xs sm:text-sm break-words">
                    {fmt(detail.minimum_bid_cents, detail.currency)}
                  </p>
                </div>
                <div className="bg-gray-50 rounded-xl p-2.5 sm:p-3">
                  <p className="text-xs text-gray-400 mb-0.5">Valor Avaliado</p>
                  <p className="font-semibold text-gray-700 text-xs sm:text-sm break-words">
                    {fmt(detail.appraised_value_cents, detail.currency)}
                  </p>
                </div>
                <div className="bg-red-50 rounded-xl p-2.5 sm:p-3">
                  <p className="text-xs text-red-400 mb-0.5">Total Dívidas</p>
                  <p className="font-bold text-red-700 text-xs sm:text-sm break-words">
                    {fmt(detail.total_debt_cents, detail.currency)}
                  </p>
                </div>
                <div className="bg-indigo-50 rounded-xl p-2.5 sm:p-3">
                  <p className="text-xs text-indigo-400 mb-0.5">ROI Estimado</p>
                  <p className="font-bold text-indigo-700 text-xs sm:text-sm">
                    {detail.estimated_profit_pct != null
                      ? `${Number(detail.estimated_profit_pct).toFixed(1)}%`
                      : '— (inserir valor de mercado)'}
                  </p>
                </div>
              </div>
              <label className="block text-xs text-gray-500 mb-1">
                Valor de Mercado ({detail.currency}) — usado para calcular ROI
              </label>
              <input
                type="number"
                inputMode="decimal"
                step="0.01"
                min="0"
                value={marketValue}
                onChange={e => setMarketValue(e.target.value)}
                placeholder={detail.currency === 'BRL' ? 'Ex: 250000.00' : 'Ex: 85000.00'}
                className="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm focus:ring-2 focus:ring-indigo-500 outline-none"
              />
            </section>

            {/* Leilão */}
            <section className="px-4 sm:px-6 py-4">
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Leilão</p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-1.5 text-sm">
                <div><span className="text-gray-400">Tipo: </span><span className="font-medium">{detail.auction_type}</span></div>
                <div>
                  <span className="text-gray-400">Data: </span>
                  <span className="font-medium">
                    {detail.auction_date ? new Date(detail.auction_date).toLocaleDateString('pt-BR') : '—'}
                  </span>
                </div>
                {detail.auction_number && (
                  <div className="break-all"><span className="text-gray-400">Nº Leilão: </span><span>{detail.auction_number}</span></div>
                )}
                {detail.process_number && (
                  <div className="break-all"><span className="text-gray-400">Processo: </span><span>{detail.process_number}</span></div>
                )}
              </div>
            </section>

            {/* Dívidas */}
            {detail.debt_details?.length > 0 && (
              <section className="px-4 sm:px-6 py-4">
                <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Detalhes das Dívidas</p>
                <div className="space-y-1.5">
                  {detail.debt_details.map((d, i) => (
                    <div key={i} className="bg-red-50 rounded-lg px-3 py-2 text-sm flex flex-wrap justify-between items-center gap-1">
                      <span className="text-gray-700 break-words">{d.type || d.description || `Dívida ${i + 1}`}</span>
                      {d.amount != null && (
                        <span className="font-semibold text-red-700 shrink-0">{fmt(d.amount * 100, detail.currency)}</span>
                      )}
                    </div>
                  ))}
                </div>
              </section>
            )}

            {/* Dados do PDF */}
            {Object.keys(keyValues).length > 0 && (
              <section className="px-4 sm:px-6 py-4">
                <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
                  Dados Extraídos do PDF
                  {debtMentions != null && (
                    <span className="ml-2 font-normal text-gray-300 normal-case">
                      · {debtMentions} menções
                    </span>
                  )}
                </p>
                <div className="bg-gray-50 rounded-lg p-3 divide-y divide-gray-100">
                  {Object.entries(keyValues).map(([k, v]) => (
                    <div key={k} className="flex flex-wrap justify-between text-sm py-1.5 first:pt-0 last:pb-0 gap-1">
                      <span className="text-gray-500 shrink-0">{k.replace(/_/g, ' ')}</span>
                      <span className="text-gray-800 font-medium text-right break-all ml-2">{v}</span>
                    </div>
                  ))}
                </div>
              </section>
            )}

            {/* PDF */}
            <section className="px-4 sm:px-6 py-4">
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Edital / PDF</p>
              {pdfUrl ? (
                <>
                  <a href={pdfUrl} target="_blank" rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 bg-indigo-50 text-indigo-700 px-4 py-2.5 rounded-lg text-sm font-medium hover:bg-indigo-100 transition-colors w-full sm:w-auto justify-center sm:justify-start">
                    Abrir PDF ↗
                  </a>
                  <iframe
                    src={pdfUrl}
                    title="Edital"
                    className="w-full mt-3 rounded-lg border border-gray-200"
                    style={{ height: 'min(50vh, 280px)' }}
                  />
                </>
              ) : (
                <p className="text-sm text-gray-400">PDF ainda não processado.</p>
              )}
            </section>

            {/* Status & Notas */}
            <section className="px-4 sm:px-6 py-4">
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Status</p>
              <div className="flex flex-wrap gap-2 mb-4">
                {STATUS_OPTIONS.map(s => (
                  <button
                    key={s.v}
                    onClick={() => setSelStatus(s.v)}
                    className={`px-3 py-2 rounded-lg text-xs font-medium transition-all touch-manipulation ${s.c} ${
                      selStatus === s.v ? 'ring-2 ring-offset-1 ring-current' : 'opacity-50 hover:opacity-80 active:opacity-100'
                    }`}>
                    {s.l}
                  </button>
                ))}
              </div>
              <label className="block text-xs text-gray-500 mb-1">Notas do VA</label>
              <textarea
                value={notes}
                onChange={e => setNotes(e.target.value)}
                rows={4}
                placeholder="Observações, checklist, pontos de atenção..."
                className="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm focus:ring-2 focus:ring-indigo-500 resize-none outline-none"
              />
            </section>

            {/* Fonte */}
            {detail.source_url && (
              <section className="px-4 sm:px-6 py-3">
                <a href={detail.source_url} target="_blank" rel="noopener noreferrer"
                  className="text-sm text-indigo-500 hover:underline break-all">
                  Ver anúncio original ↗
                </a>
              </section>
            )}
          </div>
        ) : (
          <div className="flex-1 flex items-center justify-center text-gray-400 text-sm">
            Imóvel não encontrado.
          </div>
        )}

        {/* Footer */}
        <div className="px-4 sm:px-6 py-3 sm:py-4 border-t border-gray-100 flex justify-between items-center bg-gray-50 shrink-0 gap-3">
          <button
            onClick={onClose}
            className="text-sm text-gray-500 hover:text-gray-700 transition-colors px-3 py-2 rounded-lg hover:bg-gray-100">
            Fechar
          </button>
          <button
            onClick={handleSave}
            disabled={saving || loading}
            className="flex-1 sm:flex-none bg-indigo-600 text-white px-5 py-2.5 rounded-lg text-sm font-medium hover:bg-indigo-700 disabled:opacity-50 transition-colors text-center">
            {saving ? 'Salvando...' : 'Salvar alterações'}
          </button>
        </div>
      </div>
    </div>
  );
}
