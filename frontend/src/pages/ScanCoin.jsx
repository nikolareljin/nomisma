import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation, useQuery } from '@tanstack/react-query';
import { Camera, Upload, Loader2, CheckCircle, AlertCircle } from 'lucide-react';
import { microscopeAPI, coinsAPI, aiAPI } from '../api';

export default function ScanCoin() {
    const navigate = useNavigate();
    const [step, setStep] = useState('capture'); // capture, analyze, edit, complete
    const [capturedImage, setCapturedImage] = useState(null);
    const [coinData, setCoinData] = useState({});
    const [analysisResult, setAnalysisResult] = useState(null);
    const [selectedCamera, setSelectedCamera] = useState(0);

    // Query cameras
    const { data: camerasData } = useQuery({
        queryKey: ['cameras'],
        queryFn: () => microscopeAPI.listDevices(),
    });

    const cameras = camerasData?.data?.cameras || [];

    // Capture mutation
    const captureMutation = useMutation({
        mutationFn: () => microscopeAPI.capture(selectedCamera),
        onSuccess: (response) => {
            setCapturedImage(response.data);
            setStep('analyze');
            // Auto-trigger analysis
            analyzeMutation.mutate({ image_path: response.data.file_path });
        },
    });

    // Analysis mutation
    const analyzeMutation = useMutation({
        mutationFn: (data) => aiAPI.analyze(data),
        onSuccess: (response) => {
            if (response.data.success) {
                setAnalysisResult(response.data.analysis);
                // Pre-fill coin data from AI analysis
                const ident = response.data.analysis.identification || {};
                const cond = response.data.analysis.condition || {};
                setCoinData({
                    country: ident.country || '',
                    denomination: ident.denomination || '',
                    year: ident.year || '',
                    mint_mark: ident.mint_mark || '',
                    composition: ident.composition || '',
                    condition_grade: cond.grade || '',
                });
                setStep('edit');
            }
        },
    });

    // Create coin mutation
    const createCoinMutation = useMutation({
        mutationFn: async (data) => {
            // Create coin
            const coinResponse = await coinsAPI.create(data);
            const coinId = coinResponse.data.id;

            // Upload image if we have one
            if (capturedImage) {
                const formData = new FormData();
                const imageResponse = await fetch(`http://localhost:8000/images/${capturedImage.file_path}`);
                const blob = await imageResponse.blob();
                formData.append('file', blob, 'coin.jpg');
                formData.append('image_type', 'obverse');
                formData.append('is_primary', 'true');
                await coinsAPI.uploadImage(coinId, formData);

                // Trigger AI analysis with coin_id
                await aiAPI.analyze({
                    image_path: capturedImage.file_path,
                    coin_id: coinId,
                });

                // Estimate value
                await aiAPI.estimateValue(coinId);
            }

            return coinId;
        },
        onSuccess: (coinId) => {
            setStep('complete');
            setTimeout(() => navigate(`/coins/${coinId}`), 2000);
        },
    });

    const handleCapture = () => {
        captureMutation.mutate();
    };

    const handleSave = () => {
        createCoinMutation.mutate(coinData);
    };

    return (
        <div className="max-w-4xl mx-auto space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold text-gray-900">Scan New Coin</h1>
                <p className="text-gray-600 mt-1">Capture and analyze a coin using your digital microscope</p>
            </div>

            {/* Progress Steps */}
            <div className="flex items-center justify-between">
                {['Capture', 'Analyze', 'Edit', 'Complete'].map((label, idx) => {
                    const stepNames = ['capture', 'analyze', 'edit', 'complete'];
                    const currentIdx = stepNames.indexOf(step);
                    const isActive = idx === currentIdx;
                    const isComplete = idx < currentIdx;

                    return (
                        <div key={label} className="flex items-center flex-1">
                            <div className="flex flex-col items-center flex-1">
                                <div
                                    className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold ${isComplete
                                            ? 'bg-green-500 text-white'
                                            : isActive
                                                ? 'bg-primary-600 text-white'
                                                : 'bg-gray-200 text-gray-500'
                                        }`}
                                >
                                    {isComplete ? <CheckCircle className="w-6 h-6" /> : idx + 1}
                                </div>
                                <span className={`text-sm mt-2 ${isActive ? 'font-semibold' : ''}`}>{label}</span>
                            </div>
                            {idx < 3 && (
                                <div className={`h-1 flex-1 ${isComplete ? 'bg-green-500' : 'bg-gray-200'}`} />
                            )}
                        </div>
                    );
                })}
            </div>

            {/* Content */}
            <div className="card">
                {step === 'capture' && (
                    <div className="space-y-6">
                        <div>
                            <label className="label">Select Camera</label>
                            <select
                                value={selectedCamera}
                                onChange={(e) => setSelectedCamera(Number(e.target.value))}
                                className="input"
                            >
                                {cameras.map((cam) => (
                                    <option key={cam.index} value={cam.index}>
                                        {cam.name} - {cam.resolution}
                                    </option>
                                ))}
                            </select>
                        </div>

                        <div className="bg-gray-900 rounded-lg aspect-video flex items-center justify-center">
                            <img
                                src={microscopeAPI.preview(selectedCamera)}
                                alt="Microscope preview"
                                className="max-w-full max-h-full"
                                onError={(e) => {
                                    e.target.style.display = 'none';
                                    e.target.nextSibling.style.display = 'flex';
                                }}
                            />
                            <div className="flex-col items-center justify-center text-gray-400" style={{ display: 'none' }}>
                                <Camera className="w-16 h-16 mb-4" />
                                <p>Camera preview unavailable</p>
                            </div>
                        </div>

                        <button
                            onClick={handleCapture}
                            disabled={captureMutation.isPending}
                            className="btn btn-primary w-full flex items-center justify-center space-x-2"
                        >
                            {captureMutation.isPending ? (
                                <>
                                    <Loader2 className="w-5 h-5 animate-spin" />
                                    <span>Capturing...</span>
                                </>
                            ) : (
                                <>
                                    <Camera className="w-5 h-5" />
                                    <span>Capture Image</span>
                                </>
                            )}
                        </button>
                    </div>
                )}

                {step === 'analyze' && (
                    <div className="text-center py-12">
                        <Loader2 className="w-16 h-16 text-primary-600 animate-spin mx-auto mb-4" />
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">Analyzing Coin...</h3>
                        <p className="text-gray-600">AI is examining the coin image</p>
                    </div>
                )}

                {step === 'edit' && (
                    <div className="space-y-6">
                        {capturedImage && (
                            <div className="bg-gray-100 rounded-lg p-4">
                                <img
                                    src={`http://localhost:8000/images/${capturedImage.file_path}`}
                                    alt="Captured coin"
                                    className="max-w-sm mx-auto rounded-lg"
                                />
                            </div>
                        )}

                        {analysisResult && (
                            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                                <h4 className="font-semibold text-blue-900 mb-2">AI Analysis Complete</h4>
                                <p className="text-sm text-blue-700">
                                    The form below has been pre-filled with AI-detected information. Please review and edit as needed.
                                </p>
                            </div>
                        )}

                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="label">Country</label>
                                <input
                                    type="text"
                                    value={coinData.country || ''}
                                    onChange={(e) => setCoinData({ ...coinData, country: e.target.value })}
                                    className="input"
                                />
                            </div>
                            <div>
                                <label className="label">Denomination</label>
                                <input
                                    type="text"
                                    value={coinData.denomination || ''}
                                    onChange={(e) => setCoinData({ ...coinData, denomination: e.target.value })}
                                    className="input"
                                />
                            </div>
                            <div>
                                <label className="label">Year</label>
                                <input
                                    type="number"
                                    value={coinData.year || ''}
                                    onChange={(e) => setCoinData({ ...coinData, year: e.target.value })}
                                    className="input"
                                />
                            </div>
                            <div>
                                <label className="label">Mint Mark</label>
                                <input
                                    type="text"
                                    value={coinData.mint_mark || ''}
                                    onChange={(e) => setCoinData({ ...coinData, mint_mark: e.target.value })}
                                    className="input"
                                />
                            </div>
                            <div>
                                <label className="label">Composition</label>
                                <input
                                    type="text"
                                    value={coinData.composition || ''}
                                    onChange={(e) => setCoinData({ ...coinData, composition: e.target.value })}
                                    className="input"
                                />
                            </div>
                            <div>
                                <label className="label">Condition Grade</label>
                                <select
                                    value={coinData.condition_grade || ''}
                                    onChange={(e) => setCoinData({ ...coinData, condition_grade: e.target.value })}
                                    className="input"
                                >
                                    <option value="">Select grade</option>
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

                        <div>
                            <label className="label">Notes</label>
                            <textarea
                                value={coinData.notes || ''}
                                onChange={(e) => setCoinData({ ...coinData, notes: e.target.value })}
                                className="input"
                                rows="3"
                            />
                        </div>

                        <button
                            onClick={handleSave}
                            disabled={createCoinMutation.isPending}
                            className="btn btn-primary w-full flex items-center justify-center space-x-2"
                        >
                            {createCoinMutation.isPending ? (
                                <>
                                    <Loader2 className="w-5 h-5 animate-spin" />
                                    <span>Saving...</span>
                                </>
                            ) : (
                                <>
                                    <CheckCircle className="w-5 h-5" />
                                    <span>Save Coin</span>
                                </>
                            )}
                        </button>
                    </div>
                )}

                {step === 'complete' && (
                    <div className="text-center py-12">
                        <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">Coin Saved Successfully!</h3>
                        <p className="text-gray-600">Redirecting to coin details...</p>
                    </div>
                )}
            </div>
        </div>
    );
}
