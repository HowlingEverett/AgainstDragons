{% autoescape off %}
{% block vars %}var geodjango = {};
{% endblock vars %}{% block functions %}
{% block load %}{{ js_module }}.{{ dom_id }}_load = function(){
  var map_options = {
    zoom: {{ zoom }},
    {% if max_zoom %}maxZoom: {{ max_zoom }},{% endif %}
    {% if min_zoom %}minZoom: {{ min_zoom }},{% endif %}
    {% if overview_map_control %}overviewMapControl: true,{% endif %}
    {% if pan_control %}panControl: true,{% endif %}
    {% if disable_double_click_zoom %}disableDoubleClickZoom: true,{% endif %}
    center: google.maps.LatLng({{ center.1 }}, {{ center.0 }}),
    mapTypeId: google.maps.MapTypeId.ROADMAP
  }
  {{ js_module }}.{{ dom_id }} = new google.maps.Map(document.getElementById("{{ dom_id }}"), map_options);
  {% block controls %}{% endblock %}
  {% if calc_zoom %}var bounds = new google.maps.LatLngBounds(); var i; var j;{% endif %}
  {% for kml_url in kml_urls %}{{ js_module }}.{{ dom_id }}_kml{{ forloop.counter }} = new google.maps.KmlLayer("{{ kml_url }}");
  {{ js_module }}.{{ dom_id }}_kml{{ forloop.counter }}.setMap({{ js_module }}.{{ dom_id }});{% endfor %}
  {% for polygon in polygons %}{{ js_module }}.{{ dom_id }}_poly{{ forloop.counter }} = new {{ polygon }};
  {{ js_module }}.{{ dom_id }}_poly{{ forloop.counter }}.setMap({{ js_module }}.{{ dom_id }});
  {% for event in polygon.events %}google.event.addListener({{ js_module }}.{{ dom_id }}_poly{{ forloop.parentloop.counter }}, {{ event }});{% endfor %}
  {% if calc_zoom %}paths={{ js_module }}.{{ dom_id }}_polyline{{ forloop.counter }}.getPaths(); for(i=0; i<paths.length(); i++){ for(j=0; j<paths[i].length(); j++){ bounds.extend(paths[i][j]); }}{% endif %}{% endfor %}  
  {% for polyline in polylines %}{{ js_module }}.{{ dom_id }}_polyline{{ forloop.counter }} = new google.maps.Polyline({{ polyline.latlngs }}, {{ polyline.color }}, {{ polyline.weight }}, {{ polyline.opacity }});
  {{ js_module }}.{{ dom_id }}_polyline{{ forloop.counter }}.setMap({{ js_module }}.{{ dom_id }});
  {% for event in polyline.events %}GEvent.addListener({{ js_module }}.{{ dom_id }}_polyline{{ forloop.parentloop.counter }}, {{ event }}); {% endfor %}
  {% if calc_zoom %}path={{ js_module }}.{{ dom_id }}_polyline{{ forloop.counter }}.getPath(); for(i=0; i<path.length(); i++){ bounds.extend(path[i]); }{% endif %}{% endfor %}
  {% for marker in markers %}{{ js_module }}.{{ dom_id }}_marker{{ forloop.counter }} = new {{ marker }};
  {{ js_module }}.{{ dom_id }}_marker{{ forloop.counter }}.setMap({{ js_module }}.{{ dom_id }});
  {% for event in marker.events %}GEvent.addListener({{ js_module }}.{{ dom_id }}_marker{{ forloop.parentloop.counter }}, {{ event }}); {% endfor %}
  {% if calc_zoom %}bounds.extend({{ js_module }}.{{ dom_id }}_marker{{ forloop.counter }}.getPosition());{% endif %}{% endfor %}
  {% if calc_zoom %}{{ js_module }}.{{ dom_id }}.fitBounds(bounds);{% endif %}
  {% block load_extra %}{% endblock %}
}
{% endblock load %}{% endblock functions %}{% endautoescape %}