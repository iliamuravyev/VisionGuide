document.addEventListener('DOMContentLoaded', () => {
    const menuBtn = document.querySelector('.menu-btn');
    const sideMenu = document.getElementById('side-menu');
    const closeMenuBtn = document.getElementById('close-menu-btn');
    const menuOverlay = document.getElementById('menu-overlay');

    // Функция для открытия меню
    function openMenu() {
        sideMenu.classList.add('active');
        menuOverlay.classList.add('active');
        document.body.style.overflow = 'hidden'; // Запрещаем прокрутку сайта
    }

    // Функция для закрытия меню
    function closeMenu() {
        sideMenu.classList.remove('active');
        menuOverlay.classList.remove('active');
        document.body.style.overflow = ''; // Возвращаем прокрутку
    }

    // Обработчики событий
    menuBtn.addEventListener('click', openMenu);
    closeMenuBtn.addEventListener('click', closeMenu);
    menuOverlay.addEventListener('click', closeMenu); // Закрытие при клике на темную область
});
