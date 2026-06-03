import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { PropertyCard } from './PropertyCard';
import { FilterPanel } from './FilterPanel';
import { StatsBar } from './StatsBar';
import { PropertyDetail } from './PropertyDetail';

const PAGE_SIZE = 20;

const DEFAULT_FILTERS = {
  country: '', auction_type: '', debt_type: '',
  status: '', min_roi: 0, max_bid: '', ordering: '-created_at',
};

function buildQuery(f, page) {
  const p = new URLSearchParams();
  if (f.country)      p.set('country', f.country);
  if (f.auction_type) p.set('auction_type', f.auction_type);
  if (f.debt_type)    p.set('debt_type', f.debt_type);
  if (f.status)       p.set('status', f.status);
  if (Number(f.min_roi) > 0)
    p.set('estimated_profit_pct__gte', String(f.min_roi));
  if (f.max_bid && Number(f.max_bid) > 0)
    p.set('minimum_bid_cents__lte', String(Math.round(Number(f.max_bid) * 100)));
  p.set('ordering', f.ordering || '-created_at');
  p.set('page', String(page));
  return p.toString();
}

export function Dashboard() {
  const { authFetch, API, user, logout } = useAuth();
  const [properties, setProperties] = useState([]);
  const [filters, setFilters]       = useState(DEFAULT_FILTERS);
  const [stats, setStats]           = useState(null);
  const [loading, setLoading]       = useState(false);
  const [page, setPage]             = useState(1);
  const [total, setTotal]           = useState(0);
  const [selectedId, setSelectedId] = useState(null);
  const [showFilters, setShowFilters] = useState(false);

  const fetchProperties = useCallback(async () => {
    setLoading(true);
    try {
      const res = await authFetch(`${API}/properties/?${buildQuery(filters, page)}`);
      if (!res.ok) return;
      const data = await res.json();
      setProperties(data.results || []);
      setTotal(data.count || 0);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, [filters, page, authFetch, API]);

  const fetchStats = useCallback(async () => {
    try {
      const res = await authFetch(`${API}/properties/stats/`);
      if (res.ok) setStats(await res.json());
    } catch (e) {
      console.error('[fetchStats]', e.message);
    }
  }, [authFetch, API]);

  useEffect(() => { fetchProperties(); }, [fetchProperties]);
  useEffect(() => { fetchStats(); }, [fetchStats]);

  const handleFilterChange = f => { setFilters(f); setPage(1); setShowFilters(false); };

  const handleStatusChange = async (id, newStatus) => {
    try {
      await authFetch(`${API}/properties/${id}/`, {
        method: 'PATCH',
        body: JSON.stringify({ status: newStatus }),
      });
      fetchProperties();
      fetchStats();
    } catch (e) {
      console.error('[handleStatusChange]', e.message);
    }
  };

  const totalPages = Math.ceil(total / PAGE_SIZE);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-4 sm:px-6 py-3 sm:py-4 sticky top-0 z-10">
        <div className="max-w-screen-2xl mx-auto flex items-center justify-between gap-2">
          <div className="min-w-0">
            <h1 className="text-base sm:text-xl font-bold text-gray-900 truncate">Real Estate Mining</h1>
            <p className="text-xs text-gray-400 hidden sm:block">Leilões Brasil & EUA</p>
          </div>

          <div className="flex items-center gap-2 sm:gap-3 shrink-0">
            {/* Botão filtros mobile */}
            <button
              onClick={() => setShowFilters(v => !v)}
              className="md:hidden flex items-center gap-1 text-xs border border-gray-300 rounded-lg px-2.5 py-1.5 text-gray-600 hover:bg-gray-50">
              ⚙ Filtros
            </button>

            <select value={filters.ordering}
              onChange={e => handleFilterChange({ ...filters, ordering: e.target.value })}
              className="border border-gray-300 rounded-lg px-2 sm:px-3 py-1.5 text-xs sm:text-sm focus:ring-2 focus:ring-indigo-500 max-w-[130px] sm:max-w-none">
              <option value="-created_at">Mais Recente</option>
              <option value="-estimated_profit_pct">Maior ROI</option>
              <option value="minimum_bid_cents">Menor Lance</option>
              <option value="auction_date">Data do Leilão</option>
            </select>

            <span className="text-xs sm:text-sm text-gray-500 hidden sm:block whitespace-nowrap">
              {total.toLocaleString('pt-BR')} imóveis
            </span>

            <div className="flex items-center gap-2 border-l border-gray-200 pl-2 sm:pl-3">
              <span className="text-xs text-gray-400 hidden lg:block truncate max-w-[140px]">{user?.email}</span>
              <button onClick={logout}
                className="text-xs text-red-400 hover:text-red-600 transition-colors font-medium whitespace-nowrap">
                Sair
              </button>
            </div>
          </div>
        </div>
      </header>

      {stats && <StatsBar stats={stats} />}

      {/* Filtros mobile (drawer) */}
      {showFilters && (
        <div className="md:hidden fixed inset-0 z-40 flex flex-col" onClick={() => setShowFilters(false)}>
          <div className="flex-1 bg-black/40" />
          <div
            className="bg-white shadow-2xl max-h-[80vh] overflow-y-auto rounded-t-2xl"
            onClick={e => e.stopPropagation()}>
            <div className="flex justify-between items-center px-5 py-3 border-b border-gray-100 sticky top-0 bg-white">
              <span className="font-semibold text-gray-800 text-sm">Filtros</span>
              <button onClick={() => setShowFilters(false)} className="text-2xl text-gray-400 leading-none">×</button>
            </div>
            <div className="px-4 py-4">
              <FilterPanel filters={filters} onChange={handleFilterChange} />
            </div>
          </div>
        </div>
      )}

      {/* Layout principal */}
      <div className="max-w-screen-2xl mx-auto px-4 sm:px-6 py-4 sm:py-6 flex gap-6">
        {/* Sidebar filtros desktop */}
        <aside className="hidden md:block w-56 lg:w-64 shrink-0 sticky top-20 self-start">
          <FilterPanel filters={filters} onChange={handleFilterChange} />
        </aside>

        {/* Grid de cards */}
        <main className="flex-1 min-w-0">
          {/* Contador mobile */}
          <p className="text-xs text-gray-400 mb-3 md:hidden">
            {total.toLocaleString('pt-BR')} imóveis encontrados
          </p>

          {loading ? (
            <div className="grid grid-cols-2 lg:grid-cols-2 xl:grid-cols-3 gap-2 sm:gap-4">
              {Array.from({ length: 6 }).map((_, i) => (
                <div key={i} className="bg-white rounded-xl h-44 sm:h-52 animate-pulse border border-gray-100" />
              ))}
            </div>
          ) : properties.length === 0 ? (
            <div className="text-center py-16 sm:py-24 text-gray-400">
              <p className="text-5xl mb-4">🏠</p>
              <p className="text-lg font-medium text-gray-600">Nenhum imóvel encontrado</p>
              <p className="text-sm mt-1">Ajuste os filtros ou aguarde o próximo scraping</p>
            </div>
          ) : (
            <>
              <div className="grid grid-cols-2 lg:grid-cols-2 xl:grid-cols-3 gap-2 sm:gap-4">
                {properties.map(p => (
                  <PropertyCard key={p.id} property={p}
                    onStatusChange={handleStatusChange}
                    onDetailOpen={setSelectedId}
                  />
                ))}
              </div>

              {totalPages > 1 && (
                <div className="flex justify-center gap-1 sm:gap-1.5 mt-6 sm:mt-8 flex-wrap">
                  {Array.from({ length: Math.min(totalPages, 7) }, (_, i) => {
                    const n = Math.max(1, Math.min(page - 3, totalPages - 6)) + i;
                    return (
                      <button key={n} onClick={() => setPage(n)}
                        className={`w-8 h-8 sm:w-9 sm:h-9 rounded-lg text-xs sm:text-sm font-medium transition-colors ${
                          page === n
                            ? 'bg-indigo-600 text-white'
                            : 'bg-white text-gray-600 hover:bg-gray-100 border border-gray-200'
                        }`}>{n}</button>
                    );
                  })}
                </div>
              )}
            </>
          )}
        </main>
      </div>

      {selectedId && (
        <PropertyDetail
          propertyId={selectedId}
          onClose={() => setSelectedId(null)}
          onUpdate={() => { fetchProperties(); fetchStats(); }}
        />
      )}
    </div>
  );
}
