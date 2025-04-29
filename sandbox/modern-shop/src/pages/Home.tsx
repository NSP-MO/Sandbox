import { motion } from 'framer-motion';
import ProductGrid from '../components/ProductGrid';
import CategoryNav from '../components/CategoryNav/CategoryNav';
import ProductGrid from '../components/ProductGrid/ProductGrid';

interface HomeProps {
  products: Product[];
}

export default function Home({ products }: HomeProps) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="max-w-7xl mx-auto p-6"
    >
      <h2 className="text-3xl font-bold mb-8">Featured Products</h2>
      <ProductGrid products={products} />
    </motion.div>
  );
}