import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import { Product } from '../types';

interface ProductState {
  products: Product[];
  loading: boolean;
  error: string | null;
}

const initialState: ProductState = {
  products: [],
  loading: false,
  error: null
};

export const fetchProducts = createAsyncThunk('products/fetch', async () => {
  // Mock API call
  await new Promise(resolve => setTimeout(resolve, 1000));
  return mockProducts; // Replace with actual API call
});

const productSlice = createSlice({
  name: 'products',
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchProducts.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchProducts.fulfilled, (state, action) => {
        state.products = action.payload;
        state.loading = false;
      })
      .addCase(fetchProducts.rejected, (state) => {
        state.loading = false;
        state.error = 'Failed to fetch products';
      });
  }
});

export default productSlice.reducer;

const mockProducts: Product[] = [
  {
    id: '1',
    name: 'Smartphone XYZ',
    price: 2500000,
    discount: 500000,
    rating: 4.5,
    sold: 150,
    image: '/images/phone.jpg',
    description: 'High-end smartphone with...',
    category: 'electronics',
    stock: 50
  },
  // Add more mock products
];