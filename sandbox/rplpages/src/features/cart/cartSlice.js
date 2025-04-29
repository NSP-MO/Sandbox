import { createSlice } from '@reduxjs/toolkit'

const cartSlice = createSlice({
  name: 'cart',
  initialState: {
    items: [],
    total: 0,
  },
  reducers: {
    addToCart: (state, action) => {
      const existingItem = state.items.find(
        item => item.id === action.payload.id
      )
      if (existingItem) {
        existingItem.quantity += 1
      } else {
        state.items.push({ ...action.payload, quantity: 1 })
      }
      state.total += action.payload.price
    },
    removeFromCart: (state, action) => {
      state.items = state.items.filter(item => item.id !== action.payload.id)
      state.total -= action.payload.price * action.payload.quantity
    },
    updateQuantity: (state, action) => {
      const item = state.items.find(item => item.id === action.payload.id)
      if (item) {
        state.total += (action.payload.quantity - item.quantity) * item.price
        item.quantity = action.payload.quantity
      }
    },
    clearCart: state => {
      state.items = []
      state.total = 0
    },
  },
})

export const { addToCart, removeFromCart, updateQuantity, clearCart } = cartSlice.actions
export default cartSlice.reducer