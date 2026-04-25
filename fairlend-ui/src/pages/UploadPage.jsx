import { useState } from 'react';
import { uploadDataset, runAudit, runDebias } from '../api/endpoints';

export default function UploadPage() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState(null);

  const [protectedAttr, setProtectedAttr] = useState("");
  const [targetAttr, setTargetAttr] = useState("");
  const [reportData, setReportData] = useState(null);

  // Debiasing state
  const [fairnessWeight, setFairnessWeight] = useState(0.5);
  const [debiasingData, setDebiasingData] = useState(null);
  const [debiasingLoading, setDebiasingLoading] = useState(false);

  const handleFileChange = (e) => {
    if (e.target.files[0]) {
      setFile(e.target.files[0]);
      setStats(null);
      setReportData(null);
      setDebiasingData(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      const data = await uploadDataset(file);
      setStats(data);
    } catch (err) {
      setError('Upload failed. Check backend.');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateReport = async () => {
    if (!protectedAttr || !targetAttr) return;
    setLoading(true);
    setError(null);
    setDebiasingData(null);
    try {
      const data = await runAudit(stats.session_id, protectedAttr, targetAttr);
      setReportData(data);
    } catch (err) {
      setError("Audit failed. Check backend terminal for details.");
    } finally {
      setLoading(false);
    }
  };

  const handleDebias = async (weight) => {
    setDebiasingLoading(true);
    try {
      const data = await runDebias(
        stats.session_id,
        weight,
        protectedAttr,
        targetAttr
      );
      setDebiasingData(data);
    } catch (err) {
      setError("Debiasing failed. Check backend terminal.");
    } finally {
      setDebiasingLoading(false);
    }
  };

  const handleSliderChange = (e) => {
    setFairnessWeight(parseFloat(e.target.value));
  };

  const handleSliderRelease = (e) => {
    handleDebias(parseFloat(e.target.value));
  };

  const handleReset = () => {
    setReportData(null);
    setDebiasingData(null);
    setFairnessWeight(0.5);
    setStats(null);
    setFile(null);
    setProtectedAttr("");
    setTargetAttr("");
  };

  return (
    <div className="flex flex-col items-center justify-center space-y-8 py-12 px-4">
      <div className="text-center">
        <h2 className="text-4xl font-extrabold text-white mb-3">FairLend AI Audit</h2>
        <p className="text-gray-400 max-w-md mx-auto">Real-time disparate impact analysis for lending datasets.</p>
      </div>

      {/* SCREEN 1 — Upload */}
      {!stats && (
        <div className="w-full max-w-md p-8 bg-gray-800 rounded-2xl border border-gray-700 shadow-2xl">
          <input
            type="file"
            accept=".csv"
            onChange={handleFileChange}
            className="block w-full text-sm text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:bg-blue-600 file:text-white mb-6 cursor-pointer"
          />
          <button
            onClick={handleUpload}
            disabled={!file || loading}
            className="w-full py-3 bg-blue-600 hover:bg-blue-500 disabled:opacity-40 text-white rounded-xl font-bold transition-all"
          >
            {loading ? 'Processing...' : 'Upload Dataset'}
          </button>
          {error && <p className="text-red-400 text-sm mt-4 text-center">{error}</p>}
        </div>
      )}

      {/* SCREEN 2 — Column Selection */}
      {stats && !reportData && (
        <div className="w-full max-w-2xl p-8 bg-gray-800 rounded-2xl border border-blue-500/30 shadow-2xl">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div>
              <label className="block text-xs text-gray-500 mb-2 font-bold uppercase">Protected Column</label>
              <select
                value={protectedAttr}
                onChange={(e) => setProtectedAttr(e.target.value)}
                className="w-full bg-gray-900 border border-gray-700 p-3 rounded-lg text-white"
              >
                <option value="">Select Column</option>
                {stats.columns.map(col => <option key={col} value={col}>{col}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-2 font-bold uppercase">Target (Outcome) Column</label>
              <select
                value={targetAttr}
                onChange={(e) => setTargetAttr(e.target.value)}
                className="w-full bg-gray-900 border border-gray-700 p-3 rounded-lg text-white"
              >
                <option value="">Select Column</option>
                {stats.columns.map(col => <option key={col} value={col}>{col}</option>)}
              </select>
            </div>
          </div>
          <button
            onClick={handleGenerateReport}
            disabled={loading || !protectedAttr || !targetAttr}
            className="w-full py-4 bg-blue-600 hover:bg-blue-500 disabled:opacity-40 text-white rounded-xl font-bold text-lg"
          >
            {loading ? 'Analyzing Bias...' : 'Generate Fairness Report →'}
          </button>
          {error && <p className="text-red-400 text-sm mt-4 text-center">{error}</p>}
        </div>
      )}

      {/* SCREEN 3 — Audit Report */}
      {reportData && (
        <div className="w-full max-w-4xl space-y-6">

          {/* Baseline metrics */}
          <div className="p-8 bg-gray-900 rounded-3xl border border-gray-800 shadow-2xl">
            <h3 className="text-white font-bold text-lg mb-6 uppercase tracking-widest text-xs text-gray-500">
              Baseline Model — Before Debiasing
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="p-6 bg-gray-800 rounded-2xl border border-gray-700 text-center">
                <p className="text-gray-500 text-xs uppercase font-bold mb-2">Demographic Parity Gap</p>
                <p className={`text-5xl font-black ${Math.abs(reportData.demographic_parity_gap) > 0.1 ? 'text-red-500' : 'text-green-500'}`}>
                  {reportData.demographic_parity_gap?.toFixed(3)}
                </p>
                <p className="text-gray-500 text-xs mt-2">0 = perfectly fair</p>
              </div>

              <div className="p-6 bg-gray-800 rounded-2xl border border-gray-700 text-center">
                <p className="text-gray-500 text-xs uppercase font-bold mb-2">Equalized Odds Gap</p>
                <p className={`text-5xl font-black ${Math.abs(reportData.equalized_odds_gap) > 0.1 ? 'text-red-500' : 'text-green-500'}`}>
                  {reportData.equalized_odds_gap?.toFixed(3)}
                </p>
                <p className="text-gray-500 text-xs mt-2">0 = perfectly fair</p>
              </div>

              <div className="p-6 bg-gray-800 rounded-2xl border border-gray-700 text-center">
                <p className="text-gray-500 text-xs uppercase font-bold mb-2">Model Accuracy</p>
                <p className="text-5xl font-black text-blue-400">
                  {(reportData.accuracy * 100)?.toFixed(1)}%
                </p>
                <p className="text-gray-500 text-xs mt-2">overall prediction accuracy</p>
              </div>
            </div>

            <div className="p-6 bg-blue-600/10 rounded-2xl border border-blue-500/30 mb-6">
              <h4 className="text-blue-400 font-bold mb-3 uppercase text-xs">Approval Rates by Group</h4>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {reportData.approval_rates && Object.entries(reportData.approval_rates).map(([group, rate]) => (
                  <div key={group} className="text-center p-3 bg-gray-800 rounded-xl">
                    <p className="text-gray-400 text-xs mb-1">{group}</p>
                    <p className={`text-2xl font-bold ${rate < 0.5 ? 'text-red-400' : 'text-green-400'}`}>
                      {(rate * 100).toFixed(1)}%
                    </p>
                  </div>
                ))}
              </div>
            </div>

            <div className={`p-6 rounded-2xl border text-center ${Math.abs(reportData.demographic_parity_gap) > 0.1 ? 'bg-red-900/20 border-red-500/30' : 'bg-green-900/20 border-green-500/30'}`}>
              <p className={`text-lg font-bold ${Math.abs(reportData.demographic_parity_gap) > 0.1 ? 'text-red-400' : 'text-green-400'}`}>
                {Math.abs(reportData.demographic_parity_gap) > 0.1
                  ? '⚠ Significant bias detected. This model should not be deployed without intervention.'
                  : '✓ Model meets fair lending standards. Bias gap is within acceptable threshold.'}
              </p>
            </div>
          </div>

          {/* DEBIASING SLIDER */}
          <div className="p-8 bg-gray-900 rounded-3xl border border-purple-500/30 shadow-2xl">
            <h3 className="text-white font-bold mb-1">Apply Debiasing</h3>
            <p className="text-gray-400 text-sm mb-8">
              Drag the slider to apply adversarial in-processing debiasing. Moving toward Fairness reduces bias — at a small cost to accuracy.
            </p>

            <div className="mb-3 flex justify-between text-xs text-gray-500 font-bold uppercase">
              <span>← Max Accuracy</span>
              <span>Max Fairness →</span>
            </div>

            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={fairnessWeight}
              onChange={handleSliderChange}
              onMouseUp={handleSliderRelease}
              onTouchEnd={handleSliderRelease}
              className="w-full h-3 rounded-full appearance-none cursor-pointer bg-gray-700 accent-purple-500"
            />

            <div className="text-center mt-3 mb-8">
              <span className="text-purple-400 font-bold text-sm">
                Fairness Weight: {(fairnessWeight * 100).toFixed(0)}%
              </span>
            </div>

            {/* Loading state */}
            {debiasingLoading && (
              <div className="text-center py-8">
                <p className="text-purple-400 font-bold animate-pulse">Running adversarial debiasing...</p>
                <p className="text-gray-500 text-xs mt-2">This may take 10–20 seconds</p>
              </div>
            )}

            {/* Debiased results */}
            {debiasingData && !debiasingLoading && (
              <div className="space-y-6 mt-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

                  <div className="p-6 bg-gray-800 rounded-2xl border border-purple-500/30 text-center">
                    <p className="text-gray-500 text-xs uppercase font-bold mb-2">Demographic Parity Gap</p>
                    <div className="flex items-center justify-center gap-3">
                      <p className="text-2xl font-black text-gray-600 line-through">
                        {reportData.demographic_parity_gap?.toFixed(3)}
                      </p>
                      <span className="text-gray-500">→</span>
                      <p className={`text-3xl font-black ${Math.abs(debiasingData.demographic_parity_gap) > 0.1 ? 'text-red-400' : 'text-green-400'}`}>
                        {debiasingData.demographic_parity_gap?.toFixed(3)}
                      </p>
                    </div>
                    <p className="text-green-500 text-xs mt-2 font-bold">
                      {((Math.abs(reportData.demographic_parity_gap) - Math.abs(debiasingData.demographic_parity_gap)) / Math.abs(reportData.demographic_parity_gap) * 100).toFixed(0)}% reduction
                    </p>
                  </div>

                  <div className="p-6 bg-gray-800 rounded-2xl border border-purple-500/30 text-center">
                    <p className="text-gray-500 text-xs uppercase font-bold mb-2">Equalized Odds Gap</p>
                    <div className="flex items-center justify-center gap-3">
                      <p className="text-2xl font-black text-gray-600 line-through">
                        {reportData.equalized_odds_gap?.toFixed(3)}
                      </p>
                      <span className="text-gray-500">→</span>
                      <p className={`text-3xl font-black ${Math.abs(debiasingData.equalized_odds_gap) > 0.1 ? 'text-red-400' : 'text-green-400'}`}>
                        {debiasingData.equalized_odds_gap?.toFixed(3)}
                      </p>
                    </div>
                  </div>

                  <div className="p-6 bg-gray-800 rounded-2xl border border-purple-500/30 text-center">
                    <p className="text-gray-500 text-xs uppercase font-bold mb-2">Model Accuracy</p>
                    <div className="flex items-center justify-center gap-3">
                      <p className="text-2xl font-black text-gray-600 line-through">
                        {(reportData.accuracy * 100)?.toFixed(1)}%
                      </p>
                      <span className="text-gray-500">→</span>
                      <p className="text-3xl font-black text-blue-400">
                        {(debiasingData.accuracy * 100)?.toFixed(1)}%
                      </p>
                    </div>
                    <p className="text-amber-400 text-xs mt-2 font-bold">
                      {(Math.abs(reportData.accuracy - debiasingData.accuracy) * 100).toFixed(1)}% accuracy trade-off
                    </p>
                  </div>

                </div>

                {/* Debiased approval rates */}
                <div className="p-6 bg-purple-600/10 rounded-2xl border border-purple-500/30">
                  <h4 className="text-purple-400 font-bold mb-3 uppercase text-xs">Approval Rates After Debiasing</h4>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                    {debiasingData.approval_rates && Object.entries(debiasingData.approval_rates).map(([group, rate]) => (
                      <div key={group} className="text-center p-3 bg-gray-800 rounded-xl">
                        <p className="text-gray-400 text-xs mb-1">{group}</p>
                        <p className={`text-2xl font-bold ${rate < 0.5 ? 'text-red-400' : 'text-green-400'}`}>
                          {(rate * 100).toFixed(1)}%
                        </p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Final verdict */}
                <div className={`p-6 rounded-2xl border text-center ${Math.abs(debiasingData.demographic_parity_gap) > 0.1 ? 'bg-amber-900/20 border-amber-500/30' : 'bg-green-900/20 border-green-500/30'}`}>
                  <p className={`text-lg font-bold ${Math.abs(debiasingData.demographic_parity_gap) > 0.1 ? 'text-amber-400' : 'text-green-400'}`}>
                    {Math.abs(debiasingData.demographic_parity_gap) > 0.1
                      ? '⚠ Bias reduced but still above threshold. Increase fairness weight further.'
                      : '✓ Model now meets fair lending standards. Safe to proceed to deployment review.'}
                  </p>
                </div>

              </div>
            )}
          </div>

          <button onClick={handleReset} className="text-gray-500 hover:text-white underline text-sm">
            Start New Audit
          </button>

        </div>
      )}
    </div>
  );
}