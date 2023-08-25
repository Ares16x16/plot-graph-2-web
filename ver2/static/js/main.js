var count = 10;

var x = setInterval(function() {
    count--;
    document.getElementById("counter").innerHTML = count;
    if (count == 0) {
        count = 11;
    }
}, 1000);

function genGraph() {
    fetch('/graph-data')
        .then(response => response.json())
        .then(data => {
            Plotly.react('graph', data);
        })
        .catch(error => console.log(error));
}

function updateGraph() {
    fetch('/update-graph', {
        method: 'POST',
    })
    .then(response => response.json())
    .then(data => {
        Plotly.react('graph', data.data, data.layout);
    })
    .catch(error => {
        console.error('Error updating graph:', error);
    });
}

genGraph();
setTimeout( updateGraph, 10000);
//setInterval(updateGraph, 5000); 