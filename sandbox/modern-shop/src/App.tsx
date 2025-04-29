import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AnimatePresence } from 'framer-motion';
import Header from './components/Header/Header';
import Home from './pages/Home/Home';
import ProductDetail from './pages/ProductDetail/ProductDetail';
import Checkout from './pages/Checkout/Checkout';
import NotFound from './pages/NotFound';
import Cart from './components/Cart/Cart';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="app-container">
          <Header />
          
          <AnimatePresence mode="wait">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/product/:id" element={<ProductDetail />} />
              <Route path="/checkout" element={<Checkout />} />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </AnimatePresence>

          <Cart />
        </div>
      </Router>
    </QueryClientProvider>
  );
}

// Single export default at the end
export default App;