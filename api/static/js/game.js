const card = document.querySelector('.card');
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

// Establecer el ancho y el alto del canvas
const canvasWidth = card.clientWidth - 20; // Ancho de la card menos 20 píxeles de margen
const canvasHeight = 400; // Establece la altura según tus necesidades

// Conexion con python y el controlador de game
const socket = io.connect('http://' + document.domain + ':' + location.port);

// Establecer el tamaño del canvas
canvas.width = canvasWidth;
canvas.height = canvasHeight;

// Rectángulo rojo
let rectRed = {
    x: canvas.width / 2 - 75,
    y: canvas.height - 150,
    width: 50,
    height: 50,
    color: 'red',
    jumping: false,
    jumpVelocity: 20,
    gravity: 2,
};

// Rectángulo verde
let rectGreen = {
    x: canvas.width / 2 + 25,
    y: canvas.height - 150,
    width: 50,
    height: 50,
    color: 'green',
    jumping: false,
    jumpVelocity: 20,
    gravity: 2,
};

function drawRect(rect) {
    ctx.fillStyle = rect.color;
    ctx.fillRect(rect.x, rect.y, rect.width, rect.height);
}

function update(rect) {
    if (rect.jumping) {
        rect.y -= rect.jumpVelocity;
        rect.jumpVelocity -= rect.gravity;

        if (rect.y >= canvas.height - 150) {
            rect.y = canvas.height - 150;
            rect.jumping = false;
        }
    }
}

function jump(rect) {
    if (!rect.jumping) {
        rect.jumping = true;
        rect.jumpVelocity = 20;
    }
}

function jumpSpecial(rect) {
    // Lógica específica del salto especial
    console.log('Special jump action for ' + rect.color + ' rectangle!');
    jump(rect);
}

window.addEventListener('keydown', (event) => {
    if (event.code === 'Space') {
        // Realizar el salto en el rectángulo correspondiente según la posición de la mano
        jump(rectRed); // Por defecto, salto del rectángulo rojo
        // Programar un salto automático del rectángulo verde un segundo después
        setTimeout(() => {
            jump(rectGreen);
        }, 1000);
    }
});

function gameLoop() {
    // Limpiar el canvas y establecer el ancho y alto
    canvas.width = canvasWidth;
    canvas.height = canvasHeight;

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    drawRect(rectRed);
    drawRect(rectGreen);
    update(rectRed);
    update(rectGreen);
    requestAnimationFrame(gameLoop);
}

// Llama a gameLoop una vez para inicializar
gameLoop();

// Agrega mensajes de depuración
socket.on('connect', function () {
    console.log('Socket connected successfully');
});

socket.on('disconnect', function () {
    console.log('Socket disconnected');
});

socket.on('hand_raised_event', function (data) {
    // Reemplaza la lógica de salto según la mano levantada
    if (data.left_hand_raised) {
        // Llama a la función jumpSpecial para realizar la acción especial de salto
        jumpSpecial(rectRed);
    } else if (data.right_hand_raised) {
        // Si no se levanta la mano derecha, realiza el salto con el rectángulo verde
        jump(rectGreen);
    }else{
        jump();
    }
});
