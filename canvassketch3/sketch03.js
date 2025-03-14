const canvasSketch = require('canvas-sketch');
const random = require('canvas-sketch-util/random');

const settings = {
  animate: true,
  attributes: { antialias: true }
};

// Physics parameters
const gravity = 0.5;
const damping = 0.8;
const ballRadius = 8;

let balls = [];
let isMouseDown = false;
let mousePos = { x: 0, y: 0 };

class Ball {
  constructor(x, y) {
    this.x = x;
    this.y = y;
    this.vx = random.range(-2, 2);
    this.vy = 0;
    this.radius = ballRadius;
    this.color = `hsl(${random.range(0, 360)}, 50%, 50%)`;
  }

  update() {
    this.vy += gravity;
    this.x += this.vx;
    this.y += this.vy;

    // Floor collision
    if (this.y + this.radius > 1) {
      this.y = 1 - this.radius;
      this.vy *= -damping;
      this.vx *= 0.9;
    }

    // Wall collision
    if (this.x - this.radius < 0 || this.x + this.radius > 1) {
      this.vx *= -0.7;
      this.x = Math.max(this.radius, Math.min(this.x, 1 - this.radius));
    }
  }

  draw(context, width, height) {
    context.beginPath();
    context.arc(
      this.x * width,
      this.y * height,
      this