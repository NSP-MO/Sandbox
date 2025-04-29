import { useState, useEffect } from 'react';
import { useDebounce } from '../hooks/useDebounce';

const SearchBar = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const debouncedSearch = useDebounce(searchTerm, 500);

  useEffect(() => {
    // Implement search API call here
  }, [debouncedSearch]);

  return (
    <div className="flex-1 max-w-2xl mx-4">
      <div className="relative">
        <input
          type="text"
          placeholder="Cari produk..."
          className="w-full px-4 py-2 border rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
        <button className="absolute right-3 top-2.5">
          <MagnifyingGlassIcon className="h-5 w-5 text-gray-500" />
        </button>
      </div>
    </div>
  );
};