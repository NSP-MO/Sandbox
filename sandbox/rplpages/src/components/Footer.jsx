export default function Footer() {
    return (
      <footer className="bg-gray-800 text-white mt-16">
        <div className="container mx-auto px-4 py-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            <div>
              <h4 className="font-bold mb-4">Company</h4>
              <ul className="space-y-2 text-sm">
                <li>About Us</li>
                <li>Careers</li>
                <li>Blog</li>
                <li>Contact</li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold mb-4">Help</h4>
              <ul className="space-y-2 text-sm">
                <li>FAQ</li>
                <li>Shipping</li>
                <li>Returns</li>
                <li>Payment</li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold mb-4">Follow Us</h4>
              <ul className="space-y-2 text-sm">
                <li>Facebook</li>
                <li>Instagram</li>
                <li>Twitter</li>
                <li>YouTube</li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold mb-4">Download App</h4>
              <div className="space-y-2">
                <img 
                  src="/google-play-badge.png" 
                  alt="Google Play"
                  className="h-10 w-auto"
                />
                <img 
                  src="/app-store-badge.png" 
                  alt="App Store"
                  className="h-10 w-auto"
                />
              </div>
            </div>
          </div>
          <div className="border-t border-gray-700 mt-8 pt-4 text-center text-sm">
            <p>© 2024 Tokoclone. All rights reserved.</p>
          </div>
        </div>
      </footer>
    )
  }