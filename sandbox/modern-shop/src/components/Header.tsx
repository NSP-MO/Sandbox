import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useCartStore } from '../store/cartStore';
import Search from './Search/Search'
import './Header/Header.css';

export default function Header() {
  const cartItems = useCartStore(state => state.items);

  return (
    <header className="bg-white dark:bg-gray-800 shadow-sm sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
        <motion.div whileHover={{ scale: 1.05 }}>
          <Link to="/" className="text-2xl font-bold text-primary">
            TechShop
          </Link>
        </motion.div>

        <Search />

        <div className="flex items-center gap-6">
          <Link to="/" className="hover:text-primary transition">Home</Link>
          <Link to="/products" className="hover:text-primary transition">Products</Link>
          <button className="relative">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
            {cartItems.length > 0 && (
              <span className="absolute -top-2 -right-2 bg-primary text-white w-5 h-5 rounded-full text-xs flex items-center justify-center">
                {cartItems.length}
              </span>
            )}
          </button>
        </div>
      </div>
    </header>
  );
}