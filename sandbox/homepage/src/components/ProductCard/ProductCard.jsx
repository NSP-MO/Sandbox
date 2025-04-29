// components/ProductCard/ProductCard.jsx
import { useCart } from '../../context/CartContext';
import './ProductCard.css';

export default function ProductCard({ product }) {
  const { addToCart } = useCart();

  return (
    <div className="product-card">
      <div className="product-image-container">
        <img src={product.image} alt={product.name} className="product-image" />
      </div>
      <div className="product-details">
        <h3 className="product-title">{product.name}</h3>
        <div className="product-price">
          <span className="current-price">Rp {product.price.toLocaleString()}</span>
          {product.originalPrice && (
            <span className="original-price">Rp {product.originalPrice.toLocaleString()}</span>
          )}
        </div>
        <div className="product-rating">
          ★★★★☆ <span className="rating-count">(120)</span>
        </div>
        <button 
          className="add-to-cart-btn"
          onClick={() => addToCart(product)}
        >
          + Keranjang
        </button>
      </div>
    </div>
  );
}