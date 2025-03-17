const canvasSketch = require('canvas-sketch');
const random = require('canvas-sketch-util/random');
const Papa = require('papaparse');

const settings = {
  dimensions: [1000, 1000]
};

const backgroundColor = "white";
const colorMap = {
  "Asia": "rgb(255, 0, 0)",     // Merah
  "Europe": "rgb(255, 206, 86)", // Kuning
  "Africa": "rgb(54, 162, 235)"   // Biru
};

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
    console.log("Loaded Data:", data);
    this.prepareData(data);
  }

  prepareData(data) {
    const incomeMin = Math.min(...data.map(d => d.income));
    const incomeMax = Math.max(...data.map(d => d.income));
    const lifespanMin = Math.min(...data.map(d => d.lifespan));
    const lifespanMax = Math.max(...data.map(d => d.lifespan));

    data.forEach((item) => {
      let x = this.scale(item.income, incomeMin, incomeMax, 150, this.width - 150);
      let y = this.scale(item.lifespan, lifespanMin, lifespanMax, this.height - 180, 120);
      let radius = Math.sqrt(item.population) * 0.03; // Perbesar radius agar lebih terlihat
      let color = colorMap[item.continent] || "gray"; // Default ke abu-abu jika tidak ditemukan

      console.log(`Creating circle: ${item.country} at (${x}, ${y}) with radius ${radius}`);
      this.circles.push(new Circle(x, y, radius, item.country, color));
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
    context.beginPath();
    context.moveTo(100, this.height - 100);
    context.lineTo(this.width - 100, this.height - 100);
    context.stroke();
    context.beginPath();
    context.moveTo(100, this.height - 100);
    context.lineTo(100, 100);
    context.stroke();
  }

  drawTitle(context) {
    context.font = "24px Arial";
    context.textAlign = "center";
    context.fillStyle = "#000";
    context.fillText("Perbandingan Lifespan Terhadap Income di Berbagai Negara", this.width / 2, 50);
  }

  drawAxisLabels(context) {
    context.font = "20px Arial";
    context.fillStyle = "#000";
    context.textAlign = "center";
    context.fillText("Income", this.width / 2, this.height - 50);
    
    context.save();
    context.translate(50, this.height / 2);
    context.rotate(-Math.PI / 2);
    context.fillText("Lifespan", 0, 0);
    context.restore();
  }
}

async function loadCSV() {
  return new Promise((resolve, reject) => {
    fetch("datacountry.csv")
      .then(response => response.text())
      .then(csvText => {
        Papa.parse(csvText, {
          header: true,
          skipEmptyLines: true,
          complete: function (results) {
            console.log("Parsed CSV Data:", results.data);
            resolve(results.data.map(row => ({
              country: row.country,
              income: parseFloat(row.income),
              lifespan: parseFloat(row.lifespan),
              population: parseFloat(row.population),
              continent: row.continent // Ambil data benua
            })));
          }
        });
      })
      .catch(error => {
        console.error("Error loading CSV:", error);
        reject(error);
      });
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
