// static/js/menu.js
$(document).ready(function() {
    // Mobile menu toggle
    $('.cmn-toggle-switch').on('click', function() {
        $('.main-menu').addClass('show-menu');
        $('body').addClass('menu-open');
    });

    // Close menu
    $('.open_close, .main-menu ul li a').on('click', function() {
        $('.main-menu').removeClass('show-menu');
        $('body').removeClass('menu-open');
    });

    // Submenu toggle for mobile
    $('.submenu > a').on('click', function(e) {
        if ($(window).width() < 992) {
            e.preventDefault();
            $(this).next('ul').slideToggle();
            $(this).toggleClass('active');
        }
    });
});