// Membaca data dari file CSV (pastikan file "startup_data.csv" berada di lokasi yang sama atau sesuaikan path-nya)
d3.csv("startup_data.csv").then(function(data) {
    // Contoh: Misalkan CSV memiliki kolom "Year" dan "Investment"
    // Konversi nilai numeric jika diperlukan
    var years = data.map(function(d) { return +d.Year; });
    var investments = data.map(function(d) { return +d.Investment; });

    // Jika struktur CSV berbeda, sesuaikan nama kolom dan konversinya
    // Contoh: Jika data memiliki kolom "Startup" dan "Funding", Anda bisa mengubahnya:
    // var startups = data.map(function(d) { return d.Startup; });
    // var fundings = data.map(function(d) { return +d.Funding; });

    // Konfigurasi trace untuk bar chart
    var trace = {
        x: years,           // nilai sumbu x (misalnya tahun)
        y: investments,     // nilai sumbu y (misalnya investasi)
        type: 'bar',        // tipe chart: bar chart (bisa diganti dengan 'pie', 'scatter', dll.)
        marker: {
            color: 'teal'
        }
    };

    // Konfigurasi layout chart agar lebih menarik dan interaktif
    var layout = {
        title: 'Jumlah Investasi per Tahun',
        xaxis: {
            title: 'Tahun'
        },
        yaxis: {
            title: 'Investasi (dalam jutaan atau sesuai skala data)'
        }
    };

    // Konfigurasi tambahan (opsional) untuk responsivitas, dsb.
    var config = {
        responsive: true
    };

    // Tampilkan chart pada elemen dengan id 'chart'
    Plotly.newPlot('chart', [trace], layout, config);
}).catch(function(error){
    console.error("Error loading the CSV data: " + error);
});
