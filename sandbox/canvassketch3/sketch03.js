const canvasSketch = require('canvas-sketch');

const settings = {
  animate: true,
  dimensions: [600, 600],
  context: '2d'
};

const sketch = ({ context, canvas }) => {
  let snake = [{ x: 10, y: 10 }];
  let food = { x: 15, y: 15 };
  let direction = 'right';
  let nextDirection = 'right';
  let score = 0;
  let gameOver = false;
  const gridSize = 20;
  const tileSize = 30;
  let frameCounter = 0;
  const updateInterval = 10;

  const handleKeyPress = (e) => {
    if (gameOver) {
      resetGame();
      return;
    }

    switch(e.key) {
      case 'ArrowUp':
        if (direction !== 'down') nextDirection = 'up';
        break;
      case 'ArrowDown':
        if (direction !== 'up') nextDirection = 'down';
        break;
      case 'ArrowLeft':
        if (direction !== 'right') nextDirection = 'left';
        break;
      case 'ArrowRight':
        if (direction !== 'left') nextDirection = 'right';
        break;
    }
  };

  const resetGame = () => {
    snake = [{ x: 10, y: 10 }];
    direction = 'right';
    nextDirection = 'right';
    score = 0;
    gameOver = false;
    placeFood();
  };

  window.addEventListener('keydown', handleKeyPress);

  const placeFood = () => {
    while (true) {
      food = {
        x: Math.floor(Math.random() * gridSize),
        y: Math.floor(Math.random() * gridSize)
      };
      
      if (!snake.some(segment => segment.x === food.x && segment.y === food.y)) {
        break;
      }
    }
  };

  const update = () => {
    if (gameOver) return;

    frameCounter++;
    if (frameCounter < updateInterval) return;
    frameCounter = 0;

    direction = nextDirection;
    const head = { ...snake[0] };

    switch(direction) {
      case 'up': head.y--; break;
      case 'down': head.y++; break;
      case 'left': head.x--; break;
      case 'right': head.x++; break;
    }

    if (head.x < 0 || head.x >= gridSize || head.y < 0 || head.y >= gridSize) {
      gameOver = true;
      return;
    }

    if (snake.some(segment => segment.x === head.x && segment.y === head.y)) {
      gameOver = true;
      return;
    }

    snake.unshift(head);

    if (head.x === food.x && head.y === food.y) {
      score++;
      placeFood();
    } else {
      snake.pop();
    }
  };

  const draw = () => {
    context.fillStyle = 'black';
    context.fillRect(0, 0, canvas.width, canvas.height);

    snake.forEach((segment, index) => {
      context.fillStyle = index === 0 ? '#00ff00' : '#009900';
      context.fillRect(
        segment.x * tileSize,
        segment.y * tileSize,
        tileSize - 2,
        tileSize - 2
      );
    });

    context.fillStyle = 'red';
    context.fillRect(
      food.x * tileSize,
      food.y * tileSize,
      tileSize - 2,
      tileSize - 2
    );

    context.fillStyle = 'white';
    context.font = '20px Arial';
    context.fillText(`Score: ${score}`, 10, 30);

    if (gameOver) {
      context.fillStyle = 'white';
      context.font = '40px Arial';
      context.textAlign = 'center';
      context.fillText('Game Over!', canvas.width/2, canvas.height/2);
      context.font = '20px Arial';
      context.fillText('Press any key to restart', canvas.width/2, canvas.height/2 + 40);
    }
  };

  return ({ context, width, height, time }) => {
    update();
    draw();
  };
};

canvasSketch(sketch, settings);