import { motion, AnimatePresence } from 'framer-motion';
import { useCartStore } from '../store/cartStore';
import { XMarkIcon } from '@heroicons/react/24/outline';

export default function Cart() {
  const { items, removeItem, clearCart, isOpen, toggleCart } = useCartStore();

  const total = items.reduce((sum, item) => sum + item.price * item.quantity, 0);

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ x: '100%' }}
          animate={{ x: 0 }}
          exit={{ x: '100%' }}
          transition={{ type: 'spring', stiffness: 300, damping: 30 }}
          className="fixed inset-y-0 right-0 w-full max-w-md bg-white dark:bg-gray-800 shadow-xl z-50"
        >
          <div className="p-6 h-full flex flex-col">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold">Shopping Cart</h2>
              <button
                onClick={toggleCart}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full"
              >
                <XMarkIcon className="w-6 h-6" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto space-y-4">
              <AnimatePresence>
                {items.map((item) => (
                  <motion.div
                    key={item.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, x: 50 }}
                    className="flex items-center justify-between py-2 border-b"
                  >
                    <div className="flex items-center space-x-4">
                      <img
                        src={item.image}
                        alt={item.name}
                        className="w-16 h-16 object-contain rounded-lg"
                      />
                      <div>
                        <h3 className="font-medium">{item.name}</h3>
                        <p className="text-gray-500">
                          ${item.price} × {item.quantity}
                        </p>
                      </div>
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
            </div>

            <div className="border-t pt-4 mt-4">
              <div className="flex justify-between text-xl font-bold mb-4">
                <span>Total:</span>
                <span>${total.toFixed(2)}</span>
              </div>
              <button
                onClick={clearCart}
                className="w-full bg-primary text-white py-3 rounded-lg hover:bg-primary-dark transition"
              >
                Checkout
              </button>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}