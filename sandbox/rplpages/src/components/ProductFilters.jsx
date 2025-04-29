import { useGetProductsQuery } from '../features/products/ProductsAPI'

export default function ProductFilters() {
  const { data: products } = useGetProductsQuery()
  
  // Implement filter logic using RTK Query parameters
  return (
    <div className="flex flex-wrap gap-4 mb-6">
      <select className="border rounded-md px-3 py-2">
        <option>Sort by Price</option>
        <option value="asc">Low to High</option>
        <option value="desc">High to Low</option>
      </select>
      
      <select className="border rounded-md px-3 py-2">
        <option>Filter by Category</option>
        {[...new Set(products?.map(p => p.category))].map(category => (
          <option key={category} value={category}>{category}</option>
        ))}
      </select>
    </div>
  )
}