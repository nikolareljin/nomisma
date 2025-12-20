import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { Coins, TrendingUp, Camera, ShoppingCart, ArrowRight } from 'lucide-react';
import { coinsAPI } from '../api';

export default function Dashboard() {
    const { data: coins, isLoading } = useQuery({
        queryKey: ['coins', { limit: 6 }],
        queryFn: () => coinsAPI.list({ limit: 6, sort_by: 'created_at', sort_order: 'desc' }),
    });

    const recentCoins = coins?.data || [];

    // Calculate stats
    const totalCoins = recentCoins.length; // This would come from a stats endpoint in production
    const totalValue = recentCoins.reduce((sum, coin) => sum + (coin.estimated_value || 0), 0);
    const forSale = recentCoins.filter(c => c.is_for_sale).length;

    return (
        <div className="space-y-8">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
                <p className="text-gray-600 mt-1">Welcome to your coin collection management system</p>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <StatCard
                    icon={Coins}
                    label="Total Coins"
                    value={totalCoins}
                    color="blue"
                />
                <StatCard
                    icon={TrendingUp}
                    label="Total Value"
                    value={`$${totalValue.toFixed(2)}`}
                    color="green"
                />
                <StatCard
                    icon={Camera}
                    label="Scanned Today"
                    value="0"
                    color="purple"
                />
                <StatCard
                    icon={ShoppingCart}
                    label="For Sale"
                    value={forSale}
                    color="gold"
                />
            </div>

            {/* Quick Actions */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <QuickAction
                    to="/scan"
                    icon={Camera}
                    title="Scan New Coin"
                    description="Capture and analyze a coin with your microscope"
                    color="primary"
                />
                <QuickAction
                    to="/coins"
                    icon={Coins}
                    title="Browse Collection"
                    description="View and manage your coin collection"
                    color="gray"
                />
                <QuickAction
                    to="/coins?for_sale=true"
                    icon={ShoppingCart}
                    title="Manage Listings"
                    description="View and create eBay listings"
                    color="gold"
                />
            </div>

            {/* Recent Coins */}
            <div>
                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-2xl font-bold text-gray-900">Recent Coins</h2>
                    <Link to="/coins" className="text-primary-600 hover:text-primary-700 flex items-center space-x-1">
                        <span>View all</span>
                        <ArrowRight className="w-4 h-4" />
                    </Link>
                </div>

                {isLoading ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {[...Array(6)].map((_, i) => (
                            <div key={i} className="card animate-pulse">
                                <div className="bg-gray-200 h-48 rounded-lg mb-4"></div>
                                <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                                <div className="h-4 bg-gray-200 rounded w-1/2"></div>
                            </div>
                        ))}
                    </div>
                ) : recentCoins.length === 0 ? (
                    <div className="card text-center py-12">
                        <Coins className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                        <h3 className="text-lg font-medium text-gray-900 mb-2">No coins yet</h3>
                        <p className="text-gray-600 mb-4">Start by scanning your first coin</p>
                        <Link to="/scan" className="btn btn-primary inline-flex items-center space-x-2">
                            <Camera className="w-5 h-5" />
                            <span>Scan Coin</span>
                        </Link>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {recentCoins.map((coin) => (
                            <CoinCard key={coin.id} coin={coin} />
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}

function StatCard({ icon: Icon, label, value, color }) {
    const colorClasses = {
        blue: 'bg-blue-50 text-blue-600',
        green: 'bg-green-50 text-green-600',
        purple: 'bg-purple-50 text-purple-600',
        gold: 'bg-gold-50 text-gold-600',
    };

    return (
        <div className="card">
            <div className="flex items-center justify-between">
                <div>
                    <p className="text-sm text-gray-600 mb-1">{label}</p>
                    <p className="text-2xl font-bold text-gray-900">{value}</p>
                </div>
                <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${colorClasses[color]}`}>
                    <Icon className="w-6 h-6" />
                </div>
            </div>
        </div>
    );
}

function QuickAction({ to, icon: Icon, title, description, color }) {
    const colorClasses = {
        primary: 'border-primary-200 hover:border-primary-400 hover:bg-primary-50',
        gray: 'border-gray-200 hover:border-gray-400 hover:bg-gray-50',
        gold: 'border-gold-200 hover:border-gold-400 hover:bg-gold-50',
    };

    return (
        <Link
            to={to}
            className={`card border-2 transition-all cursor-pointer ${colorClasses[color]}`}
        >
            <Icon className="w-8 h-8 text-gray-700 mb-3" />
            <h3 className="text-lg font-semibold text-gray-900 mb-1">{title}</h3>
            <p className="text-sm text-gray-600">{description}</p>
        </Link>
    );
}

function CoinCard({ coin }) {
    const imageUrl = coin.primary_image
        ? `http://localhost:8000/images/${coin.primary_image}`
        : 'https://via.placeholder.com/300x200?text=No+Image';

    return (
        <Link to={`/coins/${coin.id}`} className="card hover:shadow-lg transition-shadow">
            <div className="aspect-video bg-gray-100 rounded-lg mb-4 overflow-hidden">
                <img
                    src={imageUrl}
                    alt={`${coin.country} ${coin.denomination}`}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                        e.target.src = 'https://via.placeholder.com/300x200?text=No+Image';
                    }}
                />
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
