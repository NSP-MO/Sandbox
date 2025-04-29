import { XMarkIcon } from '@heroicons/react/24/outline';
import { useCart } from '../context/CartContext';

export default function CartSidebar() {
  const { isCartOpen, setIsCartOpen, cartItems, removeFromCart } = useCart();

  return (
    <div className={`fixed right-0 top-0 h-full w-96 bg-white shadow-lg transform ${isCartOpen ? 'translate-x-0' : 'translate-x-full'} transition-transform`}>
      <div className="p-4 flex justify-between items-center border-b">
        <h2 className="text-xl font-semibold">Shopping Cart</h2>
        <button onClick={() => setIsCartOpen(false)}>
          <XMarkIcon className="h-6 w-6" />
        </button>
      </div>
      
      <div className="p-4 space-y-4">
        {cartItems.map(item => (
          <div key={item.id} className="flex justify-between items-center">
            <div>
              <h3 className="font-medium">{item.name}</h3>
              <p>Rp {item.price.toLocaleString()}</p>
            </div>
            <button 
              onClick={() => removeFromCart(item.id)}
              className="text-red-500 hover:text-red-700"
            >
              Remove
            </button>
          </div>
        ))}
        
        <div className="border-t pt-4">
          <p className="text-xl font-semibold">
            Total: Rp {cartItems.reduce((sum, item) => sum + item.price, 0).toLocaleString()}
          </p>
          <button className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 w-full mt-4">
            Checkout
          </button>
        </div>
      </div>
    </div>
  );
}