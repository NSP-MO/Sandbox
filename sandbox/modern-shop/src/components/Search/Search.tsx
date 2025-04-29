import { useDebounce } from 'use-debounce';
import { useQuery } from '@tanstack/react-query';

export default function Search() {
  const [query, setQuery] = useState('');
  const [debouncedQuery] = useDebounce(query, 300);
  
  const { data: suggestions } = useQuery({
    queryKey: ['search', debouncedQuery],
    queryFn: async () => {
      const response = await fetch(`/api/search?q=${debouncedQuery}`);
      return response.json();
    },
    enabled: debouncedQuery.length > 2,
  });

  return (
    <div className="relative max-w-2xl w-full">
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search products..."
        className="w-full px-4 py-3 rounded-full border-2 border-gray-200 focus:border-primary outline-none transition"
      />
      
      {suggestions && (
        <div className="absolute top-full left-0 right-0 mt-2 bg-white dark:bg-gray-800 rounded-xl shadow-xl z-50">
          {suggestions.map((suggestion) => (
            <div 
              key={suggestion.id}
              className="p-4 hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer transition"
            >
              {suggestion.name}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}