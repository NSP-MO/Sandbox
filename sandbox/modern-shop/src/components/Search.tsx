import { useState } from 'react';
import { useDebounce } from 'use-debounce';
import { MagnifyingGlassIcon } from '@heroicons/react/24/outline';
import { useNavigate } from 'react-router-dom';

export default function Search() {
  const [query, setQuery] = useState('');
  const [debouncedQuery] = useDebounce(query, 300);
  const navigate = useNavigate();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (debouncedQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(debouncedQuery.trim())}`);
      setQuery('');
    }
  };

  return (
    <form onSubmit={handleSearch} className="flex-1 max-w-xl mx-4">
      <div className="relative">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search products..."
          className="w-full pl-4 pr-10 py-2 rounded-full border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all"
        />
        <button
          type="submit"
          className="absolute right-2 top-1/2 -translate-y-1/2 p-2 hover:bg-gray-100 rounded-full"
        >
          <MagnifyingGlassIcon className="w-5 h-5 text-gray-400" />
        </button>
      </div>
    </form>
  );
}