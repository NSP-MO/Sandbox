import { StarIcon } from '@heroicons/react/24/solid'
import { useDispatch } from 'react-redux'
import { addToCart } from '../features/cart/cartSlice'
import toast from 'react-hot-toast'

export default function ProductCard({ product }) {
  const dispatch = useDispatch()

  const handleAddToCart = () => {
    dispatch(addToCart(product))
    toast.success('Added to cart!')
  }

  return (
    <div className="bg-white p-4 rounded-lg shadow-sm hover:shadow-md transition-shadow">
      <img 
        src={product.image} 
        alt={product.title}
        className="h-48 w-full object-contain mb-4"
        loading="lazy"
      />
      <h3 className="font-medium mb-2 line-clamp-2">{product.title}</h3>
      <div className="flex items-center mb-2">
        <StarIcon className="h-4 w-4 text-yellow-400" />
        <span className="text-sm ml-1">{product.rating?.rate || 4.5}</span>
      </div>
      <div className="flex justify-between items-center">
        <span className="text-lg font-bold text-green-600">
          ${product.price}
        </span>
        <button 
          onClick={handleAddToCart}
          className="bg-green-500 text-white px-3 py-1 rounded-md hover:bg-green-600 transition-colors"
        >
          Add to Cart
        </button>
      </div>
    </div>
  )
}