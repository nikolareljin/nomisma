import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useMutation, useQuery } from '@tanstack/react-query';
import { Camera, Upload, Loader2, CheckCircle, AlertCircle } from 'lucide-react';
import { microscopeAPI, coinsAPI, aiAPI } from '../api';

export default function ScanCoin() {
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();
    const existingCoinId = searchParams.get('coinId');
    const requestedSide = searchParams.get('side');
    const [step, setStep] = useState('capture'); // capture, analyze, edit, complete
    const [capturedImages, setCapturedImages] = useState({ obverse: null, reverse: null });
    const [currentSide, setCurrentSide] = useState('obverse');
    const [scanPrompt, setScanPrompt] = useState('Please scan the obverse side of the coin.');
    const [qualityWarning, setQualityWarning] = useState('');
    const [coinData, setCoinData] = useState({});
    const [analysisResult, setAnalysisResult] = useState(null);
    const [valuationResult, setValuationResult] = useState(null);
    const [valuationText, setValuationText] = useState('');
    const [selectedCamera, setSelectedCamera] = useState('0');
    const [previewToken, setPreviewToken] = useState('');
    const [previewError, setPreviewError] = useState(false);

    const formatCurrency = (value) => (typeof value === 'number' ? value.toFixed(2) : 'N/A');
    const currentSideLabel = currentSide === 'obverse' ? 'front (obverse)' : 'back (reverse)';

    // Query cameras
    const { data: camerasData } = useQuery({
        queryKey: ['cameras'],
        queryFn: () => microscopeAPI.listDevices(),
    });

    const cameras = camerasData?.data?.cameras || [];

    const { data: existingCoinData } = useQuery({
        queryKey: ['coin', existingCoinId],
        queryFn: () => coinsAPI.get(existingCoinId),
        enabled: Boolean(existingCoinId),
    });

    const existingImages = existingCoinData?.data?.images || [];
    const existingObverse = existingImages.find((img) => img.image_type === 'obverse');
    const existingReverse = existingImages.find((img) => img.image_type === 'reverse');
    const hasObverse = Boolean(capturedImages.obverse || existingObverse);
    const hasReverse = Boolean(capturedImages.reverse || existingReverse);
    const missingSides = !(hasObverse && hasReverse);
    const missingSideLabel = hasObverse ? 'back (reverse)' : 'front (obverse)';

    useEffect(() => {
        if (!cameras.length) {
            return;
        }
        const selectedExists = cameras.some((cam) => String(cam.index) === selectedCamera);
        if (!selectedExists || cameras.find((cam) => String(cam.index) === selectedCamera && cam.available === false)) {
            const firstAvailable = cameras.find((cam) => cam.available !== false) || cameras[0];
            setSelectedCamera(String(firstAvailable.index));
        }
    }, [cameras, selectedCamera]);

    useEffect(() => {
        if (!selectedCamera) {
            return;
        }
        setPreviewError(false);
        const interval = setInterval(() => {
            setPreviewToken(String(Date.now()));
        }, 750);
        return () => clearInterval(interval);
    }, [selectedCamera]);

    useEffect(() => {
        if (!requestedSide) {
            return;
        }
        const normalized = requestedSide.toLowerCase();
        if (normalized === 'obverse' || normalized === 'reverse') {
            setCurrentSide(normalized);
            setScanPrompt(`Please scan the ${normalized} side of the coin.`);
        }
    }, [requestedSide]);

    // Analysis mutation
    const analyzeMutation = useMutation({
        mutationFn: (data) => aiAPI.analyze(data),
        onSuccess: (response) => {
            if (response.data.success) {
                setAnalysisResult(response.data.analysis);
                setValuationResult(response.data.valuation || null);
                setValuationText(response.data.valuation_text || '');
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

    useEffect(() => {
        if (existingCoinId) {
            return;
        }
        if (!analysisResult && capturedImages.obverse && !analyzeMutation.isPending) {
            setStep('analyze');
            analyzeMutation.mutate({ image_path: capturedImages.obverse.file_path });
        }
    }, [capturedImages.obverse, analysisResult, analyzeMutation, existingCoinId]);

    // Create coin mutation
    const createCoinMutation = useMutation({
        mutationFn: async (data) => {
            // Create coin
            const coinResponse = await coinsAPI.create(data);
            const coinId = coinResponse.data.id;

            // Upload image if we have one
            const uploads = Object.entries(capturedImages).filter(([, value]) => value);
            for (const [side, imageData] of uploads) {
                const formData = new FormData();
                const imageResponse = await fetch(`http://localhost:8000/images/${imageData.file_path}`);
                const blob = await imageResponse.blob();
                formData.append('file', blob, 'coin.jpg');
                formData.append('image_type', side);
                formData.append('is_primary', side === 'obverse' ? 'true' : 'false');
                await coinsAPI.uploadImage(coinId, formData);
            }

            const analysisImage = capturedImages.obverse || capturedImages.reverse;
            if (analysisImage) {
                // Trigger AI analysis with coin_id
                await aiAPI.analyze({
                    image_path: analysisImage.file_path,
                    coin_id: coinId,
                });
            }

            return coinId;
        },
        onSuccess: (coinId) => {
            setStep('complete');
            setTimeout(() => navigate(`/coins/${coinId}`), 2000);
        },
    });

    const attachToCoinMutation = useMutation({
        mutationFn: async ({ imageData, sideLabel }) => {
            if (!existingCoinId) {
                return null;
            }
            const formData = new FormData();
            const imageResponse = await fetch(`http://localhost:8000/images/${imageData.file_path}`);
            const blob = await imageResponse.blob();
            formData.append('file', blob, 'coin.jpg');
            formData.append('image_type', sideLabel);
            formData.append('is_primary', sideLabel === 'obverse' ? 'true' : 'false');
            await coinsAPI.uploadImage(existingCoinId, formData);

            if (sideLabel === 'obverse') {
                await aiAPI.analyze({
                    image_path: imageData.file_path,
                    coin_id: existingCoinId,
                });
            }
        },
        onSuccess: () => {
            setStep('complete');
            setTimeout(() => navigate(`/coins/${existingCoinId}`), 1500);
        },
    });

    // Capture mutation
    const captureMutation = useMutation({
        mutationFn: () => microscopeAPI.capture(selectedCamera, currentSide),
        onSuccess: (response) => {
            const quality = response.data.quality || {};
            if (quality.ok === false) {
                const reasons = [];
                if (quality.is_blurry) reasons.push('Image looks blurry');
                if (quality.is_dark) reasons.push('Image is too dark');
                if (quality.is_bright) reasons.push('Image is too bright');
                setQualityWarning(reasons.join('. ') || 'Image quality looks poor. Please rescan.');
                return;
            }

            setQualityWarning('');

            const detectedSide = response.data.side?.label || currentSide;
            const sideLabel = ['obverse', 'reverse'].includes(detectedSide) ? detectedSide : currentSide;

            setCapturedImages((prev) => ({
                ...prev,
                [sideLabel]: response.data,
            }));

            const nextSide = sideLabel === 'obverse' ? 'reverse' : 'obverse';
            setCurrentSide(nextSide);
            setScanPrompt(`Please scan the ${nextSide} side of the coin.`);

            if (existingCoinId) {
                attachToCoinMutation.mutate({ imageData: response.data, sideLabel });
                return;
            }

            if (!analysisResult && sideLabel === 'obverse') {
                setStep('analyze');
                analyzeMutation.mutate({ image_path: response.data.file_path });
            } else if (analysisResult) {
                setStep('edit');
            }
        },
    });

    const handleCapture = () => {
        captureMutation.mutate();
    };

    const handleScanOtherSide = () => {
        const nextSide = capturedImages.obverse ? 'reverse' : 'obverse';
        setCurrentSide(nextSide);
        setScanPrompt(`Please scan the ${nextSide} side of the coin.`);
        setStep('capture');
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
                        <div className="rounded-lg border border-gray-200 bg-gray-50 p-4">
                            <p className="text-sm text-gray-700">
                                Now scanning: <span className="font-semibold">{currentSideLabel}</span>
                            </p>
                            {scanPrompt && (
                                <p className="text-sm text-gray-600 mt-1">{scanPrompt}</p>
                            )}
                            <div className="flex items-center space-x-4 mt-3 text-sm text-gray-600">
                                <span>
                                    Obverse: {capturedImages.obverse ? 'captured' : 'missing'}
                                </span>
                                <span>
                                    Reverse: {capturedImages.reverse ? 'captured' : 'missing'}
                                </span>
                            </div>
                            {qualityWarning && (
                                <div className="mt-3 text-sm text-red-700">
                                    {qualityWarning} Please rescan the {currentSideLabel} side.
                                </div>
                            )}
                        </div>
                        <div>
                            <label className="label">Select Camera</label>
                            <select
                                value={selectedCamera}
                                onChange={(e) => setSelectedCamera(e.target.value)}
                                className="input"
                            >
                                {cameras.length === 0 && (
                                    <option value={0} disabled>
                                        No cameras detected
                                    </option>
                                )}
                                {cameras.map((cam) => (
                                    <option key={cam.index} value={String(cam.index)} disabled={cam.available === false}>
                                        {cam.name} - {cam.resolution}{cam.available === false ? ' (unavailable)' : ''}
                                    </option>
                                ))}
                            </select>
                        </div>

                        <div className="bg-gray-900 rounded-lg aspect-video flex items-center justify-center">
                            {cameras.length > 0 ? (
                                <>
                                    <img
                                        src={microscopeAPI.preview(selectedCamera, previewToken)}
                                        alt="Microscope preview"
                                        className="max-w-full max-h-full"
                                        onError={(e) => {
                                            setPreviewError(true);
                                        }}
                                    />
                                    {previewError && (
                                        <div className="flex-col items-center justify-center text-gray-400 flex">
                                            <Camera className="w-16 h-16 mb-4" />
                                            <p>Camera preview unavailable</p>
                                        </div>
                                    )}
                                </>
                            ) : (
                                <div className="flex-col items-center justify-center text-gray-400 flex">
                                    <Camera className="w-16 h-16 mb-4" />
                                    <p>No cameras detected</p>
                                </div>
                            )}
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
                                    <span>Capture {currentSideLabel}</span>
                                </>
                            )}
                        </button>
                        {capturedImages.obverse || capturedImages.reverse ? (
                            <button
                                onClick={handleScanOtherSide}
                                className="btn btn-secondary w-full"
                            >
                                Scan {missingSideLabel} side
                            </button>
                        ) : null}
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
                        {(capturedImages.obverse || capturedImages.reverse) && (
                            <div className="bg-gray-100 rounded-lg p-4">
                                <div className="grid grid-cols-2 gap-4">
                                    {capturedImages.obverse && (
                                        <img
                                            src={`http://localhost:8000/images/${capturedImages.obverse.file_path}`}
                                            alt="Captured obverse"
                                            className="w-full rounded-lg"
                                        />
                                    )}
                                    {capturedImages.reverse && (
                                        <img
                                            src={`http://localhost:8000/images/${capturedImages.reverse.file_path}`}
                                            alt="Captured reverse"
                                            className="w-full rounded-lg"
                                        />
                                    )}
                                </div>
                            </div>
                        )}

                        {missingSides && !existingCoinId && (
                            <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
                                <h4 className="font-semibold text-amber-900 mb-1">Scan the other side</h4>
                                <p className="text-sm text-amber-700">
                                    Please capture both sides before saving. Missing: {missingSideLabel}.
                                </p>
                                <button
                                    onClick={handleScanOtherSide}
                                    className="btn btn-secondary mt-3"
                                >
                                    Scan missing side
                                </button>
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

                        {valuationResult && (
                            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                                <h4 className="font-semibold text-green-900 mb-2">Estimated Value</h4>
                                <p className="text-lg font-bold text-green-800">
                                    ${formatCurrency(valuationResult.estimated_value_low)} - $
                                    {formatCurrency(valuationResult.estimated_value_high)}
                                </p>
                                {valuationText && (
                                    <pre className="mt-3 text-sm text-green-900 whitespace-pre-wrap leading-relaxed">
                                        {valuationText}
                                    </pre>
                                )}
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
                            disabled={createCoinMutation.isPending || missingSides}
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
                                    <span>{missingSides ? 'Scan both sides to save' : 'Save Coin'}</span>
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
