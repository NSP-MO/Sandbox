import { Link } from 'react-router-dom';
import { ShoppingCartIcon, UserIcon, MagnifyingGlassIcon } from '@heroicons/react/24/outline';
import { useAppSelector } from '../redux/store';
import SearchBar from './SearchBar';

const Header = () => {
  const { items } = useAppSelector(state => state.cart);

  return (
    <header className="sticky top-0 bg-white shadow-md z-50">
      <div className="container mx-auto px-4 py-3 flex items-center gap-4">
        <Link to="/" className="text-2xl font-bold text-blue-600">eShop</Link>
        
        <SearchBar />
        
        <div className="flex items-center gap-4 ml-auto">
          <Link to="/cart" className="flex items-center gap-1">
            <ShoppingCartIcon className="h-6 w-6" />
            <span className="bg-red-500 text-white rounded-full px-2 py-1 text-xs">
              {items.reduce((acc, item) => acc + item.quantity, 0)}
            </span>
          </Link>
          <Link to="/account">
            <UserIcon className="h-6 w-6" />
          </Link>
        </div>
      </div>
    </header>
  );
};

export default Header;