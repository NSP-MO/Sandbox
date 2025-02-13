// src/App.js
import React, { useEffect, useState } from 'react';
import './App.css';

function App() {
  const [assets, setAssets] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Replace these placeholders with your actual Canva API credentials and endpoint details
    const apiKey = 'cnv_cat3zdymjdr3GT0iQsxdaTezVfUQWTxBAKW_aMcZtZGLY71314aae';
    const userId = 'OC-AZTfPgkQKbjM';
    const apiEndpoint = `https://api.canva.com/v1/users/${userId}/assets`;

    const fetchAssets = async () => {
      try {
        const response = await fetch(apiEndpoint, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json',
          },
        });

        if (!response.ok) {
          throw new Error(`API error: ${response.status}`);
        }

        const data = await response.json();
        // Assume the API returns an object with an "assets" array
        setAssets(data.assets || []);
      } catch (err) {
        console.error('Error fetching Canva assets:', err);
        setError('Failed to load assets.');
      }
    };

    fetchAssets();
  }, []);

  return (
    <div className="App">
      <header className="header">
        <h1>Minimalist Website</h1>
      </header>

      <main>
        {error && <p className="error">{error}</p>}
        <section className="assets">
          {assets.length ? (
            assets.map((asset, index) => (
              <div className="asset" key={index}>
                <img src={asset.image_url} alt={asset.title} />
                <h3>{asset.title}</h3>
              </div>
            ))
          ) : (
            !error && <p>Loading assets...</p>
          )}
        </section>
      </main>

      <footer className="footer">
        <p>&copy; 2025 Minimalist Website</p>
      </footer>
    </div>
  );
}

export default App;
