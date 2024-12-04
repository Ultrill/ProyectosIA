var w = 800;
var h = 400;
var jugador, fondo;
var bala, balaD = false, nave;
var salto, menu;
var velocidadBala = 0, despBala;
var estatusAire = 0, estatusSuelo = 0;
var datosEntrenamiento = [];
var modoAuto = false, eCompleto = false;

var juego = new Phaser.Game(w, h, Phaser.CANVAS, '', { preload: preload, create: create, update: update, render: render });

function preload() {
    juego.load.image('fondo', 'assets/game/fondo.jpg');
    juego.load.spritesheet('mono', 'assets/sprites/altair.png', 32, 48);
    juego.load.image('nave', 'assets/game/ufo.png');
    juego.load.image('bala', 'assets/sprites/purple_ball.png');
    juego.load.image('menu', 'assets/game/menu.png');
}

function create() {
    juego.physics.startSystem(Phaser.Physics.ARCADE);
    juego.physics.arcade.gravity.y = 800;
    juego.time.desiredFps = 30;

    fondo = juego.add.tileSprite(0, 0, w, h, 'fondo');
    nave = juego.add.sprite(w - 100, h - 70, 'nave');
    bala = juego.add.sprite(w - 100, h, 'bala');
    jugador = juego.add.sprite(50, h, 'mono');

    juego.physics.enable(jugador);
    jugador.body.collideWorldBounds = true;
    var corre = jugador.animations.add('corre', [8, 9, 10, 11]);
    jugador.animations.play('corre', 10, true);

    juego.physics.enable(bala);
    bala.body.collideWorldBounds = true;

    pausaL = juego.add.text(w - 100, 20, 'Pausa', { font: '20px Arial', fill: '#fff' });
    pausaL.inputEnabled = true;
    pausaL.events.onInputUp.add(pausa, self);
    juego.input.onDown.add(mPausa, self);

    salto = juego.input.keyboard.addKey(Phaser.Keyboard.SPACEBAR);

    // Inicializar la red neuronal
    nnNetwork = new synaptic.Architect.Perceptron(3, 6, 1);
    nnEntrenamiento = new synaptic.Trainer(nnNetwork);
}

function pausa() {
    juego.paused = true;
    menu = juego.add.sprite(w / 2, h / 2, 'menu');
    menu.anchor.setTo(0.5, 0.5);
}

function mPausa(event) {
    if (juego.paused) {
        var menu_x1 = w / 2 - 270 / 2, menu_x2 = w / 2 + 270 / 2,
            menu_y1 = h / 2 - 180 / 2, menu_y2 = h / 2 + 180 / 2;

        var mouse_x = event.x,
            mouse_y = event.y;

        if (mouse_x > menu_x1 && mouse_x < menu_x2 && mouse_y > menu_y1 && mouse_y < menu_y2) {
            if (mouse_x >= menu_x1 && mouse_x <= menu_x2 && mouse_y >= menu_y1 && mouse_y <= menu_y1 + 90) {
                eCompleto = false;
                datosEntrenamiento = [];
                modoAuto = false;
            } else if (mouse_x >= menu_x1 && mouse_x <= menu_x2 && mouse_y >= menu_y1 + 90 && mouse_y <= menu_y2) {
                if (!eCompleto) {
                    console.log("Entrenando con", datosEntrenamiento.length, "valores");
                    nnEntrenamiento.train(datosEntrenamiento, {
                        rate: 0.03,
                        iterations: 10000,
                        shuffle: true
                    });
                    eCompleto = true;
                }
                modoAuto = true;
            }

            menu.destroy();
            resetVariables();
            juego.paused = false;
        }
    }
}

function resetVariables() {
    jugador.body.velocity.x = 0;
    jugador.body.velocity.y = 0;
    bala.body.velocity.x = 0;
    bala.position.x = w - 100;
    jugador.position.x = 50;
    balaD = false;
}

function saltar() {
    jugador.body.velocity.y = -270;
}

function update() {
    fondo.tilePosition.x -= 1;

    juego.physics.arcade.collide(bala, jugador, colisionH, null, this);

    estatusSuelo = jugador.body.onFloor() ? 1 : 0;

    despBala = Math.floor(jugador.position.x - bala.position.x);

    // Asegurar que velocidadBala tenga un valor inicial válido
    velocidadBala = velocidadBala || 0;

    // Normalización de entradas
    var inputNormalizado = [
        despBala / 800,
        velocidadBala / -800,
        estatusSuelo
    ];

    // Validación de entradas
    if (inputNormalizado.some(isNaN)) {
        console.error("Error: Entradas contienen NaN. Valores:", inputNormalizado);
        return;
    }

    // Modo manual
    if (!modoAuto && salto.isDown && jugador.body.onFloor()) {
        saltar();
    }

    // Modo automático
    if (modoAuto && jugador.body.onFloor() && bala.position.x > 0) {
        var nnSalida = nnNetwork.activate(inputNormalizado);

        // Validar la salida
        if (isNaN(nnSalida[0])) {
            console.error("Error: La salida de la red neuronal es NaN. Entrada:", inputNormalizado);
            return;
        }

        console.log("Salida NN:", nnSalida[0]);

        // Activar salto si la salida supera el umbral
        if (nnSalida[0] > 0.5) {
            console.log("Saltando...");
            saltar();
        }
    }

    // Generar disparo
    if (!balaD) {
        disparo();
    }

    // Reiniciar cuando la bala sale de la pantalla
    if (bala.position.x <= 0) {
        resetVariables();
    }

    // Recolectar datos para entrenamiento en modo manual
    if (!modoAuto && bala.position.x > 0) {
        datosEntrenamiento.push({
            input: inputNormalizado,
            output: [estatusSuelo]
        });
    }
}

function disparo() {
    velocidadBala = -1 * velocidadRandom(300, 800);
    bala.body.velocity.y = 0;
    bala.body.velocity.x = velocidadBala;
    balaD = true;
}

function colisionH() {
    pausa();
}

function velocidadRandom(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

function render() {}
