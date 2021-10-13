odoo.define('theme_shopoint.about_us', function (require) {
'use strict';

    $(document).ready(function() {
        $('.about_us_2').removeClass('over');
        function isScrolledIntoView(elem) {
            var scrollTop = $(window).scrollTop();
            var docHeight = scrollTop + $(window).height();

            var elemTop = $(elem).offset().top;
            var elemBottom = elemTop + $(elem).height();

            return ((elemBottom <= docHeight) && (elemTop >= scrollTop));
        }
        $(window).scroll(function(){
            if ($('.about_us_2').length) {
                var res = isScrolledIntoView($('.about_us_2'));
                if (res) {
                    $('.about_us_2:not(.over) .count span').each(function () {
                        $(this).prop('Counter',0).animate({
                            Counter: $(this).text()
                        }, {
                            duration: 4000,
                            easing: 'swing',
                            step: function (now) {
                                $(this).text(Math.ceil(now));
                            }
                        });
                    });
                    $('.about_us_2').addClass('over');
                }
            }
        });
    });
});
