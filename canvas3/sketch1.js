const canvasSketch = require('canvas-sketch');
const random = require('canvas-sketch-util/random');
const Papa = require('papaparse');

const settings = {
  dimensions: [1000, 1000]
};

const backgroundColor = "white";
const colors = ["rgb(255, 99, 132)", "rgb(54, 162, 235)", 
                "rgb(255, 206, 86)", "rgb(75, 192, 192)", 
                "rgb(153, 102, 255)", "rgb(255, 159, 64)"];

class Circle {
  constructor(x, y, radius, label, color) {
    this.x = x;
    this.y = y;
    this.radius = radius;
    this.label = label;
    this.color = color;
  }

  draw(context) {
    context.beginPath();
    context.arc(this.x, this.y, this.radius, 0, 2 * Math.PI, false);
    context.fillStyle = this.color;
    context.fill();
    context.stroke();

    context.fillStyle = "#000";
    context.font = "16px Arial";
    context.textAlign = "center";
    context.fillText(this.label, this.x, this.y - this.radius - 10);
  }
}

class BubbleChart {
  constructor(width, height, data) {
    this.width = width;
    this.height = height;
    this.circles = [];
    this.paddingX = 120; // Menyeimbangkan ruang agar tidak terlalu sempit
    this.paddingY = 140; 
    this.prepareData(data);
  }

  prepareData(data) {
    const priceMin = Math.min(...data.map(d => d.price));
    const priceMax = Math.max(...data.map(d => d.price));
    const cudaMin = Math.min(...data.map(d => d.cuda_cores));
    const cudaMax = Math.max(...data.map(d => d.cuda_cores));

    data.forEach((item, index) => {
      let x = this.scale(item.price, priceMin, priceMax, 150, this.width - 150);
      let y = this.scale(item.cuda_cores, cudaMin, cudaMax, this.height - 180, 120);
      let radius = Math.sqrt(item.sales) * 0.15; // Ukuran bubble tetap besar
      let color = colors[index % colors.length];

      this.circles.push(new Circle(x, y, radius, item.gpu, color));
    });
  }

  scale(value, min, max, newMin, newMax) {
    return ((value - min) / (max - min)) * (newMax - newMin) + newMin;
  }

  draw(context) {
    context.save();
    context.fillStyle = backgroundColor;
    context.fillRect(0, 0, this.width, this.height);
    
    this.drawAxis(context);
    this.circles.forEach(circle => circle.draw(context));
    this.drawTitle(context);
    this.drawAxisLabels(context);

    context.restore();
  }

  drawAxis(context) {
    context.strokeStyle = "#000";
    context.lineWidth = 2;

    // Garis sumbu X tetap di bawah
    context.beginPath();
    context.moveTo(100, this.height - 100);
    context.lineTo(this.width - 100, this.height - 100);
    context.stroke();

    // Garis sumbu Y tetap di kiri
    context.beginPath();
    context.moveTo(100, this.height - 100);
    context.lineTo(100, 100);
    context.stroke();
  }

  drawTitle(context) {
    context.font = "24px Arial";
    context.textAlign = "center";
    context.fillStyle = "#000";
    context.fillText("Perbandingan Harga vs Performa (CUDA Cores) RTX 4000 Series", this.width / 2, 50);
  }

  drawAxisLabels(context) {
    context.font = "20px Arial";
    context.fillStyle = "#000";
    context.textAlign = "center";

    // Label sumbu X (Harga)
    context.fillText("Harga (USD)", this.width / 2, this.height - 50);
    
    // Label sumbu Y (CUDA Cores)
    context.save();
    context.translate(50, this.height / 2);
    context.rotate(-Math.PI / 2);
    context.fillText("CUDA Cores", 0, 0);
    context.restore();
  }
}

async function loadCSV() {
  return new Promise((resolve, reject) => {
    fetch("data.csv")
      .then(response => response.text())
      .then(csvText => {
        Papa.parse(csvText, {
          header: true,
          skipEmptyLines: true,
          complete: function (results) {
            resolve(results.data.map(row => ({
              gpu: row.gpu,
              price: parseFloat(row.price),
              cuda_cores: parseFloat(row.cuda_cores),
              sales: parseFloat(row.sales)
            })));
          }
        });
      })
      .catch(error => reject(error));
  });
}

const sketch = async ({ context, width, height }) => {
  const data = await loadCSV();
  const chart = new BubbleChart(width, height, data);
  
  return ({ context, width, height }) => {
    chart.draw(context);
  };
};

canvasSketch(sketch, settings);
