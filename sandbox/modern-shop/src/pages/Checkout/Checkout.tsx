import { useCartStore } from '../../store/cartStore';
import { CreditCardIcon, LockClosedIcon } from '@heroicons/react/24/outline';
import './Checkout.css';

export default function Checkout() {
  const { items, clearCart } = useCartStore();
  const total = items.reduce((sum, item) => sum + item.price * (item.quantity || 1), 0);

  return (
    <div className="checkout-container">
      <div className="checkout-grid">
        <div className="payment-section">
          <h2>Payment Details</h2>
          
          <div className="payment-card">
            <div className="security-notice">
              <LockClosedIcon className="lock-icon" />
              <span>Secure SSL Encryption</span>
            </div>

            <form className="payment-form">
              <div className="form-group">
                <label>Card Number</label>
                <input
                  type="text"
                  placeholder="4242 4242 4242 4242"
                  className="card-input"
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Expiration Date</label>
                  <input type="text" placeholder="MM/YY" />
                </div>
                <div className="form-group">
                  <label>CVC</label>
                  <input type="text" placeholder="123" />
                </div>
              </div>

              <div className="form-group">
                <label>Cardholder Name</label>
                <input type="text" placeholder="John Doe" />
              </div>

              <button type="submit" className="pay-button">
                <CreditCardIcon className="icon" />
                Pay ${total.toFixed(2)}
              </button>
            </form>
          </div>
        </div>

        <div className="order-summary">
          <h2>Order Summary</h2>
          <div className="order-items">
            {items.map(item => (
              <div key={item.id} className="order-item">
                <img src={item.image} alt={item.name} className="item-image" />
                <div className="item-details">
                  <h3>{item.name}</h3>
                  <p>${item.price.toFixed(2)} x {item.quantity || 1}</p>
                </div>
                <p className="item-total">${(item.price * (item.quantity || 1)).toFixed(2)}</p>
              </div>
            ))}
          </div>

          <div className="total-section">
            <div className="total-row">
              <span>Subtotal:</span>
              <span>${total.toFixed(2)}</span>
            </div>
            <div className="total-row">
              <span>Shipping:</span>
              <span>Free</span>
            </div>
            <div className="total-row grand-total">
              <span>Total:</span>
              <span>${total.toFixed(2)}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}