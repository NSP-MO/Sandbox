export default function CategoryNav({ categories }) {
    return (
      <div className="flex space-x-4 overflow-x-auto pb-2">
        {categories.map(category => (
          <button
            key={category}
            className="px-4 py-2 bg-gray-100 rounded-full hover:bg-gray-200 whitespace-nowrap"
          >
            {category}
          </button>
        ))}
      </div>
    );
  }