let map, userPin, nearestShelterPin;
let allShelters, userHomeAddress;

document.addEventListener('DOMContentLoaded', function() {
    setupMap();
});

function setupMap() {
    map = L.map('map').setView([35.3331, 139.4042], 14);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    allShelters = JSON.parse(document.getElementById('sheltersData').textContent);
    userHomeAddress = JSON.parse(document.getElementById('userAddress').textContent);

    const emergencyShelters = [];
    const wideShelters = [];

    allShelters.forEach(shelter => {
        const pinColor = shelter.other ? 'white' : 'blue';
        const capacityInfo = shelter.capacity ? `想定収容人数: ${shelter.capacity}人<br>` : '想定収容人数: 不明<br>';

        const icon = L.divIcon({
            className: 'custom-icon',
            html: `<div style="background-color: ${pinColor}; width: 20px; height: 20px; border-radius: 50%; border: 2px solid black; padding: 5px; box-sizing: border-box;"></div>`,
            iconSize: [20, 20]
        });

        const marker = L.marker([shelter.latitude, shelter.longitude], { icon: icon })
            .bindPopup(`
                <strong>${shelter.name}</strong><br>
                ${capacityInfo}
                住所: ${shelter.address}<br>
                <a href="/shelter/${shelter.id}">詳細を見る</a>
            `);

        if (shelter.other) {
            wideShelters.push(marker);
        } else {
            emergencyShelters.push(marker);
        }
    });

    const emergencySheltersLayer = L.layerGroup(emergencyShelters).addTo(map);
    const wideSheltersLayer = L.layerGroup(wideShelters).addTo(map);

    L.Control.CustomButtons = L.Control.extend({
        onAdd: function(map) {
            var container = L.DomUtil.create('div', 'leaflet-bar leaflet-control custom-buttons-container');
            container.style.backgroundColor = 'white';

            var searchControl = L.DomUtil.create('div', 'custom-control-item', container);
            var searchButton = L.DomUtil.create('a', 'custom-button', searchControl);
            searchButton.innerHTML = '<i class="fas fa-search" title="住所を検索"></i>';
            searchButton.href = '#';
            var searchBar = L.DomUtil.create('div', 'control-panel search-bar', searchControl);
            searchBar.style.display = 'none';
            searchBar.innerHTML = '<input type="text" id="search-input" placeholder="住所を入力">' +
                                  '<button id="search-button">検索</button>';

            var layerControl = L.DomUtil.create('div', 'custom-control-item', container);
            var layerButton = L.DomUtil.create('a', 'custom-button', layerControl);
            layerButton.innerHTML = '<i class="fas fa-layer-group" title="レイヤー切替"></i>';
            layerButton.href = '#';
            var layerList = L.DomUtil.create('div', 'control-panel layer-list', layerControl);
            layerList.style.display = 'none';
            this._createLayerItem(layerList, '緊急指定避難所', emergencySheltersLayer);
            this._createLayerItem(layerList, '広域避難場所', wideSheltersLayer);

            var currentLocationButton = L.DomUtil.create('a', 'custom-button', container);
            currentLocationButton.innerHTML = '<i class="fas fa-map-marker-alt" title="現在地から最寄りの避難所を表示"></i>';
            currentLocationButton.href = '#';

            var registeredAddressButton = L.DomUtil.create('a', 'custom-button', container);
            registeredAddressButton.innerHTML = '<i class="fas fa-home" title="登録住所から最寄りの避難所を表示"></i>';
            registeredAddressButton.href = '#';

            L.DomEvent.on(layerButton, 'click', function(e) {
                L.DomEvent.preventDefault(e);
                L.DomEvent.stopPropagation(e);
                layerList.style.display = layerList.style.display === 'none' ? 'block' : 'none';
                searchBar.style.display = 'none';  // 検索バーを閉じる
            });

            L.DomEvent.on(searchButton, 'click', function(e) {
                L.DomEvent.preventDefault(e);
                L.DomEvent.stopPropagation(e);
                searchBar.style.display = searchBar.style.display === 'none' ? 'block' : 'none';
                layerList.style.display = 'none';  // レイヤーリストを閉じる
            });

            L.DomEvent.on(currentLocationButton, 'click', findNearestShelterFromCurrentLocation);
            L.DomEvent.on(registeredAddressButton, 'click', findNearestShelterFromHomeAddress);

            L.DomEvent.disableClickPropagation(container);

            return container;
        },

        _createLayerItem: function(container, label, layer) {
            var item = L.DomUtil.create('div', 'layer-item', container);
            var checkbox = L.DomUtil.create('input', '', item);
            checkbox.type = 'checkbox';
            checkbox.checked = true;

            var text = L.DomUtil.create('span', '', item);
            text.innerHTML = label;

            L.DomEvent.on(checkbox, 'change', function() {
                if (checkbox.checked) {
                    map.addLayer(layer);
                } else {
                    map.removeLayer(layer);
                }
            });
        }
    });

    L.control.customButtons = function(opts) {
        return new L.Control.CustomButtons(opts);
    }

    L.control.customButtons({ position: 'topright' }).addTo(map);

    document.getElementById('search-button').addEventListener('click', function() {
        var address = document.getElementById('search-input').value;
        if (address) {
            searchAddress(address);
        }
    });
}

function calculateDistance(lat1, lon1, lat2, lon2) {
    const R = 6371; // 地球の半径（km）
    const radLat1 = lat1 * Math.PI / 180; // 緯度1をラジアンに変換
    const radLat2 = lat2 * Math.PI / 180; // 緯度2をラジアンに変換
    const deltaLat = (lat2 - lat1) * Math.PI / 180; // 緯度の差
    const deltaLon = (lon2 - lon1) * Math.PI / 180; // 経度の差

    // ヒュベニの公式
    const a = Math.sin(deltaLat/2) * Math.sin(deltaLat/2) +
              Math.cos(radLat1) * Math.cos(radLat2) *
              Math.sin(deltaLon/2) * Math.sin(deltaLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));

    return R * c; // 距離（km）
}

function findNearestShelterFromCurrentLocation() {
    if ("geolocation" in navigator) {
        navigator.geolocation.getCurrentPosition(
            function(position) {
                const lat = position.coords.latitude;
                const lng = position.coords.longitude;
                showNearestShelter(lat, lng, true);
            },
            function(error) {
                alert("位置情報の取得に失敗しました。代わりにデフォルトの位置を使用します。");
                useDefaultLocation();
            },
            {
                enableHighAccuracy: true,
                timeout: 5000,
                maximumAge: 0
            }
        );
    } else {
        alert("お使いのブラウザは位置情報をサポートしていません。デフォルトの位置を使用します。");
        useDefaultLocation();
    }
}

function findNearestShelterFromHomeAddress() {
    if (userHomeAddress) {
        getLatLngFromAddress(userHomeAddress)
            .then(({ lat, lng }) => {
                showNearestShelter(lat, lng, false);
            })
            .catch(error => {
                alert("住所の緯度経度の取得に失敗しました。");
            });
    } else {
        alert("登録住所が設定されていません。");
    }
}

function useDefaultLocation() {
    getLatLngFromAddress("茅ヶ崎市役所")
        .then(({ lat, lng }) => {
            showNearestShelter(lat, lng, true);
        })
        .catch(error => {
            alert("位置情報の取得に失敗しました。");
        });
}

function showNearestShelter(lat, lng, isCurrentLocation) {
    if (userPin) {
        map.removeLayer(userPin);
    }
    userPin = L.marker([lat, lng]).addTo(map);
    
    const locationText = isCurrentLocation ? '現在地' : '自宅';
    userPin.bindPopup(`${locationText}`).openPopup();

    let nearestShelter = null;
    let minDistance = Infinity;

    allShelters.forEach(shelter => {
        if (!shelter.other) {
            const distance = calculateDistance(lat, lng, shelter.latitude, shelter.longitude);
            if (distance < minDistance) {
                minDistance = distance;
                nearestShelter = shelter;
            }
        }
    });

    if (nearestShelter) {
        if (nearestShelterPin) {
            map.removeLayer(nearestShelterPin);
        }
        nearestShelterPin = L.marker([nearestShelter.latitude, nearestShelter.longitude], {
            icon: L.divIcon({
                className: 'custom-icon',
                html: '<div style="background-color: red; width: 20px; height: 20px; border-radius: 50%; border: 2px solid black;"></div>',
                iconSize: [20, 20]
            })
        }).addTo(map);

        const capacityText = nearestShelter.capacity ? `想定収容人数: ${nearestShelter.capacity}人<br>` : '想定収容人数: 不明<br>';
        nearestShelterPin.bindPopup(`
            <strong style="color: red;">${locationText}から最寄りの緊急指定避難所</strong><br>
            <strong>${nearestShelter.name}</strong><br>
            ${capacityText}
            住所: ${nearestShelter.address}<br>
            <a href="/shelter/${nearestShelter.id}">詳細を見る</a>
        `).openPopup();

        map.setView([nearestShelter.latitude, nearestShelter.longitude], 15);
    } else {
        alert("近くに緊急指定避難所が見つかりませんでした。");
    }
}

function searchAddress(address) {
    if (address) {
        getLatLngFromAddress(address)
            .then(({ lat, lng }) => {
                map.setView([lat, lng], 15);  // 検索した位置にズーム
                if (searchPin) {
                    map.removeLayer(searchPin);
                }
                searchPin = L.marker([lat, lng]).addTo(map)  // 検索した位置にマーカーを追加
                    .bindPopup('検索した位置')
                    .openPopup();
            })
            .catch(error => {
                alert("入力された住所の緯度経度の取得に失敗しました。");
            });
    }
}

function getLatLngFromAddress(address) {
    return new Promise((resolve, reject) => {
        const geocoder = new google.maps.Geocoder();
        geocoder.geocode({ address: address }, (results, status) => {
            if (status === 'OK') {
                const lat = results[0].geometry.location.lat();
                const lng = results[0].geometry.location.lng();
                resolve({ lat, lng });
            } else {
                reject('Geocode was not successful for the following reason: ' + status);
            }
        });
    });
}
