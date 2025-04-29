import { Swiper, SwiperSlide } from 'swiper/react'
import { Autoplay, Pagination } from 'swiper/modules'
import 'swiper/css'
import 'swiper/css/pagination'
import { useGetProductsQuery } from '../features/products/ProductsAPI'
import ProductCard from '../components/ProductCard'
import CategorySection from '../components/CategorySection'

export default function Home() {
  const { data: products, isLoading } = useGetProductsQuery()

  return (
    <div className="bg-gray-50 min-h-screen">
      {/* Hero Carousel */}
      <div className="container mx-auto px-4 py-6">
        <Swiper
          modules={[Autoplay, Pagination]}
          spaceBetween={30}
          slidesPerView={1}
          autoplay={{ delay: 5000 }}
          pagination={{ clickable: true }}
          className="h-64 md:h-96 rounded-xl"
        >
          {[1, 2, 3].map((item) => (
            <SwiperSlide key={item}>
              <div className="bg-gray-200 h-full w-full rounded-xl flex items-center justify-center">
                Banner {item}
              </div>
            </SwiperSlide>
          ))}
        </Swiper>
      </div>

      {/* Categories */}
      <CategorySection />

      {/* Product Grid */}
      <div className="container mx-auto px-4 py-8">
        <h2 className="text-2xl font-bold mb-6">Popular Products</h2>
        {isLoading ? (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[...Array(8)].map((_, i) => (
              <div key={i} className="bg-white p-4 rounded-lg animate-pulse">
                <div className="h-48 bg-gray-200 rounded mb-4" />
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-2" />
                <div className="h-4 bg-gray-200 rounded w-1/2" />
              </div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {products?.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}