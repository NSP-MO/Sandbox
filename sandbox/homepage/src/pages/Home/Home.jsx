// pages/Home/Home.jsx
import { useEffect, useState } from 'react';
import ProductCard from '../../components/ProductCard/ProductCard';
import './Home.css';

export default function Home() {
  const [products, setProducts] = useState([]);

  useEffect(() => {
    const mockProducts = [
      {
        id: 1,
        name: 'Smartphone Android 128GB RAM 8GB - Garansi Resmi',
        price: 2999000,
        originalPrice: 3499000,
        image: '/images/phone.jpg',
        rating: 4.5,
        sold: 120
      },
      // Add more products
    ];
    setProducts(mockProducts);
  }, []);

  return (
    <div className="home-page">
      <div className="container">
        <div className="product-grid">
          {products.map(product => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>
      </div>
    </div>
  );
}