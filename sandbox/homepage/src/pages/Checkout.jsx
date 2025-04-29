import { useCart } from '../context/CartContext';

export default function Checkout() {
  const { cartItems } = useCart();

  return (
    <div className="max-w-7xl mx-auto px-4 py-6">
      <h1 className="text-2xl font-bold mb-6">Checkout</h1>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-4">Order Summary</h2>
            {cartItems.map(item => (
              <div key={item.id} className="flex justify-between items-center py-2 border-b">
                <span>{item.name}</span>
                <span>Rp {item.price.toLocaleString()}</span>
              </div>
            ))}
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4">Total</h2>
          <p className="text-2xl font-bold text-blue-600 mb-6">
            Rp {cartItems.reduce((sum, item) => sum + item.price, 0).toLocaleString()}
          </p>
          <button className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 w-full">
            Proceed to Payment
          </button>
        </div>
      </div>
    </div>
  );
}