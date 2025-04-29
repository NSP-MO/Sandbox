import { useEffect, useState } from 'react';
import { useCartStore } from '../../store/cartStore';
import CategoryNav from '../../components/CategoryNav/CategoryNav';
import ProductGrid from '../../components/ProductGrid/ProductGrid';
import Loader from '../../components/Loader/Loader';
import './Home.css';

export default function Home() {
  const [categories] = useState(['electronics', 'clothing', 'home', 'sports']);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [products, setProducts] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchProducts = async () => {
      setIsLoading(true);
      // Simulated API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      const mockProducts = Array.from({ length: 20 }).map((_, i) => ({
        id: `${i}`,
        name: `Product ${i + 1}`,
        price: Math.floor(Math.random() * 100) + 20,
        image: `https://picsum.photos/200?random=${i}`,
        category: categories[Math.floor(Math.random() * categories.length)],
        rating: Math.random() * 5,
        stock: Math.floor(Math.random() * 50) + 10
      }));
      setProducts(mockProducts);
      setIsLoading(false);
    };

    fetchProducts();
  }, []);

  return (
    <div className="home-page">
      <CategoryNav 
        categories={categories}
        selectedCategory={selectedCategory}
        onSelect={setSelectedCategory}
      />
      
      {isLoading ? (
        <Loader />
      ) : (
        <ProductGrid 
          products={products.filter(p =>
            selectedCategory ? p.category === selectedCategory : true
          )}
        />
      )}
    </div>
  );
}