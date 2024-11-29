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

const confirmDeleteModal = document.getElementById('confirmDeleteModal');
    confirmDeleteModal.addEventListener('show.bs.modal', function (event) {
        const button = event.relatedTarget; // Botón que activó el modal
        const deleteUrl = button.getAttribute('data-delete-url'); // URL del botón
        const deleteForm = document.getElementById('deleteForm'); // Formulario en el modal
        deleteForm.action = deleteUrl; // Asigna la URL al formulario
    });