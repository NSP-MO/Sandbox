import { useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '../redux/store';
import { fetchProductById } from '../redux/productSlice';
import { addToCart } from '../redux/cartSlice';

const ProductDetail = () => {
  const { id } = useParams();
  const dispatch = useAppDispatch();
  const { product, loading } = useAppSelector(state => state.products);

  useEffect(() => {
    if (id) {
      dispatch(fetchProductById(id));
    }
  }, [id, dispatch]);

  if (loading) return <div>Loading...</div>;

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="grid md:grid-cols-2 gap-8">
        <div className="bg-white p-4 rounded-lg shadow-md">
          <img 
            src={product?.image} 
            alt={product?.name}
            className="w-full h-96 object-contain"
          />
        </div>
        <div className="space-y-4">
          <h1 className="text-3xl font-bold">{product?.name}</h1>
          <div className="text-2xl font-bold text-red-500">
            Rp{(product?.price || 0).toLocaleString()}
          </div>
          <button 
            onClick={() => product && dispatch(addToCart(product))}
            className="bg-blue-600 text-white px-6 py-3 rounded-full hover:bg-blue-700"
          >
            Add to Cart
          </button>
          <p className="text-gray-600">{product?.description}</p>
        </div>
      </div>
    </div>
  );
};

export default ProductDetail;