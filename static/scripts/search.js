// static/js/search.js

function searchTable() {
  const input = document.getElementById("searchInput");
  const filter = input.value.toUpperCase();
  const table = document.getElementById("inventoryTable");
  const tr = table.getElementsByTagName("tr");

  // Başlık satırını atlamak için 1'den başla
  for (let i = 1; i < tr.length; i++) {
    let found = false;
    const td = tr[i].getElementsByTagName("td");
    
    for (let j = 0; j < td.length; j++) {
      if (td[j]) {
        const txtValue = td[j].textContent || td[j].innerText;
        if (txtValue.toUpperCase().indexOf(filter) > -1) {
          found = true;
          break;
        }
      }
    }
    
    tr[i].style.display = found ? "" : "none";
  }
}

// Sayfa yüklendiğinde arama çubuğuna event listener ekle
document.addEventListener('DOMContentLoaded', function() {
  const searchInput = document.getElementById('searchInput');
  if (searchInput) {
    searchInput.addEventListener('keyup', searchTable);
  }
});