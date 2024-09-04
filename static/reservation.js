document.addEventListener('DOMContentLoaded', function() {
    const calendar = document.getElementById('calendar');
    const popup = document.getElementById('bookingPopup');
    const closeBtn = document.getElementsByClassName('close')[0];
    const bookingForm = document.getElementById('bookingForm');
    const dateInput = document.getElementById('date');
    const prevMonthBtn = document.getElementById('prevMonth');
    const nextMonthBtn = document.getElementById('nextMonth');
    const currentMonthSpan = document.getElementById('currentMonth');
    const popupTitle = document.querySelector('#bookingPopup h2');

    let currentDate = new Date();
    const daysOfWeek = ['Pon', 'Uto', 'Sri', 'Čet', 'Pet', 'Sub', 'Ned'];
    const monthsInBosnian = [
        'Januar', 'Februar', 'Mart', 'April', 'Maj', 'Juni',
        'Juli', 'August', 'Septembar', 'Oktobar', 'Novembar', 'Decembar'
    ];

    function createCalendar(year, month, bookedDates) {
        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);
        const today = new Date();

        currentMonthSpan.textContent = `${monthsInBosnian[month]} ${year}`;

        let html = '<table>';
        html += '<tr>' + daysOfWeek.map(day => `<th>${day}</th>`).join('') + '</tr>';

        let day = 1;
        const totalDays = lastDay.getDate();
        const firstDayOfWeek = (firstDay.getDay() + 6) % 7; // Adjust for Monday start

        for (let i = 0; i < 6; i++) {
            html += '<tr>';
            for (let j = 0; j < 7; j++) {
                if (i === 0 && j < firstDayOfWeek) {
                    html += '<td></td>';
                } else if (day > totalDays) {
                    html += '<td></td>';
                } else {
                    const currentDate = new Date(year, month, day);
                    const dateString = currentDate.toISOString().split('T')[0];
                    const isBooked = bookedDates.includes(dateString);
                    const isPast = currentDate < new Date(today.setHours(0,0,0,0));
                    const isToday = currentDate.toDateString() === today.toDateString();
                    
                    let className = isBooked ? 'booked' : 'available';
                    if (isPast) className = 'past';
                    if (isToday) className += ' today';

                    html += `<td class="${className}" data-date="${dateString}">${day}</td>`;
                    day++;
                }
            }
            html += '</tr>';
            if (day > totalDays) break;
        }

        html += '</table>';
        calendar.innerHTML = html;

        // Add click event to available dates
        const availableDates = calendar.querySelectorAll('.available');
        availableDates.forEach(date => {
            date.addEventListener('click', function() {
                const selectedDate = new Date(this.dataset.date);
                dateInput.value = this.dataset.date;
                updatePopupTitle(selectedDate);
                popup.style.display = 'block';
            });
        });
    }
    function updatePopupTitle(date) {
        const month = date.getMonth() + 1; // JavaScript months are 0-indexed
        const day = date.getDate();
        
        if ((month === 6 && day >= 1) || month === 7 || month === 8 || (month === 9 && day <= 15)) {
            popupTitle.textContent = 'Rezervacija - Ljetna Sezona';
        } else {
            popupTitle.textContent = 'Rezervacija - Zimska Sezona';
        }
    }

    function updateCalendar() {
        fetch('/get-booked-dates')
            .then(response => response.json())
            .then(bookedDates => {
                createCalendar(currentDate.getFullYear(), currentDate.getMonth(), bookedDates);
            });
    }

    updateCalendar();

    prevMonthBtn.addEventListener('click', function() {
        currentDate.setMonth(currentDate.getMonth() - 1);
        updateCalendar();
    });

    nextMonthBtn.addEventListener('click', function() {
        currentDate.setMonth(currentDate.getMonth() + 1);
        updateCalendar();
    });

    closeBtn.onclick = function() {
        popup.style.display = 'none';
        popupTitle.textContent = 'Rezervacija'; // Reset the title
    }

    window.onclick = function(event) {
        if (event.target == popup) {
            popup.style.display = 'none';
            popupTitle.textContent = 'Rezervacija'; // Reset the title
        }
    }

    bookingForm.onsubmit = function(e) {
        e.preventDefault();
        const name = document.getElementById('name').value;
        const email = document.getElementById('email').value;
        const time = document.getElementById('time').value;
        const persons = document.getElementById('persons').value;
        const requests = document.getElementById('requests').value;

        fetch('/book', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name,
                email,
                date: dateInput.value,
                time,
                persons,
                requests
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
            } else {
                alert(`Rezervacija potvrđena za ${dateInput.value} u ${time} za ${persons} osoba(e).`);
                popup.style.display = 'none';
                updateCalendar();
                bookingForm.reset();
            }
        })
        .catch((error) => {
            console.error('Error:', error);
            alert('Došlo je do greške prilikom obrade vaše rezervacije. Molimo pokušajte ponovo.');
        });
    }

    // Funktion zum Stornieren einer Buchung (für Administratoren)
    function cancelBooking(date) {
        fetch('/cancel-booking', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ date: date }),
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            updateCalendar();
        })
        .catch((error) => {
            console.error('Error:', error);
            alert('Greška prilikom otkazivanja rezervacije');
        });
    }

  
});