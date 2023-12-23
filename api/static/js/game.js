<!-- Lógica de juego básica en JavaScript -->
    const card = document.querySelector('.card');
    const canvas = document.getElementById('gameCanvas');
    const ctx = canvas.getContext('2d');

    // Establecer el ancho y el alto del canvas
    const canvasWidth = card.clientWidth - 20; // Ancho de la card menos 20 píxeles de margen
    const canvasHeight = 400;  // Establece la altura según tus necesidades

    // Conexion con python y el controlador de game
    const socket = io.connect('http://' + document.domain + ':' + location.port);

    // Establecer el tamaño del canvas
    canvas.width = canvasWidth;
    canvas.height = canvasHeight;

    let rectX = canvas.width / 2;
    let rectY = canvas.height - 150;
    let rectWidth = 50;
    let rectHeight = 50;
    let rectColor = 'red';

    let jumping = false;
    let jumpHeight = 100;
    let jumpVelocity = 10;
    let gravity = 2;


    function drawRect() {
    ctx.fillStyle = rectColor;
    ctx.fillRect(rectX, rectY, rectWidth, rectHeight);
}

    function update() {
    if (jumping) {
    rectY -= jumpVelocity;
    jumpVelocity -= gravity;

    if (rectY >= canvas.height - 150) {
    rectY = canvas.height - 150;
    jumping = false;
}
}
}

    function jump() {
    if (!jumping) {
    jumping = true;
    jumpVelocity = 20;
}
}

    function jumpSpecial() {
        // Lógica específica del salto especial
        console.log('Special jump action!');
        jump();
    }

    window.addEventListener('keydown', (event) => {
    if (event.code === 'Space') {
    jump();
}
});

    function gameLoop() {
    // Limpiar el canvas y establecer el ancho y alto
    canvas.width = canvasWidth;
    canvas.height = canvasHeight;

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    drawRect();
    update();
    requestAnimationFrame(gameLoop);
}

    // Llama a gameLoop una vez para inicializar
    gameLoop();



    // Agrega mensajes de depuración
    socket.on('connect', function() {
        console.log('Socket connected successfully');
    });

    socket.on('disconnect', function() {
        console.log('Socket disconnected');
    });

    socket.on('hand_raised_event', function(data) {
        // Reemplaza la lógica de salto si la mano izquierda está levantada
        if (data.left_hand_raised) {
            console.log('Left hand raised - Special action');
            // Llama a la función jumpSpecial para realizar la acción especial de salto
            jumpSpecial();
        }
    });

