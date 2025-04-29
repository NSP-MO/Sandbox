import { useCartStore } from '../../store/cartStore';
import { AnimatePresence, motion } from 'framer-motion';

export default function Cart() {
  const { items, removeItem, clearCart } = useCartStore();
  const total = items.reduce((sum, item) => sum + item.price * item.quantity, 0);

  return (
    <div className="fixed right-0 top-0 h-screen w-96 bg-white dark:bg-gray-800 shadow-xl p-6">
      <h2 className="text-2xl font-bold mb-6">Your Cart</h2>
      
      <AnimatePresence>
        {items.map((item) => (
          <motion.div
            key={item.id}
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 50 }}
            className="flex items-center justify-between py-4 border-b"
          >
            <div>
              <h3 className="font-medium">{item.name}</h3>
              <p className="text-gray-500">${item.price} x {item.quantity}</p>
            </div>
            <button 
              onClick={() => removeItem(item.id)}
              className="text-red-500 hover:text-red-700"
            >
              Remove
            </button>
          </motion.div>
        ))}
      </AnimatePresence>

      <div className="mt-8">
        <div className="flex justify-between text-xl font-bold">
          <span>Total:</span>
          <span>${total.toFixed(2)}</span>
        </div>
        <button
          onClick={clearCart}
          className="w-full mt-6 bg-primary text-white py-3 rounded-lg hover:bg-primary-dark transition"
        >
          Checkout
        </button>
      </div>
    </div>
  );
}