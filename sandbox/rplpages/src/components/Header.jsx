import { MagnifyingGlassIcon, ShoppingCartIcon, UserIcon } from '@heroicons/react/24/outline'

export default function Header() {
  return (
    <header className="sticky top-0 z-50 bg-white shadow-sm">
      <div className="container mx-auto px-4 py-3">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-green-600">Tokoclone</h1>
          
          <div className="relative flex-1 mx-8">
            <input
              type="text"
              placeholder="Search products..."
              className="w-full px-4 py-2 border rounded-full focus:outline-none focus:ring-2 focus:ring-green-500"
            />
            <MagnifyingGlassIcon className="h-5 w-5 absolute right-4 top-3 text-gray-400" />
          </div>

          <div className="flex items-center space-x-4">
            <button className="flex items-center space-x-1">
              <UserIcon className="h-6 w-6" />
              <span className="hidden md:inline">Login</span>
            </button>
            <button className="flex items-center space-x-1">
              <ShoppingCartIcon className="h-6 w-6" />
              <span className="hidden md:inline">Cart</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  )
}