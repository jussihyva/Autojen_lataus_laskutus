document.addEventListener('DOMContentLoaded', function () {
    fetch('/api/getParkingPlaces')
      .then(response => response.json())
      .then(data => {
        const tableBody = document.getElementById('data-table').querySelector('tbody');
        data.forEach(item => {
          const row = document.createElement('tr');
          row.innerHTML = `
            <td>${item.Autopaikka}</td>
          `;
          tableBody.appendChild(row);
        });
      })
      .catch(error => console.error('Error fetching data:', error));
  });
