const puppeteer = require('puppeteer');
const alert = require('node-notifier'); // Install with: npm install node-notifier

(async () => {
  const browser = await puppeteer.launch({ headless: false });
  const page = await browser.newPage();
  
  // Replace with your target URL
  const TARGET_URL = 'https://your-ticket-website.com';
  
  const checkPrice = async () => {
    try {
      await page.reload({ waitUntil: 'networkidle2' });
      
      // Wait for price element to load
      const priceElement = await page.waitForSelector('span.Text_text__DSnue.Text_variant_alert__7jMF3.Text_size_b2__y3Q2E.Text_weight_bold__m4BAY', {
        timeout: 5000
      });

      // Get price text and convert to number
      const priceText = await page.evaluate(el => el.textContent, priceElement);
      const priceValue = parseInt(priceText.replace(/[^\d]/g, ''), 10);

      console.log(`Current price: ${priceText} (${priceValue}) - ${new Date().toLocaleTimeString()}`);

      // Check if price is below threshold
      if (priceValue < 300000) {
        console.log('\x07'); // System beep
        alert.notify({
          title: 'PRICE ALERT!',
          message: `Price dropped to ${priceText}`,
          sound: true
        });
        console.log(`ALERT! Price dropped to ${priceText}`);
        await browser.close();
        process.exit();
      }
    } catch (error) {
      console.log('Element not found or page load error, retrying...');
    }
  };

  await page.goto(TARGET_URL);
  
  // Initial check
  await checkPrice();

  // Set up periodic checking every 30 seconds
  setInterval(async () => {
    await checkPrice();
  }, 30000); // 30 seconds interval