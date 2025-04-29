import { useEffect, useState } from 'react';
import ProductCard from '../components/ProductCard';
import CategoryNav from '../components/CategoryNav';
import '../styles.css';

export default function Home() {
  const [products, setProducts] = useState([]);
  const [categories] = useState(['Electronics', 'Fashion', 'Home', 'Beauty']);

  useEffect(() => {
    const mockProducts = [
      { id: 1, name: 'Smartphone', price: 2999000, category: 'Electronics', image: 'phone.jpg' },
      { id: 2, name: 'Laptop', price: 8999000, category: 'Electronics', image: 'laptop.jpg' },
    ];
    setProducts(mockProducts);
  }, []);

  return (
    <div className="container">
      <CategoryNav categories={categories} />
      <div className="product-grid">
        {products.map(product => (
          <ProductCard key={product.id} product={product} />
        ))}
      </div>
    </div>
  );
}