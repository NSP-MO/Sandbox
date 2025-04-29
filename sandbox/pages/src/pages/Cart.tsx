import { useAppSelector, useAppDispatch } from '../redux/store';
import { removeFromCart } from '../redux/cartSlice';

const Cart = () => {
  const { items, total } = useAppSelector(state => state.cart);
  const dispatch = useAppDispatch();

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Shopping Cart</h1>
      {items.length === 0 ? (
        <div className="text-center text-gray-500">Your cart is empty</div>
      ) : (
        <div className="space-y-4">
          {items.map(item => (
            <div key={item.id} className="flex items-center justify-between bg-white p-4 rounded-lg shadow-md">
              <div className="flex items-center gap-4">
                <img 
                  src={item.image} 
                  alt={item.name} 
                  className="w-20 h-20 object-contain"
                />
                <div>
                  <h3 className="font-medium">{item.name}</h3>
                  <p>Quantity: {item.quantity}</p>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <span className="font-bold">
                  Rp{(item.price * item.quantity).toLocaleString()}
                </span>
                <button 
                  onClick={() => dispatch(removeFromCart(item.id))}
                  className="text-red-500 hover:text-red-700"
                >
                  Remove
                </button>
              </div>
            </div>
          ))}
          <div className="text-xl font-bold text-right mt-8">
            Total: Rp{total.toLocaleString()}
          </div>
        </div>
      )}
    </div>
  );
};

export default Cart;