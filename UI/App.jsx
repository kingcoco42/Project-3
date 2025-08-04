import { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  // input stuff
  const [playerName, setPlayerName] = useState(''); // inputted name
  const [selectedProfile, setSelectedProfile] = useState(''); // selected profile
  const [featureNames, setFeatureNames] = useState([]); // profile criteria
  const [year, setYear] = useState(''); // inputed year
  const [groupSize, setGroupSize] = useState(5); // k num
  const [exactSearch, setExactSearch] = useState(false); // KNN or ANN

  // results stuff
  const [lastSearchName, setLastSearchName] = useState(''); // freeze results title bc it changes when input name field changes for some resaons.
  const [results, setResults] = useState([]); // results table rows
  const [loading, setLoading] = useState(false); // sanity check to make sure that the program is actually running and not frozen
  const [error, setError] = useState(''); // for error messages

  // function to change selected profile in the radio section
  function toggleProfile(key, e) {
    if (selectedProfile === key) { // if clicked same nothing happens
      setSelectedProfile('');
    } else {
      setSelectedProfile(key); // if not the same update
    }
/*
    const form = e.target.form;
    if (form) {
      const radioButtons = form.querySelectorAll('input[name="profile"]');
      radioButtons.forEach(radio => radio.setCustomValidity(''));
    }
      */
  }
  function formatSeason(s) { // if an year is inputted, it shows as the year 20xy instead of 20xy-yz
    const year = Number(s);
    if (!isNaN(year)) {
      const nextTwo = String((year + 1) % 100).padStart(2, '0'); //yz, padstart for edge case like 04
      return `${year}-${nextTwo}`; // 20xy-yz
    }
    return s; // for the others already the right format
  }

  function handleSubmit(e) { // search button clicked
    e.preventDefault(); // no default options
    setError(''); // resets any error messages each time the button is clicked
    //console.log('Exact Search?', exactSearch);
    setLoading(true); // show Searching 

    //console.log('year', year);


    axios.post('http://localhost:8080/api/similar', { // send to backend
      player_name: playerName,
      feature_group: selectedProfile.toLowerCase(),
      k: groupSize,
      season: year || null,
      exact: exactSearch
    })
    .then(res => {
        //console.log('API response:', res.data);
        if (res.data.success) { // if there is data
          setResults(res.data.data);
          setFeatureNames(res.data.metadata.features || []);
          setLastSearchName(playerName); 
        } else {
          setError('Failed to get results');
        }
        setLoading(false); // done loading/searching
      })
    .catch(e => {
      console.error('Error:', e); // catch errors
      if (e.response.data.error) {
        setError(e.response.data.error);
      }
        setError('An error occurred');
        setLoading(false);
    });
    
  };

  return (
    <div className="App">
      <h1>NBA Neighborhoods</h1>

      {/* Search from */}
      <form className="search-form" onSubmit={handleSubmit}>
        {/* Player name */ }
        <div className="field"> 
          <label>Enter Player Name</label>
          <input
            type="text"
            value={playerName}
            onChange={e => setPlayerName(e.target.value)}
            required
            onInvalid={e => e.target.setCustomValidity('Please enter a name.')} // if blank
            onInput={e => e.target.setCustomValidity('')}
            placeholder='e.g. LeBron James'
          />
        </div>
        {/* Year */}
        <div className="field">
          <label>Year (Optional)</label>
          <input
            type="number" // only numbers
            value={year}
            onChange={e => setYear(e.target.value)}
            placeholder="e.g. 2023 for 2023-24"
            min="2000" // this is the earliest data poitns we have
          />
        </div>
        {/* Radios selection */}
        <fieldset className="field profile-group">
          <legend>Select Desired Profile</legend>
          {['Scoring','Style', 'Defense','Impact', 'Traditional'].map((key, i) => (
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
                {key}
              </label>
            </div>
          ))}
        </fieldset>
        {/* Group size */}
        <div className="field">
          <label>Enter Group Size</label>
          <input
            type="number"
            min="1"
            value={groupSize}
            onChange={e => setGroupSize(+e.target.value)}
          />
        </div>
        {/* knn vs ann */}
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
        {/* search button */}
        <button className="btn-search" type="submit" disabled={loading}>
          {loading ? 'Searching...' : 'Search'} 
        </button>
      </form>

      {error && ( // error message
        <div style={{color: 'red', margin: '1rem', textAlign: 'center'}}>
          <strong>Error:</strong> {error}
        </div>
      )}
      
      {/* results table */}
      {results.length > 0 && (
        <div>
          <h2>Players Similar to {lastSearchName}</h2>
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
                  <td>{formatSeason(row.season)}</td>
                  <td>{row.is_target ? 'Target' : (row.similarity || 'N/A')}</td>
                  {row.metrics && row.metrics.map((m, ci) => (
                    <td key={ci}>{m}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default App;
