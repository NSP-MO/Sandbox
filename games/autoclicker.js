const robot = require('robotjs');
const readlineSync = require('readline-sync');

let clicking = false;
let clickIntervalId = null; // Untuk menyimpan ID dari setInterval

function performClick() {
    // Ambil posisi mouse saat ini dan klik
    const mousePos = robot.getMousePos();
    console.log(`Melakukan klik pada: ${mousePos.x}, ${mousePos.y}`);
    robot.mouseClick();
}

function startClicking(delayMs, numClicksStr) {
    if (clicking) {
        console.log("Klik otomatis sudah berjalan.");
        return;
    }

    let numClicks;
    if (numClicksStr.toLowerCase() === 'inf' || numClicksStr.toLowerCase() === 'infinite') {
        numClicks = Infinity;
    } else {
        numClicks = parseInt(numClicksStr);
        if (isNaN(numClicks) || numClicks <= 0) {
            console.log("Jumlah klik tidak valid. Harus angka positif atau 'inf'.");
            return;
        }
    }

    if (isNaN(delayMs) || delayMs <= 0) {
        console.log("Jeda tidak valid. Harus angka positif.");
        return;
    }

    clicking = true;
    let clicksDone = 0;
    console.log(`Memulai klik otomatis dengan jeda ${delayMs} ms.`);
    if (numClicks === Infinity) {
        console.log("Klik akan berjalan tanpa batas. Tekan CTRL+C untuk berhenti.");
    } else {
        console.log(`Akan melakukan ${numClicks} klik. Tekan CTRL+C untuk berhenti lebih awal.`);
    }

    clickIntervalId = setInterval(() => {
        if (!clicking) {
            clearInterval(clickIntervalId);
            return;
        }

        performClick();
        clicksDone++;

        if (clicksDone >= numClicks) {
            stopClicking();
            console.log(`${clicksDone} klik telah dilakukan. Selesai.`);
        }
    }, delayMs);
}

function stopClicking() {
    if (clicking) {
        clearInterval(clickIntervalId);
        clicking = false;
        console.log("Klik otomatis dihentikan.");
    }
}

function main() {
    console.log("--- Auto Clicker Sederhana (Node.js) ---");
    console.log("PENTING: Pindahkan kursor mouse ke posisi yang diinginkan sebelum klik dimulai.");
    console.log("Tekan CTRL+C di terminal ini untuk keluar atau menghentikan paksa kapan saja.\n");

    const delayInput = readlineSync.question("Masukkan jeda antar klik (dalam milidetik, contoh: 100): ");
    const numClicksInput = readlineSync.question("Masukkan jumlah klik (angka, atau 'inf' untuk tak terbatas): ");

    const delayMs = parseInt(delayInput);

    // Beri waktu pengguna untuk memindahkan mouse setelah input
    console.log("\nAnda memiliki 5 detik untuk memindahkan kursor mouse ke posisi target...");
    setTimeout(() => {
        console.log("Memulai...");
        startClicking(delayMs, numClicksInput);
    }, 5000); // Jeda 5 detik

    // Menjaga skrip tetap berjalan sampai dihentikan manual jika klik tak terbatas
    // atau sampai selesai jika jumlah klik terbatas.
    // CTRL+C akan menghentikan proses Node.js secara keseluruhan.
    process.on('SIGINT', () => {
        console.log("\nCTRL+C ditekan.");
        stopClicking();
        process.exit();
    });
}

main();