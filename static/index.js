var nameFilterElement = document.getElementById('teamName');
var winOrLoseFilterElement = document.getElementById('winOrLoseOption');

function refreshTable() {
    console.log("refreshing table");
    const parts = window.location.pathname.split("/");
    const guildId = parts[parts.length - 1];

    var currentNameFilter = nameFilterElement.value;
    var currentWinOrLoseFilter = winOrLoseFilterElement.value;

    var queryParams = [];
    if (currentNameFilter) {
        queryParams.push("name=" + currentNameFilter);
    }
    if (currentWinOrLoseFilter) {
        queryParams.push("filter=" + currentWinOrLoseFilter);
    }
    var query = queryParams.join("&");
    var url = `/api/guild/results/${guildId}?${query}`;

    fetch(url)
        .then(response => response.json())
        .then(data => updateTable(data.data))
        .catch(error => console.log(error));
}

function updateTable(data) {
    var newBody = document.createElement('tbody');
    data.forEach(result => {
        var row = document.createElement('tr');
        var idx = document.createElement('td');
        var name = document.createElement('td');
        var date = document.createElement('td');
        var scores = document.createElement('td');
        var diff = document.createElement('td');

        idx.innerHTML = result.idx;
        name.innerHTML = result.enemy;
        date.innerHTML = result.date;
        scores.innerHTML = `${result.score} - ${result.enemyScore}`;

        var msg = "Draw";
        if (result.diff > 0) {
            msg = `Win (+${result.diff})`;
            diff.style.color = "red";
        }
        else if (result.diff < 0) {
            msg = `Lose (${result.diff})`;
            diff.style.color = "skyblue";
        }
        diff.innerHTML = msg;

        row.appendChild(idx);
        row.appendChild(name);
        row.appendChild(date);
        row.appendChild(scores);
        row.appendChild(diff);

        newBody.appendChild(row);
    });
    var tBody = document.getElementById('resultTableBody');
    tBody.parentElement.replaceChild(newBody, tBody);
    newBody.id = 'resultTableBody';

    document.getElementById('resultTable').classList.remove("d-none");
}

var nameFilter = undefined;
function refreshOnNewNameFilter() {
    var currentNameFilter = nameFilterElement.value;
    if (currentNameFilter !== nameFilter) {
        if (nameFilter !== undefined)
            refreshTable();
        nameFilter = currentNameFilter;
    }
    setTimeout(refreshOnNewNameFilter, 1000);
}


document.addEventListener("DOMContentLoaded", function (event) {
    refreshTable();
    refreshOnNewNameFilter();
});