const DEFAULT_LAT_LNG = [47, 2.21];
const DEFAULT_ZOOM = 6;
const MAX_ZOOM = 11;
const MIN_ZOOM = 2;
const AUTO_SPIDERFY_ZOOM = 10;
const MAX_CLUSTER_ITEMS = 12;
const MAP_LAYERS = {
    "Carto Light": L.tileLayer(
        "https://{s}.basemaps.cartocdn.com/rastertiles/light_all/{z}/{x}/{y}{r}.png",
        {
            attribution: '&copy; <a href="https://carto.com/basemaps">CartoDB</a>'
        }
    ),
    "Carto Dark": L.tileLayer(
        "https://{s}.basemaps.cartocdn.com/rastertiles/dark_all/{z}/{x}/{y}{r}.png",
        {
            attribution: '&copy; <a href="https://carto.com/basemaps">CartoDB</a>'
        }
    ),
    "Carto Voyager": L.tileLayer(
        "https://{s}.basemaps.cartocdn.com/rastertiles/voyager_labels_under/{z}/{x}/{y}{r}.png",
        {
            attribution: '&copy; <a href="https://carto.com/basemaps">CartoDB</a>'
        }
    ),
    "OpenStreetMap": L.tileLayer(
        "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        {
            attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        }
    ),
}

const UserIcon = L.Icon.extend({
    options: {
        iconSize: [32, 32],
        className: 'user-marker',
    }
});

// https://gist.github.com/hpfast/2fb8de57c356d8c45ce511189eec5d6a
L.TopoJSON = L.GeoJSON.extend({
    addData: function (data) {
        var geojson, key;
        if (data.type === "Topology") {
            for (key in data.objects) {
                if (data.objects.hasOwnProperty(key)) {
                geojson = topojson.feature(data, data.objects[key]);
                L.GeoJSON.prototype.addData.call(this, geojson);
                }
            }
            return this;
        }
        L.GeoJSON.prototype.addData.call(this, data);
        return this;
    }
});

L.topoJson = function (data, options) {
    return new L.TopoJSON(data, options);
};

function createMap(regions, items) {
    const itemsByLocation = new Map();
    const clustersByLocation = new Map();


    const map = L.map("map", {
        fullscreenControl: true,
        fullscreenControlOptions: {
            position: 'topleft',
        },
    });

    map.attributionControl.setPrefix(false);
    map.setMaxBounds([
        [-90, -170],
        [90, 190],
    ]);
    map.setView(DEFAULT_LAT_LNG, DEFAULT_ZOOM);
    map.setZoom(DEFAULT_ZOOM);
    map.setMaxZoom(MAX_ZOOM);
    map.setMinZoom(MIN_ZOOM);

    L.control.resetView({
        position: "topleft",
        title: "Reset view",
        latlng: L.latLng(DEFAULT_LAT_LNG),
        zoom: DEFAULT_ZOOM,
    }).addTo(map);

    MAP_LAYERS["Carto Voyager"].addTo(map);

    function newCluster(layers) {
        const options = {
            maxClusterRadius: 20,
        };

        if (layers.length <= MAX_CLUSTER_ITEMS)
            options.disableClusteringAtZoom = AUTO_SPIDERFY_ZOOM;

        const cluster = L.markerClusterGroup(options);
        cluster.addTo(map);
        for (const layer of layers)
            cluster.addLayer(layer);
        return cluster;
    }

    items.forEach((item) => {
        const key = item.point.latitude + "," + item.point.longitude;
        if (!itemsByLocation.has(key)) {
            itemsByLocation.set(key, []);
        }
        itemsByLocation.get(key).push(item);
    });

    itemsByLocation.forEach((items, key) => {
        const cluster = newCluster(items);
        clustersByLocation.set(key, cluster);
    });

    map.on('zoomend', (e) => {
        const zoom = map.getZoom();

        clustersByLocation.forEach((group) => {
            if (!group.options.disableClusteringAtZoom)
                return;

            const array = group.getLayers();

            if (array.length < 2)
                return;

            for (let i = 0; i < array.length; i++) {
                const latitude = array[i].point.latitude;
                const longitude = array[i].point.longitude;

                if (zoom < AUTO_SPIDERFY_ZOOM) {
                    array[i].setLatLng([latitude, longitude]);
                    continue;
                }

                // set markers in a grid shape
                const rows = 4;
                let row = Math.floor(i / rows);
                const col = i % rows;
                const deltaX = zoom > 10 ? 0.02 : 0.04;
                const deltaY = zoom > 10 ? 0.01 : 0.02;
                row -= array.length / rows / 2;
                const latLng = [
                    latitude + deltaY * row,
                    longitude + deltaX * (col - (rows / 2)),
                ];
                array[i].setLatLng(latLng);
            }
        });

    });


    const region = L.topoJson(null, {
        style: function(feature) {
            return {
                color: 'black',
                opacity: 0.1,
                weight: 1,
                fillColor: 'blue',
                fillOpacity: 0,
                }
            },
            onEachFeature: function(feature, layer) {
                layer.bindPopup(`${feature.properties.dep} - ${feature.properties.libgeo}`);
            }
    }).addTo(map);

    async function loadRegions() {
        const response = await fetch(regions);
        const data = await response.json();

        // remove Droms
        data.features = data.features.filter((feature) => feature.properties.dep < 900);

        region.addData(data);
    }
    loadRegions();

    return map;
}
