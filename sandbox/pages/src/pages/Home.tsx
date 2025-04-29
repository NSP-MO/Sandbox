import { useEffect } from 'react';
import { useAppDispatch } from '../redux/store';
import ProductCard from '../components/ProductCard';
import CategoryCarousel from '../components/CategoryCarousel';
import { fetchProducts } from '../redux/productSlice';

const Home = () => {
  const dispatch = useAppDispatch();
  const { products, loading } = useAppSelector(state => state.products);

  useEffect(() => {
    dispatch(fetchProducts());
  }, [dispatch]);

  return (
    <div className="container mx-auto px-4 py-6">
      <CategoryCarousel />
      
      <h2 className="text-2xl font-bold mt-8 mb-4">Produk Populer</h2>
      {loading ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {[...Array(8)].map((_, i) => (
            <div key={i} className="bg-gray-200 h-64 animate-pulse rounded-lg" />
          ))}
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {products.map(product => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>
      )}
    </div>
  );
};

export default Home;