import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'


function App() {

  const [url, setUrl] = useState('');
  const [shortenedUrl, setShortenedUrl] = useState('');
  const [loading, setLoading] = useState(false);

  const handleShorten = async () => {
    setLoading(true);
    try {
      // Replace with your actual API endpoint
      const response = await fetch('server/url', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: url }),
      });
      const data = await response.json();
      setShortenedUrl(data.shortenedUrl || 'Error shortening URL');
        } catch (error) {
      setShortenedUrl('Error shortening URL');
        }
        setLoading(false);
  };

  return (
    <>
      <div>
        <input
          type="url"
          placeholder="Enter URL"
          value={url}
          onChange={e => setUrl(e.target.value)}
          style={{ width: '300px', marginRight: '8px' }}
        />
        <button onClick={handleShorten} disabled={loading || !url}>
          {loading ? 'Shortening...' : 'Shorten URL'}
        </button>
      </div>
      <div style={{ marginTop: '16px' }}>
        <strong>Shortened URL:</strong> {shortenedUrl}
      </div>
    </>
  )
}

export default App
