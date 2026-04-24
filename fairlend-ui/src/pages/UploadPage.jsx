import { useState } from 'react';
import { uploadDataset } from '../api/endpoints';

export default function UploadPage() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState(null);
  
  const [protectedAttr, setProtectedAttr] = useState("");
  const [targetAttr, setTargetAttr] = useState("");
  const [reportData, setReportData] = useState(null);

  const handleFileChange = (e) => {
    if (e.target.files[0]) {
      setFile(e.target.files[0]);
      setStats(null);
      setReportData(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      const data = await uploadDataset(file);
      setStats(data);
      setLoading(false);
    } catch (err) {
      setError('Upload failed. Check backend.');
      setLoading(false);
    }
  };

  const handleGenerateReport = async () => {
    if (!protectedAttr || !targetAttr) return;
    setLoading(true);
    try {
      const response = await fetch('http://127.0.0.1:8000/audit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: stats.session_id,
          protected_col: protectedAttr,
          target_col: targetAttr
        })
      });
      const data = await response.json();
      setReportData(data);
    } catch (err) {
      setError("Audit failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center space-y-8 py-12 px-4">
      <div className="text-center">
        <h2 className="text-4xl font-extrabold text-white mb-3">FairLend AI Audit</h2>
        <p className="text-gray-400 max-w-md mx-auto">Real-time disparate impact analysis for lending datasets.</p>
      </div>

      {!stats && (
        <div className="w-full max-w-md p-8 bg-gray-800 rounded-2xl border border-gray-700 shadow-2xl">
          <input type="file" accept=".csv" onChange={handleFileChange} className="block w-full text-sm text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:bg-blue-600 file:text-white mb-6 cursor-pointer" />
          <button onClick={handleUpload} disabled={!file || loading} className="w-full py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-bold transition-all">
            {loading ? 'Processing...' : 'Upload Dataset'}
          </button>
        </div>
      )}

      {stats && !reportData && (
        <div className="w-full max-w-2xl p-8 bg-gray-800 rounded-2xl border border-blue-500/30 shadow-2xl">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div>
              <label className="block text-xs text-gray-500 mb-2 font-bold uppercase">Protected Column</label>
              <select value={protectedAttr} onChange={(e) => setProtectedAttr(e.target.value)} className="w-full bg-gray-900 border border-gray-700 p-3 rounded-lg text-white">
                <option value="">Select Column</option>
                {stats.columns.map(col => <option key={col} value={col}>{col}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-2 font-bold uppercase">Target (Outcome) Column</label>
              <select value={targetAttr} onChange={(e) => setTargetAttr(e.target.value)} className="w-full bg-gray-900 border border-gray-700 p-3 rounded-lg text-white">
                <option value="">Select Column</option>
                {stats.columns.map(col => <option key={col} value={col}>{col}</option>)}
              </select>
            </div>
          </div>
          <button onClick={handleGenerateReport} disabled={loading} className="w-full py-4 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-bold text-lg">
            {loading ? 'Analyzing Bias...' : 'Generate Fairness Report →'}
          </button>
        </div>
      )}

      {reportData && (
        <div className="w-full max-w-4xl p-10 bg-gray-900 rounded-3xl border border-gray-800 shadow-2xl">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="p-8 bg-gray-800 rounded-2xl border border-gray-700 text-center">
              <p className="text-gray-500 text-xs uppercase font-bold mb-2">Disparate Impact Ratio</p>
              <p className={`text-7xl font-black ${reportData.disparate_impact < 0.8 ? 'text-red-500' : 'text-green-500'}`}>
                {reportData.disparate_impact}
              </p>
            </div>
            <div className="p-8 bg-blue-600/10 rounded-2xl border border-blue-500/30">
              <h4 className="text-blue-400 font-bold mb-2 uppercase text-xs">Analysis Result</h4>
              <p className="text-xl text-white">{reportData.recommendation}</p>
              <p className="mt-4 text-sm text-gray-400">Statistical Parity: {reportData.statistical_parity}</p>
            </div>
          </div>
          <button onClick={() => setReportData(null)} className="mt-8 text-gray-500 hover:text-white underline">Start New Audit</button>
        </div>
      )}
    </div>
  );
}