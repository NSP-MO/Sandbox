import { useCart } from '../context/CartContext';
import '../styles.css';

export default function ProductCard({ product }) {
  const { addToCart } = useCart();

  return (
    <div className="product-card">
      <img 
        src={product.image} 
        alt={product.name} 
        className="product-image"
      />
      <h3 className="product-name">{product.name}</h3>
      <p className="product-price">Rp {product.price.toLocaleString()}</p>
      <button 
        onClick={() => addToCart(product)}
        className="btn-primary"
      >
        Add to Cart
      </button>
    </div>
  );
}