document.addEventListener("DOMContentLoaded", function () {
    const selectAllButton = document.getElementById("select-all");
    const playlistCards = document.querySelectorAll(".playlist-card");
    const checkboxes = document.querySelectorAll(".checkbox");
  
    // Handle "Select All" button
    selectAllButton.addEventListener("click", function () {
      const allSelected = [...checkboxes].every((checkbox) => checkbox.checked);
      checkboxes.forEach((checkbox) => {
        checkbox.checked = !allSelected;
        const card = checkbox.closest(".playlist-card");
        card.classList.toggle("selected", !allSelected);
      });
    });
  
    // Handle individual playlist card clicks
    playlistCards.forEach((card) => {
      card.addEventListener("click", function () {
        const checkbox = card.querySelector(".checkbox");
        checkbox.checked = !checkbox.checked; // Toggle checkbox state
        card.classList.toggle("selected", checkbox.checked); // Toggle "selected" class
      });
    });
  });
  