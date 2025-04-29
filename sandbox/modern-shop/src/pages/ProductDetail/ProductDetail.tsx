import { useParams } from 'react-router-dom';
import { useCartStore } from '../../store/cartStore';
import { ArrowLeftIcon } from '@heroicons/react/24/outline';
import { useEffect, useState } from 'react';
import './ProductDetail.css';

interface Product {
  id: string;
  name: string;
  price: number;
  description: string;
  image: string;
  rating: number;
  stock: number;
}

export default function ProductDetail() {
  const { id } = useParams<{ id: string }>();
  const [product, setProduct] = useState<Product | null>(null);
  const { addItem } = useCartStore();

  useEffect(() => {
    // Mock API call
    const fetchProduct = async () => {
      await new Promise(resolve => setTimeout(resolve, 500));
      const mockProduct: Product = {
        id: id || '1',
        name: `Product ${id}`,
        price: Math.floor(Math.random() * 100) + 50,
        description: 'Premium quality product with advanced features',
        image: `https://picsum.photos/400/600?random=${id}`,
        rating: Math.random() * 5,
        stock: Math.floor(Math.random() * 50) + 10
      };
      setProduct(mockProduct);
    };

    fetchProduct();
  }, [id]);

  if (!product) return <div>Loading...</div>;

  return (
    <div className="product-detail-container">
      <button className="back-button" onClick={() => window.history.back()}>
        <ArrowLeftIcon className="icon" />
        Back
      </button>
      
      <div className="product-detail-grid">
        <div className="product-image-container">
          <img 
            src={product.image} 
            alt={product.name} 
            className="product-image"
          />
        </div>
        
        <div className="product-info">
          <h1 className="product-title">{product.name}</h1>
          <p className="product-price">${product.price.toFixed(2)}</p>
          
          <div className="product-rating">
            {Array.from({ length: 5 }).map((_, i) => (
              <span key={i} className={`star ${i < Math.floor(product.rating) ? 'filled' : ''}`}>
                ★
              </span>
            ))}
            <span className="rating-text">({product.rating.toFixed(1)})</span>
          </div>
          
          <p className="product-description">{product.description}</p>
          
          <button 
            className="add-to-cart-button"
            onClick={() => addItem({
              id: product.id,
              name: product.name,
              price: product.price,
              image: product.image
            })}
          >
            Add to Cart
          </button>
        </div>
      </div>
    </div>
  );
}