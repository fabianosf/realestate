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

  const handleFilterChange = f => { setFilters(f); setPage(1); };

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
      <header className="bg-white border-b border-gray-200 px-6 py-4 sticky top-0 z-10">
        <div className="max-w-screen-2xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-gray-900">Real Estate Mining</h1>
            <p className="text-xs text-gray-400">Leilões Brasil & EUA</p>
          </div>
          <div className="flex items-center gap-3">
            <select value={filters.ordering}
              onChange={e => handleFilterChange({ ...filters, ordering: e.target.value })}
              className="border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:ring-2 focus:ring-indigo-500">
              <option value="-created_at">Mais Recente</option>
              <option value="-estimated_profit_pct">Maior ROI</option>
              <option value="minimum_bid_cents">Menor Lance</option>
              <option value="auction_date">Data do Leilão</option>
            </select>
            <span className="text-sm text-gray-500">{total.toLocaleString('pt-BR')} imóveis</span>
            <div className="flex items-center gap-2 border-l border-gray-200 pl-3">
              <span className="text-xs text-gray-400 hidden sm:block">{user?.email}</span>
              <button onClick={logout}
                className="text-xs text-red-400 hover:text-red-600 transition-colors font-medium">
                Sair
              </button>
            </div>
          </div>
        </div>
      </header>

      {stats && <StatsBar stats={stats} />}

      <div className="max-w-screen-2xl mx-auto px-6 py-6 flex gap-6">
        <aside className="w-64 shrink-0 sticky top-20 self-start">
          <FilterPanel filters={filters} onChange={handleFilterChange} />
        </aside>

        <main className="flex-1 min-w-0">
          {loading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
              {Array.from({ length: 6 }).map((_, i) => (
                <div key={i} className="bg-white rounded-xl h-52 animate-pulse border border-gray-100" />
              ))}
            </div>
          ) : properties.length === 0 ? (
            <div className="text-center py-24 text-gray-400">
              <p className="text-5xl mb-4">🏠</p>
              <p className="text-lg font-medium text-gray-600">Nenhum imóvel encontrado</p>
              <p className="text-sm mt-1">Ajuste os filtros ou aguarde o próximo scraping</p>
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                {properties.map(p => (
                  <PropertyCard key={p.id} property={p}
                    onStatusChange={handleStatusChange}
                    onDetailOpen={setSelectedId}
                  />
                ))}
              </div>

              {totalPages > 1 && (
                <div className="flex justify-center gap-1.5 mt-8">
                  {Array.from({ length: Math.min(totalPages, 7) }, (_, i) => {
                    const n = Math.max(1, Math.min(page - 3, totalPages - 6)) + i;
                    return (
                      <button key={n} onClick={() => setPage(n)}
                        className={`w-9 h-9 rounded-lg text-sm font-medium transition-colors ${
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
