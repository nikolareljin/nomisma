import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Coins, Camera, LayoutDashboard, ShoppingCart } from 'lucide-react';
import Dashboard from './pages/Dashboard';
import ScanCoin from './pages/ScanCoin';
import CoinList from './pages/CoinList';
import CoinDetail from './pages/CoinDetail';

function Navigation() {
    const location = useLocation();

    const isActive = (path) => location.pathname === path;

    const navItems = [
        { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
        { path: '/scan', icon: Camera, label: 'Scan Coin' },
        { path: '/coins', icon: Coins, label: 'Collection' },
    ];

    return (
        <nav className="bg-white border-b border-gray-200 sticky top-0 z-50 shadow-sm">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between h-16">
                    <div className="flex items-center">
                        <Link to="/" className="flex items-center space-x-3">
                            <div className="w-10 h-10 bg-gradient-to-br from-gold-400 to-gold-600 rounded-full flex items-center justify-center">
                                <Coins className="w-6 h-6 text-white" />
                            </div>
                            <span className="text-2xl font-bold bg-gradient-to-r from-gold-600 to-gold-800 bg-clip-text text-transparent">
                                Nomisma
                            </span>
                        </Link>
                    </div>

                    <div className="flex items-center space-x-1">
                        {navItems.map((item) => {
                            const Icon = item.icon;
                            const active = isActive(item.path);

                            return (
                                <Link
                                    key={item.path}
                                    to={item.path}
                                    className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all ${active
                                            ? 'bg-primary-50 text-primary-700 font-medium'
                                            : 'text-gray-600 hover:bg-gray-100'
                                        }`}
                                >
                                    <Icon className="w-5 h-5" />
                                    <span>{item.label}</span>
                                </Link>
                            );
                        })}
                    </div>
                </div>
            </div>
        </nav>
    );
}

function App() {
    return (
        <Router>
            <div className="min-h-screen bg-gray-50">
                <Navigation />
                <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                    <Routes>
                        <Route path="/" element={<Dashboard />} />
                        <Route path="/scan" element={<ScanCoin />} />
                        <Route path="/coins" element={<CoinList />} />
                        <Route path="/coins/:id" element={<CoinDetail />} />
                    </Routes>
                </main>
            </div>
        </Router>
    );
}

export default App;
