document.addEventListener('DOMContentLoaded', function() {
    const galleries = {
        sauna: [],
        pool: []
    };

    let currentGallery = [];
    let currentIndex = 0;

    function loadGalleryImages() {
        const types = ['sauna', 'pool'];
        types.forEach(type => {
            for (let i = 1; i <= 5; i++) {
                galleries[type].push(`/static/Bilder/${type}/${type}_${i}.jpeg`);
            }
            console.log(`Geladene Bilder für ${type}:`, galleries[type]);
        });
    }

    function openGallery(roomType) {
        console.log(`Öffne Galerie für: ${roomType}`);
        currentGallery = galleries[roomType];
        currentIndex = 0;
        console.log(`Aktuelle Galerie enthält ${currentGallery.length} Bilder`);
        if (currentGallery.length > 0) {
            document.getElementById('gallery-image').src = currentGallery[currentIndex];
            document.getElementById('gallery-popup').style.display = 'block';
        } else {
            alert('Keine Bilder in dieser Galerie gefunden.');
        }
    }

    function closeGallery() {
        document.getElementById('gallery-popup').style.display = 'none';
    }

    function changeImage(direction) {
        currentIndex += direction;
        if (currentIndex < 0) {
            currentIndex = currentGallery.length - 1;
        } else if (currentIndex >= currentGallery.length) {
            currentIndex = 0;
        }
        document.getElementById('gallery-image').src = currentGallery[currentIndex];
    }

    // Attach event listeners to gallery buttons
    document.querySelectorAll('.gallery-button').forEach(button => {
        button.addEventListener('click', function() {
            const roomType = this.getAttribute('data-room-type');
            if (roomType === 'unterkunft') {
                alert('Bit će uskoro objavljeno');
            } else {
                openGallery(roomType);
            }
        });
    });

    // Attach event listeners to navigation buttons and close button
    document.querySelector('.close').addEventListener('click', closeGallery);
    document.querySelector('.nav-button.prev').addEventListener('click', () => changeImage(-1));
    document.querySelector('.nav-button.next').addEventListener('click', () => changeImage(1));

    // Close popup when clicking outside the image
    window.addEventListener('click', function(event) {
        if (event.target == document.getElementById('gallery-popup')) {
            closeGallery();
        }
    });

    // Load images when the page is loaded
    loadGalleryImages();
    console.log('Bilder wurden geladen');
});