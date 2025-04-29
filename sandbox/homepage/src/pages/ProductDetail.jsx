import { useParams } from 'react-router-dom';
import { useCart } from '../context/CartContext';

export default function ProductDetail() {
  const { id } = useParams();
  const { addToCart } = useCart();

  // Temporary product data
  const product = {
    id: 1,
    name: 'Smartphone',
    price: 2999000,
    description: 'High-end smartphone with 128GB storage',
    image: 'phone.jpg'
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <img 
          src={product.image} 
          alt={product.name} 
          className="w-full h-96 object-cover rounded-lg"
        />
        <div>
          <h1 className="text-3xl font-bold mb-4">{product.name}</h1>
          <p className="text-2xl text-blue-600 mb-4">Rp {product.price.toLocaleString()}</p>
          <p className="text-gray-600 mb-6">{product.description}</p>
          <button
            onClick={() => addToCart(product)}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700"
          >
            Add to Cart
          </button>
        </div>
      </div>
    </div>
  );
}