document.addEventListener("DOMContentLoaded", function () {
    const menuLinks = document.querySelectorAll(".menu a");

    menuLinks.forEach(link => {
        link.addEventListener("mouseenter", () => {
            link.style.color = "#ff6347"; // Cambia a un color visible (naranja rojizo)
        });
        link.addEventListener("mouseleave", () => {
            link.style.color = ""; // Vuelve al color original definido en CSS
        });
    });
});