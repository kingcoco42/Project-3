import { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  // form state
  const [playerName, setPlayerName] = useState('');
  const [year, setYear] = useState(''); // set default year
  const [selectedProfile, setSelectedProfile] = useState('');
  const [groupSize, setGroupSize] = useState(5);
  const [exactSearch, setExactSearch] = useState(false);
  const [featureNames, setFeatureNames] = useState([]);

  // table data state
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const toggleProfile = (key, e) => {
    if (selectedProfile === key) {
      setSelectedProfile('');
    } else {
      setSelectedProfile(key);
    }
    const form = e.target.form;
    if (form) {
      const radioButtons = form.querySelectorAll('input[name="profile"]');
      radioButtons.forEach(radio => radio.setCustomValidity(''));
    }
  }

  const handleSubmit = e => {
    e.preventDefault();
    setLoading(true);
    //console.log('Exact Search?', exactSearch);
    
    axios.post('http://localhost:8080/api/similar', {
      player_name: playerName,
      feature_group: selectedProfile.toLowerCase(),
      k: groupSize,
      season: year || null,
      exact: exactSearch
    })
    .then(res => {
        console.log('API Response:', res.data);
        if (res.data.success) {
          setResults(res.data.data);
          setFeatureNames(res.data.metadata.features || []);
        } else {
          setError('Failed to get results');
        }
        setLoading(false);
      })
    .catch(err => {
      console.error('Error:', err);
        setError(err.response?.data?.error || 'An error occurred');
        setLoading(false);
    });
    
  };

  return (
    <div className="App">
      <h1>NBA Neighborhoods</h1>

      {/* --- SEARCH FORM --- */}
      <form className="search-form" onSubmit={handleSubmit}>
        <div className="field"> 
          <label>Enter Player Name</label>
          <input
            type="text"
            value={playerName}
            onChange={e => setPlayerName(e.target.value)}
            required
            onInvalid={e => e.target.setCustomValidity('Please enter a name.')}
            onInput={e => e.target.setCustomValidity('')}
            placeholder='e.g. LeBron James'
          />
        </div>

        <div className="field">
          <label>Year (Optional)</label>
          <input
            type="number"
            value={year}
            onChange={e => setYear(e.target.value)}
            placeholder="e.g. 2023"
          />
        </div>

        <fieldset className="field profile-group">
          <legend>Select Desired Profile</legend>
          {['Scoring', 'Defense','Impact', 'Traditional'].map((key, i) => (
            <div key={key}>
              <label key={key}>
                <input
                  type="radio"
                  name="profile"
                  value={key}
                  checked={selectedProfile === key}
                  onChange={e => toggleProfile(key, e)}
                  required
                  onInvalid={e => e.target.setCustomValidity('Please select a profile.')}
                  onInput={e => e.target.setCustomValidity('')}
                />
                {key.charAt(0).toUpperCase() + key.slice(1)}
              </label>
            </div>
          ))}
        </fieldset>

        <div className="field">
          <label>Enter Group Size</label>
          <input
            type="number"
            min="1"
            value={groupSize}
            onChange={e => setGroupSize(+e.target.value)}
          />
        </div>
        <div className="field exact-toggle">
          <label>
            <input
              type="checkbox"
              checked={exactSearch}
              onChange={e => setExactSearch(e.target.checked)}
            />
            Exact Search (KD-Tree) 
          </label>
          <small className="exact-subtext">
             Unchecked = ANN
          </small>
        </div>
        <button className="btn-search" type="submit" disabled={loading}>
          {loading ? 'Searching...' : 'Search'}
        </button>
      </form>

      {error && (
        <div style={{color: 'red', margin: '1rem', textAlign: 'center'}}>
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* --- RESULTS TABLE --- */}
      {results.length > 0 && (
        <>
          <h2>{selectedProfile} Results</h2>
          <table className="results-table">
            <thead>
              <tr>
                <th>Player Name</th>
                <th>Season</th>
                <th>Similarity</th>
                  {featureNames.map((featureName, i) => (
                  <th key={i}>{featureName}</th>
              ))}
              </tr>
            </thead>
            <tbody>
              {results.map((row, ri) => (
                <tr key={ri} style={row.is_target ? {backgroundColor:'#e8f4fd'} : {}}>
                  <td>
                    {row.player}
                  </td>
                  <td>{row.season}</td>
                  <td>{row.is_target ? 'Target' : (row.similarity || 'N/A')}</td>
                  {row.metrics && row.metrics.map((m, ci) => (
                    <td key={ci}>{m}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </div>
  );
}

export default App;
