import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import UploadPage from './pages/UploadPage';

export default function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-900 text-white font-sans">
        <header className="p-4 border-b border-gray-800">
          <h1 className="text-2xl font-bold text-blue-400">FairLend AI</h1>
        </header>
        <main className="p-8 max-w-5xl mx-auto">
          <Routes>
            <Route path="/" element={<UploadPage />} />
            <Route path="*" element={<Navigate to="/" />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}