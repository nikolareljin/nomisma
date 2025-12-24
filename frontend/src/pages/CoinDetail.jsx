import { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Edit2, Save, X, Trash2, ShoppingCart, TrendingUp, Camera, ArrowLeft } from 'lucide-react';
import { coinsAPI, aiAPI, ebayAPI } from '../api';

export default function CoinDetail() {
    const { id } = useParams();
    const navigate = useNavigate();
    const queryClient = useQueryClient();
    const [isEditing, setIsEditing] = useState(false);
    const [editData, setEditData] = useState({});
    const [showEbayModal, setShowEbayModal] = useState(false);

    const { data: coin, isLoading } = useQuery({
        queryKey: ['coin', id],
        queryFn: () => coinsAPI.get(id),
        onSuccess: (response) => {
            setEditData(response.data);
        },
    });

    const { data: similarCoins } = useQuery({
        queryKey: ['similar', id],
        queryFn: () => aiAPI.findSimilar(id),
    });

    const updateMutation = useMutation({
        mutationFn: (data) => coinsAPI.update(id, data),
        onSuccess: () => {
            queryClient.invalidateQueries(['coin', id]);
            setIsEditing(false);
        },
    });

    const deleteMutation = useMutation({
        mutationFn: () => coinsAPI.delete(id),
        onSuccess: () => {
            navigate('/coins');
        },
    });

    const coinData = coin?.data;
    const latestAnalysis = coinData?.analyses?.[coinData.analyses.length - 1];
    const latestValuation = coinData?.valuations?.[coinData.valuations.length - 1];
    const similar = similarCoins?.data?.similar_coins || [];
    const pricingNotes = latestValuation?.recent_sales_data?.formatted_response;

    const quickListingData = coinData ? {
        listing_title: `${coinData.year} ${coinData.country} ${coinData.denomination} - ${coinData.condition_grade}`,
        listing_description: `${coinData.country} ${coinData.denomination} from ${coinData.year}. Condition: ${coinData.condition_grade}. ${coinData.notes || ''}`,
        starting_price: latestValuation?.estimated_value_low || 10,
        buy_it_now_price: latestValuation?.estimated_value_avg || 20,
    } : null;

    const quickListMutation = useMutation({
        mutationFn: () => {
            if (!coinData || !quickListingData) {
                return Promise.reject(new Error('Coin data unavailable for listing.'));
            }
            return ebayAPI.createListing({ coin_id: coinData.id, ...quickListingData });
        },
        onSuccess: () => {
            alert('eBay listing created successfully!');
        },
        onError: (error) => {
            const message = error?.response?.data?.detail?.error || error?.response?.data?.detail?.message || 'eBay listing failed.';
            alert(message);
        },
    });

    if (isLoading) {
        return <div className="text-center py-12">Loading...</div>;
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                    <Link to="/coins" className="text-gray-600 hover:text-gray-900">
                        <ArrowLeft className="w-6 h-6" />
                    </Link>
                    <div>
                        <div className="flex items-center space-x-3">
                            <h1 className="text-3xl font-bold text-gray-900">
                                {coinData.country} {coinData.denomination}
                            </h1>
                            <span className="text-sm font-mono text-gray-500">{coinData.inventory_number}</span>
                        </div>
                        <p className="text-gray-600 mt-1">{coinData.year || 'Unknown year'}</p>
                    </div>
                </div>
                <div className="flex items-center space-x-2">
                    {!isEditing ? (
                        <>
                            <button onClick={() => setIsEditing(true)} className="btn btn-secondary flex items-center space-x-2">
                                <Edit2 className="w-4 h-4" />
                                <span>Edit</span>
                            </button>
                            <button
                                onClick={() => quickListMutation.mutate()}
                                className="btn btn-gold flex items-center space-x-2"
                                disabled={quickListMutation.isPending}
                            >
                                <ShoppingCart className="w-4 h-4" />
                                <span>{quickListMutation.isPending ? 'Listing...' : 'Quick List on eBay'}</span>
                            </button>
                            <button onClick={() => setShowEbayModal(true)} className="btn btn-secondary flex items-center space-x-2">
                                <span>Customize Listing</span>
                            </button>
                        </>
                    ) : (
                        <>
                            <button onClick={() => setIsEditing(false)} className="btn btn-secondary flex items-center space-x-2">
                                <X className="w-4 h-4" />
                                <span>Cancel</span>
                            </button>
                            <button
                                onClick={() => updateMutation.mutate(editData)}
                                className="btn btn-primary flex items-center space-x-2"
                            >
                                <Save className="w-4 h-4" />
                                <span>Save</span>
                            </button>
                        </>
                    )}
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Main Content */}
                <div className="lg:col-span-2 space-y-6">
                    {/* Images */}
                    <div className="card">
                        <h2 className="text-xl font-semibold mb-4">Images</h2>
                        <div className="grid grid-cols-2 gap-4">
                            {coinData.images?.map((img) => (
                                <img
                                    key={img.id}
                                    src={`http://localhost:8000/images/${img.file_path}`}
                                    alt={img.image_type}
                                    className="w-full rounded-lg"
                                />
                            ))}
                            {coinData.images?.length === 0 && (
                                <div className="col-span-2 text-center py-8 text-gray-500">
                                    No images available
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Details */}
                    <div className="card">
                        <h2 className="text-xl font-semibold mb-4">Details</h2>
                        {isEditing ? (
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="label">Country</label>
                                    <input
                                        type="text"
                                        value={editData.country || ''}
                                        onChange={(e) => setEditData({ ...editData, country: e.target.value })}
                                        className="input"
                                    />
                                </div>
                                <div>
                                    <label className="label">Denomination</label>
                                    <input
                                        type="text"
                                        value={editData.denomination || ''}
                                        onChange={(e) => setEditData({ ...editData, denomination: e.target.value })}
                                        className="input"
                                    />
                                </div>
                                <div>
                                    <label className="label">Year</label>
                                    <input
                                        type="number"
                                        value={editData.year || ''}
                                        onChange={(e) => setEditData({ ...editData, year: e.target.value })}
                                        className="input"
                                    />
                                </div>
                                <div>
                                    <label className="label">Mint Mark</label>
                                    <input
                                        type="text"
                                        value={editData.mint_mark || ''}
                                        onChange={(e) => setEditData({ ...editData, mint_mark: e.target.value })}
                                        className="input"
                                    />
                                </div>
                                <div className="col-span-2">
                                    <label className="label">Composition</label>
                                    <input
                                        type="text"
                                        value={editData.composition || ''}
                                        onChange={(e) => setEditData({ ...editData, composition: e.target.value })}
                                        className="input"
                                    />
                                </div>
                                <div className="col-span-2">
                                    <label className="label">Notes</label>
                                    <textarea
                                        value={editData.notes || ''}
                                        onChange={(e) => setEditData({ ...editData, notes: e.target.value })}
                                        className="input"
                                        rows="3"
                                    />
                                </div>
                            </div>
                        ) : (
                            <dl className="grid grid-cols-2 gap-4">
                                <DetailItem label="Mint Mark" value={coinData.mint_mark} />
                                <DetailItem label="Composition" value={coinData.composition} />
                                <DetailItem label="Weight" value={coinData.weight_grams ? `${coinData.weight_grams}g` : null} />
                                <DetailItem label="Diameter" value={coinData.diameter_mm ? `${coinData.diameter_mm}mm` : null} />
                                <DetailItem label="Condition" value={coinData.condition_grade} />
                                <DetailItem label="Catalog #" value={coinData.catalog_number} />
                                {coinData.notes && (
                                    <div className="col-span-2">
                                        <dt className="text-sm font-medium text-gray-500">Notes</dt>
                                        <dd className="mt-1 text-sm text-gray-900">{coinData.notes}</dd>
                                    </div>
                                )}
                            </dl>
                        )}
                    </div>

                    {/* AI Analysis */}
                    {latestAnalysis && (
                        <div className="card">
                            <h2 className="text-xl font-semibold mb-4">AI Analysis</h2>
                            <div className="space-y-3">
                                <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                                    <span className="text-sm font-medium text-blue-900">Authenticity</span>
                                    <span className="text-sm text-blue-700">
                                        {latestAnalysis.authenticity_assessment} ({latestAnalysis.authenticity_confidence}%)
                                    </span>
                                </div>
                                <div className="grid grid-cols-2 gap-3">
                                    <div className="p-3 bg-gray-50 rounded-lg">
                                        <p className="text-xs text-gray-600">Wear Level</p>
                                        <p className="text-sm font-medium">{latestAnalysis.wear_level}</p>
                                    </div>
                                    <div className="p-3 bg-gray-50 rounded-lg">
                                        <p className="text-xs text-gray-600">Surface Quality</p>
                                        <p className="text-sm font-medium">{latestAnalysis.surface_quality}</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}
                </div>

                {/* Sidebar */}
                <div className="space-y-6">
                    {/* Valuation */}
                    {latestValuation && (
                        <div className="card bg-gradient-to-br from-green-50 to-emerald-50 border-green-200">
                            <div className="flex items-center space-x-2 mb-4">
                                <TrendingUp className="w-5 h-5 text-green-600" />
                                <h3 className="font-semibold text-green-900">Estimated Value</h3>
                            </div>
                            <div className="text-center">
                                <p className="text-3xl font-bold text-green-700">
                                    ${latestValuation.estimated_value_avg?.toFixed(2) || 'N/A'}
                                </p>
                                <p className="text-sm text-green-600 mt-1">
                                    ${latestValuation.estimated_value_low?.toFixed(2)} - $
                                    {latestValuation.estimated_value_high?.toFixed(2)}
                                </p>
                                <div className="mt-4 pt-4 border-t border-green-200">
                                    <div className="flex justify-between text-sm">
                                        <span className="text-green-700">Market Demand</span>
                                        <span className="font-medium text-green-900">{latestValuation.market_demand}</span>
                                    </div>
                                </div>
                                {pricingNotes && (
                                    <pre className="mt-4 text-sm text-green-900 whitespace-pre-wrap leading-relaxed">
                                        {pricingNotes}
                                    </pre>
                                )}
                            </div>
                        </div>
                    )}

                    {/* Similar Coins */}
                    {similar.length > 0 && (
                        <div className="card">
                            <h3 className="font-semibold mb-4">Similar Coins</h3>
                            <div className="space-y-3">
                                {similar.map((s) => (
                                    <Link
                                        key={s.id}
                                        to={`/coins/${s.id}`}
                                        className="flex items-center space-x-3 p-2 rounded hover:bg-gray-50"
                                    >
                                        <img
                                            src={s.primary_image ? `http://localhost:8000/images/${s.primary_image}` : 'https://via.placeholder.com/50'}
                                            alt={s.denomination}
                                            className="w-12 h-12 rounded object-cover"
                                        />
                                        <div className="flex-1 min-w-0">
                                            <p className="text-sm font-medium text-gray-900 truncate">
                                                {s.country} {s.denomination}
                                            </p>
                                            <p className="text-xs text-gray-500">{s.year}</p>
                                        </div>
                                    </Link>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Danger Zone */}
                    <div className="card border-red-200">
                        <h3 className="font-semibold text-red-900 mb-4">Danger Zone</h3>
                        <button
                            onClick={() => {
                                if (confirm('Are you sure you want to delete this coin?')) {
                                    deleteMutation.mutate();
                                }
                            }}
                            className="btn bg-red-600 text-white hover:bg-red-700 w-full flex items-center justify-center space-x-2"
                        >
                            <Trash2 className="w-4 h-4" />
                            <span>Delete Coin</span>
                        </button>
                    </div>
                </div>
            </div>

            {/* eBay Modal */}
            {showEbayModal && (
                <EbayListingModal coin={coinData} onClose={() => setShowEbayModal(false)} />
            )}
        </div>
    );
}

function DetailItem({ label, value }) {
    if (!value) return null;
    return (
        <div>
            <dt className="text-sm font-medium text-gray-500">{label}</dt>
            <dd className="mt-1 text-sm text-gray-900">{value}</dd>
        </div>
    );
}

function EbayListingModal({ coin, onClose }) {
    const [listingData, setListingData] = useState({
        listing_title: `${coin.year} ${coin.country} ${coin.denomination} - ${coin.condition_grade}`,
        listing_description: `${coin.country} ${coin.denomination} from ${coin.year}. Condition: ${coin.condition_grade}. ${coin.notes || ''}`,
        starting_price: coin.valuations?.[0]?.estimated_value_low || 10,
        buy_it_now_price: coin.valuations?.[0]?.estimated_value_avg || 20,
    });

    const createListingMutation = useMutation({
        mutationFn: () => ebayAPI.createListing({ coin_id: coin.id, ...listingData }),
        onSuccess: () => {
            alert('eBay listing created successfully!');
            onClose();
        },
        onError: (error) => {
            const message = error?.response?.data?.detail?.error || error?.response?.data?.detail?.message || 'eBay listing failed.';
            alert(message);
        },
    });

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-xl p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
                <div className="flex items-center justify-between mb-6">
                    <h2 className="text-2xl font-bold">Create eBay Listing</h2>
                    <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
                        <X className="w-6 h-6" />
                    </button>
                </div>

                <div className="space-y-4">
                    <div>
                        <label className="label">Listing Title</label>
                        <input
                            type="text"
                            value={listingData.listing_title}
                            onChange={(e) => setListingData({ ...listingData, listing_title: e.target.value })}
                            className="input"
                            maxLength="80"
                        />
                        <p className="text-xs text-gray-500 mt-1">{listingData.listing_title.length}/80 characters</p>
                    </div>

                    <div>
                        <label className="label">Description</label>
                        <textarea
                            value={listingData.listing_description}
                            onChange={(e) => setListingData({ ...listingData, listing_description: e.target.value })}
                            className="input"
                            rows="4"
                        />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="label">Starting Price ($)</label>
                            <input
                                type="number"
                                step="0.01"
                                value={listingData.starting_price}
                                onChange={(e) => setListingData({ ...listingData, starting_price: parseFloat(e.target.value) })}
                                className="input"
                            />
                        </div>
                        <div>
                            <label className="label">Buy It Now Price ($)</label>
                            <input
                                type="number"
                                step="0.01"
                                value={listingData.buy_it_now_price}
                                onChange={(e) => setListingData({ ...listingData, buy_it_now_price: parseFloat(e.target.value) })}
                                className="input"
                            />
                        </div>
                    </div>

                    <div className="flex items-center space-x-3 pt-4">
                        <button onClick={onClose} className="btn btn-secondary flex-1">
                            Cancel
                        </button>
                        <button
                            onClick={() => createListingMutation.mutate()}
                            disabled={createListingMutation.isPending}
                            className="btn btn-gold flex-1"
                        >
                            {createListingMutation.isPending ? 'Creating...' : 'Create Listing'}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
