import { motion } from 'framer-motion';
import { useCartStore } from '../store/cartStore';
import { StarIcon } from '@heroicons/react/24/solid';
import Image from './Image';

interface ProductCardProps {
  product: {
    id: string;
    name: string;
    price: number;
    image: string;
    rating: number;
    stock: number;
  };
}

export default function ProductCard({ product }: ProductCardProps) {
  const addToCart = useCartStore((state) => state.addItem);

  return (
    <motion.div
      whileHover={{ scale: 1.03 }}
      className="bg-white dark:bg-gray-800 rounded-xl shadow-sm overflow-hidden group"
    >
      <div className="relative aspect-square">
        <Image
          src={product.image}
          alt={product.name}
          className="p-4 hover:scale-105 transition-transform"
        />
        <div className="absolute top-2 right-2 bg-primary text-white px-2 py-1 rounded-full text-xs">
          {product.stock} in stock
        </div>
      </div>

      <div className="p-4 space-y-2">
        <h3 className="font-semibold line-clamp-2">{product.name}</h3>
        
        <div className="flex items-center space-x-1">
          <StarIcon className="w-4 h-4 text-yellow-400" />
          <span className="text-sm">{product.rating.toFixed(1)}</span>
        </div>

        <div className="flex justify-between items-center">
          <span className="text-xl font-bold text-primary">
            ${product.price.toFixed(2)}
          </span>
          <button
            onClick={() => addToCart({ 
              ...product, 
              quantity: 1,
              image: product.image 
            })}
            className="bg-primary text-white px-4 py-2 rounded-lg hover:bg-primary-dark transition"
          >
            Add to Cart
          </button>
        </div>
      </div>
    </motion.div>
  );
}