import { useCartStore } from "../store/cartStore";
import { motion } from "framer-motion";
import { CreditCardIcon } from "@heroicons/react/24/outline";

export default function Checkout() {
  const { items, clearCart } = useCartStore();
  const total = items.reduce((sum, item) => sum + item.price * item.quantity, 0);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="max-w-7xl mx-auto p-6"
    >
      <h1 className="text-3xl font-bold mb-8">Checkout</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="space-y-6">
          <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm">
            <h2 className="text-xl font-semibold mb-4">Order Summary</h2>
            {items.map((item) => (
              <div
                key={item.id}
                className="flex items-center justify-between py-3 border-b"
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
                <p className="font-medium">
                  ${(item.price * item.quantity).toFixed(2)}
                </p>
              </div>
            ))}
            
            {items.length === 0 && (
              <p className="text-center text-gray-500 py-8">
                Your cart is empty
              </p>
            )}
          </div>

          <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm">
            <h2 className="text-xl font-semibold mb-4">Payment Information</h2>
            <div className="space-y-4">
              <div className="flex flex-col space-y-2">
                <label className="text-sm font-medium">Card Number</label>
                <div className="flex items-center space-x-2 border rounded-lg p-3">
                  <CreditCardIcon className="w-6 h-6 text-gray-400" />
                  <input
                    type="text"
                    placeholder="4242 4242 4242 4242"
                    className="flex-1 outline-none bg-transparent"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="flex flex-col space-y-2">
                  <label className="text-sm font-medium">Expiration</label>
                  <input
                    type="text"
                    placeholder="MM/YY"
                    className="border rounded-lg p-3 outline-none"
                  />
                </div>
                <div className="flex flex-col space-y-2">
                  <label className="text-sm font-medium">CVC</label>
                  <input
                    type="text"
                    placeholder="123"
                    className="border rounded-lg p-3 outline-none"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm h-fit sticky top-8">
          <h2 className="text-xl font-semibold mb-6">Order Total</h2>
          <div className="space-y-4">
            <div className="flex justify-between">
              <span>Subtotal</span>
              <span>${total.toFixed(2)}</span>
            </div>
            <div className="flex justify-between">
              <span>Shipping</span>
              <span>Free</span>
            </div>
            <div className="flex justify-between">
              <span>Taxes</span>
              <span>$0.00</span>
            </div>
            <div className="flex justify-between font-bold text-lg pt-4 border-t">
              <span>Total</span>
              <span>${total.toFixed(2)}</span>
            </div>
          </div>

          <button
            onClick={clearCart}
            className="w-full bg-primary text-white py-3 rounded-lg mt-6 hover:bg-primary-dark transition"
          >
            Confirm Payment
          </button>
        </div>
      </div>
    </motion.div>
  );
}