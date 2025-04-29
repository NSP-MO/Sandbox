import { ShoppingCartIcon, UserIcon } from '@heroicons/react/24/outline';
import { Link } from 'react-router-dom';
import { useCart } from '../context/CartContext';
import SearchBar from './SearchBar';
import '../styles.css';

export default function Header() {
  const { cartItems, setIsCartOpen } = useCart();
  
  return (
    <header className="header">
      <div className="header-content">
        <Link to="/" className="logo">Tokopaedi</Link>
        <SearchBar />
        <div className="header-actions">
          <button 
            onClick={() => setIsCartOpen(true)}
            className="cart-button"
          >
            <ShoppingCartIcon style={{ width: '24px', height: '24px' }} />
            <span>({cartItems.length})</span>
          </button>
          <UserIcon style={{ width: '24px', height: '24px' }} />
        </div>
      </div>
    </header>
  );
}