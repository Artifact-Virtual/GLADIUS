import { useState, useEffect } from 'react'
import { Bar } from 'react-chartjs-2';
import artifactLogo from './assets/artifact.svg'
import './App.css'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

function isValidUrl(url) {
  try {
    new URL(url)
    return true
  } catch {
    return false
  }
}

const TABS = ["Scrape", "All Data"];

function App() {
  const [tab, setTab] = useState("Scrape")
  const [urls, setUrls] = useState('https://books.toscrape.com/')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [search, setSearch] = useState('')

  const handleScrape = async () => {
    setLoading(true)
    setError('')
    try {
      const urlList = urls
        .split('\n')
        .map(u => u.trim())
        .filter(Boolean)
        .filter(isValidUrl)
      if (urlList.length === 0) throw new Error('Please enter at least one valid URL (including http/https).')
      const res = await fetch('http://localhost:5174/api/scrape', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ urls: urlList })
      })
      const data = await res.json()
      if (data.error) throw new Error(data.error)
      await fetchResults()
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const fetchResults = async () => {
    const res = await fetch('http://localhost:5174/api/results')
    const data = await res.json()
    setResults(data.reverse())
  }

  useEffect(() => { fetchResults() }, [])

  // Filtered results for All Data tab
  const filteredResults = results.filter(r =>
    !search ||
    (r.url && r.url.toLowerCase().includes(search.toLowerCase())) ||
    (r.emails && r.emails.join(' ').toLowerCase().includes(search.toLowerCase())) ||
    (r.nouns && r.nouns.join(' ').toLowerCase().includes(search.toLowerCase()))
  )

  // Metrics for visualization
  const entityCounts = {};
  results.forEach(r => {
    (r.namedEntities || []).forEach(e => {
      entityCounts[e.entity] = (entityCounts[e.entity] || 0) + 1;
    });
  });
  const entityChartData = {
    labels: Object.keys(entityCounts),
    datasets: [
      {
        label: 'Named Entity Frequency',
        data: Object.values(entityCounts),
        backgroundColor: 'rgba(54, 162, 235, 0.5)',
      },
    ],
  };
  const entityChartOptions = {
    responsive: true,
    plugins: {
      legend: { position: 'top' },
      title: { display: true, text: 'Named Entity Distribution' },
    },
  };

  return (
    <div className="artifact-app">
      <header>
        <img src={artifactLogo} className="logo" alt="Artifact logo" />
        <h1>Artifact Web Hunter 2.0 <span style={{color:'#b00'}}>(blackwidow)</span></h1>
        <p className="subtitle">Stealthy, intelligent web scraping &amp; entity extraction</p>
        <nav className="tabs">
          {TABS.map(t => (
            <button key={t} className={tab===t?"active":""} onClick={()=>setTab(t)}>{t}</button>
          ))}
        </nav>
      </header>
      {tab==="Scrape" && (
        <section className="scrape-controls">
          <textarea value={urls} onChange={e => setUrls(e.target.value)} placeholder="Enter one or more URLs, one per line" rows={4} style={{width:'350px',resize:'vertical'}} />
          <button onClick={handleScrape} disabled={loading}>{loading ? 'Scraping...' : 'Scrape'}</button>
        </section>
      )}
      {error && <div className="error">{error}</div>}
      {tab==="Scrape" && (
        <section className="results">
          <h2>Scraped Results</h2>
          {results.length === 0 && <p>No results yet.</p>}
          {results.slice(0,5).map((r, i) => (
            <div key={i} className="result-card">
              <div><b>URL:</b> <a href={r.url} target="_blank" rel="noopener noreferrer">{r.url}</a></div>
              <div><b>Timestamp:</b> {r.timestamp}</div>
              <div><b>Emails:</b> {r.emails && r.emails.length ? r.emails.join(', ') : 'None'}</div>
              <div><b>Named Entities:</b> {r.namedEntities && r.namedEntities.length ? r.namedEntities.map(e => `${e.entity}: ${e.word}`).join('; ') : 'None'}</div>
              <div><b>Summary:</b> {r.summary || 'None'}</div>
            </div>
          ))}
        </section>
      )}
      {tab==="All Data" && (
        <section className="results">
          <h2>All Scraped Data</h2>
          <input value={search} onChange={e=>setSearch(e.target.value)} placeholder="Search by URL, email, or entity..." style={{width:'100%',marginBottom:'1rem',padding:'0.5rem'}} />
          <div style={{overflowX:'auto'}}>
            <table className="artifact-table">
              <thead>
                <tr>
                  <th>URL</th>
                  <th>Timestamp</th>
                  <th>Emails</th>
                  <th>Named Entities</th>
                  <th>Summary</th>
                </tr>
              </thead>
              <tbody>
                {filteredResults.length === 0 && <tr><td colSpan={5}>No results found.</td></tr>}
                {filteredResults.map((r, i) => (
                  <tr key={i}>
                    <td><a href={r.url} target="_blank" rel="noopener noreferrer">{r.url}</a></td>
                    <td>{r.timestamp}</td>
                    <td>{r.emails && r.emails.length ? r.emails.join(', ') : 'None'}</td>
                    <td>{r.namedEntities && r.namedEntities.length ? r.namedEntities.map(e => `${e.entity}: ${e.word}`).join('; ') : 'None'}</td>
                    <td>{r.summary || 'None'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div style={{marginTop:'2rem'}}>
            <Bar data={entityChartData} options={entityChartOptions} />
          </div>
        </section>
      )}
      <footer>
        <p>Artifact Web Hunter 2.0 (blackwidow) &copy; 2025</p>
      </footer>
    </div>
  )
}

export default App
