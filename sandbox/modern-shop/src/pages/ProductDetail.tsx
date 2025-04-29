import { useParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useCartStore } from '../store/cartStore';
import Image from '../components/Image';

interface ProductDetailProps {
  products: Product[];
}

export default function ProductDetail({ products }: ProductDetailProps) {
  const { id } = useParams();
  const product = products.find(p => p.id === id);
  const addToCart = useCartStore(state => state.addItem);

  if (!product) return <div>Product not found</div>;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="max-w-7xl mx-auto p-6"
    >
      <div className="grid md:grid-cols-2 gap-8">
        <div className="relative aspect-square">
          <Image
            src={product.image}
            alt={product.name}
            className="rounded-xl bg-white p-8 shadow-lg"
          />
        </div>
        
        <div className="space-y-6">
          <h1 className="text-4xl font-bold">{product.name}</h1>
          <p className="text-2xl text-primary font-bold">${product.price}</p>
          
          <div className="flex items-center space-x-2">
            <div className="flex text-yellow-400">
              {[...Array(5)].map((_, i) => (
                <svg key={i} className={`w-6 h-6 ${i < Math.floor(product.rating) ? 'fill-current' : 'fill-gray-300'}`} viewBox="0 0 20 20">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
              ))}
            </div>
            <span>({product.rating})</span>
          </div>

          <p className="text-gray-600 dark:text-gray-300">{product.description}</p>

          <button
            onClick={() => addToCart(product)}
            className="w-full bg-primary text-white py-3 rounded-lg hover:bg-primary-dark transition"
          >
            Add to Cart
          </button>
        </div>
      </div>
    </motion.div>
  );
}