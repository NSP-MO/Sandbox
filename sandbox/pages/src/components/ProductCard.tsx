import { Link } from 'react-router-dom';
import { Product } from '../types';
import { StarIcon } from '@heroicons/react/24/solid';

const ProductCard = ({ product }: { product: Product }) => {
  return (
    <div className="bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow">
      <Link to={`/products/${product.id}`} className="block p-4">
        <img 
          src={product.image} 
          alt={product.name} 
          className="w-full h-48 object-contain mb-4"
        />
        <h3 className="text-lg font-medium truncate">{product.name}</h3>
        <div className="flex items-center gap-1 mt-2">
          <span className="text-red-500 font-bold">
            Rp{(product.price - (product.discount || 0)).toLocaleString()}
          </span>
          {product.discount && (
            <span className="text-gray-500 line-through text-sm">
              Rp{product.price.toLocaleString()}
            </span>
          )}
        </div>
        <div className="flex items-center gap-1 mt-2">
          <StarIcon className="h-4 w-4 text-yellow-400" />
          <span className="text-sm">{product.rating}</span>
          <span className="text-sm text-gray-500 ml-2">Terjual {product.sold}</span>
        </div>
      </Link>
    </div>
  );
};

export default ProductCard;