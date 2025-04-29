export default function SearchBar() {
    return (
      <div className="flex-1 mx-8">
        <input
          type="text"
          placeholder="Search products..."
          className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>
    );
  }