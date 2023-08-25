var count = 5;
var x = setInterval(function() {
    count--;
    document.getElementById("counter").innerHTML = count;
    if (count == 0) {
        count = 6;
        console.log("Refresh");
        loadGraph();
    }
}, 1000);

function loadGraph() {
    fetch('/public_display/{{ number }}')
        .then(response => response.text())

    var gallerySelector = document.getElementsByClassName('gallery__selector');
    var selectedIndex = -1;

    for (var i = 0; i < gallerySelector.length; i++) {
        if (gallerySelector[i].checked) {
            selectedIndex = i;
            break;
        }
    }
    if (selectedIndex >= 0) {
        var link = "/public_display/" + selectedIndex;
        location.href = link;
    }
}