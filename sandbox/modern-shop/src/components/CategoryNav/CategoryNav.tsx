interface CategoryNavProps {
    categories: string[];
    selectedCategory: string;
    onSelect: (category: string) => void;
  }
  
  export default function CategoryNav({ 
    categories, 
    selectedCategory,
    onSelect 
  }: CategoryNavProps) {
    return (
      <div className="category-nav">
        {categories.map((category) => (
          <button
            key={category}
            className={`category-button ${
              category === selectedCategory ? 'active' : ''
            }`}
            onClick={() => onSelect(category)}
          >
            {category}
          </button>
        ))}
      </div>
    );
  }