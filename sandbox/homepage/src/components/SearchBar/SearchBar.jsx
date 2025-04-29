// components/SearchBar/SearchBar.jsx
import { SearchIcon } from '@heroicons/react/outline';
import './SearchBar.css';

export default function SearchBar() {
  return (
    <div className="search-bar">
      <div className="search-input-container">
        <input 
          type="text" 
          placeholder="Cari di Tokopedia" 
          className="search-input"
        />
        <button className="search-button">
          <SearchIcon className="search-icon" />
        </button>
      </div>
    </div>
  );
}