function redirect() {
    const param = window.location.href.split('/');
    const prevId = param[param.length-1].replace("?","");
    const guildId = document.getElementById('guildId').value;
    if (prevId==guildId) {
        alert("同じサーバーです");
        return;
    }
    const url = `/api/guild/results/${guildId}`
    fetch(url)
        .then(response => {
            if (response.ok) {
                window.location.reload(`/guild/details/${guildId}`);
            } else {
                alert("戦績が存在しません");
            }
        })
}