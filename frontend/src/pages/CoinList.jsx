import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { Search, Filter, Grid, List as ListIcon } from 'lucide-react';
import { coinsAPI } from '../api';

export default function CoinList() {
    const [search, setSearch] = useState('');
    const [filters, setFilters] = useState({});
    const [viewMode, setViewMode] = useState('grid'); // grid or list

    const { data: coins, isLoading } = useQuery({
        queryKey: ['coins', { search, ...filters }],
        queryFn: () => coinsAPI.list({ search, ...filters, limit: 100 }),
    });

    const coinsList = coins?.data || [];

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">Coin Collection</h1>
                    <p className="text-gray-600 mt-1">{coinsList.length} coins in your collection</p>
                </div>
                <div className="flex items-center space-x-2">
                    <button
                        onClick={() => setViewMode('grid')}
                        className={`p-2 rounded ${viewMode === 'grid' ? 'bg-primary-100 text-primary-700' : 'text-gray-600'}`}
                    >
                        <Grid className="w-5 h-5" />
                    </button>
                    <button
                        onClick={() => setViewMode('list')}
                        className={`p-2 rounded ${viewMode === 'list' ? 'bg-primary-100 text-primary-700' : 'text-gray-600'}`}
                    >
                        <ListIcon className="w-5 h-5" />
                    </button>
                </div>
            </div>

            {/* Search and Filters */}
            <div className="card">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="md:col-span-2">
                        <div className="relative">
                            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                            <input
                                type="text"
                                placeholder="Search by inventory #, country, denomination..."
                                value={search}
                                onChange={(e) => setSearch(e.target.value)}
                                className="input pl-10"
                            />
                        </div>
                    </div>
                    <div>
                        <select
                            value={filters.country || ''}
                            onChange={(e) => setFilters({ ...filters, country: e.target.value || undefined })}
                            className="input"
                        >
                            <option value="">All Countries</option>
                            <option value="United States">United States</option>
                            <option value="Canada">Canada</option>
                            <option value="United Kingdom">United Kingdom</option>
                            <option value="Germany">Germany</option>
                            <option value="France">France</option>
                        </select>
                    </div>
                    <div>
                        <select
                            value={filters.condition_grade || ''}
                            onChange={(e) => setFilters({ ...filters, condition_grade: e.target.value || undefined })}
                            className="input"
                        >
                            <option value="">All Conditions</option>
                            <option value="Poor">Poor</option>
                            <option value="Fair">Fair</option>
                            <option value="Good">Good</option>
                            <option value="Very Good">Very Good</option>
                            <option value="Fine">Fine</option>
                            <option value="Very Fine">Very Fine</option>
                            <option value="Extremely Fine">Extremely Fine</option>
                            <option value="About Uncirculated">About Uncirculated</option>
                            <option value="Uncirculated">Uncirculated</option>
                        </select>
                    </div>
                </div>
            </div>

            {/* Coins Grid/List */}
            {isLoading ? (
                <div className="text-center py-12">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
                </div>
            ) : coinsList.length === 0 ? (
                <div className="card text-center py-12">
                    <p className="text-gray-600">No coins found</p>
                </div>
            ) : viewMode === 'grid' ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {coinsList.map((coin) => (
                        <CoinCard key={coin.id} coin={coin} />
                    ))}
                </div>
            ) : (
                <div className="card divide-y divide-gray-200">
                    {coinsList.map((coin) => (
                        <CoinListItem key={coin.id} coin={coin} />
                    ))}
                </div>
            )}
        </div>
    );
}

function CoinCard({ coin }) {
    const obversePath = coin.obverse_image || coin.primary_image;
    const obverseUrl = obversePath
        ? `http://localhost:8000/images/${obversePath}`
        : 'https://via.placeholder.com/300x200?text=No+Image';
    const reverseUrl = coin.reverse_image
        ? `http://localhost:8000/images/${coin.reverse_image}`
        : null;

    return (
        <Link to={`/coins/${coin.id}`} className="card hover:shadow-lg transition-shadow">
            <div className="aspect-video bg-gray-100 rounded-lg mb-4 overflow-hidden grid grid-cols-2">
                <img
                    src={obverseUrl}
                    alt={`${coin.country} ${coin.denomination} obverse`}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                        e.target.src = 'https://via.placeholder.com/300x200?text=No+Image';
                    }}
                />
                {reverseUrl ? (
                    <img
                        src={reverseUrl}
                        alt={`${coin.country} ${coin.denomination} reverse`}
                        className="w-full h-full object-cover"
                        onError={(e) => {
                            e.target.src = 'https://via.placeholder.com/300x200?text=No+Image';
                        }}
                    />
                ) : (
                    <div className="flex items-center justify-center text-xs text-gray-400 bg-gray-50">
                        No reverse
                    </div>
                )}
            </div>
            <div className="space-y-2">
                <div className="flex items-center justify-between">
                    <span className="text-xs font-mono text-gray-500">{coin.inventory_number}</span>
                    {coin.estimated_value && (
                        <span className="text-sm font-semibold text-green-600">
                            ${coin.estimated_value.toFixed(2)}
                        </span>
                    )}
                </div>
                <h3 className="font-semibold text-gray-900">
                    {coin.country} {coin.denomination}
                </h3>
                <div className="flex items-center justify-between text-sm text-gray-600">
                    <span>{coin.year || 'Unknown year'}</span>
                    {coin.condition_grade && (
                        <span className="px-2 py-1 bg-gray-100 rounded text-xs">{coin.condition_grade}</span>
                    )}
                </div>
            </div>
        </Link>
    );
}

function CoinListItem({ coin }) {
    const obversePath = coin.obverse_image || coin.primary_image;
    const obverseUrl = obversePath
        ? `http://localhost:8000/images/${obversePath}`
        : 'https://via.placeholder.com/100x100?text=No+Image';
    const reverseUrl = coin.reverse_image
        ? `http://localhost:8000/images/${coin.reverse_image}`
        : null;

    return (
        <Link to={`/coins/${coin.id}`} className="flex items-center space-x-4 py-4 hover:bg-gray-50 transition-colors">
            <div className="flex space-x-2">
                <img
                    src={obverseUrl}
                    alt={`${coin.country} ${coin.denomination} obverse`}
                    className="w-16 h-16 object-cover rounded-lg"
                    onError={(e) => {
                        e.target.src = 'https://via.placeholder.com/100x100?text=No+Image';
                    }}
                />
                {reverseUrl ? (
                    <img
                        src={reverseUrl}
                        alt={`${coin.country} ${coin.denomination} reverse`}
                        className="w-16 h-16 object-cover rounded-lg"
                        onError={(e) => {
                            e.target.src = 'https://via.placeholder.com/100x100?text=No+Image';
                        }}
                    />
                ) : (
                    <div className="w-16 h-16 rounded-lg bg-gray-100 text-xs text-gray-400 flex items-center justify-center">
                        No reverse
                    </div>
                )}
            </div>
            <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-3 mb-1">
                    <span className="text-xs font-mono text-gray-500">{coin.inventory_number}</span>
                    {coin.condition_grade && (
                        <span className="px-2 py-1 bg-gray-100 rounded text-xs">{coin.condition_grade}</span>
                    )}
                </div>
                <h3 className="font-semibold text-gray-900 truncate">
                    {coin.country} {coin.denomination} {coin.year}
                </h3>
            </div>
            {coin.estimated_value && (
                <div className="text-right">
                    <p className="text-sm font-semibold text-green-600">${coin.estimated_value.toFixed(2)}</p>
                    <p className="text-xs text-gray-500">Estimated Value</p>
                </div>
            )}
        </Link>
    );
}
