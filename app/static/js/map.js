document.addEventListener('DOMContentLoaded', function() {
    const map = L.map('map').setView([35.3331, 139.4042], 14);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    const sheltersData = JSON.parse(document.getElementById('sheltersData').textContent);
    const markersWithOther = [];
    const markersWithoutOther = [];

    sheltersData.forEach(shelter => {
        const markerColor = shelter.other ? 'white' : 'blue';
        const capacityText = shelter.capacity ? `想定収容人数: ${shelter.capacity}人<br>` : '想定収容人数: 不明<br>';

        // カスタムアイコンの作成
        const icon = L.divIcon({
            className: 'custom-icon',
            html: `<div style="background-color: ${markerColor}; width: 20px; height: 20px; border-radius: 50%; border: 2px solid black; padding: 5px; box-sizing: border-box;"></div>`,
            iconSize: [20, 20]
        });

        const marker = L.marker([shelter.latitude, shelter.longitude], { icon: icon })
            .bindPopup(`
                <strong>${shelter.name}</strong><br>
                ${capacityText}
                住所: ${shelter.address}<br>
                <a href="/shelter/${shelter.id}">詳細を見る</a>
            `);

        if (shelter.other) {
            markersWithOther.push(marker);
        } else {
            markersWithoutOther.push(marker);
        }
    });

    // レイヤーのコントロールを作成
    const layerControl = L.control.layers({}, {
        '緊急指定避難所': L.layerGroup(markersWithoutOther).addTo(map),
        '広域避難場所': L.layerGroup(markersWithOther).addTo(map),
    }).addTo(map);
});
