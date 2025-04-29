import { Link } from 'react-router-dom';
import { ShoppingCartIcon, UserIcon } from '@heroicons/react/24/outline';
import { useCartStore } from '../../store/cartStore';
import Search from '../Search/Search';
import './Header.css';

export default function Header() {
  const { items, toggleCart } = useCartStore();
  
  return (
    <header className="header">
      <div className="header-container">
        <Link to="/" className="logo">
          <span className="logo-primary">Toko</span>
          <span className="logo-secondary">pedia</span>
        </Link>
        
        <Search />
        
        <div className="header-actions">
          <button className="cart-button" onClick={toggleCart}>
            <ShoppingCartIcon className="icon" />
            {items.length > 0 && (
              <span className="cart-count">{items.length}</span>
            )}
          </button>
          <button className="auth-button">
            <UserIcon className="icon" />
            <span>Login</span>
          </button>
        </div>
      </div>
    </header>
  );
}