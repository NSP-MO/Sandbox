// components/Header/Header.jsx
import { SearchIcon, ShoppingCartIcon, UserIcon } from '@heroicons/react/outline';
import { Link } from 'react-router-dom';
import { useCart } from '../../context/CartContext';
import SearchBar from '../SearchBar/SearchBar';
import './Header.css';

export default function Header() {
  const { cartItems, setIsCartOpen } = useCart();

  return (
    <header className="header">
      <div className="header-top">
        <div className="container">
          <Link to="/" className="logo">
            <span className="logo-primary">Toko</span>
            <span className="logo-secondary">pedia</span>
          </Link>
          
          <SearchBar />
          
          <div className="header-actions">
            <button className="cart-btn" onClick={() => setIsCartOpen(true)}>
              <ShoppingCartIcon className="icon" />
              <span className="cart-count">{cartItems.length}</span>
            </button>
            <button className="auth-btn">
              <UserIcon className="icon" />
              <span>Masuk</span>
            </button>
          </div>
        </div>
      </div>
      
      <div className="header-bottom">
        <div className="container">
          <CategoryNav />
        </div>
      </div>
    </header>
  );
}