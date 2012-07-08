(function ($) {
    "use strict";
    var settings,
        defaults = {

        };


    var methods = {
        init:function (options) {
            settings = $.extend(defaults, options);

            return this.each(function () {
                var $this = $(this),
                    data = $this.data('tripmap'),
                    map = loadMap(this);

                // Save the plugin data against the element
                if (!data) {
                    $(this).data('tripmap', {
                        target: $this,
                        map: map
                    });
                }
            });
        },

        destroy:function () {
            return this.each(function() {
                var $this,
                    data = $this.data('tripmap');

                data.map.remove();
            });
        },

        plotTrip:function () {

        }
    };

    $.fn.tripmap = function (method) {

        // Method calling logic
        if (methods[method]) {
            return methods[ method ].apply(this, Array.prototype.slice.call(arguments, 1));
        } else if (typeof method === 'object' || !method) {
            return methods.init.apply(this, arguments);
        } else {
            $.error('Method ' + method + ' does not exist on jQuery.tooltip');
        }
    };

    /**
     * Loads a Google Map with the given options into the container element
     * @param container DOM element in which to load the map
     * @param options {object} Google Maps API options object
     * @private
     */
    var loadMap = function (container, options) {
        var mapSettings,
            mapDefaults = {
                center: new google.maps.LatLng(-27.4667, 153.0333),
                zoom: 12,
                mapTypeId: google.maps.MapTypeId.ROADMAP
            };
        mapSettings = $.extend(mapDefaults, options);
        return new google.maps.Map(container, mapSettings);
    };
})(jQuery);