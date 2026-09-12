import { Route, Routes, useParams } from 'react-router-dom';
import Landing from './pages/Landing';
import Watch from './pages/Watch';

function WatchRoute() {
  const { videoId } = useParams();
  // remount Watch on every videoId change so its state always starts fresh
  return <Watch key={videoId} />;
}

export default function App() {
  return (
    <div style={{ background: 'var(--ground)', color: 'var(--ink)', minHeight: '100vh' }}>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/watch/:videoId" element={<WatchRoute />} />
      </Routes>
    </div>
  );
}
